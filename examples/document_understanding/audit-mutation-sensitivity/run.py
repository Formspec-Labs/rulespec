"""Measure planted semantic errors through the current audit comparison."""
import argparse
from copy import deepcopy
from pathlib import Path
import random
import shutil

from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent


def prepare():
    assert not (ROOT/'design.json').exists()
    config, mutations = {}, {}
    for case in ('passport','waste'):
        source = ROOT.parent/'passage-id-transfer'/case/'audit'
        book,labels = e._load(source/'rulebook.json'),e._load(source/'labels.json')
        window, = e._load(source/'audit.json')['windows']
        assert window['start']==0 and window['end']==len(book['document']['text'])
        e._save(ROOT/'fixtures'/(case+'.json'),{'book':book,'labels':labels,'window':window})
        views = {'A':{'document':book['document'],'accepted':deepcopy(book['accepted'])}}
        views['B'] = deepcopy(views['A'])
        rows = views['B']['accepted']
        if case == 'passport':
            rows[4]['summary'] = rows[4]['summary'].replace('Passport agencies/centers must not','Posts must not')
            rows[4]['scope_text'] = rows[4]['scope_text'].replace('At passport agencies/centers,','At posts,')
            rows[13].update(summary='INs require a response from the applicant.',kind='requirement',modality='must')
            targets = {4:'actor',13:'negation'}
        else:
            rows[8]['summary'] = rows[8]['summary'].replace('both the words "Hazardous Waste" and an indication',
                'either the words "Hazardous Waste" or an indication')
            rows[8]['choice_text'] = rows[8]['choice_text'].replace('both (a)','either (a)').replace(' and (b)',' or (b)')
            for field in ('summary','choice_text'):
                assert rows[9][field].count('three consecutive calendar days')==2
                rows[9][field] = rows[9][field].replace('three consecutive calendar days','thirty consecutive calendar days')
            targets = {8:'alternatives',9:'deadline'}
        mutations[case] = {str(i):{'type':kind,'changes':{field:{'original':views['A']['accepted'][i][field],'mutated':value}
            for field,value in rows[i].items() if value!=views['A']['accepted'][i][field]}} for i,kind in targets.items()}
        for i in targets:
            assert mutations[case][str(i)]['changes']
        payloads = {}
        for arm,view in views.items():
            for i in targets:view['accepted'][i]['id']='urn:rulespec:experiment:audit-sensitivity:'+case+':'+arm+':'+str(i)
            e._save(ROOT/'views'/(case+'-'+arm+'.json'),view)
            payloads[arm]=a._model_input(a._comparison_input(view,labels,window)[0])
        for i in range(len(rows)):
            alias=f'C{i:04d}'
            if i not in targets:assert payloads['A']['claims'][alias]==payloads['B']['claims'][alias]
        assert payloads['A']['units']==payloads['B']['units']
        prefix=e._window_prompt(e._prompt_generator([],a.comparison_prompt()),book['document'],window)
        config[case]={arm:{'payload':payload,'prompt':prefix+'\nDraft and inventory: '+e._canonical(payload)}
                      for arm,payload in payloads.items()}
    e._save(ROOT/'mutations.json',mutations)
    runtime=e._runtime_sources()
    for name,path in runtime.items():
        target=ROOT/'frozen'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
    inputs=['PLAN.md','run.py','mutations.json']+[str(p.relative_to(ROOT)) for folder in ('fixtures','views') for p in (ROOT/folder).glob('*.json')]
    cells=[case+'/'+arm for case in config for arm in ('A','B')];random.SystemRandom().shuffle(cells)
    e._save(ROOT/'design.json',{'cells':cells,'max_provider_calls':4,'config':config,'model':e.DEFAULT_MODEL,
        'schema':a.COMPARISON_SCHEMA,'prompt':a.comparison_prompt(),'thinking_level':'medium','temperature':0,
        'inputs_sha256':{name:e._digest((ROOT/name).read_bytes()) for name in inputs},
        'runtime_sources_sha256':{name:e._digest(path.read_bytes()) for name,path in runtime.items()}})
    print('Frozen four-call diagnostic:',', '.join(cells))


def execute(mode,env_file):
    design=e._load(ROOT/'design.json')
    for name,digest in design['inputs_sha256'].items():assert e._digest((ROOT/name).read_bytes())==digest,name
    assert {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}==design['runtime_sources_sha256']
    assert a.COMPARISON_SCHEMA==design['schema'] and a.comparison_prompt()==design['prompt']
    key=e._credential(env_file) if mode=='run' else None
    results={}
    for cell in design['cells']:
        case,arm=cell.split('/');directory=ROOT/'runs'/case/arm
        fixture=e._load(ROOT/'fixtures'/(case+'.json'));view=e._load(ROOT/'views'/(case+'-'+arm+'.json'))
        doc,window,labels=view['document'],fixture['window'],fixture['labels']
        payload=a._model_input(a._comparison_input(view,labels,window)[0])
        assert payload==design['config'][case][arm]['payload']
        prompt=e._window_prompt(e._prompt_generator([],a.comparison_prompt()),doc,window)+'\nDraft and inventory: '+e._canonical(payload)
        assert prompt==design['config'][case][arm]['prompt']
        if mode=='run':
            attempts=a._capture(directory,doc,[window],[prompt],a.COMPARISON_SCHEMA,design['model'],key,None,
                max_output_tokens=None,thinking_level='medium');e._save(directory/'attempts.json',attempts)
        else:
            artifacts=e._load(directory/'manifest.json')['artifacts_sha256']
            assert set(artifacts)=={str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p!=directory/'manifest.json'}
            for name,digest in artifacts.items():assert e._digest((directory/name).read_bytes())==digest,name
            attempts=e._load(directory/'attempts.json')
        attempt,=attempts
        if attempt.get('request_file'):
            assert e._load(directory/attempt['request_file'])=={'model':design['model'],'contents':prompt,'config':{
                'temperature':0,'candidate_count':1,'thinking_config':{'thinking_level':'medium'},
                **GeminiSchema(a.COMPARISON_SCHEMA,_use_json_schema=True).to_provider_config()}}
        judgments,issues=a._judgments(directory,view,labels,[window],attempts,design['model'])
        report=a._assessment(view,labels,judgments,issues)
        response=e._load(directory/attempt['response_file']) if attempt.get('response_file') else {}
        result={'judgments':judgments,'issues':issues,'report':report,'usage':response.get('usage_metadata')}
        if mode=='run':e._save(directory/'result.json',result);e._write_manifest(directory)
        else:assert result==e._load(directory/'result.json')
        results[cell]=result
        print(cell,len(judgments['claim_judgments']),'claims',len(judgments['unit_judgments']),'units',len(issues),'issues',flush=True)
    if mode=='replay':
        assert results==e._load(ROOT/'results.json');print('All four comparisons replay identically; zero provider calls.');return
    e._save(ROOT/'results.json',results)
    cells=list(results);random.SystemRandom().shuffle(cells)
    key={'R'+str(i):cell for i,cell in enumerate(cells,1)};packet={}
    for masked,cell in key.items():
        raw,_=a._read_response(ROOT/'runs'/cell,e._load(ROOT/'runs'/cell/'attempts.json')[0])
        packet[masked]={field:[{k:v for k,v in row.items() if k!='source_refs'} for row in rows] for field,rows in raw.items()}
    e._save(ROOT/'blind-review.json',packet);e._save(ROOT/'review-key.json',key)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['prepare','run','replay'])
    parser.add_argument('--env-file',type=Path);args=parser.parse_args()
    prepare() if args.mode=='prepare' else execute(args.mode,args.env_file)
