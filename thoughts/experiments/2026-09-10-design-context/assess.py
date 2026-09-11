from pathlib import Path
import json,collections
from jsonschema import validate
from rulespec_extrapolator import extraction as e
ROOT=Path(__file__).resolve().parent
d=e._load(ROOT/'design.json');cases={c['id']:c for c in e._load(ROOT/'cases.json')};schema=e._load(ROOT/'schema.json');out=[]
for cell in d['cells']:
 c=cases[cell['case']];path=ROOT/'cells'/cell['id'];decoded=e._load(path/'decoded.json');payload=decoded['payload'];validate(payload,schema)
 assert {q['question_id'] for q in payload['answers']}=={q[0] for q in c['questions']} and len(payload['answers'])==len(c['questions'])
 allowed={'statement'}|({s['id'] for s in c['context']} if cell['arm']=='B' else set())
 assert all(set(q['support_refs'])<=allowed for q in payload['answers'])
 usage=e.recorded_usage(path)
 out.append({**cell,'schema_valid':True,'refs_exist':True,'errors':decoded['errors'],'usage':usage})
 print('\n'+cell['case']+' '+cell['arm']+' '+cell['id'])
 for q in payload['answers']:print(q['question_id'],q['conclusion'],q['answer'],'UNCERTAINTY',q['remaining_uncertainty'])
sums={}
for arm in ['A','B']:
 t=collections.Counter()
 for row in out:
  if row['arm']==arm:t.update(row['usage']['tokens'])
 sums[arm]=dict(t)
e._save(ROOT/'mechanical-assessment.json',{'cells':out,'tokens':sums});print('\nTOKENS',json.dumps(sums))
