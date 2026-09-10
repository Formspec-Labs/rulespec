from experiment import *

def prompt(data,arm):
    if arm=='B':return actor_prompt(data,arm)
    return actor_prompt(data,arm).replace('Return the shortest exact quotation identifying the actor as actor_quote.','Return an exact quotation identifying the actor as actor_quote. Use exact contiguous quotations. Use longer distinctive quotes when short words repeat.')

def freeze():
    pairs=[dict(case=c,arm=a) for c in ['alcohol','roles'] for a in ['A','B']];random.Random(20260920).shuffle(pairs)
    e._save(ROOT/'followup-design.json',dict(cells=[dict(id=f'followup-{i}',**v) for i,v in enumerate(pairs)],inputs={str(p.relative_to(ROOT)):e._digest(p.read_bytes()) for p in [ROOT/'FOLLOWUP-PLAN.md',Path(__file__),ROOT/'experiment.py',ROOT/'inputs/alcohol.json',ROOT/'inputs/roles.json']},runtime={n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()},max_calls=4,model=e.DEFAULT_MODEL))

def run_followup(replay=False):
    design=e._load(ROOT/'followup-design.json')
    assert e._load(ROOT/'completion.json')['calls']==8
    for n,d in design['inputs'].items():assert e._digest((ROOT/n).read_bytes())==d
    assert design['runtime']=={n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}
    key='' if replay else e._credential(ENV)
    for cell in design['cells']:
        path=ROOT/'cells'/cell['id'];data=e._load(ROOT/'inputs'/f"{cell['case']}.json");view={k:data[k] for k in ['catalog','claims']};arm=cell['arm'];text=prompt(view,arm)
        if replay:
            attempt=e._load(path/'actor/attempt-0000.json');request=e._load(path/'actor'/attempt['request_file']);assert request['contents']==text and request['config']['response_json_schema']==actor_schema(arm)
            payload,errs=a._read_response(path/'actor',attempt)
        else:
            print('Call',cell,flush=True);payload,errs,_=r._call(path/'actor',text,actor_schema(arm),e.DEFAULT_MODEL,key,None)
        result=actor_result(data,payload,errs,arm)
        if replay:assert result==e._load(path/'result.json')
        else:e._save(path/'result.json',result)
    e._save(ROOT/('followup-replay.json' if replay else 'followup-completion.json'),{'calls':0 if replay else 4,'status':'decoding matched' if replay else 'captured'})

if __name__=='__main__':{'freeze':freeze,'run':run_followup,'replay':lambda:run_followup(True)}[sys.argv[1]]()
