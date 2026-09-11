"""Reference candidates preserve evidence without promoting mentions to claims."""
from copy import deepcopy
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

from rulespec_extrapolator import cli
from rulespec_extrapolator.core import compile_candidates, digest
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document, source_passages
from rulespec_extrapolator.references import scan_references

CASES = json.loads((Path(__file__).parent / 'fixtures/reference-occurrences.json').read_text())['cases']


@pytest.mark.parametrize('case', CASES, ids=lambda c: c['id'])
def test_frozen_source_occurrences(case):
    assert digest(case['raw']) == case['text_sha256']
    doc = prepare_document(case['raw'])
    result = scan_references(doc)
    # These frozen labels cover the original five families; CFR/USC have separate controls.
    families = {'public_law', 'statutes_at_large', 'executive_order', 'docket', 'rin'}
    actual = [{'kind': c['kind'], 'value': c['value'], 'quote': c['evidence'][0]['quote'],
               'span': [c['evidence'][0]['start'], c['evidence'][0]['end']]} for c in result['candidates'] if c['kind'] in families]
    assert actual == case['expected_additions']
    assert not [c for c in result['rejected'] if c['kind'] in families]
    assert result['target_resolution'] == 'not_performed'
    assert result['semantic_completeness'] == 'not_established'
    assert scan_references(doc) == result


def test_repeated_mentions_keep_distinct_evidence_and_passage_ids():
    doc = prepare_document('🧭 E.O. 12866.\n\nUnder Executive\nOrder 12866, act.')
    result = scan_references(doc)
    a, b = result['candidates']
    assert a['value'] == b['value'] == 'Executive Order 12866'
    assert a['id'] != b['id']
    assert a['evidence'][0]['fragment_id'] != b['evidence'][0]['fragment_id']
    for candidate, passage in zip(result['candidates'], source_passages(doc), strict=True):
        support = candidate['evidence'][0]
        assert doc['text'][support['start']:support['end']] == support['quote']
        assert candidate['record_ids'] == [passage['id']]


def test_amendment_heading_rin_refusal_preserves_source_and_adjacent_law():
    # Original 5 U.S.C. 5721 amendment entry, not an invented RIN example.
    text = '1998—Pars. (6), (7). Pub. L. 105–264 added pars. (6) and (7).'
    doc = prepare_document(text)
    scan = scan_references(doc)
    law, = scan['candidates']
    assert law['kind'] == 'public_law' and law['value'] == 'Public Law 105-264'
    refused, = scan['rejected']
    assert refused['value'] == '1998-PARS'
    assert refused['code'] == 'rin_outside_supported_identifier_space'
    support, = refused['evidence']
    assert support['quote'] == text[support['start']:support['end']] == '1998—Pars'
    assert any(p['name'] == 'refspec.registry.iri_minting.mint_rin_iri' and p['module_sha256'] for p in scan['parsers'])
    exported = export_discovery({'document': doc, 'accepted': []}, include_references=True)
    saved, = exported['reference_scan']['rejected']
    evidence, = saved['evidence_refs']
    assert saved['code'] == refused['code']
    position = exported['evidence'][evidence['id']]
    assert doc['text'][position['start']:position['end']] == support['quote']


def test_rin_space_check_keeps_normalized_mentions_and_distinct_occurrences():
    doc = prepare_document('🧭 RIN 2060–as32.\n\nRIN 2060—AS32.')
    scan = scan_references(doc)
    first, second = scan['candidates']
    assert first['value'] == second['value'] == '2060-AS32'
    assert first['id'] != second['id']
    assert first['evidence'][0]['quote'] == '2060–as32'
    assert second['evidence'][0]['quote'] == '2060—AS32'
    assert not scan['rejected']
    assert scan['target_resolution'] == 'not_performed'


def test_rin_shape_acceptance_is_not_issuance_and_query_defaults_stay_permissive():
    from spicysearch.identifiers import detect_identifiers
    text = 'Product SKU 9999-ZZ99; query candidate 0648-ABCD.'
    assert [m.value for m in detect_identifiers(text) if m.kind == 'rin'] == ['9999-ZZ99', '0648-ABCD']
    scan = scan_references(prepare_document(text))
    assert [r['value'] for r in scan['candidates']] == ['9999-ZZ99']
    assert [r['value'] for r in scan['rejected']] == ['0648-ABCD']
    assert scan['target_resolution'] == 'not_performed'
    assert scan['semantic_completeness'] == 'not_established'


def test_reference_crossing_passage_boundary_links_both_passages():
    doc = prepare_document('Public Law\n\n119-20')
    candidate, = scan_references(doc)['candidates']
    assert candidate['record_ids'] == [p['id'] for p in source_passages(doc)]
    assert candidate['evidence'][0]['quote'] == doc['text']


def test_inserted_text_cannot_create_source_evidence():
    doc = prepare_document('Public Law (Pub. L.) 119-20')
    doc['source_map'] = [
        {'kind': 'source', 'start': 0, 'end': 11, 'source_id': 'original', 'source_start': 0, 'source_end': 11},
        {'kind': 'inserted', 'start': 11, 'end': 21, 'text': doc['text'][11:21]},
        {'kind': 'source', 'start': 21, 'end': len(doc['text']), 'source_id': 'original',
         'source_start': 11, 'source_end': 11 + len(doc['text']) - 21},
    ]
    result = scan_references(doc)
    assert not result['candidates']
    assert result['rejected'][0]['code'] == 'reference_not_grounded_in_source'
    assert result['rejected'][0]['value'] == 'Public Law 119-20'


def test_changed_document_and_invalid_parser_span_refuse(monkeypatch):
    from spicysearch import identifiers
    doc = prepare_document('Public Law 119-20')
    modified = {**doc, 'text': 'Public Law 119-21'}
    with pytest.raises(ValueError, match='identity or digest'):
        scan_references(modified)
    monkeypatch.setattr(identifiers, 'detect_identifiers', lambda _: [
        SimpleNamespace(kind='public_law', value='Public Law 119-20', span=(-1, 4))])
    with pytest.raises(ValueError, match='invalid source coordinates'):
        scan_references(doc)


def test_discovery_reuses_evidence_without_changing_statements():
    statement = 'Visitors must consult E.O. 12866.'
    doc = prepare_document(statement + '\n\nPublic Law (Pub. L.) 119-20.')
    book = compile_candidates(doc, [{'summary': statement, 'quote': statement, 'actor': 'Visitors', 'actor_quote': 'Visitors',
                                    'kind': 'requirement', 'modality': 'must', 'modality_quote': 'must'}],
                              {'id': 'urn:test:reference-discovery'})
    assert len(book['accepted']) == 1
    original = deepcopy(book)
    baseline = export_discovery(book)
    result = export_discovery(book, include_references=True)
    scan = result.pop('reference_scan')
    added_evidence = set(result['evidence']) - set(baseline['evidence'])
    assert added_evidence
    for candidate in scan['candidates']:
        support, = candidate['evidence_refs']
        assert support['roles'] == ['reference']
        evidence = result['evidence'][support['id']]
        assert candidate['record_ids'] == evidence['record_ids']
        assert 'evidence' not in candidate
    for identity in added_evidence:
        result['evidence'].pop(identity)
    assert result == baseline
    assert book == original


def test_missing_optional_parser_does_not_break_default_discovery(monkeypatch):
    monkeypatch.setitem(sys.modules, 'spicysearch', None)
    doc = prepare_document('Public Law 119-20')
    assert 'reference_scan' not in export_discovery({'document': doc, 'accepted': []})
    with pytest.raises(RuntimeError, match='verified SpicySearch and RefSpec wheels'):
        scan_references(doc)


@pytest.mark.parametrize('form', ['text', 'document', 'rulebook', 'directory'])
def test_reference_cli_and_no_overwrite(tmp_path, form):
    doc = prepare_document('Public Law (Pub. L.) 119-20')
    source = tmp_path / ('source.txt' if form == 'text' else 'source.json')
    if form == 'directory':
        source = tmp_path / 'run'
        source.mkdir()
        (source / 'document.json').write_text(json.dumps(doc))
    else:
        source.write_text(doc['text'] if form == 'text' else json.dumps({'document': doc} if form == 'rulebook' else doc))
    output = tmp_path / 'references.json'
    assert cli.main(['references', str(source), '--output', str(output)]) == 0
    saved = output.read_bytes()
    assert json.loads(saved)['candidates'][0]['value'] == 'Public Law 119-20'
    with pytest.raises(FileExistsError):
        cli.main(['references', str(source), '--output', str(output)])
    assert output.read_bytes() == saved


def test_discovery_cli_enables_reference_scan(monkeypatch, tmp_path):
    from rulespec_extrapolator.review_store import ReviewStore
    doc = prepare_document('Public Law 119-20')
    monkeypatch.setattr(ReviewStore, '__init__', lambda self, directory: None)
    monkeypatch.setattr(ReviewStore, 'snapshot', lambda self: {'document': doc, 'accepted': []})
    output = tmp_path / 'discovery.json'
    assert cli.main(['discovery-export', str(tmp_path), '--references', '--output', str(output)]) == 0
    assert json.loads(output.read_text())['reference_scan']['candidates'][0]['value'] == 'Public Law 119-20'


def test_cfr_list_retains_native_readings_and_grounded_title_context():
    doc = prepare_document('🧭 See 40 CFR §§ 82.155(a), 82.156(b), and Pub. L. 119-20.')
    result = scan_references(doc)
    first, second = [c for c in result['candidates'] if c['kind'] == 'cfr']
    assert [c['value'] for c in (first, second)] == ['40 CFR 82.155(a)', '40 CFR 82.156(b)']
    assert [c['reading']['pinpoint'] for c in (first, second)] == [['a'], ['b']]
    assert [c['reading']['cfr_section'] for c in (first, second)] == ['155', '156']
    assert first['evidence'][0]['quote'] == '40 CFR §§ 82.155(a)'
    assert second['evidence'][0]['quote'] == ', 82.156(b)'
    assert second['evidence'][1] == {**first['evidence'][0], 'field': 'reference_context'}
    assert first['reading']['title_is_possible'] is True
    assert first['reading']['part_is_plausible'] is True
    assert len([c for c in result['candidates'] if c['kind'] == 'public_law']) == 1


def test_cfr_repeated_occurrences_keep_spaced_pinpoints_and_original_spans():
    quote = '14 CFR § 91.107(a)(3)(iii)(B)( 4 )'
    doc = prepare_document(f'😀 {quote}; then {quote}.')
    first, second = scan_references(doc)['candidates']
    assert first['id'] != second['id']
    for candidate in (first, second):
        assert candidate['reading']['pinpoint'] == ['a', '3', 'iii', 'B', '4']
        assert candidate['evidence'][0]['quote'] == quote
        support = candidate['evidence'][0]
        assert doc['text'][support['start']:support['end']] == quote


def test_cfr_discovery_shares_context_and_refused_evidence():
    doc = prepare_document('See 40 CFR §§ 82.155(a), 82.156(b). Compare 99 CFR 1.2.')
    book = {'document': doc, 'accepted': []}
    result = export_discovery(book, include_references=True)
    first, second = result['reference_scan']['candidates']
    context = second['evidence_refs'][1]
    assert context == {'id': first['evidence_refs'][0]['id'], 'roles': ['reference_context']}
    refused, = result['reference_scan']['rejected']
    assert 'evidence' not in refused
    support, = refused['evidence_refs']
    assert support['roles'] == ['reference']
    span = result['evidence'][support['id']]
    assert doc['text'][span['start']:span['end']] == '99 CFR 1.2'
    assert refused['reading']['title_is_possible'] is False
    assert not result['statements']


def test_historically_used_cfr_title_is_not_rejected_by_current_roster():
    candidate, = scan_references(prepare_document('35 CFR 1.1'))['candidates']
    assert candidate['reading']['title_is_possible'] is True
    assert candidate['value'] == '35 CFR 1.1'


@pytest.mark.parametrize('text, code, field', [
    ('99 CFR 1.2', 'cfr_title_impossible', 'title_is_possible'),
    ('40 CFR 123456', 'cfr_part_implausible', 'part_is_plausible'),
])
def test_cfr_native_refusals_preserve_the_reading(text, code, field):
    result = scan_references(prepare_document(text))
    assert not result['candidates']
    refused, = result['rejected']
    assert refused['code'] == code
    assert refused['reading'][field] is False
    assert refused['evidence'][0]['quote'] == text


def test_cfr_context_from_inserted_text_cannot_ground_a_list_continuation():
    doc = prepare_document('40 CFR §§ 82.155(a), 82.156(b)')
    doc['source_map'] = [
        {'kind': 'inserted', 'start': 0, 'end': 7, 'text': doc['text'][:7]},
        {'kind': 'source', 'start': 7, 'end': len(doc['text']), 'source_id': 'original',
         'source_start': 0, 'source_end': len(doc['text']) - 7},
    ]
    result = scan_references(doc)
    assert not result['candidates']
    assert [c['code'] for c in result['rejected']] == [
        'reference_not_grounded_in_source', 'reference_context_not_grounded_in_source']
    assert result['rejected'][1]['reading']['cfr_section'] == '156'


@pytest.mark.parametrize('reader, text', [('find_cfr_citations', '40 CFR 82.155(a)'),
                                         ('find_usc_citations', '5 USC 552(a)'),
                                         ('find_eo_compilation_locators', '3 CFR 127 (1981 Comp.)')])
def test_parser_text_mismatch_is_not_replaced_with_plausible_source(monkeypatch, reader, text):
    from dataclasses import replace
    from refspec.registry import citation_grammar
    doc = prepare_document(text)
    match, = getattr(citation_grammar, reader)(doc['text'])
    monkeypatch.setattr(citation_grammar, reader, lambda _: [replace(match, text='different quotation')])
    with pytest.raises(ValueError, match='quotation differs'):
        scan_references(doc)


@pytest.mark.parametrize('text', ['§ 82.155(a)', 'paragraph (b) of this section'])
def test_cfr_does_not_invent_local_titles(text):
    assert not scan_references(prepare_document(text))['candidates']


def test_year_first_compilation_is_a_locator_not_a_cfr_part():
    row, = scan_references(prepare_document('3 CFR, 1977 Comp., p. 123'))['candidates']
    assert row['kind'] == 'eo_compilation'
    assert row['reading'] == {'compilation_start': '1977', 'page': '123'}


def test_compilation_locators_preserve_endpoints_repeats_and_discovery_evidence():
    text = '3 CFR 60–61 (1971–1975 Comp.); 3 CFR 100; 3 CFR 60–61 (1971–1975 Comp.).'
    doc = prepare_document(text)
    result = scan_references(doc)
    first, part, repeated = result['candidates']
    assert first['kind'] == repeated['kind'] == 'eo_compilation'
    assert first['id'] != repeated['id']
    assert first['reading'] == repeated['reading'] == {
        'compilation_start': '1971', 'compilation_end': '1975', 'page': '60', 'page_end': '61'}
    assert part['kind'] == 'cfr' and part['reading']['cfr_part'] == '100'
    for candidate in (first, repeated):
        support, = candidate['evidence']
        assert candidate['value'] == support['quote'] == text[support['start']:support['end']]
    exported = export_discovery({'document': doc, 'accepted': []}, include_references=True)
    for source, saved in zip(result['candidates'], exported['reference_scan']['candidates'], strict=True):
        assert {k: v for k, v in saved.items() if k != 'evidence_refs'} == {
            k: v for k, v in source.items() if k != 'evidence'}
        for support, reference in zip(source['evidence'], saved['evidence_refs'], strict=True):
            position = exported['evidence'][reference['id']]
            assert text[position['start']:position['end']] == support['quote']
    assert result['target_resolution'] == 'not_performed'
    assert result['semantic_completeness'] == 'not_established'


def test_unclosed_compilation_parenthetical_remains_a_refusal():
    text = '3 CFR 127 (1981 Comp.'
    result = scan_references(prepare_document(text))
    assert not result['candidates']
    refused, = result['rejected']
    assert refused['code'] == 'compilation_parenthetical_unclosed'
    assert refused['reading'] == {'compilation_start': '1981', 'page': '127'}
    assert refused['evidence'][0]['quote'] == text
