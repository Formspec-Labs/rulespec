"""Installed commands over published fields and labeled diagnostic mentions."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document

HERE=Path(__file__).resolve().parent
WORK=HERE.parents[3]
parser=argparse.ArgumentParser()
parser.add_argument('--output-dir',type=Path,required=True)
out=parser.parse_args().output_dir.resolve()
out.mkdir()
published=json.loads((HERE.parent/'2026-09-11-source-credit-consumption/publication-fields.json').read_text())
cases=[{'text':row['authority_text'],'origin':'published authority field','rin':row['rin'],'publication_id':row['publication_id']}
       for row in published[:2]]
cases += [{'text':text,'origin':'constructed diagnostic mention of a source-indexed act/section'} for text in (
    'Defense Against Weapons of Mass Destruction Act of 1996 section 1416',
    'Energy Act of 2020 section 8004','Clean Air Act section 111')]
doc=prepare_document('\n\n'.join(c['text'] for c in cases),title='Constructed policy CLI fixture with published and diagnostic fields')
doc['source_map']=[]
start=0
for n,case in enumerate(cases):
    if n:
        doc['source_map'].append({'kind':'inserted','start':start,'end':start+2,'text':'\n\n'})
        start+=2
    end=start+len(case['text'])
    doc['source_map'].append({'kind':'source','start':start,'end':end,'source_id':f'urn:test:policy-field:{n}',
                              'source_start':0,'source_end':end-start})
    start=end
run={'id':'urn:test:act-resolution-policy'}
book=compile_candidates(doc,[],run)
for name,value in [('cases',cases),('document',doc),('run',run),('rulebook',book)]:
    (out/f'{name}.json').write_text(json.dumps(value,indent=2))
options=['--act-index',str(WORK/'RefSpec/output/usc-act-index-2026-08-22'),
         '--source-credit-index',str(WORK/'RefSpec/output/usc-source-credit-index-2026-08-02')]
commands=[]
for name,args in [('references',['references',*options]),('default',['discovery-export']),
                 ('discovery',['discovery-export',*options])]:
    argv=[str(Path(sys.executable).with_name('rulespec-understand')),*args,str(out),'--output',str(out/f'{name}.json')]
    proc=subprocess.run(argv,cwd='/tmp',capture_output=True,text=True)
    commands.append({'argv':argv,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
    (out/'commands.json').write_text(json.dumps(commands,indent=2))
    proc.check_returncode()
read=lambda name:json.loads((out/f'{name}.json').read_text())
scan,default,enriched=read('references'),read('default'),read('discovery')
shared=enriched.pop('reference_scan')
assert len(scan['candidates'])==5 and not scan['rejected']
answers=[r['resolution'] for r in scan['candidates']]
assert [r.get('iri') for r in answers]==['urn:rkaf:us:usc:49:60303',None,None,None,'urn:rkaf:us:usc:42:7411']
assert answers[1]['table3_reason']==answers[3]['table3_reason']=='act_section_outside_act'
assert [len(answers[n]['source_credit_targets']) for n in (1,2,3)]==[4,2,2]
assert answers[2]['table3_candidate_iri']=='urn:rkaf:us:usc:50:2316'
assert answers[2]['unresolved_reason']=='act_section_ambiguous'
assert 'quarantine.parquet' in scan['indexes']['acts']['sha256']
for original,exported in zip(scan['candidates'],shared['candidates'],strict=True):
    assert original['resolution']==exported['resolution']
    support,=original['evidence'];ref,=exported['evidence_refs']
    assert (ref['id'],ref['roles'])==(support['fragment_id'],[support['field']])
    span=enriched['evidence'][ref['id']]
    assert doc['text'][span['start']:span['end']]==support['quote']
enriched['evidence']={key:enriched['evidence'][key] for key in default['evidence']}
assert enriched==default and not default['statements']
print('Three commands passed outside checkout: two unchanged mappings, two scope refusals, preserved plural targets/table candidate, shared exact evidence and unchanged default records.')
