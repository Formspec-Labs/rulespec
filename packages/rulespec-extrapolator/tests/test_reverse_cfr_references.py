"""Use the upstream reader; preserve exact quotations and shared list context."""
from pathlib import Path

import pytest

from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator.uslm import prepare_xml


def test_publisher_reverse_titles_survive_reference_and_discovery_export():
    xml = Path(__file__).with_name('fixtures').joinpath('cfr-reverse-title.xml').read_text()
    document = prepare_xml(xml, title='Title 41 source excerpt')
    scan = scan_references(document)
    rows = [r for r in scan['candidates'] if r['kind'] == 'cfr']
    assert [(r['reading']['cfr_title'], r['reading']['cfr_part'], r['reading']['cfr_section']) for r in rows] == [
        (29, '1910', None), (29, '1954', '3'), (29, '1910', None)]
    assert rows[1]['reading']['pinpoint'] == ['d', '1', 'i']
    assert rows[0]['id'] != rows[2]['id']
    assert rows == [r for r in scan_references(document)['candidates'] if r['kind'] == 'cfr']
    for row in rows:
        support, = row['evidence']  # A whole single citation needs no duplicate context quote.
        assert document['text'][support['start']:support['end']] == support['quote'] == row['value']
    exported = export_discovery({'document': document, 'accepted': []}, include_references=True)
    saved = exported['reference_scan']['candidates']
    assert [(r['id'], r['value'], r['reading']) for r in saved] == [(r['id'], r['value'], r['reading']) for r in rows]


def test_reverse_list_requires_actual_title_evidence():
    text = '§§ 82.155, 82.156 of title 40, Code of Federal Regulations'
    document = prepare_document(text)
    scan = scan_references(document)
    assert len(scan['candidates']) == 2 and not scan['rejected']
    for row in scan['candidates']:
        assert row['evidence'][1]['quote'] == text
    split = text.index(' of title')
    document['source_map'] = [
        {'kind': 'source', 'start': 0, 'end': split, 'source_id': 'original', 'source_start': 0, 'source_end': split},
        {'kind': 'inserted', 'start': split, 'end': len(text), 'text': text[split:]},
    ]
    scan = scan_references(document)
    assert not scan['candidates']
    assert [r['code'] for r in scan['rejected']] == [
        'reference_context_not_grounded_in_source', 'reference_not_grounded_in_source']


@pytest.mark.parametrize('tail,code', [('note', 'cfr_note_target_unresolved'),
                                       ('et seq.', 'cfr_open_ended_reference_unresolved')])
def test_shared_reverse_qualification_refuses_every_list_member(tail, code):
    text = f'§§ 82.155, 82.156 of title 40, Code of Federal Regulations, {tail}'
    scan = scan_references(prepare_document(text))
    assert not scan['candidates'] and len(scan['rejected']) == 2
    assert all(row['code'] == code for row in scan['rejected'])
    assert all(row['evidence'][1]['quote'] == text for row in scan['rejected'])
