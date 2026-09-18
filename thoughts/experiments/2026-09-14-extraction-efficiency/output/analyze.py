from pathlib import Path
from collections import Counter
from datetime import datetime
from copy import deepcopy
import json,hashlib
from jsonschema import Draft202012Validator
from rulespec_extrapolator import extraction as ex
R=Path(__file__).resolve().parent
reqfields={'statement','actor','actor_quote','kind','modality'}
rows=[]
for name in ['csbg-A','csbg-B','benefits-A','benefits-B']:
 p=R/name;request=json.loads(next(p.glob('*.request.json')).read_text());response=json.loads(next(p.glob('*.response.json')).read_text());attempt=json.loads(next(p.glob('attempt-????.json')).read_text());d=json.loads((p/'document.json').read_text());w=json.loads((p/'window.json').read_text());parsed=json.loads((p/'parsed.json').read_text());text=''.join(x.get('text','') for c in response.get('candidates',[]) for x in c.get('content',{}).get('parts',[]) if not x.get('thought'));data=json.loads(text)
 (p/'answer.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');(p/'source-focus.txt').write_text(d['text'][w['start']:w['end']]);
 fields=Counter();empty=Counter();pop=Counter();size=Counter()
 for item in data['extractions']:
  for k,v in item['unit_attributes'].items():
   fields[k]+=1;size[k]+=len(json.dumps({k:v},ensure_ascii=False,separators=(',',':')))
   if v is None or v=='' or v==[]:empty[k]+=1
   else:pop[k]+=1
 lines=[]
 for i,c in enumerate(parsed['candidates']):
  lines.append(f"## {i}: {c['kind']} / {c['modality']}\n\n{c['summary']}\n\nActor: {c['actor']}\n\n")
  for key in ['defined_terms','term_refs','scope_text','scope_quotes','context_quotes','modality_quote','choice_text','choice_quote','alternative_quotes','logic_text','references']:
   if c.get(key):lines.append(f'{key}: {json.dumps(c[key],ensure_ascii=False)}\n\n')
 (p/'review.md').write_text(''.join(lines))
 usage=response['usage_metadata'];keys=['prompt_token_count','candidates_token_count','thoughts_token_count','total_token_count','cached_content_token_count']
 rows.append({'case':name,'request_model':request['model'],'model_version':response.get('model_version'),'actual_config_keys':list(request['config']),'max_output_tokens':request['config'].get('max_output_tokens'),'thinking_config':request['config'].get('thinking_config'),'sampling_keys_present':[k for k in ['temperature','top_p','top_k','candidate_count'] if k in request['config']], 'records':len(parsed['candidates']),'terms':len(data['terms']),'empty_optional_values':sum(v for k,v in empty.items() if k not in reqfields),'populated_optional_values':sum(v for k,v in pop.items() if k not in reqfields),'field_counts':dict(fields),'empty_values':dict(empty),'populated_values':dict(pop),'field_serialized_chars':dict(size),'usage':{k:usage.get(k) for k in keys},'response_chars':len(text),'wall_seconds':(datetime.fromisoformat(attempt['finished_at'])-datetime.fromisoformat(attempt['started_at'])).total_seconds(),'parsed_status':parsed['status'],'refusals':parsed['refusals'],'actual_schema_valid':not list(Draft202012Validator(request['config']['response_json_schema']).iter_errors(data)),'redecode_equal':parsed==ex._attempt_result(attempt,p,d,w),'source_catalog_sha256':ex._digest(ex.passage_catalog(d,w)),'source_sha256':d['sha256']})
(R/'metrics.json').write_text(json.dumps(rows,indent=2)+'\n')
for row in rows: print({k:v for k,v in row.items() if k in ['case','records','terms','empty_optional_values','populated_optional_values','usage','wall_seconds','actual_schema_valid','redecode_equal']})
files={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in R.rglob('*') if p.is_file() and p.name!='MANIFEST.json'}
(R/'MANIFEST.json').write_text(json.dumps({'sha256':files},indent=2)+'\n')
