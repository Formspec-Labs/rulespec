"""Three bounded native extraction calls; no production mutation."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from rulespec_extrapolator import extraction as e, documents

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
SOURCE=REPO/'thoughts/experiments/2026-09-13-csbg-retest/B/document.json'

def save(name,value):
    target=HERE/name
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x') as out:json.dump(value,out,ensure_ascii=False,indent=2);out.write('\n')

def union(doc, windows, index):
    lo,hi=windows[0]['start'],windows[-1]['end']
    return documents.with_context(doc, dict(id='window-'+e._digest([doc['sha256'],lo,hi])[:20],index=index,start=lo,end=hi,text_sha256=e._digest(doc['text'][lo:hi]),section_ids=[s['id'] for s in doc['sections'] if s['start']<hi and s['end']>lo]))

def prepare():
    doc=json.loads(SOURCE.read_text());documents.validate_document(doc)
    planned=e.plan_windows(doc,section_windows=True)
    cases={'A9913':dict(planned[13],index=0),'B9913_9914':union(doc,planned[13:15],1),'A9914':dict(planned[14],index=2)}
    assert cases['A9913']['end']==cases['A9914']['start']
    assert sum(x['end']-x['start'] for k,x in cases.items() if k.startswith('A'))==cases['B9913_9914']['end']-cases['B9913_9914']['start']
    examples=e.invented_examples();schema=e.provider_schema()
    fingerprints=e._freeze(HERE,examples,schema.schema_dict)
    save('setup.json',dict(source=str(SOURCE),source_sha256=doc['sha256'],git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),runtime=e.__file__,fingerprints=fingerprints,cases=cases,order=list(cases),model='gemini-3.8-flash',thinking_level='low',max_output_tokens=16384))
    gen=e._prompt_generator(examples)
    for name,w in cases.items():(HERE/(name+'.prompt.txt')).write_text(e._window_prompt(gen,doc,w))
    save('pins.json',{str(p):sha256(p.read_bytes()).hexdigest() for p in [SOURCE,HERE/'PLAN.md',HERE/'run.py',HERE/'setup.json',*HERE.glob('*.prompt.txt')]})

def capture(name):
    for p,h in json.loads((HERE/'pins.json').read_text()).items():assert sha256(Path(p).read_bytes()).hexdigest()==h,p
    setup=json.loads((HERE/'setup.json').read_text());w=setup['cases'][name]
    doc=json.loads(SOURCE.read_text());out=HERE/name;out.mkdir(exist_ok=False)
    key=e._credential('/Users/mikewolfd/Work/spicy-regs/.env')
    model=e._create_model(setup['model'],key,e.provider_schema())
    start=time.monotonic()
    attempt=e._record_window(model,(HERE/(name+'.prompt.txt')).read_text(),out,w,key,max_output_tokens=16384,thinking_level='low')
    result=e._attempt_result(attempt,out,doc,w)
    save(name+'/parsed.json',result)
    raw=json.loads((out/attempt['response_file']).read_text()) if attempt.get('response_file') else {}
    save(name+'/receipt.json',dict(seconds=time.monotonic()-start,attempt=attempt,status=result['status'],candidates=len(result['candidates']),refusals=result['refusals'],usage=raw.get('usage_metadata'),finish_reasons=[x.get('finish_reason') for x in raw.get('candidates',[])]))
    print(name,result['status'],len(result['candidates']),len(result['refusals']),flush=True)

if __name__=='__main__':
    prepare() if sys.argv[1]=='prepare' else capture(sys.argv[1])
