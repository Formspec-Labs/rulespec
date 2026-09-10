"""Resolve document definitions and uses without equating matching labels."""
from collections import Counter

from jsonschema import Draft202012Validator, ValidationError


def term_identity(document, claim, term):
    from .core import NS, digest, _evidence
    support = _evidence(document, term['quote'], 'definition', within=(claim['start'], claim['end']))
    if support is None:
        raise ValueError('Term definition needs exact, unambiguous source evidence')
    if term.get('id'):
        if not term['id'].startswith(NS + 'term:'):
            raise ValueError('Local term identity must use the document-understanding term namespace')
        return term['id']
    return NS + 'term:' + digest([document['id'], support['start'], support['end'],
                                  term['label'], claim['summary']])


def definition_error(claim, term):
    from .core import NS
    if term.get('id') and not term['id'].startswith(NS + 'term:'):
        return 'Local term identity must use the document-understanding term namespace'
    if claim['kind'] != 'definition':
        return 'A term must be attached to a defining claim'
    text = '\n'.join([term['quote'], *term['source_quotes']]).casefold()
    if any(label.casefold() not in text for label in [term['label'], *term['aliases']]):
        return 'The defined name or an alias is absent from its source support'
    return None


def resolve_components(document, window, terms, rows, *, existing_claims=()):
    """Add grounded definitions/IRIs; retain per-component failures and raw data.

    rows contains (candidate, original model attributes, original row index).
    Invalid registry entries never erase an otherwise valid extracted statement.
    """
    from . import extraction as e
    errors, resolved = [], {}
    existing = {(c['rule_id'], t['label'], t['quote']): term_identity(document, c, t)
                for c in existing_claims for t in c.get('defined_terms', [])}
    if not isinstance(terms, list):
        return [{'code': 'invalid_term_registry', 'raw': terms, 'disposition': 'component_withheld'}]
    schema = e.load_schema('provider')['properties']['terms']['items']
    validator = Draft202012Validator(schema)
    counts = Counter(t.get('id') for t in terms if isinstance(t, dict) and isinstance(t.get('id'), str))
    catalog = e.passage_catalog(document, window)
    for term in terms:
        try:
            validator.validate(term)
            key = term['id']
            if counts[key] != 1:
                raise ValueError('Duplicate local term ID')
            definitions = [(c, i) for c, attrs, i in rows if attrs.get('defines_term') == key]
            if len(definitions) != 1:
                raise ValueError('Term needs exactly one accepted defining unit in this source window')
            claim, _ = definitions[0]
            sources = [e.resolve_passage(ref, catalog, document)['quote'] for ref in term['source_refs']]
            if not sources:
                raise ValueError('Term needs definition and name evidence')
            stored = {'label': term['label'], 'aliases': term['aliases'],
                      'quote': claim['quote'], 'source_quotes': list(dict.fromkeys(sources))}
            if identity := existing.get((claim.get('rule_id'), stored['label'], stored['quote'])):
                stored['id'] = identity
            if error := definition_error(claim, stored):
                raise ValueError(error)
            identity = term_identity(document, claim, stored)
            stored['id'] = identity
            claim.setdefault('defined_terms', []).append(stored)
            resolved[key] = identity
        except (ValueError, TypeError, KeyError) as exc:
            errors.append({'code': 'term_definition_unresolved', 'message': str(exc),
                           'raw': term, 'disposition': 'component_withheld'})
        except ValidationError:
            errors.append({'code': 'invalid_term_definition', 'raw': term, 'disposition': 'component_withheld'})
    for candidate, attrs, index in rows:
        refs = list(attrs.get('term_refs') or [])
        defined = attrs.get('defines_term')
        if defined and defined not in resolved:
            errors.append({'code': 'defined_term_unresolved', 'row_index': index,
                           'raw': defined, 'disposition': 'component_withheld'})
        for ref in dict.fromkeys(refs):
            if ref == defined:
                continue
            if ref in resolved:
                candidate.setdefault('term_refs', []).append(resolved[ref])
            else:
                errors.append({'code': 'term_reference_unresolved', 'row_index': index,
                               'raw': ref, 'disposition': 'component_withheld'})
    return errors


def definition_records(document, claim):
    """Only source-validated definitions participate in navigation or the graph."""
    evidence = {item['field']: item for item in claim['evidence']}
    for i, term in enumerate(claim.get('defined_terms', [])):
        keys = [f'defined_terms:{i}', *[f'defined_terms:{i}:source:{j}' for j in range(len(term['source_quotes']))]]
        if definition_error(claim, term) or any(key not in evidence for key in keys):
            continue
        yield {'id': term_identity(document, claim, term), 'label': term['label'],
               'aliases': term['aliases'], 'definition': claim['summary'], 'claim_id': claim['id'],
               'evidence': [evidence[key] for key in keys]}


def term_index(document, claims):
    return {term['id']: term for claim in claims for term in definition_records(document, claim)}


def term_lookup(book):
    """Current senses and named historical targets, with availability explicit."""
    current = term_index(book['document'], book['accepted'])
    history = term_index(book['document'], book.get('revisions', []))
    rejected = {c['id'] for c in book.get('rejected', []) if c.get('id')}
    result = {key: {**term, 'status': 'unavailable',
                    'reason': 'Definition rejected' if term['claim_id'] in rejected else 'Definition replaced'}
              for key, term in history.items() if key not in current}
    result.update({key: {**term, 'status': 'available'} for key, term in current.items()})
    for claim in book['accepted']:
        for key in claim.get('term_refs', []):
            result.setdefault(key, {'id': key, 'status': 'unavailable', 'reason': 'Definition not recorded'})
    return result


def term_link_issues(document, claims):
    index = term_index(document, claims)
    return [{'claim_id': claim['id'], 'code': 'term_target_unavailable', 'field': 'term_refs',
             'term_id': ref, 'message': 'The defining claim is unavailable, rejected or changed.'}
            for claim in claims for ref in claim.get('term_refs', []) if ref not in index]


def add_term_graph(document, claim, disposition, add):
    from .core import NS, assertion_id, digest
    scheme_id = NS + 'defined-term-scheme:' + document['sha256']
    definitions = list(definition_records(document, claim))
    if definitions:
        add({'@id': scheme_id, '@type': 'rkaf:ConceptScheme',
             'skos:prefLabel': {'en': 'Defined terms'}, 'rkaf:schemeFacet': NS + 'defined-terms',
             'rkaf:definedInScope': document['id']})
    def relationship(predicate, target, evidence):
        proposition = {'rkaf:assertsSubject': claim['rule_id'], 'rkaf:assertsPredicate': NS + predicate,
                       'rkaf:assertsObject': target, 'rkaf:assertionPolarity': 'rkaf:affirmed'}
        identity = assertion_id(proposition)
        add({'@id': identity, '@type': 'rkaf:RelationshipAssertion', **disposition, **proposition})
        fragments = list(dict.fromkeys(item['fragment_id'] for item in evidence))
        add({'@id': NS + 'binding:' + digest([identity, fragments, claim['occurrence_id']]),
             '@type': 'rkaf:EvidenceBinding', 'rkaf:bindsAssertion': identity,
             'rkaf:bindsSourceFragment': fragments, 'rkaf:evidenceRole': 'rkaf:textualEvidence',
             'rkaf:evidentiaryFunction': 'rkaf:supports'})
        claim['assertion_ids'].append(identity)
    for term in definitions:
        node = {'@id': term['id'], '@type': 'rkaf:LocalConcept',
                'skos:prefLabel': {'en': term['label']}, 'skos:definition': {'en': term['definition']},
                'skos:inScheme': scheme_id, 'rkaf:definedInScope': document['id'],
                'rkaf:conceptScope': document['id']}
        if term['aliases']:
            node['skos:altLabel'] = {'en': term['aliases']}
        add(node)
        relationship('defines', term['id'], term['evidence'])
    main = [item for item in claim['evidence'] if item['field'] == 'summary']
    for ref in dict.fromkeys(claim.get('term_refs', [])):
        relationship('uses-term', ref, main)
