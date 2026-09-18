"""Provider-free structural/cost accounting and capture replay."""
from datetime import datetime
import json
from pathlib import Path
import sys
from rulespec_extrapolator import documents, extraction as e
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run
HERE=run.HERE
SOURCE=run.SOURCE
PAST=SOURCE.parent

def size(value):return len(json.dumps(value,ensure_ascii=False,separators=(',',':')))

def main():
 doc=json.loads(SOURCE.read_text());saved=json.loads((PAST/'run.json').read_text());windows=e.plan_windows(doc,section_windows=True)
 gen=e._prompt_generator(e.invented_examples());schema=e.provider_schema().schema_dict
 per=[]
 for w in windows:
  recorded=saved['windows'][w['index']];a=json.loads((PAST/recorded['attempts'][0]).read_text());rq=json.loads((PAST/a['request_file']).read_text());rs=json.loads((PAST/a['response_file']).read_text());prompt=rq['contents'];ix=prompt.index('Document section index');cat=prompt.index('Passage catalog');sec=prompt.index('\nThis window covers')
  per.append(dict(index=w['index'],focus_chars=w['end']-w['start'],context_chars=sum(s['end']-s['start'] for s in w['context_spans']),prompt_chars=len(prompt),schema_json_chars=size(rq['config']['response_json_schema']),fixed_prefix_chars=ix,full_index_chars=sec-ix,usage=rs.get('usage_metadata'),seconds=(datetime.fromisoformat(a['finished_at'])-datetime.fromisoformat(a['started_at'])).total_seconds(),candidate_count=recorded['candidate_count']))
 simulations=[]
 for cap in (4000,6000,8000,10000):
  groups=[];pending=[]
  for w in windows:
   if pending and w['end']-pending[0]['start']>cap:groups.append(pending);pending=[]
   pending.append(w)
  if pending:groups.append(pending)
  merged=[run.union(doc,g,i) for i,g in enumerate(groups)]
  assert merged[0]['start']==0 and merged[-1]['end']==len(doc['text'])
  assert all(x['end']==y['start'] for x,y in zip(merged,merged[1:]))
  hard=windows[8];matching=[x for x in merged if x['start']<hard['end'] and x['end']>hard['start']]
  assert len(matching)==1 and matching[0]['start']==hard['start'] and matching[0]['end']==hard['end']
  prompts=[e._window_prompt(gen,doc,w) for w in merged]
  simulations.append(dict(cap_chars=cap,calls=len(merged),section_groups=[[x['index'] for x in g] for g in groups],focus_chars=sum(w['end']-w['start'] for w in merged),context_chars=sum(s['end']-s['start'] for w in merged for s in w['context_spans']),prompt_chars=sum(map(len,prompts)),schema_json_chars=sum(size(schema) for _ in merged),hard_9908_unchanged=True))
 jobs=[]
 for workers in (1,2,4):
  lanes=[0.0]*workers
  for job in per:
   pick=min(range(workers),key=lanes.__getitem__);lanes[pick]+=job['seconds']
  jobs.append(dict(workers=workers,simulated_provider_seconds=max(lanes),assumption='saved per-call times fixed; no service contention/rate limit/retry modeled'))
 report=dict(historical=dict(per_window=per,total_prompt_chars=sum(x['prompt_chars'] for x in per),total_schema_json_chars=sum(x['schema_json_chars'] for x in per),total_fixed_prefix_chars=sum(x['fixed_prefix_chars'] for x in per),total_full_index_chars=sum(x['full_index_chars'] for x in per),total_focus_chars=sum(x['focus_chars'] for x in per),total_context_chars=sum(x['context_chars'] for x in per)),grouping_simulations=simulations,concurrency_simulations=jobs)
 (HERE/'accounting.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 setup=json.loads((HERE/'setup.json').read_text());checks=[]
 cases=dict(setup['cases'])
 if (HERE/'Btasks-setup.json').exists():cases['Btasks']=json.loads((HERE/'Btasks-setup.json').read_text())['window']
 for name,w in cases.items():
  out=HERE/name
  if not (out/'parsed.json').exists():continue
  attempt=json.loads((out/f"attempt-{w['index']:04d}.json").read_text())
  parsed=e._attempt_result(attempt,out,doc,w)
  checks.append(dict(case=name,replay_equal=parsed==json.loads((out/'parsed.json').read_text())))
 (HERE/'replay.json').write_text(json.dumps(checks,indent=2)+'\n')
 print(json.dumps(dict(simulations=simulations,concurrency=jobs,replay=checks),indent=2))
if __name__=='__main__':main()
