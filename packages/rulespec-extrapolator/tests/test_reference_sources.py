"""Supplied provision bodies are navigation, not edition or applicability verdicts."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from rulespec_extrapolator import cli, uslm
from rulespec_extrapolator.core import build_graph, compile_candidates, validate_graph
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import load_document, prepare_document
from rulespec_extrapolator.references import scan_references

NS = 'http://xml.house.gov/schemas/uslm/1.0'


def source(body='', edition='119-102', extra=''):
    return uslm.prepare_uslm(f'<uscDoc xmlns="{NS}" {extra}><meta><docPublicationName>{edition}</docPublicationName></meta>'
        '<main><section identifier="/us/usc/t5/s553"><num>553</num><heading>Rule making</heading>'
        '<subsection identifier="/us/usc/t5/s553/b"><continuation>Except when notice or hearing is required by statute, this subsection does not apply—</continuation>'
        '<subparagraph identifier="/us/usc/t5/s553/b/B"><num>(B)</num><content>when the agency finds good cause.</content></subparagraph>'
        f'</subsection>{body}</section></main></uscDoc>')


def test_exact_target_has_its_own_source_and_parent_context():
    doc, external = prepare_document('5 USC 553(b)(B). Again: 5 USC 553(b)(B).'), source()
    before = deepcopy(external)
    scan = scan_references(doc, reference_sources=[external])
    a, b = scan['candidates']
    assert a['id'] != b['id']
    assert a['resolution'] == b['resolution']
    assert a['resolution']['status'] == 'located'
    assert a['resolution']['edition_match'] == 'not_established'
    target, = scan['targets'].values()
    src, = scan['reference_sources'].values()
    record, = src['records'].values()
    assert 'Except when notice or hearing is required by statute' in record['text']
    assert external['text'][target['start']:target['end']] == '(B)when the agency finds good cause.'
    assert all(external['text'][e['start']:e['end']] == e['quote'] for e in target['evidence'])
    assert src['publication'][0]['value'] == '119-102'
    graph = build_graph(doc, [], {})
    graph['@graph'].extend([src['publisher_source'], *src['xml_fragments'].values()])
    assert validate_graph(graph)['shacl_conforms']
    assert external == before and scan['semantic_completeness'] == 'not_established'


def test_external_discovery_evidence_resolves_in_its_own_records():
    doc, external = prepare_document('5 USC 553(b)(B).'), source()
    result = export_discovery({'document': doc, 'accepted': []}, reference_sources=[external])
    scan = result['reference_scan']
    target, = scan['targets'].values()
    src = scan['reference_sources'][target['source_id']]
    record = src['records'][target['record_id']]
    assert 'evidence' not in target and target['evidence_refs']
    for ref in target['evidence_refs']:
        position = src['evidence'][ref['id']]
        assert ref['id'] not in result['evidence']
        assert record['text'][position['start']-record['start']:position['end']-record['start']] == external['text'][position['start']:position['end']]
    assert result['records'][0]['text'] == doc['text']


@pytest.mark.parametrize('text', ['5 USC 553 note', '5 USC 553-554', '38 USC 4301 et seq.', '5 USC chapter 5'])
def test_qualified_or_refused_readings_are_not_reduced_to_anchors(text):
    scan = scan_references(prepare_document(text), reference_sources=[source()])
    assert not scan['targets']
    assert all(not row.get('resolution', {}).get('target_ids') for row in scan['candidates'] + scan['rejected'])


def test_missing_pinpoint_does_not_fall_back_to_section():
    row, = scan_references(prepare_document('5 USC 553(z)'), reference_sources=[source()])['candidates']
    assert row['resolution']['status'] == 'not_in_selected_sources'
    assert not row['resolution']['target_ids']


@pytest.mark.parametrize('other', [source(edition='118-1'), source(extra='id="changed-xml-only"')])
def test_distinct_editions_or_xml_with_same_readable_text_remain_ambiguous(other):
    doc = prepare_document('5 USC 553(b)(B)')
    result = export_discovery({'document':doc,'accepted':[]}, reference_sources=[source(), other])
    scan = result['reference_scan']
    row, = scan['candidates']
    assert row['resolution']['status'] == 'ambiguous'
    assert len(row['resolution']['target_ids']) == 2
    assert len(scan['reference_sources']) == 2
    assert len({t['source_id'] for t in scan['targets'].values()}) == 2
    for target in scan['targets'].values():
        assert all(ref['id'] in scan['reference_sources'][target['source_id']]['evidence'] for ref in target['evidence_refs'])


def test_duplicate_identifiers_are_not_first_match_wins():
    external = source('<paragraph identifier="/us/usc/t5/s553/b/B">Different.</paragraph>')
    scan = scan_references(prepare_document('5 USC 553(b)(B)'), reference_sources=[external])
    assert scan['candidates'][0]['resolution']['status'] == 'ambiguous'
    assert len(scan['targets']) == 2
    assert len(next(iter(scan['reference_sources'].values()))['records']) == 1


def test_supplied_source_is_parsed_once_despite_repeated_mentions(monkeypatch):
    external = source()
    actual, calls = uslm.read_uslm, []
    def observed(document):
        calls.append(document['id'])
        return actual(document)
    monkeypatch.setattr(uslm, 'read_uslm', observed)
    scan_references(prepare_document('5 USC 553(b)(B).\n' * 20), reference_sources=[external, external])
    assert calls == [external['id']]


@pytest.mark.parametrize('mutation', ['xml', 'text', 'source_map'])
def test_altered_external_source_is_refused(mutation):
    external = source()
    if mutation == 'xml': external['uslm_source']['xml'] += ' '
    elif mutation == 'text': external['text'] += 'changed'
    else: external['source_map'][0]['source_start'] += 1
    with pytest.raises(ValueError):
        scan_references(prepare_document('5 USC 553'), reference_sources=[external])


def test_wrong_format_is_not_accepted_as_an_external_body():
    with pytest.raises(ValueError, match='USLM'):
        scan_references(prepare_document('5 USC 553'), reference_sources=[prepare_document('553: text')])


def test_publisher_and_text_disagreement_does_not_resolve_the_text_target():
    doc = uslm.prepare_uslm(f'<uscDoc xmlns="{NS}"><section><p><ref href="/us/usc/t5/s999">5 USC 553(b)(B)</ref></p></section></uscDoc>')
    scan = scan_references(doc, reference_sources=[source()])
    row, = scan['candidates']
    assert row['value'] == '/us/usc/t5/s999'
    assert row['text_readings'][0]['value'] == '5 USC 553(b)(B)'
    assert not row['resolution']['target_ids'] and not scan['targets']


def test_section_dash_normalization_preserves_pinpoint_case():
    external = source('<section identifier="/us/usc/t42/s1395w–4"><paragraph identifier="/us/usc/t42/s1395w–4/A">Yes</paragraph></section>')
    rows = scan_references(prepare_document('42 USC 1395w-4(A). 42 USC 1395w-4(a).'), reference_sources=[external])['candidates']
    assert [r['resolution']['status'] for r in rows] == ['located', 'not_in_selected_sources']


def test_references_cli_matches_api(tmp_path):
    doc, external = prepare_document('5 USC 553(b)(B)'), source()
    primary, supplied, output = [tmp_path/n for n in ('document.json', 'source.json', 'out.json')]
    primary.write_text(json.dumps(doc))
    supplied.write_text(json.dumps(external))
    cli.main(['references', str(primary), '--reference-source', str(supplied), '--output', str(output)])
    assert json.loads(output.read_text()) == scan_references(doc, reference_sources=[external])


def test_broad_publisher_targets_do_not_export_whole_titles():
    external = uslm.prepare_uslm(f'<uscDoc xmlns="{NS}" identifier="/us/usc/t5"><main><title identifier="/us/usc/t5"><section identifier="/us/usc/t5/s553">Body.</section></title></main></uscDoc>')
    doc = uslm.prepare_uslm(f'<uscDoc xmlns="{NS}"><section><ref href="/us/usc/t5">Title 5</ref></section></uscDoc>')
    scan = scan_references(doc, reference_sources=[external])
    assert scan['candidates'][0]['resolution']['status'] == 'target_scope_not_supported'
    assert not scan['targets']
    assert not next(iter(scan['reference_sources'].values()))['records']


def test_explicitly_resupplied_document_resolves_its_plain_text_reference():
    doc = source('<p>5 USC 553</p>')
    scan = scan_references(doc, reference_sources=[doc])
    row, = [r for r in scan['candidates'] if r['kind'] == 'usc']
    assert row['resolution']['status'] == 'located'


def test_actual_xml_pinpoint_and_discovery_cli(tmp_path):
    fixture = Path(__file__).parent/'fixtures/uslm/reference-title5-s553.xml'
    external = load_document(fixture)
    document = prepare_document('5 U.S.C. 553(b)(B).')
    run = tmp_path/'run'
    run.mkdir()
    book = compile_candidates(document, [], {})
    for name, value in {'document.json':document, 'run.json':{}, 'rulebook.json':book,
                        'candidates.json':[], 'graph.jsonld':book['graph']}.items():
        (run/name).write_text(json.dumps(value))
    output = tmp_path/'discovery.json'
    cli.main(['discovery-export', str(run), '--reference-source', str(fixture), '--output', str(output)])
    scan = json.loads(output.read_text())['reference_scan']
    row, = scan['candidates']
    target = scan['targets'][row['resolution']['target_ids'][0]]
    assert external['text'][target['start']:target['end']].startswith('(B) when the agency for good cause finds')
    src = scan['reference_sources'][target['source_id']]
    record = src['records'][target['record_id']]
    assert 'Except when notice or hearing is required by statute' in record['text']
    assert 'Historical and Revision Notes' in record['text']
    assert row['resolution']['edition_match'] == 'not_established'
    assert next(p['value'] for p in src['publication'] if p['field'] == 'docPublicationName') == 'Online@119-102'
