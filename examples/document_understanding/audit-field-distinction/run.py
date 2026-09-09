"""Controlled draft variants through the existing audit comparison functions."""
import argparse
from copy import deepcopy
from pathlib import Path
import random
import shutil

from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent


def prepare():
    assert not (ROOT / 'design.json').exists()
    original = e._load(ROOT.parent / 'comparison-passage-ids/fixture.json')
    e._save(ROOT / 'original-fixture.json', original)
    document, window = original['book']['document'], original['window']
    span = e.resolve_passage('F003:F004', e.passage_catalog(document, window), document)
    views = {'A': {'document': document, 'accepted': deepcopy(original['book']['accepted'])}}
    views['B'] = deepcopy(views['A'])
    target = views['B']['accepted'][14]
    target.update(quote=span['quote'], start=span['start'], end=span['end'], logic_text=span['quote'])
    for evidence in target['evidence']:
        if evidence['field'] in ('summary', 'logic_text'):
            evidence.update(span)
            evidence.pop('fragment_id', None)
    views['C'] = deepcopy(views['B'])
    views['C']['accepted'][14]['summary'] = (
        "For unforeseeable leave, an employer may require employees to call a designated number or a specific individual "
        "as part of its usual and customary notice and procedural requirements. Compliance is required absent unusual "
        "circumstances; an employee requiring emergency medical treatment is not required to follow the call-in "
        "procedure until the employee's condition is stabilized and the employee has access to, and is able to use, a phone.")
    for arm, view in views.items():
        view['accepted'][14]['id'] = 'urn:rulespec:experiment:audit-field-distinction:' + arm
        e._save(ROOT / 'views' / (arm + '.json'), view)
    payloads = {arm:a._model_input(a._comparison_input(view, original['labels'], window)[0])
                for arm,view in views.items()}
    for arm,payload in payloads.items():
        unchanged = deepcopy(payload); unchanged['claims'].pop('C0014')
        baseline = deepcopy(payloads['A']); baseline['claims'].pop('C0014')
        assert unchanged == baseline
    b, c = deepcopy(payloads['B']), deepcopy(payloads['C'])
    c['claims']['C0014']['summary'] = b['claims']['C0014']['summary']
    assert b == c
    prefix = e._window_prompt(e._prompt_generator([], a.comparison_prompt()), document, window)
    prompts = {arm:prefix + '\nDraft and inventory: ' + e._canonical(payload)
               for arm,payload in payloads.items()}
    cells = [arm + str(i) for i in (1,2) for arm in ('A','B','C')]
    random.SystemRandom().shuffle(cells)
    files = ['PLAN.md','run.py','original-fixture.json'] + ['views/' + arm + '.json' for arm in views]
    runtime = e._runtime_sources()
    for name,path in runtime.items():
        target = ROOT / 'frozen' / name; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,target)
    e._save(ROOT / 'design.json', {'cells':cells,'max_provider_calls':6,
        'model':e.DEFAULT_MODEL,'temperature':0,'thinking_level':'medium','max_output_tokens':None,
        'prompts':prompts,'payloads':payloads,'schema':a.COMPARISON_SCHEMA,'prompt':a.comparison_prompt(),
        'provenance':'A is a comparison view of the original draft; B/C are constructed diagnostic variants. No Core graph or provider extraction was rewritten.',
        'inputs_sha256':{name:e._digest((ROOT/name).read_bytes()) for name in files},
        'runtime_sources_sha256':{name:e._digest(path.read_bytes()) for name,path in runtime.items()}})
    print('Frozen six-call comparison:', ', '.join(cells))


def execute(mode, env_file):
    design = e._load(ROOT / 'design.json')
    for name,digest in design['inputs_sha256'].items():
        assert e._digest((ROOT/name).read_bytes()) == digest,name
    assert {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    assert a.COMPARISON_SCHEMA == design['schema'] and a.comparison_prompt() == design['prompt']
    original = e._load(ROOT / 'original-fixture.json')
    document, window, labels = original['book']['document'], original['window'], original['labels']
    key = e._credential(env_file) if mode == 'run' else None
    results = {}
    for cell in design['cells']:
        arm, directory = cell[0], ROOT / 'runs' / cell
        view = e._load(ROOT / 'views' / (arm + '.json'))
        payload = a._model_input(a._comparison_input(view,labels,window)[0])
        assert payload == design['payloads'][arm]
        prompt = e._window_prompt(e._prompt_generator([],a.comparison_prompt()),document,window)
        prompt += '\nDraft and inventory: ' + e._canonical(payload)
        assert prompt == design['prompts'][arm]
        if mode == 'run':
            attempts = a._capture(directory,document,[window],[prompt],a.COMPARISON_SCHEMA,
                design['model'],key,None,max_output_tokens=None,thinking_level='medium')
            e._save(directory/'attempts.json',attempts)
        else:
            e._verify_manifest(directory)
            attempts = e._load(directory/'attempts.json')
        assert len(attempts) == 1
        attempt = attempts[0]
        if attempt.get('request_file'):
            assert e._load(directory/attempt['request_file']) == {'model':design['model'],'contents':prompt,
                'config':{'temperature':0,'candidate_count':1,'thinking_config':{'thinking_level':'medium'},
                    **GeminiSchema(a.COMPARISON_SCHEMA,_use_json_schema=True).to_provider_config()}}
        judgments, issues = a._judgments(directory,view,labels,[window],attempts,design['model'])
        report = a._assessment(view,labels,judgments,issues)
        response = e._load(directory/attempt['response_file']) if attempt.get('response_file') else {}
        result = {'judgments':judgments,'issues':issues,'report':report,'usage':response.get('usage_metadata')}
        if mode == 'run':
            e._save(directory/'result.json',result); e._write_manifest(directory)
        else:
            assert result == e._load(directory/'result.json')
        results[cell] = result
        print(cell,len(judgments['claim_judgments']),'claims',len(judgments['unit_judgments']),
            'units',len(issues),'issues',flush=True)
    if mode == 'replay':
        assert results == e._load(ROOT/'results.json')
        print('Six comparisons replay identically; zero provider calls.')
        return
    e._save(ROOT/'results.json',results)
    cells = list(results);random.SystemRandom().shuffle(cells)
    mapping = {'R'+str(i):cell for i,cell in enumerate(cells,1)}
    packet = {}
    for masked,cell in mapping.items():
        payload,_ = a._read_response(ROOT/'runs'/cell,e._load(ROOT/'runs'/cell/'attempts.json')[0])
        packet[masked] = {field:[{k:v for k,v in row.items() if k != 'source_refs'} for row in rows]
                          for field,rows in payload.items()}
    e._save(ROOT/'blind-review.json',packet);e._save(ROOT/'review-key.json',mapping)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=['prepare','run','replay'])
    parser.add_argument('--env-file',type=Path)
    args=parser.parse_args()
    prepare() if args.mode == 'prepare' else execute(args.mode,args.env_file)
