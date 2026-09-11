"""Qualified addresses keep exact source and unresolved pairings through export."""
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.references import scan_references


def test_subpart_alternatives_preserve_source_roles_and_distinct_ids():
    text = '49 CFR Part 172 subpart E (labeling) or subpart F (placarding)'
    doc = prepare_document(text)
    scan = scan_references(doc)
    first, second = scan['candidates']
    assert [r['value'] for r in scan['candidates']] == ['49 CFR 172 subpart E', '49 CFR 172 subpart F']
    assert second['evidence'][0]['quote'] == ' or subpart F (placarding)'
    assert second['evidence'][1] == {**first['evidence'][0], 'field': 'reference_context'}
    assert first['id'] != second['id']
    assert first['record_ids'] == second['record_ids']
    exported = export_discovery({'document': doc, 'accepted': []}, include_references=True)
    a, b = exported['reference_scan']['candidates']
    assert b['evidence_refs'][1] == {'id': a['evidence_refs'][0]['id'], 'roles': ['reference_context']}
    assert len(exported['evidence']) == 3  # Source passage plus two exact occurrences.
    assert not exported['statements']


def test_appendix_under_subpart_is_not_the_subpart_itself():
    text = '40 CFR part 82, appendix A to subpart A'
    row, = scan_references(prepare_document(text))['candidates']
    assert row['value'] == '40 CFR 82 appendix A to subpart A'
    assert (row['reading']['appendix'], row['reading']['subpart']) == ('A', 'A')
    assert row['evidence'][0]['quote'] == text


def test_part_list_does_not_create_guessed_subpart_targets():
    doc = prepare_document('45 CFR parts 160 and 164, subparts A and E')
    scan = scan_references(doc)
    assert [r['value'] for r in scan['candidates']] == ['45 CFR 160']
    assert [r['reading']['subpart'] for r in scan['rejected']] == ['A', 'E']
    assert {r['code'] for r in scan['rejected']} == {'cfr_ambiguous_part_scope'}
    assert scan['rejected'][0]['evidence'][1]['quote'] == '45 CFR parts 160'
    assert scan['rejected'][1]['evidence'][1]['quote'] == '45 CFR parts 160 and 164, subparts A'
    export = export_discovery({'document': doc, 'accepted': []}, include_references=True)
    for row in export['reference_scan']['rejected']:
        assert 'evidence' not in row
        assert all(ref['id'] in export['evidence'] for ref in row['evidence_refs'])


def test_stated_range_is_one_reading_not_generated_intermediate_targets():
    text = '49 CFR part 172 subparts E through G'
    row, = scan_references(prepare_document(text))['candidates']
    assert (row['reading']['subpart'], row['reading']['subpart_end']) == ('E', 'G')
    assert row['evidence'][0]['quote'] == text


def test_inserted_subpart_context_does_not_license_the_second_alternative():
    doc = prepare_document('49 CFR part 172 subpart E or subpart F')
    end = doc['text'].index(' or')
    doc['source_map'] = [
        {'kind': 'inserted', 'start': 0, 'end': end, 'text': doc['text'][:end]},
        {'kind': 'source', 'start': end, 'end': len(doc['text']), 'source_id': 'original',
         'source_start': 0, 'source_end': len(doc['text']) - end},
    ]
    scan = scan_references(doc)
    assert not scan['candidates']
    assert [r['code'] for r in scan['rejected']] == [
        'reference_not_grounded_in_source', 'reference_context_not_grounded_in_source']


def test_unqualified_readings_gain_no_empty_fields():
    row, = scan_references(prepare_document('40 CFR 82.154(a)'))['candidates']
    assert not {'subpart', 'subpart_end', 'appendix', 'qualifier_status'} & row['reading'].keys()
