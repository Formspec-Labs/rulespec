"""Vary source-inventory allocation; reuse production capture and audit helpers."""
from hashlib import sha256
import json
from pathlib import Path
import random
import sys
import tempfile
import time
from unittest.mock import patch
from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import audit as a, extraction as e

HERE = Path(__file__).resolve().parent
CHECKLIST = """
Complete the ordered passage checklist below. For EVERY listed focus passage,
emit at least one inventory unit with quote_ref equal to that SINGLE passage ID.
Do not substitute a passage range or a parent summary for an item's own decision.
A passage may require several units when it contains several substantive meanings.
For a heading, bare marker or text without another substantive meaning, use
background and explain why. Do not invent a duty for every passage: preserve
definitions, examples, options and conditions in their actual roles. A child
component's meaning must include its governing lead-ins and qualifications from
elsewhere in the supplied source; select those in scope_refs. Preserve every
substantive detail within the selected passage. Do not require a duplicate parent
statement when component meanings jointly state its complete contents. This is
source accounting, not proof of semantic completeness.
Ordered focus passage checklist: """


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def pins():
    for ledger in ('pre-extraction-pins.json', 'pre-audit-pins.json'):
        for name, expected in e._load(HERE / ledger).items():
            assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name


def book_for(case):
    data = e._load(HERE / case['book_path'])
    return data['book'] if case['id'] == 'csbg' else data


def prepare():
    old = e._load(HERE / '../2026-09-12-csbg-focus/cells.json')
    cases = [{'id': 'csbg', 'book_path': '../2026-09-12-csbg-focus/decoded/plan.json',
              'window': next(c['window'] for c in old if c['id'] == 'plan')}]
    for name in ('iep', 'lea'):
        path = f'extract/{name}/rulebook.json'
        cases.append({'id': name, 'book_path': path,
                      'window': e.plan_windows(e._load(HERE / path)['document'])[0]})
    cells, key = [], {}
    for case in cases:
        doc = book_for(case)['document']
        refs = [r for r in e.passage_catalog(doc, case['window']) if r.startswith('F')]
        arms = ['A', 'B']
        random.SystemRandom().shuffle(arms)
        for index, arm in enumerate(arms, 1):
            identity = f"{case['id']}-{index}"
            description = a.INVENTORY_PROMPT + (CHECKLIST + ', '.join(refs) if arm == 'B' else '')
            cells.append({'id': identity, 'case': case['id'], 'arm': arm, 'required_refs': refs,
                'prompt': e._window_prompt(e._prompt_generator([], description), doc, case['window'])})
            key[identity] = arm
    random.SystemRandom().shuffle(cells)
    save('cells.json', {'cases': cases, 'cells': cells})
    save('review-key.json', key)
    save('configuration.json', {'model': e.DEFAULT_MODEL, 'temperature': 0,
        'max_output_tokens': 32768, 'thinking_level': 'medium', 'checklist': CHECKLIST,
        'inventory_prompt': a.INVENTORY_PROMPT, 'comparison_prompt': a.comparison_prompt(),
        'inventory_schema': a.INVENTORY_SCHEMA, 'comparison_schema': a.COMPARISON_SCHEMA})
    paths = [HERE / n for n in ('PLAN.md', 'PRELABELS.md', 'run.py', 'cells.json',
                               'review-key.json', 'configuration.json')]
    paths += [p for p in (HERE / 'extract').rglob('*') if p.is_file()]
    save('pre-audit-pins.json', {str(p.relative_to(HERE)): sha256(p.read_bytes()).hexdigest() for p in paths})
    print('Prepared six inventory and six comparison requests; source labels pinned')


def inventory(name, case, directory, attempts):
    doc = book_for(case)['document']
    value = a._inventory(directory, doc, [case['window']], attempts)
    return value, a._labels(doc, value, e.DEFAULT_MODEL)


def capture():
    pins()
    assert not (HERE / 'inventory').exists()
    config = e._load(HERE / 'cells.json')
    cases = {c['id']: c for c in config['cases']}
    key = e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    started = time.monotonic()
    elapsed = e._load(HERE / 'extraction-time.json')['seconds']
    calls = 2
    def call(stage, cell, prompt, schema):
        nonlocal calls
        usage = e.recorded_usage(HERE)['tokens'].get('total_token_count', 0)
        if calls >= 14 or time.monotonic() - started + elapsed >= 1200 or usage >= 350000:
            save('stopped.json', {'calls': calls, 'tokens': usage, 'reason': 'predeclared_bound'})
            raise RuntimeError('Predeclared bound reached')
        case = cases[cell['case']]
        directory = HERE / stage / cell['id']
        start = time.monotonic()
        attempts = a._capture(directory, book_for(case)['document'], [case['window']], [prompt], schema,
            e.DEFAULT_MODEL, key, None, max_output_tokens=32768, thinking_level='medium')
        save(f"{stage}/{cell['id']}/attempts.json", attempts)
        save(f"{stage}/{cell['id']}/timing.json", {'seconds': time.monotonic() - start})
        calls += 1
        print(f'Captured {calls}/14', flush=True)
        return directory, attempts
    usable = []
    for cell in config['cells']:
        directory, attempts = call('inventory', cell, cell['prompt'], a.INVENTORY_SCHEMA)
        value, labels = inventory(cell['id'], cases[cell['case']], directory, attempts)
        payload, errors = a._read_response(directory, attempts[0])
        direct_refs = {u.get('quote_ref') for u in payload.get('units', []) if isinstance(u, dict)}
        save(f"inventory/{cell['id']}/decoded.json", value)
        save(f"inventory/{cell['id']}/labels.json", labels)
        save(f"inventory/{cell['id']}/adherence.json", {'required': len(cell['required_refs']),
            'explicit_single_passage_decisions': len(set(cell['required_refs']) & direct_refs),
            'missing_refs': [r for r in cell['required_refs'] if r not in direct_refs]})
        if labels['expected_units'] and not errors:
            usable.append(cell)
        else:
            save(f"inventory/{cell['id']}/comparison-skipped.json", {'reason': 'unusable_inventory', 'errors': errors})
    random.SystemRandom().shuffle(usable)
    save('comparison-order.json', [c['id'] for c in usable])
    for cell in usable:
        case = cases[cell['case']]
        book = book_for(case)
        labels = e._load(HERE / f"inventory/{cell['id']}/labels.json")
        prompt = a._comparison_request(book, labels, case['window'])
        directory, attempts = call('comparison', cell, prompt, a.COMPARISON_SCHEMA)
        judgments, issues = a._judgments(directory, book, labels, [case['window']], attempts, e.DEFAULT_MODEL)
        save(f"comparison/{cell['id']}/decoded.json", {'judgments': judgments, 'issues': issues})
        packet, _, _ = a._comparison_input(book, labels, case['window'])
        response, errors = a._read_response(directory, attempts[0])
        save(f"review/{cell['id']}.json", {'draft': {alias: {k: c.get(k) for k in
            ('summary', 'scope_text', 'kind', 'modality', 'logic_text', 'choice_text')}
            for alias, c in packet['claims'].items()}, 'inventory': {alias: u['meaning']
            for alias, u in packet['units'].items()}, 'response': response, 'issues': issues, 'errors': errors})
    save('usage.json', e.recorded_usage(HERE))
    save('capture-time.json', {'audit_seconds': time.monotonic() - started, 'extraction_seconds': elapsed, 'calls': calls})


def verify():
    pins()
    config = e._load(HERE / 'cells.json')
    cases = {c['id']: c for c in config['cases']}
    checks = []
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider call')):
        for cell in config['cells']:
            case = cases[cell['case']]
            book = book_for(case)
            directory = HERE / 'inventory' / cell['id']
            attempts = e._load(directory / 'attempts.json')
            value, labels = inventory(cell['id'], case, directory, attempts)
            assert value == e._load(directory / 'decoded.json')
            assert labels == e._load(directory / 'labels.json')
            for stage, prompt, schema in [('inventory', cell['prompt'], a.INVENTORY_SCHEMA),
                ('comparison', a._comparison_request(book, labels, case['window']), a.COMPARISON_SCHEMA)]:
                directory = HERE / stage / cell['id']
                if not directory.exists():
                    checks.append({'cell': cell['id'], 'stage': stage, 'status': 'not_captured'});continue
                attempts = e._load(directory / 'attempts.json')
                actual = e._load(directory / attempts[0]['request_file'])
                expected = {'model': e.DEFAULT_MODEL, 'contents': prompt, 'config': {
                    'temperature': 0, 'max_output_tokens': 32768, 'thinking_config': {'thinking_level': 'medium'},
                    'candidate_count': 1, **GeminiSchema(schema, _use_json_schema=True).to_provider_config()}}
                assert actual == expected
                receipt = {'cell': cell['id'], 'stage': stage, 'request_equal': True, 'replay_equal': True}
                if stage == 'comparison':
                    judgments, issues = a._judgments(directory, book, labels, [case['window']], attempts, e.DEFAULT_MODEL)
                    assert {'judgments': judgments, 'issues': issues} == e._load(directory / 'decoded.json')
                    _, claims, units = a._comparison_input(book, labels, case['window'])
                    receipt.update(issues=issues, expected_claims=len(claims), judged_claims=len(judgments['claim_judgments']),
                        expected_units=len(units), judged_units=len(judgments['unit_judgments']),
                        reciprocal_links={(c['claim_id'],u) for c in judgments['claim_judgments'] for u in c['unit_ids']} ==
                                         {(c,u['unit_id']) for u in judgments['unit_judgments'] for c in u['claim_ids']})
                checks.append(receipt)
        with tempfile.TemporaryDirectory(prefix='rulespec-subordinate-replay-') as name:
            for case in ('iep','lea'):
                assert e.replay_run(HERE / 'extract' / case, Path(name) / case) == e._load(HERE / f'extract/{case}/rulebook.json')
    save('verification.json', {'provider_calls': 0, 'checks': checks, 'fresh_extraction_replays_identical': True})
    print('Verified saved requests, audit observations and both extraction replays')


if __name__ == '__main__':
    {'prepare': prepare, 'capture': capture, 'verify': verify}[sys.argv[1]]()
