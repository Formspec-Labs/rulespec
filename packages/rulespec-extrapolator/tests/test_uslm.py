"""Publisher links retain exact source evidence and do not become legal verdicts."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from rulespec_extrapolator import cli
from rulespec_extrapolator.core import build_graph, compile_candidates, validate_graph
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import load_document
from rulespec_extrapolator.extraction import _window_prompt, plan_windows
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator.uslm import SourceIndex, prepare_xml, read_xml

NS = 'http://xml.house.gov/schemas/uslm/1.0'
FIXTURE = Path(__file__).parent/'fixtures/uslm/fresh-title-05-pair.xml'


def document(body):
    return prepare_xml(f'<uscDoc xmlns="{NS}" identifier="/us/usc/t5"><section identifier="/us/usc/t5/s1">{body}</section></uscDoc>')


@pytest.mark.parametrize('path, expected', [
    ('/*[1]/*[1]', [('Café 😀.', 0, 7), ('Second.', 9, 16)]),
    ('/*[1]/*[1]/*[1]', [('Café 😀.', 0, 7)]),
    ('/*[1]/*[1]/*[2]', [('Second.', 9, 16)]),
])
def test_native_support_keeps_exact_unicode_source_intervals_and_xpath(path, expected):
    doc = document('<p>Café 😀.</p><p>Second.</p>')
    assert doc['text'] == 'Café 😀.\n\nSecond.'
    index = SourceIndex(doc)
    fragment, evidence = index.support(path, index.prepared['nodes'][path], 'target')
    assert [(item['quote'], item['start'], item['end']) for item in evidence] == expected
    assert all(item['field'] == 'target' for item in evidence)
    assert index.fragments[fragment]['oa:hasSelector'] == [
        {'@type': 'oa:XPathSelector', 'rdf:value': path}]
    assert index.fragments[fragment]['oa:hasSource'] == index.source_id
    assert index.support(path, index.prepared['nodes'][path], 'target', include_text=False) == (fragment, [])


def test_fresh_definition_target_and_core_fragments():
    doc = load_document(FIXTURE)
    scan = scan_references(doc)
    rows = [r for r in scan['candidates'] if r['kind']=='publisher_reference']
    assert len(rows)==37
    row, = [r for r in rows if r['value']=='/us/usc/t5/s5721']
    assert row['reading']['context']=='operative'
    assert row['resolution']['status']=='located'
    assert row['record_ids']
    target, = [scan['targets'][key] for key in row['resolution']['target_ids']]
    target_text=doc['text'][target['start']:target['end']]
    assert '“agency” means—' in target_text
    assert 'but does not include a Government controlled corporation;' in target_text
    assert all(doc['text'][e['start']:e['end']]==e['quote'] for e in target['evidence'])
    graph = build_graph(doc, [], {})
    graph['@graph'].extend([scan['publisher_source'], *scan['xml_fragments'].values()])
    assert validate_graph(graph)['shacl_conforms']
    assert scan['semantic_completeness']=='not_established'


def test_discovery_shares_targets_and_uses_existing_evidence_table():
    doc = document('<p><ref href="/us/usc/t5/s1/a">Same</ref></p><p><ref href="/us/usc/t5/s1/a">Same</ref></p><subsection identifier="/us/usc/t5/s1/a"><num>(a)</num><heading>Target</heading><content>Meaning.</content></subsection>')
    book=compile_candidates(doc, [], {})
    output=export_discovery(book, include_references=True)
    scan=output['reference_scan']
    assert len(scan['candidates'])==2 and len(scan['targets'])==1
    assert scan['candidates'][0]['id']!=scan['candidates'][1]['id']
    assert scan['candidates'][0]['resolution']['target_ids']==scan['candidates'][1]['resolution']['target_ids']
    target, = scan['targets'].values()
    assert 'evidence' not in target and target['evidence_refs']
    for reference in target['evidence_refs']:
        position=output['evidence'][reference['id']]
        assert not any(p['kind']=='inserted' and p['start']<position['end'] and position['start']<p['end'] for p in doc['source_map'])


def test_duplicate_and_absent_targets_remain_explicit():
    doc=document('<p><ref href="/us/usc/t5/s1/a">(a)</ref> and <ref href="/us/usc/t5/s999">missing</ref></p><subsection identifier="/us/usc/t5/s1/a">One</subsection><subsection identifier="/us/usc/t5/s1/a">Two</subsection>')
    rows=scan_references(doc)['candidates']
    assert rows[0]['resolution']['status']=='ambiguous'
    assert len(rows[0]['resolution']['target_ids'])==2
    assert rows[1]['resolution']=={'status':'not_in_selected_source','target_ids':[]}


def test_empty_publisher_mention_has_xml_evidence_without_a_quote():
    scan=scan_references(document('<p>Before<ref href="/us/usc/t5/s1/a"/>after.</p>'))
    row, = scan['candidates']
    assert row['text_status']=='no_visible_text' and row['evidence']==[]
    assert row['xml_evidence_refs'][0] in scan['xml_fragments']


def test_text_reading_prefix_merges_without_losing_a_disagreement():
    doc=document('<p><ref href="/us/pl/89/554/s2">Pub. L. 94–183, § 2(1)</ref></p>')
    row, = scan_references(doc)['candidates']
    assert row['value']=='/us/pl/89/554/s2'
    reading, = row['text_readings']
    assert reading['kind']=='public_law' and reading['value']=='Public Law 94-183'
    assert reading['evidence'][0]['quote']=='Pub. L. 94–183'
    assert reading['disposition']=='candidates'
    assert row['resolution']['status']=='not_in_selected_source'


def test_merged_rejected_reading_keeps_its_reason_and_discovery_evidence():
    doc=document('<p><ref href="/us/usc/t5/s1">99 CFR 1.1</ref></p>')
    scan=scan_references(doc)
    row, = scan['candidates']
    reading, = row['text_readings']
    assert scan['rejected']==[]
    assert reading['disposition']=='rejected' and reading['code']=='cfr_title_impossible'
    assert reading['evidence'][0]['quote']=='99 CFR 1.1'
    exported=export_discovery(compile_candidates(doc, [], {}), include_references=True)
    saved=exported['reference_scan']['candidates'][0]['text_readings'][0]
    assert saved['code']==reading['code'] and saved['disposition']=='rejected'
    assert saved['evidence_refs'] and 'evidence' not in saved
    assert all(r['id'] in exported['evidence'] for r in saved['evidence_refs'])


def test_publisher_xml_compilations_keep_separate_occurrences_and_editorial_uncertainty():
    doc = load_document(FIXTURE.with_name('compilation-title-18.xml'))
    scan = scan_references(doc)
    assert len([r for r in scan['candidates'] if r['kind'] == 'publisher_reference']) == 12
    first, second = [r for r in scan['candidates'] if r['kind'] == 'eo_compilation']
    assert first['id'] != second['id']
    for row in (first, second):
        assert row['reading'] == {'compilation_start': '1950', 'page': '71'}
        support, = row['evidence']
        assert doc['text'][support['start']:support['end']] == row['value'] == support['quote']
    assert 'probably should refer to Proc. 2914' in doc['text']
    assert not any(r['kind'] == 'cfr' for r in scan['candidates'])


def test_compilation_text_reading_retains_publisher_link_and_shared_evidence():
    # Constructed disagreement: a publisher link does not prove that its label
    # names the same target. Use a supported USLM identifier family.
    doc = document('<p><ref href="/us/usc/t50/s1">3 CFR 60–61 (1971–1975 Comp.)</ref></p>')
    exported = export_discovery(compile_candidates(doc, [], {}), include_references=True)
    row, = exported['reference_scan']['candidates']
    assert row['kind'] == 'publisher_reference' and row['value'] == '/us/usc/t50/s1'
    assert row['resolution']['status'] == 'not_in_selected_source'
    reading, = row['text_readings']
    assert reading['kind'] == 'eo_compilation'
    assert reading['reading'] == {'compilation_start': '1971', 'compilation_end': '1975', 'page': '60', 'page_end': '61'}
    support, = reading['evidence_refs']
    position = exported['evidence'][support['id']]
    assert doc['text'][position['start']:position['end']] == '3 CFR 60–61 (1971–1975 Comp.)'
    assert row['xml_evidence_refs']


def test_compilation_like_xml_attributes_are_not_visible_references():
    doc = document('<p title="3 CFR 127 (1981 Comp.)">Ordinary text.</p>')
    assert '3 CFR' not in doc['text']
    assert not scan_references(doc)['candidates']


@pytest.mark.parametrize('case', json.loads((Path(__file__).parent/'fixtures/uslm/containment.json').read_text()), ids=lambda c: c['id'])
def test_unique_publisher_containment_preserves_ambiguity_and_reading_targets(case):
    doc = document(case['body'])
    scan = scan_references(doc)
    publisher = [row for row in scan['candidates'] if row['kind'] == 'publisher_reference']
    associated = [(parent, row) for parent in publisher for row in parent.get('text_readings', [])]
    assert len(associated) == case['associated']
    assert sum(row['kind'] != 'publisher_reference' for row in scan['candidates'] + scan['rejected']) == case['separate']
    nodes = read_xml(doc)['nodes']
    spans = {parent['id']: nodes[scan['xml_fragments'][parent['xml_evidence_refs'][0]]['oa:hasSelector'][0]['rdf:value']]
             for parent in publisher}
    for parent, reading in associated:
        evidence = reading['evidence'][0]
        assert doc['text'][evidence['start']:evidence['end']] == evidence['quote']
        # Independent exhaustive test oracle; production follows only enclosing anchors.
        owners = [identity for identity, node in spans.items()
                  if 'start' in node and node['start'] <= evidence['start'] and evidence['end'] <= node['end']]
        assert owners == [parent['id']]
    if case['id'] == 'conflicting_target':
        parent, reading = associated[0]
        assert parent['value'] == '/us/pl/89/554/s2'
        assert reading['value'] == 'Public Law 94-183'
    if case['id'] == 'rejected_interior':
        assert associated[0][1]['disposition'] == 'rejected'
        assert associated[0][1]['code'] == 'cfr_title_impossible'


@pytest.mark.parametrize('mutation', ['xml','text','source_map','version'])
def test_saved_transformation_mutations_are_refused(mutation):
    doc=document('<p>Original.</p>')
    if mutation=='xml': doc['uslm_source']['xml']=doc['uslm_source']['xml'].replace('Original','Changed')
    elif mutation=='text': doc['text']='Changed.'
    elif mutation=='source_map': doc['source_map'][0]['source_start']+=1
    else: doc['uslm_source']['preparation']='unknown-version'
    with pytest.raises(ValueError): read_xml(doc)


def test_raw_xml_attributes_do_not_enter_model_prompt():
    doc=prepare_xml(f'<uscDoc xmlns="{NS}" id="XML_ONLY_SENTINEL"><section><p>Source sentence.</p></section></uscDoc>')
    window, = plan_windows(doc, 1000)
    generator=SimpleNamespace(render=lambda text, additional_context: text+additional_context)
    prompt=_window_prompt(generator, doc, window)
    assert 'Source sentence.' in prompt and 'XML_ONLY_SENTINEL' not in prompt


def test_prepare_and_references_cli_use_pinned_xml(tmp_path):
    prepared=tmp_path/'document.json'
    output=tmp_path/'references.json'
    cli.main(['prepare', str(FIXTURE), '--output', str(prepared)])
    cli.main(['references', str(prepared), '--output', str(output)])
    saved=json.loads(prepared.read_text())
    assert saved['uslm_source']['xml']==FIXTURE.read_text()
    assert json.loads(output.read_text())==scan_references(saved)
