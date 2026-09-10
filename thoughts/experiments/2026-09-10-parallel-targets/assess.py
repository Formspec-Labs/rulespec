"""Replay and token/edge accounting; manual semantics remain in REVIEW.md."""
from pathlib import Path
from rulespec_extrapolator import extraction as e, refinement as r
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.review_store import ReviewStore
ROOT=Path(__file__).resolve().parent
rows=[]
for cell in e._load(ROOT/'design.json')['cells']:
 p=ROOT/'cells'/cell['id']; result=e._load(p/'result.json')
 before=e._load(ROOT/'inputs'/cell['case']/'book.json'); after=e._load(p/'after.json')
 assert ReviewStore(p/'workspace').snapshot()==after
 assert ReviewStore(ROOT/'baseline'/cell['case'])._snapshot(after['history'])==after
 assert after['history']==[o['event'] for o in result['outcomes'] if o['status']=='applied']
 assert export_discovery(after)==e._load(p/'discovery.json')
 old={c['rule_id']:c for c in before['accepted']}; now={c['rule_id']:c for c in after['accepted']}
 fields=r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
 preserved=[]
 for identity,c in old.items():
  d=now[identity]
  assert all(c.get(k)==d.get(k) for k in fields if k!='relation'),identity
  assert c['quote']==d['quote'] and c['evidence']==d['evidence'],identity
  preserved.append(identity)
 aliases={c['id']:f'C{i:04d}' for i,c in enumerate(before['accepted'])}
 alias_rule={c['rule_id']:f'C{i:04d}' for i,c in enumerate(before['accepted'])}
 links=[dict(source=alias_rule.get(c['rule_id'],'new'),kind=c['kind'],summary=c['summary'],targets=[aliases.get(t,t) for t in c['target_ids']]) for c in after['accepted'] if c['target_ids']]
 stages={}
 for stage in ['proposal','challenge']:
  ap=p/stage/'attempt-0000.json'
  if not ap.exists():continue
  attempt=e._load(ap); req=e._load(p/stage/attempt['request_file']);resp=e._load(p/stage/attempt['response_file'])
  assert req['model']==e.DEFAULT_MODEL
  schema=r.proposal_schema() if stage=='proposal' else r.CHECK_SCHEMA
  assert req['config']==dict(temperature=0,max_output_tokens=32768,candidate_count=1,response_mime_type='application/json',response_json_schema=schema)
  use=resp.get('usage_metadata') or {}
  stages[stage]={k:use.get(v) for k,v in dict(input='prompt_token_count',answer='candidates_token_count',thinking='thoughts_token_count',total='total_token_count').items()}
 rows.append(dict(**cell,links=links,stages=stages,issues=result['issues'],decoded=len(result['proposals']),prepared=len(result['prepared']),supported=sum(c['verdict']=='supported' for c in result['checks'].values()),applied=sum(o['status']=='applied' for o in result['outcomes']),original_meanings_and_evidence_preserved=len(preserved),current_issues=after['current_issues']))
totals={arm:{key:sum((stage[key] or 0) for row in rows if row['arm']==arm for stage in row['stages'].values()) for key in ['input','answer','thinking','total']} for arm in ['A','B']}
e._save(ROOT/'assessment.json',dict(cells=rows,totals=totals,total_ratio=totals['B']['total']/totals['A']['total'],missing_usage=[(row['id'],name,k) for row in rows for name,stage in row['stages'].items() for k,v in stage.items() if v is None]))
print(e._canonical(dict(totals=totals,cells=[{k:v for k,v in row.items() if k not in ['current_issues','stages']} for row in rows])))
