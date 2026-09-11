"""Application evidence checks with a constructed index; real indexes live in the experiment."""
import json

import pytest

from rulespec_extrapolator import cli
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.references import scan_references


@pytest.fixture
def act_index(tmp_path, monkeypatch):
    from refspec.registry import act_resolution as acts
    index = acts.ActIndex(table3_key_by_name={'clean air act':'1955:360'},
        classifications={'1955:360':{'111':(acts.Classification('42','7411',None,None),)}})
    # This unit fixture isolates adapter behavior, not upstream artifact verification.
    for name in ('receipt.json','usc-popular-names.parquet','usc-act-sections.parquet','quarantine.parquet'):
        (tmp_path/name).write_text('Constructed unit fixture, not a sealed release')
    monkeypatch.setattr(acts.ActIndex, 'from_artifact', classmethod(lambda cls,path:index))
    return tmp_path


def test_act_occurrences_keep_readings_and_unresolved_results(act_index):
    doc = prepare_document('Clean Air Act section 111(d). Clean Air Act section 111(d). Clean Air Act section 999999.')
    result = scan_references(doc, act_index=act_index)
    first, second, absent = result['candidates']
    assert first['id'] != second['id']
    assert first['reading']['pinpoint'] == ['d']
    assert first['resolution']['iri'] == 'urn:rkaf:us:usc:42:7411'
    assert first['resolution']['pinpoint_mapping'] == 'not_performed'
    assert first['resolution']['source_credit_status'] == 'not_consulted'
    assert 'citation' not in first['resolution']
    assert 'iri' not in absent['resolution']
    assert absent['resolution']['unresolved_reason'] == 'act_section_not_classified'
    assert result['indexes']['acts']['directory'] == str(act_index)
    assert 'quarantine.parquet' in result['indexes']['acts']['sha256']
    assert result['target_resolution'] == 'named_act_section_identity_only'
    assert result['semantic_completeness'] == 'not_established'


def test_inserted_act_name_cannot_acquire_a_resolved_identity(act_index):
    doc = prepare_document('Clean Air Act section 111')
    doc['source_map'] = [{'kind':'inserted','start':0,'end':len(doc['text']),'text':doc['text']}]
    result = scan_references(doc, act_index=act_index)
    assert not result['candidates']
    refused, = result['rejected']
    assert refused['code'] == 'reference_not_grounded_in_source'
    assert 'resolution' not in refused


def test_source_credits_require_an_act_index(tmp_path):
    with pytest.raises(ValueError, match='requires an act index'):
        scan_references(prepare_document('Clean Air Act section 111'), source_credit_index=tmp_path)


def test_discovery_uses_existing_evidence_for_act_readings(act_index):
    book = {'document':prepare_document('Section 111(d) of the Clean Air Act.'),'accepted':[]}
    default = export_discovery(book)
    assert 'reference_scan' not in default
    exported = export_discovery(book, act_index=act_index)
    row, = exported['reference_scan']['candidates']
    support, = row['evidence_refs']
    span = exported['evidence'][support['id']]
    assert book['document']['text'][span['start']:span['end']] == 'Section 111(d) of the Clean Air Act'
    assert exported['statements'] == default['statements']
    assert exported['records'] == default['records']
    assert row['resolution']['pinpoint_mapping'] == 'not_performed'


def test_cli_passes_explicit_index_path(act_index, tmp_path):
    source=tmp_path/'document.txt'
    source.write_text('Clean Air Act section 111')
    output=tmp_path/'references.json'
    assert cli.main(['references',str(source),'--act-index',str(act_index),'--output',str(output)]) == 0
    row, = json.loads(output.read_text())['candidates']
    assert row['resolution']['iri'] == 'urn:rkaf:us:usc:42:7411'


@pytest.mark.parametrize('mode', ['agreement','conflict','multiple','plural-with-table','wrong-division'])
def test_source_credit_outcomes_and_competing_evidence_survive_export(act_index, monkeypatch, mode):
    from refspec.registry import act_resolution as acts
    index = acts.ActIndex(table3_key_by_name={'pipes act of 2020':'116-260'},
        classifications={'116-260':{'103':() if mode == 'multiple' else (
            acts.Classification('49','60303',None,2215),)}},
        division_by_name={'pipes act of 2020':('R',2210)})
    sections = ['60303','60304'] if mode in ('multiple','plural-with-table') else ['60304' if mode == 'conflict' else '60303']
    credits = acts.SourceCreditIndex.from_rows([('116-260','R','103','49',s,None,None) for s in sections])
    monkeypatch.setattr(acts.ActIndex,'from_artifact',classmethod(lambda cls,path:index))
    monkeypatch.setattr(acts.SourceCreditIndex,'from_artifact',classmethod(lambda cls,path:credits))
    (act_index/'usc-source-credits.parquet').write_text('Constructed source-credit unit fixture')
    text = ('division N of the PIPES Act of 2020 section 103' if mode == 'wrong-division'
            else 'sec. 103 of the 2020 PIPES Act')
    doc = prepare_document(text)
    scan = scan_references(doc,act_index=act_index,source_credit_index=act_index)
    row, = scan['candidates']
    resolution = row['resolution']
    assert row['reading']['act_key'] == 'pipes act of 2020'
    assert row['evidence'][0]['quote'] == text
    if mode == 'agreement':
        assert resolution['answered_by'] == 'both'
        assert resolution['iri'] == 'urn:rkaf:us:usc:49:60303'
        assert 'source_credit_targets' not in resolution and 'conflicting_targets' not in resolution
    else:
        assert 'iri' not in resolution
        if mode == 'conflict':
            assert resolution['unresolved_reason'] == 'sources_disagree'
            assert resolution['conflicting_targets'] == {
                'table3':'urn:rkaf:us:usc:49:60303','source_credits':'urn:rkaf:us:usc:49:60304'}
        elif mode in ('multiple','plural-with-table'):
            assert resolution['source_credit_status'] == 'multi_target'
            assert resolution['source_credit_targets'] == [{'usc_title':'49','usc_section':s} for s in sections]
            if mode == 'plural-with-table':
                assert resolution['unresolved_reason'] == 'act_section_ambiguous'
                assert resolution['table3_candidate_iri'] == 'urn:rkaf:us:usc:49:60303'
        else:
            assert resolution['unresolved_reason'] == 'act_division_conflict'
            assert resolution['source_credit_status'] == 'not_consulted'
    export = export_discovery({'document':doc,'accepted':[]},act_index=act_index,source_credit_index=act_index)
    shared, = export['reference_scan']['candidates']
    assert shared['resolution'] == resolution
    assert 'evidence' not in shared and 'source_credits' in export['reference_scan']['indexes']
    assert not export['statements']


def test_name_candidates_survive_without_repeating_the_written_citation(act_index, monkeypatch):
    from refspec.registry import act_resolution as acts
    name='example act of 2000'
    records=tuple(acts.PopularNameRecord('Example Act of 2000','cite',table3_key=law)
                  for law in ('100-1','100-2'))
    index=acts.ActIndex(table3_key_by_name={name:None},name_candidates={name:records},
        classifications={law:{'101':(acts.Classification('42',target,None,None),)}
                         for law,target in [('100-1','1'),('100-2','2')]})
    monkeypatch.setattr(acts.ActIndex,'from_artifact',classmethod(lambda cls,path:index))
    doc=prepare_document('§ Example Act of 2000 section 101.')
    scan=scan_references(doc,act_index=act_index)
    occurrence,=scan['candidates']
    resolution=occurrence['resolution']
    assert resolution['unresolved_reason']=='act_name_ambiguous' and 'iri' not in resolution
    assert {c['iri'] for c in resolution['candidate_resolutions']}=={'urn:rkaf:us:usc:42:1','urn:rkaf:us:usc:42:2'}
    assert all('citation' not in c for c in resolution['candidate_resolutions'])
    assert [r['table3_key'] for r in resolution['name_sources']]==['100-1','100-2']
    exported=export_discovery({'document':doc,'accepted':[]},act_index=act_index)
    shared,=exported['reference_scan']['candidates']
    assert shared['resolution']==resolution
    assert exported['statements']==[]
