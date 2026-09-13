"""Two isolated prompt diagnostics using existing captures, schemas and decoding."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch

from rulespec_extrapolator import audit as a, extraction as e, refinement as r

HERE = Path(__file__).resolve().parent
FRESH = HERE.parent / '2026-09-13-fresh-complete-reading'
OLD = HERE.parent / '2026-09-13-complete-reading-check'
spec = importlib.util.spec_from_file_location('shared_check', OLD / 'run.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
OPTIONAL = '''\nEmpty optional action/object fields are valid when the default statement already
expresses that meaning. Filling them alone is not a needed correction; judge such
an edit unsupported. Continue to support source-backed corrections to incorrect
populated components and missing qualification links, even when the default
statement is unchanged.
'''
NEGATIVE = ('A full quotation or another record retaining a condition does not incorporate it\n'
            'into this statement.')
POSITIVE = ('Assess completeness in the selected statement\'s fields.summary: include every\n'
            'supplied condition that governs that statement, including those recorded in\n'
            'quotations or other records.')
DEPENDENCIES = set()


def read(path):
    DEPENDENCIES.add(path)
    return e._load(path)


def save(name, value):
    path = HERE / name
    assert not path.exists(), name
    path.parent.mkdir(parents=True, exist_ok=True)
    e._save(path, value)


def existing(root, source, arm):
    key = read(root / 'arm-key.json')
    cell, = [c for c, v in key.items() if v.get('source', v.get('group')) == source
             and v['arm'] == arm and v['repeat'] == 0]
    data = read(root / f'inputs/{cell}.json')
    if 'document' not in data:
        data['document'] = read(root / 'books.json')[source]['document']
    return data


def prepare():
    assert prior.CHECK_TASK.count(NEGATIVE) == 1
    instructions = dict(M4a=dict(A=r.CHECK, B=r.CHECK + OPTIONAL),
                        M4b=dict(A=prior.CHECK_TASK,
                                 B=prior.CHECK_TASK.replace(NEGATIVE, POSITIVE)))
    save('instructions.json', instructions)
    groups, labels = {}, {}
    fresh_labels = read(FRESH / 'labels.json')
    old_labels = read(OLD / 'labels.json')
    for source in ('inspection', 'jury', 'compensatory', 'medical'):
        name = 'M4a/' + source
        groups[name] = existing(FRESH, source, 'A')
        labels[name] = {p['id']: fresh_labels[source + '/' + p['id']]
                        for p in groups[name]['candidates']}
    notice = existing(OLD, 'notice', 'A')
    saved = read(OLD / 'groups.json')['notice']
    # Deliberate mixed fixture: complete prose with the actual saved bad components.
    data = deepcopy(notice)
    target = saved[1]['proposal']['target']
    baseline = deepcopy(saved[1]['fields'])
    for field in ('action', 'action_quote', 'object', 'object_quote'):
        baseline[field] = saved[0]['fields'][field]
    data['packet']['claims'][target].update(baseline)
    data['packet']['claims'][target]['target_ids'] = ['C0000']
    correct = prior.item(target, deepcopy(saved[1]['fields']), qualifies=['C0000'])
    wrong = deepcopy(correct)
    wrong['fields'].update(actor='Commission', actor_quote='Commission')
    data['candidates'] = [correct, wrong]
    for i, p in enumerate(data['candidates']): p['id'] = f'P{i:04d}'
    groups['M4a/components'] = data
    labels['M4a/components'] = {
        'P0000': dict(expected='supported', category='component_fix', origin='constructed draft with saved component error'),
        'P0001': dict(expected='unsupported', category='wrong_meaning', origin='constructed actor error')}
    data = deepcopy(notice)
    values = prior.fields(data['packet']['claims'][target])
    values.update(relation='exception', applies_to=[data['packet']['claims']['C0000']['id']])
    correct = prior.item(target, values, qualifies=['C0000'])
    wrong = deepcopy(correct)
    wrong['proposal']['qualifies'] = ['C0002']
    wrong['fields']['applies_to'] = [data['packet']['claims']['C0002']['id']]
    data['candidates'] = [correct, wrong]
    for i, p in enumerate(data['candidates']): p['id'] = f'P{i:04d}'
    groups['M4a/links'] = data
    labels['M4a/links'] = {
        'P0000': dict(expected='supported', category='qualification_link', origin='constructed missing link'),
        'P0001': dict(expected='unsupported', category='wrong_meaning', origin='constructed wrong target')}
    for source in ('privacy', 'medical', 'notice', 'control'):
        name = 'M4b/' + source
        root = FRESH if source in ('privacy', 'medical') else OLD
        groups[name] = existing(root, source, 'B')
        labels[name] = {}
        for p in groups[name]['candidates']:
            label = deepcopy((fresh_labels if root == FRESH else old_labels)[source + '/' + p['id']])
            if root == OLD:
                label['category'] = ({'notice': ['wrong_meaning', 'complete_repair', 'wrong_meaning', 'incomplete_noop'],
                    'control': ['complete_repair', 'unnecessary_incomplete_edit', 'incomplete_noop', 'complete_noop',
                                'unnecessary_enrichment', 'wrong_meaning']}[source][int(p['id'][1:])])
            labels[name][p['id']] = label
    checks = []
    for name, data in groups.items():
        for p in data['candidates']:
            if p['proposal']['operation'] == 'no_change': continue
            raw = deepcopy(p['proposal'])
            raw['quote'] = p['fields']['quote']
            raw['fields'] = {k: v for k, v in p['fields'].items()
                             if k in r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']}
            decoded, issues = r._decode_proposals(dict(proposals=[raw], observations=[]), [],
                data['document'], data['window'], data['packet'], 'recovery')
            assert len(decoded) == 1 and not issues, (name, p['id'], issues)
            checks.append(dict(group=name, candidate=p['id'], source_and_schema_valid=True))
    save('candidate-checks.json', checks)
    save('labels.json', labels)
    # Both arms receive identical candidate order and data, including rationale.
    combos = [(name, arm, rep) for name in groups for arm in ('A', 'B') for rep in range(2)]
    random.Random(913142).shuffle(combos)
    cells, key = [], {}
    for i, (name, arm, rep) in enumerate(combos):
        data = deepcopy(groups[name])
        experiment, source = name.split('/')
        original = data.pop('prompt')
        prefix = r.CHECK if experiment == 'M4a' else prior.CHECK_TASK
        assert original.startswith(prefix)
        tail = original[original.index(prior.INDEPENDENT):]
        random.Random(913142 + 100 * list(groups).index(name) + rep).shuffle(data['candidates'])
        body = r._challenge_prompt(data['packet'], data['candidates'], data['document'])[len(r.CHECK):]
        data['prompt'] = instructions[experiment][arm] + body + tail
        cell = f'cell-{i+1:02d}'
        save(f'inputs/{cell}.json', data)
        cells.append(cell)
        key[cell] = dict(experiment=experiment, source=source, arm=arm, repeat=rep)
    save('cells.json', cells)
    save('arm-key.json', key)
    save('schema.json', r.CHECK_SCHEMA)
    save('runtime.json', e._runtime_versions())
    dependencies = DEPENDENCIES | {OLD / 'run.py', OLD / 'TASK.txt'} | set(e._runtime_sources().values())
    paths = dependencies | {p for p in HERE.rglob('*') if p.is_file()}
    save('pins.json', {str(p.resolve()): sha256(p.read_bytes()).hexdigest() for p in sorted(paths)})
    print('Frozen 40 calls, paired prompts, labels and source/runtime hashes; zero provider calls.')


def pins():
    for name, digest in e._load(HERE / 'pins.json').items():
        assert sha256(Path(name).read_bytes()).hexdigest() == digest, name


def capture():
    pins()
    key = e._credential(prior.ENV)
    for name in e._load(HERE / 'cells.json'):
        ledger = e._load(HERE / 'calls.json') if (HERE / 'calls.json').exists() else []
        if name in {c['name'] for c in ledger}: continue  # Failed starts remain failures, never retried.
        assert len(ledger) < 40 and sum(c['seconds'] for c in ledger) < 1200
        assert e.recorded_usage(HERE)['tokens'].get('total_token_count', 0) < 450000
        ledger.append(dict(name=name, status='started', seconds=0))
        e._save(HERE / 'calls.json', ledger)
        data = e._load(HERE / f'inputs/{name}.json')
        directory = HERE / 'captures' / name
        start = time.monotonic()
        try:
            attempt, = a._capture(directory, data['document'], [data['window']], [data['prompt']],
                r.CHECK_SCHEMA, e.DEFAULT_MODEL, key, None, max_output_tokens=32768, thinking_level='medium')
            save(f'captures/{name}/attempt.json', attempt)
            ledger[-1]['status'] = attempt['status']
        finally:
            ledger[-1]['seconds'] = time.monotonic() - start
            e._save(HERE / 'calls.json', ledger)
        payload, errors = a._read_response(directory, attempt)
        judgments, issues = r._decode_checks(payload, errors, data['candidates'], data['document'], data['packet'])
        save(f'decoded/{name}.json', dict(payload=payload, errors=errors, judgments=judgments, issues=issues))
        print(name, len(judgments), 'judgments;', len(issues), 'issues', flush=True)
    e._save(HERE / 'usage.json', e.recorded_usage(HERE))


def verify():
    pins()
    with patch.object(e, '_create_model', side_effect=AssertionError('Provider forbidden')):
        for name in e._load(HERE / 'cells.json'):
            data = e._load(HERE / f'inputs/{name}.json')
            directory = HERE / 'captures' / name
            attempt = e._load(directory / 'attempt.json')
            expected = dict(model=e.DEFAULT_MODEL, contents=data['prompt'], config=dict(
                max_output_tokens=32768, response_mime_type='application/json',
                response_json_schema=r.CHECK_SCHEMA, thinking_config=dict(thinking_level='medium')))
            assert e._load(directory / attempt['request_file']) == expected
            payload, errors = a._read_response(directory, attempt)
            judgments, issues = r._decode_checks(payload, errors, data['candidates'], data['document'], data['packet'])
            assert dict(payload=payload, errors=errors, judgments=judgments, issues=issues) == e._load(HERE / f'decoded/{name}.json')
    save('verification.json', dict(calls=40, exact_request_shape=True, saved_responses_redecoded_identically=True,
                                  provider_blocked=True, all_pins_match=True))
    print('All 40 exact requests and provider-blocked saved response decodes verified.')


if __name__ == '__main__':
    {'prepare': prepare, 'capture': capture, 'verify': verify}[sys.argv[1]]()
