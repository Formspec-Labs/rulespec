from experiment import *
from rulespec_extrapolator.discovery import export_discovery

design=e._load(ROOT/'design.json');cells=[dict(phase='initial',**c) for c in design['cells']]
if (ROOT/'followup-completion.json').exists():cells += [dict(phase='current-guidance',**c) for c in e._load(ROOT/'followup-design.json')['cells']]
rows=[]
for cell in cells:
 path=ROOT/'cells'/cell['id'];result=e._load(path/'result.json');stages={}
 for stage in ['actor','proposal','challenge']:
  if not (path/stage/'attempt-0000.json').exists():continue
  attempt=e._load(path/stage/'attempt-0000.json');req=e._load(path/stage/attempt['request_file']);resp=e._load(path/stage/attempt['response_file']);u=resp.get('usage_metadata') or {}
  assert req['model']==e.DEFAULT_MODEL and req['config']['temperature']==0 and req['config']['max_output_tokens']==32768
  stages[stage]={k:u.get(v) for k,v in [('input','prompt_token_count'),('answer','candidates_token_count'),('thinking','thoughts_token_count'),('total','total_token_count')]}
 row=dict(**cell,stages=stages)
 if cell['case']=='links':
  before=e._load(ROOT/'inputs/rail-book.json');after=e._load(path/'after.json');store=ReviewStore(path/'workspace')
  assert store.snapshot()==after and store._snapshot(after['history'])==after and store._snapshot(before['history'])==before
  props=r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
  originals={c['rule_id']:c for c in before['accepted']}
  for c in after['accepted']:
   old=originals[c['rule_id']];assert all(c[k]==old[k] for k in props if k!='relation') and c['quote']==old['quote'] and c['evidence']==old['evidence']
  for out in result['outcomes']:
   if out['applied']:
    p=next(p for p in result['prepared'] if p['id']==out['id']);event=out['event']
    assert result['checks'][p['id']]['verdict']=='supported'
    assert event['replacement_fields']==[p['fields']]
    assert set(event['replacements'][0]['target_ids'])==set(p['qualification_ids'])
  assert after['history']==[o['event'] for o in result['outcomes'] if o['applied']]
  e._save(path/'discovery.json',export_discovery(after))
  row.update(applied=sum(x['applied'] for x in result['outcomes']),issues=result['issues'],review_evidence_reconstructed=True,original_fields_preserved=True)
 else:
  row.update(rows=len(result.get('rows',[])),grounded=sum(bool(x['evidence']) and (all(x['evidence']) if isinstance(x['evidence'],list) else True) for x in result.get('rows',[])))
 rows.append(row)
e._save(ROOT/'assessment.json',{'cells':rows,'totals':e.recorded_usage(ROOT/'cells',exclude=('workspace',))})
print(e._canonical(rows))
