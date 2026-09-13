"""Two input factors; reuse native checker formatting, decoding and captures."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import random
import sys
from rulespec_extrapolator import audit as a, extraction as e, refinement as r

HERE = Path(__file__).resolve().parent
BRIDGE = HERE.parent / '2026-09-13-focused-check-integration'
FRESH = HERE.parent / '2026-09-13-fresh-field-completeness'
spec = importlib.util.spec_from_file_location('capture_helpers', HERE.parent / '2026-09-13-fresh-complete-reading/run.py')
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
x.HERE = HERE
CASES = dict(leave='cell-07', hazard='cell-03')
FACTORS = dict(A=(True, False), B=(True, True), C=(False, False), D=(False, True))


def make_inputs():
    bridge_key = e._load(BRIDGE / 'arm-key.json')
    labels = e._load(FRESH / 'labels.json')
    policy = e._load(FRESH / 'instructions.json')['B']
    prepared, checks = {}, []
    for source, cell in CASES.items():
        original = e._load(BRIDGE / f'inputs/{cell}.json')
        info = bridge_key[cell]
        paired, = [c for c,v in bridge_key.items() if v['source']==source and v['repeat']==info['repeat'] and v['arm']=='A']
        rich = e._load(BRIDGE / f'inputs/{paired}.json')
        noop, = original['candidates']
        assert noop['id'] == 'N0000' and noop['proposal']['operation'] == 'no_change'
        suffix = original['prompt'][original['prompt'].index('\nEach candidate is an independent alternative'):]
        expected = {}
        alternatives = []
        for candidate in rich['candidates']:
            if candidate['proposal']['operation']=='no_change':
                assert candidate['fields']==noop['fields']
                alternatives.append(deepcopy(noop))
                expected['N0000'] = dict(expected='supported', category='complete_noop')
            else:
                alternatives.append(deepcopy(candidate))
                expected[candidate['id']] = labels[source + '/' + candidate['id']]
        for arm, (others, status) in FACTORS.items():
            data = deepcopy(original)
            data.pop('expected_request')
            data['candidates'] = deepcopy(alternatives if others else [noop])
            if not status:
                for alias, claim in data['packet']['claims'].items():
                    claim['link_issues'] = deepcopy(rich['packet']['claims'][alias]['link_issues'])
            data['prompt'] = policy + r._challenge_prompt(data['packet'], data['candidates'], data['document'])[len(r.CHECK):] + suffix
            data['expected_request'] = dict(model=e.DEFAULT_MODEL, contents=data['prompt'], config=dict(
                max_output_tokens=32768, response_mime_type='application/json', response_json_schema=r.CHECK_SCHEMA,
                thinking_config=dict(thinking_level='medium')))
            data['labels'] = {p['id']:expected[p['id']] for p in data['candidates']}
            prepared[source, arm] = data
        assert prepared[source, 'D']['expected_request'] == original['expected_request']
        for arm in ('A','B','C','D'):
            data = prepared[source, arm]
            restored = deepcopy(data['packet'])
            for alias,c in restored['claims'].items(): c['link_issues']=original['packet']['claims'][alias]['link_issues']
            assert restored==original['packet']
            assert data['document']==original['document']
        assert prepared[source,'A']['candidates']==prepared[source,'B']['candidates']
        assert prepared[source,'C']['candidates']==prepared[source,'D']['candidates']
        assert prepared[source,'A']['packet']==prepared[source,'C']['packet']
        assert prepared[source,'B']['packet']==prepared[source,'D']['packet']
        changed = [alias for alias,c in original['packet']['claims'].items()
            if c['link_issues'] != rich['packet']['claims'][alias]['link_issues']]
        checks.append(dict(source=source, original_cell=cell, exact_standalone_request=True,
            invariant_source_meaning_evidence_and_other_status=True, changed_link_status_aliases=changed))
    return prepared, checks


def prepare():
    prepared, checks = make_inputs()
    cells = [(s,arm,rep) for s in CASES for arm in FACTORS for rep in range(2)]
    random.Random(913614).shuffle(cells)
    keys={}
    for i, (source,arm,rep) in enumerate(cells,1):
        name=f'cell-{i:02d}'
        x.save(f'inputs/{name}.json',prepared[source,arm])
        keys[name]=dict(source=source,arm=arm,repeat=rep)
    x.save('arm-key.json',keys)
    x.save('cells.json',list(keys))
    x.save('input-checks.json',checks)
    x.save('schema.json',r.CHECK_SCHEMA)
    x.save('runtime.json',e._runtime_versions())
    paths=[p for p in HERE.rglob('*') if p.is_file()]
    paths += list(e._runtime_sources().values()) + [Path(x.__file__), x.OLD / 'run.py', FRESH / 'instructions.json', FRESH / 'labels.json', BRIDGE / 'arm-key.json']
    paths += list((BRIDGE / 'inputs').glob('*.json'))
    x.freeze('source-pins.json',paths)
    print('Frozen sixteen requests; both standalone/current-status inputs exactly match their saved requests.')


def check():
    key=e._credential(x.ENV)
    for name in e._load(HERE/'cells.json'):
        if (HERE/'decoded'/f'{name}.json').exists(): continue
        ledger=e._load(HERE/'calls.json') if (HERE/'calls.json').exists() else []
        assert len(ledger)<16 and sum(c['seconds'] for c in ledger)<1200
        assert x.usage()['tokens'].get('total_token_count',0)<250000
        data=e._load(HERE/f'inputs/{name}.json')
        directory=HERE/'captures'/name
        assert not directory.exists(), 'No retries'
        attempt, = x.call(name,lambda: a._capture(directory,data['document'],[data['window']],[data['prompt']],
            r.CHECK_SCHEMA,e.DEFAULT_MODEL,key,None,max_output_tokens=32768,thinking_level='medium'))
        x.save(f'captures/{name}/attempt.json',attempt)
        if attempt.get('request_file'): assert e._load(directory/attempt['request_file'])==data['expected_request']
        payload,errors=a._read_response(directory,attempt)
        judgments,issues=r._decode_checks(payload,errors,data['candidates'],data['document'],data['packet'])
        x.save(f'decoded/{name}.json',dict(payload=payload,errors=errors,judgments=judgments,issues=issues))
        print(name,len(judgments),'judgments;',len(issues),'decode issues',flush=True)
    e._save(HERE/'usage.json',x.usage())


if __name__=='__main__': {'prepare':prepare,'check':check}[sys.argv[1]]()
