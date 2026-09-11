from pathlib import Path
import sys,time
from rulespec_extrapolator import extraction as e, refinement as r, audit as a
from rulespec_extrapolator.documents import with_context,prepare_document
from rulespec_extrapolator.discovery import verified
ROOT=Path(__file__).resolve().parent
SCHEMA=a._object({'answers':a._list(a._object({'question_id':a.TEXT,'conclusion':{'type':'string','enum':['yes','no','unknown','ambiguous']},'answer':a.TEXT,'support_refs':a.STRINGS,'remaining_uncertainty':a.STRINGS}))})
INSTRUCTION='Answer each fixed comprehension question using ONLY the supplied material. The extracted statement may omit qualifications. Do not fill gaps with remembered law or external facts. A source passage selected for proximity, structure or evidence is context, not proof its condition governs this statement. If the supplied material does not settle a question, say unknown; if it supports conflicting readings, say ambiguous and preserve them. Briefly state the actor/action/conditions relevant to the question. Cite supplied source IDs or statement. Do not invent absent requirements. Return the requested JSON.'
def setup():
 assert not (ROOT/'design.json').exists()
 cases=[]
 defs=[('refrigerants',0,'venting',[
 ('q1','Does the supplied material establish that every knowing release during maintenance violates this venting prohibition, including a de-minimis release during good-faith recovery that satisfies the applicable compliance route?','no','Full source a2 expressly exempts the compliant good-faith release. Unknown is faithful abstention when selected material lacks a2; categorical yes is an overbroad default.'),
 ('q2','Is good faith alone sufficient to establish that a non-exempt refrigerant release qualifies for the de-minimis exemption?','no','Full source requires goodfaith plus one complete compliance route; unknown if absent.'),
 ('q3','Does the de-minimis venting exemption itself waive the independent servicing practices and certified-equipment duties?','no','No waiver of b by a2; unknown if relevant source absent.'),
 ('q4','Who does the default venting prohibition regulate, and what conduct does it prohibit?','yes','Any person maintaining/servicing/repairing/disposing; knowingly vent/release. Preserve specific-substitute qualification.')]),
 ('seatbelts',7,'label-scope',[
 ('q1','Does this material establish a general manufacturing requirement for every U.S.-standard seat made in the stated date range, regardless of aircraft use?','no','Child-restraint aircraft-use condition scopes this provision; do not turn it into universal manufacturing law. Unknown in A accepted abstention.'),
 ('q2','In the supplied provision, is the dated label requirement part of conditions for occupying an approved child restraint system in an aircraft?','yes','Existing scope evidence supplies aircraft-use parent.'),
 ('q3','Does this material identify the manufacturer as the person legally required to perform the labeling action?','unknown','Do not infer a named manufacturer actor from manufactured-to-standards.'),
 ('q4','Does this material establish that a child restraint meeting this dated label rule can be used without any other conditions?','no','Other conditions in parent and exception; isolated statement cannot establish sufficiency.')]),
 ('seatbelts',12,'child-ambiguity',[
 ('q1','Who is responsible for securing the child restraint, and to what must it be secured?','yes','Operator; approved forward-facing seat or berth.'),
 ('q2','Does this securing requirement apply whenever any child restraint exists anywhere, including use outside aircraft?','no','Express child-use under a3iii; preserve aircraft context.'),
 ('q3','For an operation under part135, does the supplied material conclusively settle whether this child-restraint securing requirement applies?','ambiguous','Full source has notwithstanding any other requirement of chapter vs b unlessotherwise stated exclusion; accept unknown if remote exclusion unavailable. Do not force applies or excluded.'),
 ('q4','Does the phrase notwithstanding any other requirement automatically authorize ignoring every condition of the child-restraint permission?','no','Permission itself is conditional; notwithstanding is not unconditional erasure. Unknown if phrase absent acceptable.')])]
 for source,index,name,qs in defs:
  book=e._load(ROOT.parent/'2026-09-10-parallel-targets/inputs'/source/'book.json');claim=book['accepted'][index];doc=book['document']
  cases.append(make(name,doc,claim,qs,{'kind':'saved-provider-extraction','book_path':str(ROOT.parent/'2026-09-10-parallel-targets/inputs'/source/'book.json'),'claim_index':index}))
 text='(a) Staff entering the laboratory must hold a laboratory permit. The permit condition applies only to staff laboratory entry.\n\n(1) Staff must sign the laboratory entry log.\n\n(2) Visitors may use the public waiting room whether or not they have a laboratory permit. This permission is independent of the staff entry conditions.\n\n(b) The waiting room closes at 18:00.'
 doc=prepare_document(text,title='Constructed structural-parent counterexample');quote='(2) Visitors may use the public waiting room whether or not they have a laboratory permit. This permission is independent of the staff entry conditions.';start=text.index(quote)
 claim={'summary':'Visitors may use the public waiting room whether or not they have a laboratory permit.','start':start,'end':start+len(quote),'evidence':[{'field':'summary','start':start,'end':start+len(quote),'quote':quote}]}
 qs=[('q1','Must a visitor obtain a laboratory permit before using the public waiting room?','no','Explicit independent permission defeats structural parent inheritance.'),('q2','Must a visitor sign the laboratory entry log solely to use the public waiting room?','no','Staff entry log addresses staff; no visitor requirement.'),('q3','Does the visitor waiting-room permission authorize entry into the laboratory without a permit?','unknown','Different action/location; permission does not establish laboratory entry.'),('q4','Does the supplied material establish that the waiting room closes at18:00?','yes','B adjacent b provides time; A should abstain.')]
 cases.append(make('constructed-parent',doc,claim,qs,{'kind':'constructed','not_provider_output':True}))
 e._save(ROOT/'cases.json',cases);e._save(ROOT/'schema.json',SCHEMA)
 order=[(0,'B'),(0,'A'),(1,'A'),(1,'B'),(2,'B'),(2,'A'),(3,'A'),(3,'B')]
 cells=[]
 for i,(idx,arm) in enumerate(order):
  c=cases[idx];material={'statement':c['statement'],'source_context':c['context'] if arm=='B' else []}
  p=INSTRUCTION+'\nMaterial: '+e._canonical(material)+'\nQuestions: '+e._canonical([{'id':q[0],'question':q[1]} for q in c['questions']])
  path=ROOT/'prompts'/f'cell-{i:02d}.json';e._save(path,{'text':p});cells.append({'id':f'cell-{i:02d}','case':c['id'],'arm':arm})
 paths=[ROOT/'PLAN.md',Path(__file__),ROOT/'cases.json',ROOT/'schema.json',*sorted((ROOT/'prompts').glob('*.json'))]
 e._save(ROOT/'design.json',{'cells':cells,'model':e.DEFAULT_MODEL,'max_calls':8,'runtime':e._runtime_versions(),'fingerprints':e._freeze(ROOT,[],SCHEMA),'hashes':{str(p.relative_to(ROOT)):e._digest(p.read_bytes()) for p in paths}})
 print([(c['id'],len(c['statement']),sum(len(x['text']) for x in c['context'])) for c in cases])
def make(name,doc,claim,qs,origin):
 w=with_context(doc,{'start':claim['start'],'end':claim['end']});cat=e.passage_catalog(doc,w)
 spans={ (x['start'],x['end']):dict(x,reason='focus-or-structural-adjacent') for x in cat.values() }
 for x in verified({'document':doc},claim['evidence']):
  key=(x['start'],x['end']);spans.setdefault(key,{'start':x['start'],'end':x['end'],'text':x['quote'],'reason':'existing-evidence'}).setdefault('roles',[]).append(x['field'])
 context=[dict(x,id=f'S{i:03d}') for i,x in enumerate(sorted(spans.values(),key=lambda x:(x['start'],x['end'])))]
 assert all(doc['text'][x['start']:x['end']]==x['text'] for x in context)
 return {'id':name,'origin':origin,'document':doc,'claim':claim,'statement':claim['summary'],'window':w,'context':context,'questions':qs}
def run(replay=False):
 d=e._load(ROOT/'design.json')
 for name,digest in d['hashes'].items():assert e._digest((ROOT/name).read_bytes())==digest,name
 assert d['runtime']==e._runtime_versions()
 assert d['fingerprints']['sources_sha256']=={n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}
 key='' if replay else e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'));start=time.monotonic()
 for cell in d['cells']:
  path=ROOT/'cells'/cell['id'];prompt=e._load(ROOT/'prompts'/f"{cell['id']}.json")['text']
  if replay:
   attempt=e._load(path/'attempt-0000.json');payload,errors=a._read_response(path,attempt);assert {'payload':payload,'errors':errors}==e._load(path/'decoded.json')
  else:
   assert time.monotonic()-start<1800 and not path.exists()
   print('Calling',cell,flush=True);payload,errors,attempt=r._call(path,prompt,SCHEMA,d['model'],key,None);e._save(path/'decoded.json',{'payload':payload,'errors':errors})
  request=e._load(path/attempt['request_file']);assert request['contents']==prompt and request['model']==d['model'];assert request['config']=={'temperature':0,'max_output_tokens':32768,'candidate_count':1,'response_mime_type':'application/json','response_json_schema':SCHEMA}
 e._save(ROOT/('replay.json' if replay else 'completion.json'),{'calls':0 if replay else len(d['cells']),'status':'matched' if replay else 'captured','usage':e.recorded_usage(ROOT/'cells')})
if __name__=='__main__': {'prepare':setup,'run':run,'replay':lambda:run(True)}[sys.argv[1]]()
