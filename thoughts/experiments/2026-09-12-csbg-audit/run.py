"""Selected-window diagnostic through the existing audit functions; nine calls."""
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch

from rulespec_extrapolator import audit as a, extraction as e

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-09-12-csbg-focus'
MODEL = e.DEFAULT_MODEL


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def prepare():
    cells = {c['id']: c for c in e._load(BASE / 'cells.json')}
    doc = e._load(BASE.parent / '2026-09-12-csbg/sources/document.json')
    groups, comparisons, key = [], [], {}
    for name, baseline in [('plan', 'broad-1'), ('boards', 'broad-2'), ('correction', 'broad-2')]:
        window = cells[name]['window']
        groups.append({'id': name, 'window': window, 'prompt': e._window_prompt(
            e._prompt_generator([], a.INVENTORY_PROMPT), doc, window)})
        identities = [baseline, name]
        random.SystemRandom().shuffle(identities)
        for index, identity in enumerate(identities, 1):
            alias = f'{name}-{index}'
            comparisons.append({'id': alias, 'group': name, 'draft': identity})
            key[alias] = identity
    random.SystemRandom().shuffle(groups)
    random.SystemRandom().shuffle(comparisons)
    save('cells.json', {'groups': groups, 'comparisons': comparisons})
    save('review-key.json', key)
    save('configuration.json', {'model': MODEL, 'temperature': 0, 'thinking_level': 'medium',
        'max_output_tokens': 32768, 'inventory_prompt': a.INVENTORY_PROMPT,
        'comparison_prompt': a.comparison_prompt(), 'inventory_schema': a.INVENTORY_SCHEMA,
        'comparison_schema': a.COMPARISON_SCHEMA})
    save('runtime.json', e._freeze(HERE, [], a.INVENTORY_SCHEMA))
    pins = {str(p.relative_to(HERE)): sha256(p.read_bytes()).hexdigest()
            for p in HERE.rglob('*') if p.is_file()}
    for name in ['cells.json', 'manifest.json', *['decoded/' + n + '.json'
                 for n in ('plan', 'boards', 'correction', 'broad-1', 'broad-2')]]:
        pins['../2026-09-12-csbg-focus/' + name] = sha256((BASE / name).read_bytes()).hexdigest()
    pins['../2026-09-12-csbg/sources/document.json'] = sha256(
        (BASE.parent / '2026-09-12-csbg/sources/document.json').read_bytes()).hexdigest()
    save('precall-pins.json', pins)
    print('Prepared three inventories and six comparisons', flush=True)


def verify_pins():
    for name, expected in e._load(HERE / 'precall-pins.json').items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name


def capture():
    verify_pins()
    assert not (HERE / 'captures').exists()
    cells = e._load(HERE / 'cells.json')
    groups = {g['id']: g for g in cells['groups']}
    doc = e._load(BASE.parent / '2026-09-12-csbg/sources/document.json')
    key = e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    started = time.monotonic()
    count = 0

    def call(name, window, prompt, schema):
        nonlocal count
        if count >= 9 or time.monotonic() - started >= 900:
            raise RuntimeError('Predeclared capture bound reached')
        directory = HERE / 'captures' / name
        start = time.monotonic()
        attempts = a._capture(directory, doc, [window], [prompt], schema, MODEL, key, None,
                              max_output_tokens=32768, thinking_level='medium')
        save(f'captures/{name}/attempts.json', attempts)
        save(f'captures/{name}/timing.json', {'seconds': time.monotonic() - start})
        count += 1
        print(f'Captured {count}/9', flush=True)
        return directory, attempts

    for group in cells['groups']:
        name, window = group['id'], group['window']
        directory, attempts = call('inventory-' + name, window, group['prompt'], a.INVENTORY_SCHEMA)
        inventory = a._inventory(directory, doc, [window], attempts)
        save(f'inventory/{name}.json', inventory)
        save(f'labels/{name}.json', a._labels(doc, inventory, MODEL))
    for cell in cells['comparisons']:
        window = groups[cell['group']]['window']
        book = e._load(BASE / f"decoded/{cell['draft']}.json")['book']
        labels = e._load(HERE / f"labels/{cell['group']}.json")
        prompt = a._comparison_request(book, labels, window)
        directory, attempts = call(cell['id'], window, prompt, a.COMPARISON_SCHEMA)
        judgments, issues = a._judgments(directory, book, labels, [window], attempts, MODEL)
        save(f"decoded/{cell['id']}.json", {'judgments': judgments, 'issues': issues})
        packet, _, _ = a._comparison_input(book, labels, window)
        payload, errors = a._read_response(directory, attempts[0])
        save(f"review/{cell['id']}.json", {'draft': {alias: {k: c.get(k) for k in
            ('summary', 'scope_text', 'kind', 'modality', 'logic_text', 'choice_text')}
            for alias, c in packet['claims'].items()}, 'inventory': {
            alias: u['meaning'] for alias, u in packet['units'].items()},
            'response': payload, 'parse_issues': issues, 'response_errors': errors})
    save('usage.json', e.recorded_usage(HERE / 'captures'))
    save('capture-time.json', {'seconds': time.monotonic() - started, 'calls': count})


def verify():
    verify_pins()
    cells = e._load(HERE / 'cells.json')
    groups = {g['id']: g for g in cells['groups']}
    doc = e._load(BASE.parent / '2026-09-12-csbg/sources/document.json')
    checks = []
    def check(name, prompt, schema):
        directory = HERE / 'captures' / name
        attempts = e._load(directory / 'attempts.json')
        assert len(attempts) == 1
        expected = {'model': MODEL, 'contents': prompt, 'config': {'temperature': 0,
            'candidate_count': 1, 'max_output_tokens': 32768, 'thinking_config': {'thinking_level': 'medium'},
            'response_json_schema': schema}}
        assert e._load(directory / attempts[0]['request_file']) == expected
        return directory, attempts
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider call')):
        for g in cells['groups']:
            directory, attempts = check('inventory-' + g['id'], g['prompt'], a.INVENTORY_SCHEMA)
            inventory = a._inventory(directory, doc, [g['window']], attempts)
            assert inventory == e._load(HERE / f"inventory/{g['id']}.json")
            assert a._labels(doc, inventory, MODEL) == e._load(HERE / f"labels/{g['id']}.json")
            checks.append('inventory-' + g['id'])
        for c in cells['comparisons']:
            book = e._load(BASE / f"decoded/{c['draft']}.json")['book']
            labels = e._load(HERE / f"labels/{c['group']}.json")
            window = groups[c['group']]['window']
            directory, attempts = check(c['id'], a._comparison_request(book, labels, window), a.COMPARISON_SCHEMA)
            judgments, issues = a._judgments(directory, book, labels, [window], attempts, MODEL)
            assert {'judgments': judgments, 'issues': issues} == e._load(HERE / f"decoded/{c['id']}.json")
            checks.append(c['id'])
    save('verification.json', {'provider_calls': 0, 'identical_request_and_replay': checks,
                              'scope': 'selected-window diagnostic only'})
    print('Verified all nine actual requests and replayed observations', flush=True)


if __name__ == '__main__':
    {'prepare': prepare, 'capture': capture, 'verify': verify}[sys.argv[1]]()
