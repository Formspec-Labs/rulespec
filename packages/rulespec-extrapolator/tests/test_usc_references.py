"""Native qualified USC readings survive source evidence and discovery export."""
from copy import deepcopy

import pytest

from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document, source_passages
from rulespec_extrapolator.references import scan_references


@pytest.mark.parametrize('text, expected', [
    ('5 U.S.C. 5372(b)', {'usc_title': 5, 'usc_section': '5372', 'pinpoint': ['b']}),
    ('5 U.S.C. chapter 81, subchapter I', {'usc_chapter': '81', 'subchapter': 'I'}),
    ('50 U.S.C. App. 2401 note', {'usc_appendix': True, 'usc_note': True, 'usc_section': '2401'}),
    ('50 U.S.C. 402, note', {'usc_note': True, 'usc_section': '402'}),
    ('19 U.S.C. 1484-86', {'usc_section': '1484', 'usc_section_end': '1486',
                           'usc_section_span_rule': 'abbreviated-span'}),
    ('5 U.S.C. 552(a) through 553(b)', {'usc_section': '552', 'usc_section_end': '553',
                                      'pinpoint': ['a'], 'range_end_pinpoint': ['b'],
                                      'usc_section_span_rule': 'stated'}),
    ('5 USC subchapters I-II', {}),  # A missing chapter is not an inferred address.
])
def test_source_wording_and_native_fields_keep_qualified_targets(text, expected):
    doc = prepare_document(text)
    scan = scan_references(doc)
    if not expected:
        assert not scan['candidates']
        return
    row, = scan['candidates']
    assert row['kind'] == 'usc' and row['value'] == text
    assert row['reading'].items() >= expected.items()
    assert row['evidence'][0]['quote'] == text
    assert row['record_ids'] == [p['id'] for p in source_passages(doc)]
    assert not scan['rejected']
    assert not any(value is None for value in row['reading'].values())
    assert scan['target_resolution'] == 'not_performed'
    assert scan['semantic_completeness'] == 'not_established'
    assert any(p['name'].endswith('.find_usc_citations') and p['module_sha256'] for p in scan['parsers'])


@pytest.mark.parametrize('text, code', [
    ('42 USC 1983affirmed', 'usc_token_continuation_unresolved'),
    ('26 USC 1.104-1(c)', 'usc_token_continuation_unresolved'),
    ('0 USC 1', 'usc_title_outside_supported_space'),
    ('53 USC 101', 'usc_title_outside_supported_space'),
    ('49 USC 42301 preceding note', 'usc_note_position_unresolved'),
    ('5 USC chapters 5-7, subchapter I', 'usc_subchapter_scope_ambiguous'),
    ('49 USC 1354(a) to 1354(c)', 'usc_range_unresolved'),
    ('38 U.S.C. 4301, et seq.', 'usc_open_ended_reference_unresolved'),
])
def test_refused_readings_remain_refused_in_discovery(text, code):
    doc = prepare_document(text)
    book = {'document': doc, 'accepted': []}
    original = deepcopy(book)
    scan = scan_references(doc)
    assert not scan['candidates']
    row, = scan['rejected']
    assert row['kind'] == 'usc' and row['value'] == text and row['code'] == code
    assert row['evidence'][0]['quote'] == text
    exported = export_discovery(book, include_references=True)
    saved, = exported['reference_scan']['rejected']
    assert saved['reading'] == row['reading'] and saved['code'] == code
    evidence, = saved['evidence_refs']
    support = exported['evidence'][evidence['id']]
    assert doc['text'][support['start']:support['end']] == text
    assert not exported['statements'] and book == original


def test_inherited_title_and_repeated_mentions_keep_their_own_evidence():
    doc = prepare_document('🧭 5 USC 552, 552a.\n\n5 USC 552.')
    scan = scan_references(doc)
    first, second, repeated = scan['candidates']
    assert first['value'] == repeated['value'] == '5 USC 552'
    assert first['id'] != repeated['id']
    assert second['value'] == ', 552a' and second['reading']['usc_title'] == 5
    assert second['evidence'][1] == {**first['evidence'][0], 'field': 'reference_context'}
    assert first['record_ids'] != repeated['record_ids']
    export = export_discovery({'document': doc, 'accepted': []}, include_references=True)
    a, b, _ = export['reference_scan']['candidates']
    assert b['evidence_refs'][1] == {'id': a['evidence_refs'][0]['id'], 'roles': ['reference_context']}


def test_inserted_usc_title_cannot_ground_an_inherited_reference():
    doc = prepare_document('5 USC 552 and 552a')
    doc['source_map'] = [
        {'kind': 'inserted', 'start': 0, 'end': 5, 'text': doc['text'][:5]},
        {'kind': 'source', 'start': 5, 'end': len(doc['text']), 'source_id': 'original',
         'source_start': 0, 'source_end': len(doc['text']) - 5},
    ]
    scan = scan_references(doc)
    assert not scan['candidates']
    assert [r['code'] for r in scan['rejected']] == [
        'reference_not_grounded_in_source', 'reference_context_not_grounded_in_source']


def test_prose_counts_do_not_turn_into_additional_references():
    doc = prepare_document('Under 5 USC 552 the agency counts 2020, 2021, and 2022 applications.')
    row, = scan_references(doc)['candidates']
    assert row['reading']['usc_section'] == '552'


def test_grounding_failure_does_not_erase_the_native_refusal():
    doc = prepare_document('0 USC 1 and 2')
    doc['source_map'] = [
        {'kind': 'inserted', 'start': 0, 'end': 5, 'text': doc['text'][:5]},
        {'kind': 'source', 'start': 5, 'end': len(doc['text']), 'source_id': 'original',
         'source_start': 0, 'source_end': len(doc['text']) - 5},
    ]
    exported = export_discovery({'document': doc, 'accepted': []}, include_references=True)
    scan = exported['reference_scan']
    assert not scan['candidates']
    assert [r['code'] for r in scan['rejected']] == [
        'reference_not_grounded_in_source', 'reference_context_not_grounded_in_source']
    assert all(r['parser_refusal'] == 'usc_title_outside_supported_space' for r in scan['rejected'])
    assert all(r['reading']['usc_title'] == 0 for r in scan['rejected'])
