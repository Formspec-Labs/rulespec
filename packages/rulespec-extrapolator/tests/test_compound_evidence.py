"""Complete prepared quotations retain every original-source evidence piece."""
from copy import deepcopy

import pytest

from rulespec_extrapolator import extraction as ex
from rulespec_extrapolator.core import NS, _evidence, compile_candidates, evidence_parts, validate_graph
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewIntegrityError, ReviewStore
from rulespec_extrapolator.terms import definition_records
from test_discovery_source_map import mapped_document
from test_enrichment import TEXT, candidate as enriched_candidate


def statement_book():
    doc = mapped_document([('source', 'Staff must:'), ('inserted', '\n\n'),
                           ('source', '(a) log requests; and'), ('inserted', '\n\n'),
                           ('source', '(b) archive records.')])
    candidate = {'kind': 'requirement', 'actor': '', 'summary': 'Staff must log requests and archive records.',
                 'quote': doc['text'], 'logic_text': doc['text'], 'modality': 'must', 'modality_quote': 'must'}
    return compile_candidates(doc, [candidate], {'id': 'urn:test:compound'})


def save_book(path, book):
    for name, value in [('document.json', book['document']), ('run.json', book['run']), ('rulebook.json', book)]:
        ex._save(path / name, value)
    return ReviewStore(path)


def supports(claim, field):
    return [e for e in claim['evidence'] if e['field'] == field]


def test_complete_statement_keeps_coordinates_core_and_discovery_source_support(tmp_path):
    book = statement_book()
    assert not book['rejected']
    claim, doc = book['accepted'][0], book['document']
    assert (claim['quote'], claim['start'], claim['end']) == (doc['text'], 0, len(doc['text']))
    assert len(supports(claim, 'summary')) == len(supports(claim, 'logic_text')) == 3
    assert all(_evidence(doc, e['quote'], e['field'], e['start'], e['end']) == e for e in claim['evidence'])
    assert validate_graph(book['graph'])['shacl_conforms']
    discovery = export_discovery(book)
    assert discovery['statements'][0]['statement'] == claim['summary']
    assert ''.join(p['text'] for p in discovery['records']) == doc['text']
    summary = [ref for ref in discovery['statements'][0]['evidence_refs'] if 'summary' in ref['roles']]
    assert len(summary) == 3
    assert all(doc['text'][e['start']:e['end']].strip() for e in discovery['evidence'].values())
    store = save_book(tmp_path, book)
    assert store.snapshot() == ReviewStore(tmp_path).snapshot()
    original = (tmp_path / 'rulebook.json').read_bytes()
    store.apply({'action': 'edit', 'actor': 'Reviewer', 'actor_kind': 'humanUser',
                 'expected_revision': 0, 'targets': [claim['id']], 'rationale': 'Clarify wording.',
                 'replacements': [{'summary': 'Log requests and archive records.'}]})
    assert len(ReviewStore(tmp_path).snapshot()['revisions'][0]['evidence']) == len(claim['evidence'])
    assert (tmp_path / 'rulebook.json').read_bytes() == original


@pytest.mark.parametrize('change', ['missing', 'duplicate', 'moved', 'fabricated', 'identity', 'wrong-main-position'])
def test_review_refuses_incomplete_or_changed_compound_support(tmp_path, change):
    book = statement_book()
    claim = book['accepted'][0]
    if change == 'missing':
        claim['evidence'].pop(1)
    elif change == 'duplicate':
        claim['evidence'].insert(1, deepcopy(claim['evidence'][0]))
    elif change == 'moved':
        claim['evidence'][1]['start'] -= 1
    elif change == 'fabricated':
        claim['evidence'][1]['quote'] = 'Invented support'
    elif change == 'identity':
        claim['evidence'][1]['fragment_id'] = 'urn:test:invented'
    else:
        claim['start'] += 1
    with pytest.raises(ReviewIntegrityError):
        save_book(tmp_path, book).snapshot()


@pytest.mark.parametrize('insertion', ['not ', '\u200b', 'editorial '])
def test_nonwhitespace_insertion_cannot_become_statement_evidence(insertion):
    doc = mapped_document([('source', 'Staff must '), ('inserted', insertion), ('source', 'file.')])
    candidate = {'kind': 'requirement', 'actor': '', 'summary': 'File.', 'quote': doc['text']}
    result = compile_candidates(doc, [candidate], {})
    assert not result['accepted']
    assert 'inserted content' in result['rejected'][0]['reason']
    assert not evidence_parts(doc, insertion, 'actor', 11, 11 + len(insertion))


def test_original_whitespace_and_exact_occurrences_remain_distinct():
    text = 'Café 😀 must file.\n\nCafé 😀 must file.'
    doc = prepare_document(text)
    quote = 'Café 😀 must file.'
    assert not evidence_parts(doc, quote, 'summary')
    for start in (0, text.rindex('Café')):
        evidence = evidence_parts(doc, quote, 'summary', start, start + len(quote))
        assert evidence == [_evidence(doc, quote, 'summary', start, start + len(quote))]
    assert evidence_parts(doc, text, 'summary') == [_evidence(doc, text, 'summary')]
    inserted = mapped_document([('source', 'Café'), ('inserted', ' '), ('source', '😀')])
    assert evidence_parts(inserted, ' ', 'summary', 4, 5) == []
    assert evidence_parts(inserted, 'Invented', 'summary', 0, 4) == []


def test_compound_definition_retains_all_name_and_definition_evidence():
    doc = mapped_document([('source', 'A widget means:'), ('inserted', '\n\n'),
                           ('source', 'a handled device.')])
    candidate = {'kind': 'definition', 'actor': '', 'summary': 'A widget is a handled device.', 'quote': doc['text'],
                 'defined_terms': [{'label': 'widget', 'aliases': [], 'quote': doc['text'],
                                    'source_quotes': [doc['text']]}]}
    book = compile_candidates(doc, [candidate], {})
    assert not book['rejected']
    claim = book['accepted'][0]
    term = list(definition_records(doc, claim))[0]
    assert len(term['evidence']) == 4
    assert len(export_discovery(book)['terms'][term['id']]['evidence_refs']) == 2
    assert validate_graph(book['graph'])['shacl_conforms']


def test_structured_components_keep_all_pieces_and_tag_the_complete_region(tmp_path):
    parts = []
    for index, word in enumerate(TEXT.split(' ')):
        if index:
            parts.append(('inserted', ' '))
        parts.append(('source', word))
    doc = mapped_document(parts)
    book = compile_candidates(doc, [enriched_candidate()], {})
    assert not book['rejected']
    claim = book['accepted'][0]
    assert not claim['issues']
    nodes = {n['@id']: n for n in book['graph']['@graph']}
    claimant = next(n for n in nodes.values() if n['@type'] == 'rkaf:SourceClaimant')
    assert claimant['rkaf:attributedInFragment'] == [e['fragment_id'] for e in supports(claim, 'claimants:0')]
    assert len(claimant['rkaf:attributedInFragment']) > 1
    assignment = next(n for n in nodes.values() if n['@type'] == 'rkaf:ConceptAssignment')
    target = nodes[assignment['rkaf:assertsSubject']]
    assert target['oa:hasSelector'][0]['oa:exact'] == TEXT
    for binding in (n for n in nodes.values() if n['@type'] == 'rkaf:EvidenceBinding'):
        assert target['@id'] not in binding['rkaf:bindsSourceFragment']
    for field in ('scope_text:0', 'typed_values:0', 'concepts:0', 'effective_periods:0'):
        assert len(supports(claim, field)) > 1
    assert validate_graph(book['graph'])['shacl_conforms']
    assert save_book(tmp_path, book).snapshot() == ReviewStore(tmp_path).snapshot()


def test_qualification_and_fallback_context_retain_every_main_piece():
    doc = mapped_document([('source', 'Staff must file.'), ('inserted', '\n\n'),
                           ('source', 'Except'), ('inserted', '\n'), ('source', 'during closure.')])
    target = {'kind': 'requirement', 'actor': '', 'summary': 'Staff must file.', 'quote': 'Staff must file.'}
    target_id = compile_candidates(doc, [target], {})['accepted'][0]['id']
    exception = {'kind': 'exception', 'summary': 'Except during closure.', 'quote': 'Except\nduring closure.',
                 'relation': 'exception', 'applies_to': [target_id], 'actor': 'Unresolved actor'}
    book = compile_candidates(doc, [target, exception], {})
    claim = book['accepted'][1]
    main = {e['fragment_id'] for e in supports(claim, 'summary')}
    bindings = [n for n in book['graph']['@graph'] if n['@type'] == 'rkaf:EvidenceBinding']
    qualification = next(n for n in bindings if n['rkaf:evidentiaryFunction'] == 'rkaf:qualifies')
    assert main < set(qualification['rkaf:bindsSourceFragment'])
    actor = next(n for n in book['graph']['@graph'] if n.get('rkaf:assertsPredicate') == NS + 'actor')
    fallback = next(n for n in bindings if n['rkaf:bindsAssertion'] == actor['@id'])
    assert fallback['rkaf:evidentiaryFunction'] == 'rkaf:providesContext'
    assert set(fallback['rkaf:bindsSourceFragment']) == main
