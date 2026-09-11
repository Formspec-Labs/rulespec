"""Frozen representation comparison using the existing discovery BM25 diagnostic."""
import copy,hashlib,importlib.util,json,sys,time
from pathlib import Path
from rulespec_extrapolator.discovery import records
from rulespec_extrapolator.documents import source_passages
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[2]
HARNESS=REPO/'packages/rulespec-extrapolator/evaluation/discovery_trial.py'
spec=importlib.util.spec_from_file_location('discovery_trial',HARNESS); trial=importlib.util.module_from_spec(spec);spec.loader.exec_module(trial)
MODES=['source','summaries','combined']
def rows_for(books,mode):
 rows=[]
 for source,b in books.items():
  if mode!='combined': rows.extend(records(b,source,mode));continue
  claims={c['id']:c for c in b['accepted']}
  for r in records(b,source,'packets'):
   parts=[r['text']]+[claims[c]['summary'] for c in r['claim_ids']]
   parts += [e['quote'] for e in r['evidence'] if e['field'].startswith(('scope_text:','context:'))]
   r['text']='\n'.join(dict.fromkeys(parts));rows.append(r)
 return rows

def spans_for(hits,budget=None):
 # Retain exact spans without silently truncating a qualification. Cost is unique
 # source characters. Admit a complete evidence span only when budget permits.
 spans={}; used=0
 for h in hits:
  for e in h['evidence']:
   keys={(h['source'],i) for i in range(e['start'],e['end'])}
   prior=spans.setdefault(h['source'],set())
   extra={i for _,i in keys}-prior
   if budget is not None and used+len(extra)>budget:continue
   prior.update(extra);used+=len(extra)
 return spans,used

def support(spans,q,quote,books):
 text=books[q['source']]['document']['text'];start=0
 while True:
  at=text.find(quote,start)
  if at<0:return False
  if set(range(at,at+len(quote)))<=spans.get(q['source'],set()):return True
  start=at+1

def score(rows,questions,books):
 out=[]
 for q in questions:
  hits=trial.search(rows,q['query'],limit=len(rows)); top=hits[:3]
  spans,n=spans_for(top); budgeted,bn=spans_for(top,6000)
  def found(ss):return [support(ss,q,quote,books) for quote in q['required_quotes']]
  rank=next((i+1 for i,h in enumerate(hits) if support(spans_for([h])[0],q,q['relevant_quote'],books)),None)
  allchar=sum(len(e['quote']) for h in top for e in h['evidence'])
  overlap_pairs=sum(bool(spans_for([a])[0].get(a['source'],set()) & spans_for([b])[0].get(a['source'],set())) for i,a in enumerate(top) for b in top[i+1:] if a['source']==b['source'])
  out.append({'id':q['id'],'first_relevant_rank':rank,'support_at_3':found(spans),'support_within_6000_chars':found(budgeted),'unique_evidence_chars':n,'budgeted_evidence_chars':bn,'serialized_evidence_chars':allchar,'repeated_evidence_chars':allchar-n,'overlapping_hit_pairs':overlap_pairs,'indexed_hit_text_chars':sum(len(h['text']) for h in top),'hits':top,'full_ranking':[{'id':h['id'],'source':h['source'],'score':h['score']} for h in hits]})
 return {'relevant_support_at_3':sum(x['support_at_3'][0] for x in out),'complete_support_at_3':sum(all(x['support_at_3']) for x in out),'complete_support_within_6000_chars':sum(all(x['support_within_6000_chars']) for x in out),'mrr':sum(1/x['first_relevant_rank'] if x['first_relevant_rank'] else 0 for x in out)/len(out),'unique_evidence_chars':sum(x['unique_evidence_chars'] for x in out),'repeated_evidence_chars':sum(x['repeated_evidence_chars'] for x in out),'overlapping_hit_pairs':sum(x['overlapping_hit_pairs'] for x in out),'questions':out}

def execute():
 frozen=json.loads((ROOT/'freeze.json').read_text())
 for path,digest in frozen['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 books={p.stem:json.loads(p.read_text()) for p in sorted((ROOT/'inputs').glob('*.json'))}
 questions=json.loads((ROOT/'queries.json').read_text())
 rows={mode:rows_for(books,mode) for mode in MODES}
 # Counterfactual controls isolate source fallback and duplicated provider records.
 empty=copy.deepcopy(books)
 for b in empty.values():b['accepted']=[]
 duplicated=copy.deepcopy(books)
 for b in duplicated.values():
  dup=copy.deepcopy(b['accepted'][0]);dup['id']+=':duplicate-control';b['accepted'].append(dup)
 controls={'zero_statements':{},'duplicate_first_statement':{}}
 for m in MODES:
  er=rows_for(empty,m);dr=rows_for(duplicated,m)
  controls['zero_statements'][m]={'rows':len(er),'same_indexed_text_as_source':[(x['source'],x['id'],x['text']) for x in er]==[(x['source'],x['id'],x['text']) for x in rows['source']]}
  controls['duplicate_first_statement'][m]={'rows':len(dr),'same_indexed_text_as_original':[(x['source'],x['id'],x['text']) for x in dr]==[(x['source'],x['id'],x['text']) for x in rows[m]]}
 result={'provider_calls':0,'retrieval':'unchanged local BM25 diagnostic; lexical only','runtime_files':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [HARNESS,REPO/'packages/rulespec-extrapolator/src/rulespec_extrapolator/discovery.py',REPO/'packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py',Path(__file__)]},'rows':{m:len(rs) for m,rs in rows.items()},'index_characters':{m:sum(len(r['text']) for r in rs) for m,rs in rows.items()},'controls':controls,'arms':{m:score(rs,questions,books) for m,rs in rows.items()}}
 # Verify all stored evidence resolves exactly to the frozen source.
 for mode,rs in rows.items():
  for r in rs:
   for e in r['evidence']:assert books[r['source']]['document']['text'][e['start']:e['end']]==e['quote']
 return rows,result

if __name__=='__main__':
 rows,result=execute()
 if '--replay' in sys.argv:
  assert rows==json.loads((ROOT/'indexes.json').read_text())
  assert result==json.loads((ROOT/'results.json').read_text())
  with (ROOT/'replay.json').open('x') as f:json.dump({'provider_calls':0,'status':'exact indexes, ranking, support and control results reproduced'},f,indent=2)
  print('Replay matched')
 else:
  for name,value in [('indexes.json',rows),('results.json',result)]:
   with (ROOT/name).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2)
  print(json.dumps({m:{k:v for k,v in a.items() if k!='questions'} for m,a in result['arms'].items()},indent=2))
