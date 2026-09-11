"""CFR scope survives native reading, evidence storage and discovery export."""
import pytest

from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.references import scan_references


@pytest.mark.parametrize('text, start, end', [
    ('41 CFR 101-19.600 to 101-19.607', ('101-19', '600'), ('101-19', '607')),
    ('40 CFR parts 1500 through 1508', ('1500', None), ('1508', None)),
    ('40 CFR §§ 60.1(a) through 61.2(b)', ('60', '1'), ('61', '2')),
])
def test_complete_range_preserves_endpoints_and_original_spelling(text, start, end):
    result = scan_references(prepare_document(text))
    row, = result['candidates']
    assert not result['rejected']
    assert row['value'] == row['evidence'][0]['quote'] == text
    for name, expected in [('start', start), ('end', end)]:
        endpoint = row['reading'][name]
        assert (endpoint['cfr_part'], endpoint['cfr_section']) == expected
    assert 'cfr_part' not in row['reading']  # The whole range is not its first part.
    assert result['target_resolution'] == 'not_performed'
    if '(a)' in text:
        assert row['reading']['pinpoint'] == ['a']
        assert row['reading']['range_end_pinpoint'] == ['b']


def test_range_and_following_list_item_keep_distinct_support():
    text = '🧭 40 CFR §§ 60.1(a) through 61.2(b), and 63.3(c).'
    doc = prepare_document(text)
    first, second = scan_references(doc)['candidates']
    assert first['value'] == '40 CFR §§ 60.1(a) through 61.2(b)'
    assert second['reading']['cfr_part'] == '63'
    assert second['reading']['pinpoint'] == ['c']
    assert second['evidence'][1] == {**first['evidence'][0], 'field': 'reference_context'}
    exported = export_discovery({'document': doc, 'accepted': []}, include_references=True)
    a, b = exported['reference_scan']['candidates']
    assert a['reading'] == first['reading']
    assert b['evidence_refs'][1]['id'] == a['evidence_refs'][0]['id']
    assert not exported['statements']


def test_real_compound_list_keeps_both_parts_without_splitting_hyphens():
    text = 'For information on records and standard and optional forms, see FMR parts '
    text += '102-193 and 102-194 (41 CFR parts 102-193 and 102-194).'
    result = scan_references(prepare_document(text))
    assert not result['rejected']
    assert [r['reading']['cfr_part'] for r in result['candidates']] == ['102-193', '102-194']
    assert all(r['reading']['part_is_plausible'] for r in result['candidates'])


@pytest.mark.parametrize('text', [
    '40 CFR parts 60 through',
    '40 CFR parts 60 through unknown',
    '41 CFR 60-1-60-2',
    '17 CFR 15c3-3',
])
def test_uncertain_scope_stays_refused_with_complete_source(text):
    result = scan_references(prepare_document(text))
    assert not result['candidates']
    refused, = result['rejected']
    assert refused['code'].startswith('cfr_')
    assert refused['value'] == refused['evidence'][0]['quote'] == text


def test_implausible_range_end_cannot_hide_behind_plausible_start():
    text = '40 CFR parts 60 through 123456'
    result = scan_references(prepare_document(text))
    assert not result['candidates']
    row, = result['rejected']
    assert row['code'] == 'cfr_part_implausible'
    assert row['reading']['end']['part_is_plausible'] is False
    assert row['evidence'][0]['quote'] == text
