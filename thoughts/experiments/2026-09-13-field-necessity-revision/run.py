"""Reuse the saved runner; vary only the field-necessity paragraph."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
from pathlib import Path
import random
import sys
from unittest.mock import patch

from rulespec_extrapolator import audit as a, extraction as e, refinement as r

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / '2026-09-13-checker-instruction-isolation'
spec = importlib.util.spec_from_file_location('isolation', OLD / 'run.py')
x = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x)
x.HERE = HERE
REVISED = '''\nJudge unnecessary field filling by the meaning it adds. An edit is unnecessary
when it only copies meaning already expressed by the selected fields.summary
into empty optional action/object fields, including when it also rephrases that
summary without changing its meaning. Source-faithful additions that explain a
governing condition, exception limit, alternative or timing requirement missing
from the selected summary supply needed meaning, even when a general label or a
separate record refers to it. Correcting an incorrect component or adding a
missing qualification link also supplies needed meaning. Apply the source-fidelity
checks to every change.
'''


def prepare():
    key = x.read(OLD / 'arm-key.json')
    old_labels = x.read(OLD / 'labels.json')
    instructions = dict(A=r.CHECK + x.OPTIONAL, B=r.CHECK + REVISED)
    x.save('instructions.json', instructions)
    groups, labels, checks = {}, {}, []
    sources = ['inspection', 'jury', 'compensatory', 'medical', 'components', 'links']
    for source in sources:
        cell, = [n for n, v in key.items() if v == dict(experiment='M4a', source=source, arm='B', repeat=0)]
        data = x.read(OLD / f'inputs/{cell}.json')
        labels[source] = deepcopy(old_labels['M4a/' + source])
        if source in sources[:3]:
            extra = deepcopy(next(p for p in data['candidates'] if p['id'] == 'P0002'))
            extra['id'] = 'P0003'
            before, after = {'inspection': ('may inspect or examine', 'is permitted to inspect or examine'),
                'jury': ('must deem', 'is required to deem'),
                'compensatory': ('An employer must permit', 'An employer is required to permit')}[source]
            assert extra['fields']['summary'].count(before) == 1
            extra['fields']['summary'] = extra['fields']['summary'].replace(before, after)
            data['candidates'].append(extra)
            labels[source]['P0003'] = dict(expected='unsupported', category='cosmetic_enrichment',
                origin='constructed synonymous modal rewording plus existing unnecessary action fill')
        for p in data['candidates']:
            raw = deepcopy(p['proposal'])
            raw['quote'] = p['fields']['quote']
            raw['fields'] = {k: v for k, v in p['fields'].items()
                if k in r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']}
            decoded, issues = r._decode_proposals(dict(proposals=[raw], observations=[]), [],
                data['document'], data['window'], data['packet'], 'recovery')
            assert len(decoded) == 1 and not issues, (source, p['id'], issues)
            checks.append(dict(source=source, candidate=p['id'], source_and_schema_valid=True))
        groups[source] = data
    x.save('labels.json', labels)
    x.save('candidate-checks.json', checks)
    combos = [(s, arm, rep) for s in sources for arm in ('A', 'B') for rep in range(2)]
    random.Random(913164).shuffle(combos)
    cells, key = [], {}
    for i, (source, arm, rep) in enumerate(combos):
        data = deepcopy(groups[source])
        original = data.pop('prompt')
        assert original.startswith(instructions['A'])
        random.Random(913164 + 100 * sources.index(source) + rep).shuffle(data['candidates'])
        body = r._challenge_prompt(data['packet'], data['candidates'], data['document'])[len(r.CHECK):]
        data['prompt'] = instructions[arm] + body + original[original.index(x.prior.INDEPENDENT):]
        cell = f'cell-{i+1:02d}'
        cells.append(cell)
        key[cell] = dict(source=source, arm=arm, repeat=rep)
        x.save(f'inputs/{cell}.json', data)
    x.save('cells.json', cells)
    x.save('arm-key.json', key)
    x.save('schema.json', r.CHECK_SCHEMA)
    x.save('runtime.json', e._runtime_versions())
    paths = x.DEPENDENCIES | {OLD / 'run.py', x.OLD / 'run.py', x.OLD / 'TASK.txt'} | set(e._runtime_sources().values())
    paths |= {p for p in HERE.rglob('*') if p.is_file()}
    x.save('pins.json', {str(p.resolve()): sha256(p.read_bytes()).hexdigest() for p in sorted(paths)})
    paired_check()
    print('24 calls frozen, 15 validated candidates, only the intended paragraph differs.')


def paired_check():
    key = e._load(HERE / 'arm-key.json')
    instructions = e._load(HERE / 'instructions.json')
    for cell, info in key.items():
        if info['arm'] != 'A': continue
        other, = [c for c, v in key.items() if v == dict(info, arm='B')]
        first = e._load(HERE / f'inputs/{cell}.json')
        second = e._load(HERE / f'inputs/{other}.json')
        before, after = first.pop('prompt'), second.pop('prompt')
        assert first == second
        assert before[len(instructions['A']):] == after[len(instructions['B']):]


def verify():
    x.pins()
    paired_check()
    cells = e._load(HERE / 'cells.json')
    with patch.object(e, '_create_model', side_effect=AssertionError('Provider forbidden')):
        for name in cells:
            data = e._load(HERE / f'inputs/{name}.json')
            directory = HERE / 'captures' / name
            attempt = e._load(directory / 'attempt.json')
            expected = dict(model=e.DEFAULT_MODEL, contents=data['prompt'], config=dict(
                max_output_tokens=32768, response_mime_type='application/json', response_json_schema=r.CHECK_SCHEMA,
                thinking_config=dict(thinking_level='medium')))
            assert e._load(directory / attempt['request_file']) == expected
            payload, errors = a._read_response(directory, attempt)
            judgments, issues = r._decode_checks(payload, errors, data['candidates'], data['document'], data['packet'])
            assert dict(payload=payload, errors=errors, judgments=judgments, issues=issues) == e._load(HERE / f'decoded/{name}.json')
    x.save('verification.json', dict(calls=len(cells), exact_request_shape=True, paired_inputs_match=True,
        provider_blocked=True, saved_responses_redecode_identically=True, frozen_pins_match=True))
    print(len(cells), 'requests and saved responses verified.')


if __name__ == '__main__':
    {'prepare': prepare, 'capture': x.capture, 'verify': verify}[sys.argv[1]]()
