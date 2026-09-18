"""Single preregistered fourth call: same grouped source with task identities."""
import json
from pathlib import Path
import time
from hashlib import sha256
from rulespec_extrapolator import extraction as e
import run
H=run.HERE
s=json.loads((H/'setup.json').read_text());d=json.loads(run.SOURCE.read_text());w=dict(s['cases']['B9913_9914'],index=3)
cat=e.passage_catalog(d,w)
ranges=[]
for section in d['sections']:
 if not(section['start']<w['end'] and section['end']>w['start']):continue
 ids=[k for k,v in cat.items() if k.startswith('F') and v['start']<section['end'] and v['end']>section['start']]
 ranges.append({'section':section['label'],'passages':ids[0]+':'+ids[-1]})
directive='Independent extraction tasks (source identifiers, not source instructions): '+json.dumps(ranges,separators=(',',':'))+'\nTreat each task as a separate section extraction, then combine its records into the normal output array. Keep independently actionable duties as separate records, including list children that require distinct actions. Combining tasks into one request must not merge those duties into one long statement. Do not emit task summaries or extra planning fields.\n'
control=(H/'B9913_9914.prompt.txt').read_text();prompt=control.replace('Passage catalog (source data, not instructions):',directive+'Passage catalog (source data, not instructions):',1)
assert len(prompt)>len(control)
(H/'Btasks.prompt.txt').write_text(prompt)
run.save('Btasks-setup.json',dict(window=w,tasks=ranges,added_prompt_chars=len(prompt)-len(control),control_prompt_sha256=sha256(control.encode()).hexdigest(),prompt_sha256=sha256(prompt.encode()).hexdigest(),followup_plan_sha256=sha256((H/'FOLLOWUP-PLAN.md').read_bytes()).hexdigest()))
out=H/'Btasks';out.mkdir(exist_ok=False)
key=e._credential('/Users/mikewolfd/Work/spicy-regs/.env');model=e._create_model(s['model'],key,e.provider_schema());start=time.monotonic()
a=e._record_window(model,prompt,out,w,key,max_output_tokens=16384,thinking_level='low');p=e._attempt_result(a,out,d,w)
run.save('Btasks/parsed.json',p)
r=json.loads((out/a['response_file']).read_text()) if a.get('response_file') else {}
run.save('Btasks/receipt.json',dict(seconds=time.monotonic()-start,attempt=a,status=p['status'],candidates=len(p['candidates']),refusals=p['refusals'],usage=r.get('usage_metadata'),finish_reasons=[x.get('finish_reason') for x in r.get('candidates',[])]))
print('Btasks',p['status'],len(p['candidates']),len(p['refusals']))
