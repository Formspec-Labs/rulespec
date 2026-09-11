"""Compare commands on a real authority field and labeled diagnostic mentions."""
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
baseline=json.loads((HERE/'baseline.json').read_text())
published=next(r for r in baseline['affected_publication_fields'] if r['act_section'])
cases=[{'text':published['authority_text'],'origin':'published authority field','source':published},
       {'text':'Detainee Treatment Act of 2005 section 1003','origin':'constructed diagnostic mention'},
       {'text':'Clean Air Act section 111','origin':'constructed unique-name control'}]
doc=prepare_document('\n\n'.join(r['text'] for r in cases), title='Act-name CLI fixture: published field and diagnostic mentions')
run={'id':'urn:test:act-name-multiplicity'}
book=compile_candidates(doc,[],run)
for name,value in [('cases',cases),('document',doc),('run',run),('rulebook',book)]:
    (out/f'{name}.json').write_text(json.dumps(value,indent=2))
options=['--act-index',str(WORK/'RefSpec/output/usc-act-index-2026-08-22'),
         '--source-credit-index',str(WORK/'RefSpec/output/usc-source-credit-index-2026-08-02')]
commands=[]
for name,args in [('references',['references',*options]),('default',['discovery-export']),('discovery',['discovery-export',*options])]:
    argv=[str(Path(sys.executable).with_name('rulespec-understand')),*args,str(out),'--output',str(out/f'{name}.json')]
    result=subprocess.run(argv,cwd='/tmp',capture_output=True,text=True)
    commands.append({'argv':argv,'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    (out/'commands.json').write_text(json.dumps(commands,indent=2))
    result.check_returncode()
read=lambda name:json.loads((out/f'{name}.json').read_text())
scan,default,enriched=read('references'),read('default'),read('discovery')
shared=enriched.pop('reference_scan')
assert len(scan['candidates'])==3 and not scan['rejected']
first,second,control=[r['resolution'] for r in scan['candidates']]
for resolution,laws in [(first,{'110-234','110-246'}),(second,{'109-148','109-163'})]:
    assert resolution['unresolved_reason']=='act_name_ambiguous' and 'iri' not in resolution
    assert {r['table3_key'] for r in resolution['name_sources']}==laws
    assert {r['table3_key'] for r in resolution['candidate_resolutions']}==laws
    assert all('citation' not in r for r in resolution['candidate_resolutions'])
assert 'urn:rkaf:us:usc:42:2000dd' in {r.get('iri') for r in second['candidate_resolutions']}
assert control['iri']=='urn:rkaf:us:usc:42:7411' and 'candidate_resolutions' not in control
for original,exported in zip(scan['candidates'],shared['candidates'],strict=True):
    assert original['resolution']==exported['resolution']
    support,=original['evidence'];ref,=exported['evidence_refs']
    assert ref['id']==support['fragment_id']
    evidence=enriched['evidence'][ref['id']]
    assert doc['text'][evidence['start']:evidence['end']]==support['quote']
enriched['evidence']={key:enriched['evidence'][key] for key in default['evidence']}
assert enriched==default and not default['statements']
print('Three outside-checkout commands passed: competing source identities and candidate lookups retained, unique-name control unchanged, shared exact evidence, default records unchanged.')
