"""Source-bound terms, immutable enrichment and current versus historical links."""
from copy import deepcopy
import json

import pytest

from rulespec_extrapolator import extraction as e, structure as s
from rulespec_extrapolator.core import compile_candidates, digest, validate_graph
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore
from rulespec_extrapolator.terms import term_index
from rulespec_extrapolator.discovery import export_discovery
from test_audit import provider
from test_review_store import action

TEXT = 'Record notice (RN) means a receipt.\n\nPosts must retain the RN unless it is withdrawn.'


def output():
    return {'terms': [{'id': 'T1', 'label': 'Record notice', 'aliases': ['RN'], 'source_refs': ['F000']}],
            'extractions': [
                {'unit': 'F000', 'unit_attributes': {'defines_term': 'T1', 'term_refs': ['T1'],
                    'statement': TEXT.splitlines()[0], 'kind': 'definition', 'modality': 'not_stated', 'actor': None, 'actor_quote': None}},
                {'unit': 'F001', 'unit_attributes': {'term_refs': ['T1'], 'statement': TEXT.splitlines()[-1],
                    'kind': 'requirement', 'modality': 'must', 'actor': 'Posts', 'actor_quote': 'Posts'}}]}


def compile_output(payload=None):
    doc = prepare_document(TEXT)
    window, = e.plan_windows(doc)
    parsed = e.parse_response_text(json.dumps(payload or output()), doc, window)
    return compile_candidates(doc, parsed['candidates'], {}), parsed


def workspace(tmp_path, *, enriched=False):
    book, _ = compile_output()
    if not enriched:
        candidates = [{k: v for k, v in c.items() if k in e.core.CANDIDATE_SCHEMA['properties']}
                      for c in book['accepted']]
        for c in candidates:
            c.update(actor='', actor_quote='', defined_terms=[], term_refs=[])
        book = compile_candidates(book['document'], candidates, {})
    root = tmp_path / 'workspace'
    root.mkdir()
    for name, data in [('document.json', book['document']), ('run.json', book['run']), ('rulebook.json', book)]:
        e._save(root / name, data)
    return root


def enrichment():
    return {'terms': output()['terms'], 'enrichments': [
        {'claim_id': 'C0000', 'actor': None, 'actor_quote': None, 'defines_term': 'T1', 'term_refs': ['T1']},
        {'claim_id': 'C0001', 'actor': 'Posts', 'actor_quote': 'Posts', 'defines_term': None, 'term_refs': ['T1']}]}


def test_parser_connects_names_aliases_and_exact_core_evidence():
    book, parsed = compile_output()
    assert not parsed['refusals'] and not book['rejected']
    terms = term_index(book['document'], book['accepted'])
    term, = terms.values()
    assert term['label'] == 'Record notice' and term['aliases'] == ['RN']
    assert book['accepted'][1]['term_refs'] == [term['id']]
    validate_graph(book['graph'])
    nodes = book['graph']['@graph']
    assert any(n['@type'] == 'rkaf:LocalConcept' and n['@id'] == term['id'] for n in nodes)
    assert any(n.get('rkaf:assertsObject') == term['id'] for n in nodes)
    discovery = export_discovery(book)
    assert discovery['terms'][term['id']]['label'] == term['label']
    support, = [r for r in discovery['statements'][1]['evidence_refs'] if 'actor' in r['roles']]
    span = discovery['evidence'][support['id']]
    assert book['document']['text'][span['start']:span['end']] == 'Posts'


@pytest.mark.parametrize('mutation,code', [
    (lambda p: p['terms'].append(deepcopy(p['terms'][0])), 'term_definition_unresolved'),
    (lambda p: p['terms'][0].update(aliases=['invented expansion']), 'term_definition_unresolved'),
    (lambda p: p['terms'][0].update(source_refs=['F999']), 'term_definition_unresolved'),
    (lambda p: p['extractions'][1]['unit_attributes'].update(term_refs=['unknown']), 'term_reference_unresolved'),
    (lambda p: p['extractions'][0]['unit_attributes'].update(defines_term=None), 'term_definition_unresolved'),
])
def test_bad_registry_withholds_components_without_losing_statements(mutation, code):
    payload = output(); mutation(payload)
    book, parsed = compile_output(payload)
    assert len(book['accepted']) == 2
    assert code in {r['code'] for r in parsed['refusals']}
    assert all('raw' in r for r in parsed['refusals'])


def test_equal_acronyms_do_not_merge_different_definitions():
    doc = prepare_document('Record notice (RN) means a receipt.\n\nRecord notice (RN) means an archive entry.')
    candidates = []
    for quote in doc['text'].split('\n\n'):
        candidates.append({'quote': quote, 'summary': quote, 'kind': 'definition', 'modality': 'not_stated', 'actor': '',
                           'defined_terms': [{'label': 'Record notice', 'aliases': ['RN'], 'quote': quote, 'source_quotes': [quote]}]})
    book = compile_candidates(doc, candidates, {})
    assert len(term_index(doc, book['accepted'])) == 2


@pytest.mark.parametrize('operation', ['reject', 'replace'])
def test_replaced_or_rejected_definition_marks_current_link_unresolved(tmp_path, operation):
    store = ReviewStore(workspace(tmp_path, enriched=True))
    before = store.snapshot(); definition = before['accepted'][0]
    term_id, = before['terms']
    fields = {'summary': 'A record notice is a receipt.',
              'defined_terms': [{k: v for k, v in t.items() if k != 'id'} for t in definition['defined_terms']]}
    kwargs = {'replacements': [fields]} if operation == 'replace' else {}
    after = store.apply(action(before, 'edit' if operation == 'replace' else operation, [definition['id']], **kwargs))
    assert term_id not in after['terms']
    assert any(i['code'] == 'term_target_unavailable' for i in after['unresolved'])
    assert any(n['@id'] == term_id for n in after['graph']['@graph'])
    assert ReviewStore(store.run_dir).snapshot() == after


def test_editorial_definition_and_alias_changes_preserve_links_and_history(tmp_path):
    store = ReviewStore(workspace(tmp_path, enriched=True))
    before = store.snapshot(); definition = before['accepted'][0]
    term_id, = before['terms']
    terms = deepcopy(definition['defined_terms']); terms[0]['aliases'] = []
    after = store.apply(action(before, 'edit', [definition['id']], replacements=[{
        'summary': 'A record notice is a receipt.', 'defined_terms': terms}]))
    assert after['terms'][term_id]['definition'] == 'A record notice is a receipt.'
    assert after['terms'][term_id]['aliases'] == []
    assert not after['unresolved']
    use = next(c for c in after['accepted'] if c['rule_id'] == before['accepted'][1]['rule_id'])
    assert use['term_refs'] == [term_id]
    node, = [n for n in after['graph']['@graph'] if n['@id'] == term_id]
    assert node['skos:definition']['en'] == after['terms'][term_id]['definition']
    assert 'skos:altLabel' not in node
    assert after['revisions'][0]['defined_terms'][0]['aliases'] == ['RN']
    assert ReviewStore(store.run_dir).snapshot() == after


def test_concept_scope_is_document_scoped_rdf_text_and_definition_has_no_self_use():
    import rdflib
    from rulespec_extrapolator.core import canonical
    book, _ = compile_output()
    graph = rdflib.Graph().parse(data=canonical(book['graph']), format='json-ld')
    scope, = graph.objects(None, rdflib.URIRef('https://rulespec.org/ns/v1#conceptScope'))
    assert isinstance(scope, rdflib.Literal)
    assert str(scope) == book['document']['id']
    assert scope.datatype == rdflib.XSD.string
    assert book['accepted'][0]['term_refs'] == []


def test_enrichment_adds_missing_reference_to_nonempty_list(tmp_path):
    book = ReviewStore(workspace(tmp_path)).snapshot()
    book['accepted'][1]['term_refs'] = ['urn:existing:term']
    window, = e.plan_windows(book['document'])
    changes, issues = s.changes_for(book, window, enrichment())
    assert not issues
    fields = next(c['fields'] for c in changes if c['target'] == book['accepted'][1]['id'])
    assert fields['term_refs'][0] == 'urn:existing:term'
    assert len(fields['term_refs']) == 2


def test_unlocated_component_retains_context_without_claiming_hypothesis():
    from rulespec_extrapolator.core import NS
    doc = prepare_document('Staff must log notices.')
    book = compile_candidates(doc, [{'kind': 'requirement', 'modality': 'must',
        'summary': doc['text'], 'quote': doc['text'], 'actor': 'Staff', 'actor_quote': 'missing'}], {})
    claim, = book['accepted']
    assert any(i['field'] == 'actor' for i in claim['issues'])
    nodes = book['graph']['@graph']
    actor, = [n for n in nodes if n.get('rkaf:assertsPredicate') == NS + 'actor']
    binding, = [n for n in nodes if n.get('rkaf:bindsAssertion') == actor['@id']]
    assert binding['rkaf:evidentiaryFunction'] == 'rkaf:providesContext'
    assert not any('rkaf:noEvidenceReason' in n for n in nodes)
    validate_graph(book['graph'])


def test_enrichment_preserves_prior_values_and_refuses_rewrites_and_wrong_ids(tmp_path):
    book = ReviewStore(workspace(tmp_path, enriched=True)).snapshot()
    window, = e.plan_windows(book['document'])
    payload = enrichment(); payload['enrichments'][1].update(actor='Approver', actor_quote='Posts')
    changes, issues = s.changes_for(book, window, payload)
    assert changes == [] and any(i['code'] == 'existing_component_preserved' for i in issues)
    payload['enrichments'][0]['summary'] = 'Invented rewrite'
    assert s.changes_for(book, window, payload)[0] == []
    for ids in [('C0000', 'C0000'), ('C0000', 'unknown')]:
        payload = enrichment()
        for row, key in zip(payload['enrichments'], ids): row['claim_id'] = key
        assert s.changes_for(book, window, payload)[1][0]['code'] == 'claim_ids_not_exactly_once'


def test_captured_enrichment_retains_approval_and_all_old_meaning_then_replays(tmp_path, monkeypatch):
    root = workspace(tmp_path)
    store = ReviewStore(root); initial = store.snapshot()
    before = store.apply(action(initial, 'approve', [initial['accepted'][1]['id']]))
    original_files = {p.name: p.read_bytes() for p in root.glob('*.json')}
    env, requests = provider(monkeypatch, tmp_path, [enrichment()])
    result = s.enrich_run(root, tmp_path / 'enrich', env_file=env)
    assert result['status'] == 'complete' and result['applied_actions'] == 2
    after = store.snapshot()
    assert after['history'][:1] == before['history']
    for old, new in zip(before['accepted'], after['accepted']):
        for field in e.core.CANDIDATE_SCHEMA['properties']:
            if field not in s.FIELDS: assert old.get(field) == new.get(field), field
        assert new['review_status'] == 'pending'
    assert original_files == {p.name: p.read_bytes() for p in root.glob('*.json')}
    assert after['accepted'][1]['actor'] == 'Posts' and len(after['terms']) == 1
    event = after['history'][-1]
    provenance = event['provenance']
    assert provenance['model_version'] == 'gemini-3.8-flash'
    assert provenance['input_sha256'] == digest(requests[0]['contents'])
    assert provenance['request_sha256'] == digest(requests[0])
    assert any(n.get('rkaf:inputContextHash') == 'sha256:' + provenance['input_sha256']
               and n.get('rkaf:modelVersion') == provenance['model_version'] for n in after['graph']['@graph'])
    assert len(requests) == 1
    monkeypatch.setattr(e, '_create_model', lambda *args: pytest.fail('Replay called provider'))
    assert s.replay_enrichment(tmp_path / 'enrich', tmp_path / 'replay')['provider_calls'] == 0


def test_unsupported_actor_evidence_is_retained_as_issue(tmp_path):
    book = ReviewStore(workspace(tmp_path)).snapshot()
    window, = e.plan_windows(book['document'])
    payload = enrichment(); payload['enrichments'][1]['actor_quote'] = 'Imaginary authority'
    changes, issues = s.changes_for(book, window, payload)
    assert all('actor' not in c['fields'] for c in changes)
    assert any(i['code'] == 'actor_evidence_unresolved' and i['raw']['actor_quote'] == 'Imaginary authority' for i in issues)


def test_withheld_actor_is_visible_on_current_revision_and_replays(tmp_path, monkeypatch):
    root = workspace(tmp_path)
    payload = enrichment(); payload['enrichments'][1]['actor_quote'] = 'Imaginary authority'
    env, _ = provider(monkeypatch, tmp_path, [payload])
    result = s.enrich_run(root, tmp_path / 'enrich', env_file=env)
    after = ReviewStore(root).snapshot()
    claim = next(c for c in after['accepted'] if c['kind'] == 'requirement')
    assert not claim['actor']
    issue = next(i for i in claim['issues'] if i['code'] == 'actor_evidence_unresolved')
    assert issue['capture'] == 'step-0000/result.json'
    assert issue['raw']['actor_quote'] == 'Imaginary authority'
    assert result['recorded_observations'] == 1
    assert any(n.get('rkaf:subject') == claim['id'] and n['@type'] == 'rkaf:Finding' for n in after['graph']['@graph'])
    validate_graph(after['graph'])
    assert s.replay_enrichment(tmp_path / 'enrich', tmp_path / 'replay')['recorded_observations'] == 1


def test_audit_supplies_out_of_window_definition_lookup_without_opaque_term_ids():
    from rulespec_extrapolator import audit
    book, _ = compile_output()
    use = book['accepted'][1]
    window = {'id': 'use-only', 'start': use['start'], 'end': use['end'], 'context_spans': []}
    packet = audit._comparison_model_input(book, {'expected_units': []}, window)
    assert list(packet['claims']) == ['C0001']
    alias, = packet['claims']['C0001']['term_refs']
    assert packet['terms'][alias]['label'] == 'Record notice'
    assert packet['terms'][alias]['definition'] == book['accepted'][0]['summary']
    assert packet['terms'][alias]['status'] == 'available'
    assert use['term_refs'][0] not in json.dumps(packet)


def test_discovery_uses_shared_evidence_preserves_identity_and_omits_absent_values():
    book, _ = compile_output()
    exported = export_discovery(book)
    for original, statement in zip(book['accepted'], exported['statements']):
        assert statement['rule_id'] == original['rule_id']
        assert 'choice_text' not in statement and 'logic_text' not in statement
        for ref in statement['evidence_refs']:
            evidence = exported['evidence'][ref['id']]
            source = ''.join(r['text'] for r in exported['records'])
            assert source[evidence['start']:evidence['end']] == next(e['quote'] for e in original['evidence'] if e['fragment_id'] == ref['id'])
    assert all('quote' not in e for e in exported['evidence'].values())
    assert 'actor' not in exported['statements'][0]


def test_provider_failure_is_saved_and_replayable_without_changing_claims(tmp_path, monkeypatch):
    root = workspace(tmp_path); before = ReviewStore(root).snapshot()
    env, _ = provider(monkeypatch, tmp_path, [RuntimeError('offline')])
    result = s.enrich_run(root, tmp_path / 'enrich', env_file=env)
    assert result['status'] == 'needs_attention' and result['applied_actions'] == 0
    after = ReviewStore(root).snapshot()
    assert after['accepted'] == before['accepted']
    assert after['enrichment_issues'] and result['recorded_observations'] == 1
    assert after['history'][-1]['action'] == 'observe'
    monkeypatch.setattr(e, '_create_model', lambda *args: pytest.fail('Replay called provider'))
    assert s.replay_enrichment(tmp_path / 'enrich', tmp_path / 'replay')['provider_calls'] == 0


@pytest.mark.parametrize('relation', ['scope', 'prerequisite', 'trigger', 'exception'])
def test_term_relationships_do_not_disrupt_qualification_revision_families(relation):
    from rulespec_extrapolator.core import NS, _component_family
    node = {'@type': 'rkaf:RelationshipAssertion', 'rkaf:assertsPredicate': NS + relation}
    assert _component_family(node) == 'qualification'
    for predicate in ('defines', 'uses-term'):
        node['rkaf:assertsPredicate'] = NS + predicate
        assert _component_family(node) == NS + predicate


def test_enrichment_retains_claim_with_an_existing_unlocated_definition():
    book, _ = compile_output()
    candidates = [{k: v for k, v in c.items() if k in e.core.CANDIDATE_SCHEMA['properties']}
                  for c in book['accepted']]
    candidates[0]['defined_terms'][0]['quote'] = 'Record notice (RN) means an invented thing.'
    book = compile_candidates(book['document'], candidates, {})
    assert len(book['accepted']) == 2
    assert book['accepted'][0]['issues']
    window, = e.plan_windows(book['document'])
    changes, issues = s.changes_for(book, window, enrichment())
    assert len(book['accepted']) == 2
    assert changes or issues
