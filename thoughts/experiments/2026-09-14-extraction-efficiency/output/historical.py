from pathlib import Path
from collections import Counter
import json
from rulespec_extrapolator import extraction as ex
ROOT=Path(__file__).resolve().parent; P=ROOT.parents[3]/'thoughts/experiments/2026-09-13-csbg-retest/B'
fields=Counter(); chars=Counter(); empty=Counter(); empty_chars=Counter(); required={'statement','kind','modality','actor','actor_quote'}
doc=json.loads((P/'document.json').read_text());windows={w['index']:w for w in json.loads((P/'run.json').read_text())['windows']}
checks=[];usage=Counter();raw_chars=0;compact_chars=0
for p in sorted(P.glob('attempt-*.response.json')):
 raw=json.loads(p.read_text());text=''.join(x.get('text','') for c in raw.get('candidates',[]) for x in c.get('content',{}).get('parts',[]) if not x.get('thought'))
 try: data=json.loads(text)
 except ValueError: continue
 for k,v in raw['usage_metadata'].items():
  if isinstance(v,int):usage[k]+=v
 compact=json.loads(text)
 for item,comp in zip(data.get('extractions',[]),compact.get('extractions',[])):
  for k,v in item['unit_attributes'].items():
   size=len(json.dumps({k:v},ensure_ascii=False,separators=(',',':')))-2
   fields[k]+=1;chars[k]+=size
   if v is None or v=='' or v==[]:
    empty[k]+=1;empty_chars[k]+=size
    if k not in required:comp['unit_attributes'].pop(k)
 before=ex.parse_response_text(text,doc,windows[int(p.name.split('.')[0].split('-')[1])])
 after=ex.parse_response_text(json.dumps(compact),doc,windows[int(p.name.split('.')[0].split('-')[1])])
 # Refusal raw rows can naturally differ; primary reconstructed candidates must not.
 checks.append({'file':p.name,'candidates_equal':before['candidates']==after['candidates'],'status_equal':before['status']==after['status'],'refusal_codes_equal':[x['code'] for x in before['refusals']]==[x['code'] for x in after['refusals']]})
 raw_chars+=len(json.dumps(data,ensure_ascii=False,separators=(',',':')));compact_chars+=len(json.dumps(compact,ensure_ascii=False,separators=(',',':')))
out={'records':fields['statement'],'fields':dict(fields),'empty_values':dict(empty),'serialized_field_chars':dict(chars),'empty_value_chars':dict(empty_chars),'empty_optional_values':sum(v for k,v in empty.items() if k not in required),'empty_optional_chars':sum(v for k,v in empty_chars.items() if k not in required),'compact_response_chars':raw_chars,'without_empty_optional_chars':compact_chars,'historical_provider_usage':dict(usage),'native_decode_checks':checks,'note':'Character attribution is not token attribution. Removing fields after a response saves no provider tokens. These are fixed-response parser compatibility checks.'}
(ROOT/'historical-analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in {'fields','empty_values','serialized_field_chars','empty_value_chars','native_decode_checks'}},indent=2));print('all_native_decode_checks',all(all(v for k,v in c.items() if k!='file') for c in checks))
