"""Replay source outputs and test target/occurrence counterexamples."""
import json
from pathlib import Path

from probe import locate
from refspec.registry.uslm import USLM_NS

HERE=Path(__file__).resolve().parent
source=json.loads((HERE/'source-probe.json').read_text())
for row in source:
    case=next(x for x in json.loads((HERE/'cases.json').read_text()) if x['id']==row['id'])
    assert locate((HERE/row['capture']).read_bytes(),case['title']) == {
        k:v for k,v in row.items() if k not in ('id','capture')}

controls=[
    ('duplicate-targets', '<section identifier="/us/usc/t5/s1"><p><ref href="/us/usc/t5/s1/a">(a)</ref></p>'
        '<subsection identifier="/us/usc/t5/s1/a">First</subsection>'
        '<subsection identifier="/us/usc/t5/s1/a">Second</subsection></section>', ['ambiguous']),
    ('absent-target', '<section identifier="/us/usc/t5/s1"><ref href="/us/usc/t5/s2">section 2</ref></section>', ['not_in_selected_source']),
    ('repeated-mentions', '<section identifier="/us/usc/t5/s1"><ref href="/us/usc/t5/s1/a">same</ref> then '
        '<ref href="/us/usc/t5/s1/a">same</ref><subsection identifier="/us/usc/t5/s1/a">Target</subsection></section>', ['located','located']),
    ('inline-unicode', '<section identifier="/us/usc/t5/s1">🧭 before <ref href="/us/usc/t5/s1/a">§ 1'
        '<inline>(a)</inline> &amp; details</ref><subsection identifier="/us/usc/t5/s1/a">Target — text</subsection></section>', ['located']),
    ('empty-link-text', '<section identifier="/us/usc/t5/s1"><ref href="/us/usc/t5/s1/a"/>'
        '<subsection identifier="/us/usc/t5/s1/a">Target</subsection></section>', ['located']),
    ('contexts', '<toc><ref href="/us/usc/t5/s1">Contents</ref></toc>'
        '<section identifier="/us/usc/t5/s1"><ref href="/us/usc/t5/s1/a">operative</ref>'
        '<subsection identifier="/us/usc/t5/s1/a">Target</subsection>'
        '<sourceCredit><ref href="/us/usc/t5/s1/a">credit</ref></sourceCredit>'
        '<note topic="amendments"><ref href="/us/usc/t5/s1/a">note</ref></note></section>', ['located']*4),
    ('non-section-unit', '<reorganizationPlan identifier="/us/usc/t5a/rp1"><ref href="/us/usc/t5/s2">section 2</ref></reorganizationPlan>', ['not_in_selected_source']),
    ('missing-source-identifier', '<section status="repealed"><ref href="/us/pl/117/1">Repealed by law</ref></section>', ['not_in_selected_source']),
    ('fragment-and-footnote', '<section identifier="/us/usc/t5/s1"><ref href="#local">table</ref>'
        '<ref idref="footnote">1</ref><ref href="/us/usc/t5/s2">section 2</ref></section>', ['not_in_selected_source']),
    ('unknown-prefix', '<section identifier="/us/usc/t5/s1"><ref href="/us/unknown/2">unknown</ref></section>', None),
]
inputs=[{'id':name,'xml':f'<uscDoc xmlns="{USLM_NS}">{body}</uscDoc>', 'expected_target_status':expected}
        for name,body,expected in controls]
with (HERE/'controls.json').open('x') as f:
    json.dump(inputs,f,indent=2,ensure_ascii=False);f.write('\n')
results=[]
for case in inputs:
    error=None
    result=None
    try:
        result=locate(case['xml'].encode(),'05')
    except Exception as exc:
        error={'type':type(exc).__name__,'message':str(exc)}
    if case['expected_target_status'] is None:
        assert error and error['type']=='ExtractionError',case['id']
    else:
        assert error is None,(case['id'],error)
        assert [r['target']['status'] for r in result['occurrences']] == case['expected_target_status'],case['id']
    if case['id']=='duplicate-targets':
        assert len(result['occurrences'][0]['target']['sources'])==2
    if case['id']=='repeated-mentions':
        a,b=result['occurrences']
        assert a['source']['text_evidence']['fragment_id']!=b['source']['text_evidence']['fragment_id']
        assert a['reading']['sourceXPath']!=b['reading']['sourceXPath']
    if case['id']=='contexts':
        assert [r['reading']['context'] for r in result['occurrences']]==['toc','operative','sourceCredit','note']
    if case['id']=='empty-link-text':
        assert result['occurrences'][0]['source']['text_status']=='no_visible_text'
    results.append({**case,'result':result,'error':error})
with (HERE/'control-results.json').open('x') as f:
    json.dump(results,f,indent=2,ensure_ascii=False);f.write('\n')
print('Both source captures replay exactly; all 10 target/occurrence controls passed.')
