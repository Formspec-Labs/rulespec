from pathlib import Path
from copy import deepcopy
import json, re, time, hashlib
from rulespec_extrapolator import extraction as ex
from rulespec_extrapolator.schemas import load_schema
from langextract.providers.schemas.gemini import GeminiSchema

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
CSBG=REPO/'thoughts/experiments/2026-09-13-csbg-retest/B'
BENEFITS=REPO/'thoughts/experiments/2026-09-13-repair-finish/extract/benefits'

def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def nonempty(node):
    node=deepcopy(node)
    if 'anyOf' in node:
        node['anyOf']=[nonempty(x) for x in node['anyOf'] if x.get('type')!='null']
    if node.get('type')=='string': node['minLength']=max(1,node.get('minLength',0))
    if node.get('type')=='array': node['minItems']=max(1,node.get('minItems',0))
    # Preserve domain descriptions, adapting only the absent-value vocabulary.
    if 'description' in node:
        node['description']=re.sub(r'\bNull\b','Omit this field',node['description'])
        node['description']=re.sub(r'\bnull\b','omitted',node['description'])
    return node

def schema_b():
    s=deepcopy(load_schema('provider'))
    attrs=s['properties']['extractions']['items']['properties']['unit_attributes']
    for k,v in list(attrs['properties'].items()):
        if k not in attrs['required']:
            attrs['properties'][k]=nonempty(v)
    return s

if __name__=='__main__':
    start=time.monotonic()
    save(ROOT/'runtime.json',{'versions':ex._runtime_versions(),'extraction_path':str(Path(ex.__file__)),'extraction_sha256':hashlib.sha256(Path(ex.__file__).read_bytes()).hexdigest()})
    a=load_schema('provider'); b=schema_b()
    save(ROOT/'A.schema.json',a);save(ROOT/'B.schema.json',b)
    desc_b=ex.PROMPT+'\n\nOutput representation for this request: Optional attributes must be OMITTED when they add no substantive information. Do not emit optional nulls, empty strings, or empty arrays; do not invent or duplicate content to fill them. Keep required actor and actor_quote null when source support is absent. All meanings and governing conditions must still be fully present in statement. All useful optional fields remain available.\n'
    (ROOT/'A.prompt-description.txt').write_text(ex.PROMPT)
    (ROOT/'B.prompt-description.txt').write_text(desc_b)
    key=ex._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    for case,arm in [('csbg','A'),('csbg','B'),('benefits','B'),('benefits','A')]:
        if time.monotonic()-start>900: raise SystemExit('15-minute capture bound reached')
        out=ROOT/f'{case}-{arm}';out.mkdir(exist_ok=False)
        folder=CSBG if case=='csbg' else BENEFITS
        document=json.loads((folder/'document.json').read_text())
        window=json.loads((folder/'run.json').read_text())['windows'][8 if case=='csbg' else 0]
        save(out/'document.json',document);save(out/'window.json',window)
        desc=ex.PROMPT if arm=='A' else desc_b
        prompt=ex._window_prompt(ex._prompt_generator([],description=desc),document,window)
        model=ex._create_model('gemini-3.8-flash',key,GeminiSchema.from_schema_dict(a if arm=='A' else b))
        print('start',case,arm,flush=True)
        attempt=ex._record_window(model,prompt,out,window,key,max_output_tokens=16384,thinking_level='low')
        result=ex._attempt_result(attempt,out,document,window);save(out/'parsed.json',result)
        print('finish',case,arm,result['status'],'candidates',len(result['candidates']),'refusals',len(result['refusals']),flush=True)
    save(ROOT/'run-receipt.json',{'capture_wall_seconds':time.monotonic()-start,'calls':4,'retries':0})
