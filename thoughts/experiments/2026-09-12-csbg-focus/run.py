"""Five bounded captures through existing extraction helpers; no new pipeline."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch

from rulespec_extrapolator import audit, core, documents, extraction as e

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-09-12-csbg'


def save(name, value):
    p = HERE / name
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def prepare():
    doc = e._load(BASE / 'sources/document.json')
    original = e._load(BASE / 'extract/run.json')
    cells = []
    for index in (1, 2):
        w = {k:v for k,v in original['windows'][index].items() if k in e.plan_windows(doc)[index]}
        cells.append(dict(id=f'broad-{index}', arm='A', window=w, historical=f'attempt-{index:04d}.request.json'))
    for name, number in (('plan',9908), ('boards',9910), ('correction',9915)):
        section = next(s for s in doc['sections'] if s['label'] == f'/us/usc/t42/s{number}')
        lo, hi = section['start'], section['end']
        window = dict(id='window-'+e._digest([doc['sha256'],lo,hi])[:20], index=0, start=lo,end=hi,
            text_sha256=e._digest(doc['text'][lo:hi]),
            section_ids=[s['id'] for s in doc['sections'] if s['start']<hi and s['end']>lo])
        cells.append(dict(id=name, arm='B', window=documents.with_context(doc,window)))
    schema = e.provider_schema().schema_dict
    examples = e.invented_examples()
    generator = e._prompt_generator(examples)
    for c in cells:
        c['prompt'] = e._window_prompt(generator,doc,c['window'])
        if c['arm']=='A':
            historical=e._load(BASE/'extract'/c['historical'])
            assert c['prompt']==historical['contents']
            assert schema==historical['config']['response_json_schema']
    random.SystemRandom().shuffle(cells)
    save('cells.json',cells)
    save('schema.json',schema)
    save('runtime.json',e._freeze(HERE,examples,schema))
    pins={name:sha256((HERE/name).read_bytes()).hexdigest() for name in ('PLAN.md','run.py','cells.json','schema.json','runtime.json')}
    for path in sorted((HERE/'frozen').rglob('*')):
        if path.is_file():pins[str(path.relative_to(HERE))]=sha256(path.read_bytes()).hexdigest()
    for name in ('sources/document.json','extract/run.json','state-plan-content-review.json'):
        pins['../2026-09-12-csbg/'+name]=sha256((BASE/name).read_bytes()).hexdigest()
    save('precall-pins.json',pins)
    print('Prepared five cells; exact historical baseline prompts and schema verified')


def verify_pins():
    for name,h in e._load(HERE/'precall-pins.json').items():
        assert sha256((HERE/name).read_bytes()).hexdigest()==h,name


def decode(cell):
    doc=e._load(BASE/'sources/document.json')
    directory=HERE/'captures'/cell['id']
    attempt=e._load(directory/'attempts.json')[0]
    parsed=e._attempt_result(attempt,directory,doc,cell['window'])
    run=dict(id=core.NS+'run:'+e._digest([HERE.name,cell['id']]),model=e.DEFAULT_MODEL,
        status=parsed['status'],scope='Experimental selected window only; not whole-document completeness',
        windows=[{**cell['window'],'status':parsed['status']}])
    book=core.compile_candidates(doc,parsed['candidates'],run)
    return {'parsed':parsed,'book':book,'validation':e._check_graph(book['graph'])}


def capture():
    verify_pins()
    assert not (HERE/'captures').exists()
    key=e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    doc=e._load(BASE/'sources/document.json')
    schema=e._load(HERE/'schema.json')
    cells=e._load(HERE/'cells.json')
    assert len(cells)==5
    started=time.monotonic()
    for cell in cells:
        if time.monotonic()-started>=1200:
            save('stopped.json',{'reason':'capture_time_bound'});break
        directory=HERE/'captures'/cell['id']
        start=time.monotonic()
        attempts=audit._capture(directory,doc,[cell['window']],[cell['prompt']],schema,
            e.DEFAULT_MODEL,key,None,max_output_tokens=16384,thinking_level='low')
        save(f"captures/{cell['id']}/attempts.json",attempts)
        save(f"captures/{cell['id']}/timing.json",{'seconds':time.monotonic()-start})
        save(f"decoded/{cell['id']}.json",decode(cell))
        print('Captured cell',len(list((HERE/'decoded').glob('*.json'))),flush=True)
    save('usage.json',e.recorded_usage(HERE/'captures'))
    save('capture-time.json',{'seconds':time.monotonic()-started})
    make_review()


def make_review():
    doc=e._load(BASE/'sources/document.json')
    pairs={}
    for name,number,baseline in (('plan',9908,'broad-1'),('boards',9910,'broad-2'),('correction',9915,'broad-2')):
        section=next(s for s in doc['sections'] if s['label']==f'/us/usc/t42/s{number}')
        # Compare only 9908(b) for the primary thirteen-content question.
        lo,hi=(37820,46469) if name=='plan' else (section['start'],section['end'])
        arms=[baseline,name];random.SystemRandom().shuffle(arms)
        pairs[name]={}
        for i,identity in enumerate(arms,1):
            decoded=e._load(HERE/f'decoded/{identity}.json')
            filename=f'{name}-{i}'
            rows=[]
            for index,c in enumerate(decoded['book']['accepted']):
                if c['start']>=hi or c['end']<=lo:continue
                rows.append(dict(index=index,start=c['start'],end=c['end'],
                    **{k:c[k] for k in ('summary','actor','modality','kind','scope_text','choice_text','logic_text','references','issues')},
                    source_evidence=[dict(field=x['field'],start=x['start'],end=x['end'],quote=x['quote']) for x in c['evidence']]))
            save('review/'+filename+'.json',{'records':rows,'rejected':decoded['book']['rejected'],
                'capture_refusals':decoded['parsed']['refusals']})
            pairs[name][filename]=identity
    save('review-key.json',pairs)


def verify():
    verify_pins()
    checks=[]
    with patch.object(e,'_create_model',side_effect=AssertionError('Unexpected provider setup')):
        for c in e._load(HERE/'cells.json'):
            directory=HERE/'captures'/c['id']
            actual=e._load(directory/e._load(directory/'attempts.json')[0]['request_file'])
            assert actual['contents']==c['prompt']
            assert actual['config']==dict(e._load(BASE/'extract/attempt-0001.request.json')['config'])
            if c['arm']=='A':assert actual==e._load(BASE/'extract'/c['historical'])
            assert decode(c)==e._load(HERE/f"decoded/{c['id']}.json")
            checks.append(dict(cell=c['id'],replay_equal=True,request_verified=True))
    save('verification.json',{'checks':checks,'provider_calls':0,'runtime_file':e.__file__})
    print('All five saved captures parse and compile identically; requests verified')


if __name__=='__main__':
    {'prepare':prepare,'capture':capture,'verify':verify}[sys.argv[1]]()
