"""Nine-call bounded comparison using existing audit capture and replay helpers."""
import argparse
from contextlib import nullcontext
from copy import deepcopy
from pathlib import Path
import random
import time
from unittest.mock import patch

from rulespec_extrapolator import audit as a, extraction as e
from rulespec_extrapolator.core import compile_candidates, validate_graph
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
EXTRA = '''
Applicability contrast requirement: Start each claim rationale with one concrete
case for which the draft's applicability differs from the supplied source, naming
what the draft says and what the source supports. If you find no supported
contrast, explicitly say so; do not invent a scenario or force an error. Then
explain the evidence and assess every existing dimension normally. Distinguish
an actual lost governing condition from an unrelated branch's condition. Source
uncertainty must stay unknown. A contrast in rationale does not change the draft.
'''
ORIGINAL = a.comparison_prompt


def prepare():
    assert not (ROOT / 'design.json').exists()
    sources = ROOT / 'sources'
    books = {}
    labels = {}
    for name in ('emergency-plan', 'extinguishers'):
        text = (sources / f'{name}.txt').read_text()
        if name == 'extinguishers':
            text = text[:text.index('\n\n(e)')]
        (sources / f'{name}.selected.txt').write_text(text)
        doc = prepare_document(text, title=name + ' official 2025 source',
                               source_url=(sources / f'{name}.url').read_text().strip())
        paragraphs = text.split('\n\n')
        def para(needle):
            found = [p for p in paragraphs if needle in p]
            assert len(found) == 1, needle
            return found[0]
        rows = []
        expected = []
        def add(code, faithful, shown, quote, kind, modality, expected_error, reason,
                scope='', scope_quotes=()):
            candidate = {'summary': shown, 'quote': quote, 'kind': kind,
                         'modality': modality, 'modality_quote': quote,
                         'scope_text': scope, 'scope_quotes': list(scope_quotes)}
            rows.append(candidate)
            expected.append({'label': code, 'faithful_reading': faithful, 'shown_reading': shown,
                             'expected_error': expected_error, 'reason': reason})
        if name == 'emergency-plan':
            application = para('An employer must have an emergency action plan whenever')
            writing = para('An emergency action plan must be in writing')
            training = para('An employer must designate and train employees')
            add('E0', 'An employer must have an emergency action plan whenever an OSHA standard in this part requires one.',
                'An employer must have an emergency action plan.', application, 'requirement', 'must', True,
                'Drops the OSHA-standard-requires-one applicability trigger.')
            add('E1', 'When an OSHA standard in this part requires an emergency action plan, it must be written, kept in the workplace and available for employee review, but employers with 10 or fewer employees may communicate it orally.',
                'When an OSHA standard in this part requires an emergency action plan, it must be in writing, kept in the workplace, and available to employees for review.',
                writing, 'requirement', 'must', True, 'Drops the <=10-employee oral alternative.',
                'When an OSHA standard in this part requires an emergency action plan.', [application])
            oral = 'When an OSHA standard in this part requires an emergency action plan, an employer with 10 or fewer employees may communicate the plan orally to employees.'
            add('E2', oral, oral, writing, 'permission', 'may', False,
                'Correct oral permission with required-plan scope; do not demand writing for <=10.',
                'When an OSHA standard in this part requires an emergency action plan.', [application])
            train = 'When an OSHA standard in this part requires an emergency action plan, an employer must designate and train employees to assist in a safe and orderly evacuation of other employees.'
            add('E3', train, train, training, 'requirement', 'must', False,
                'The small-employer oral-plan exception does not remove evacuation training.',
                'When an OSHA standard in this part requires an emergency action plan.', [application])
        else:
            scope = para('The requirements of this section apply to the placement')
            exempt_all = para('Where the employer has established and implemented')
            designated = para('Where the employer has an emergency action plan meeting')
            class_a = para('travel distance for employees to any extinguisher is 75 feet')
            charged = para('maintained in a fully charged and operable condition')
            add('F0', 'Where paragraph (d) applies, subject to the (a) and (b) exemptions, employers must distribute Class A extinguishers so employee travel distance is at most 75 feet (22.9 m).',
                'The employer shall distribute portable fire extinguishers for use by employees on Class A fires so that the travel distance for employees to any extinguisher is 75 feet (22.9 m) or less.',
                class_a, 'requirement', 'must', True, 'Omits (a)/(b) exclusions governing distribution (d).')
            applicable = 'For employee-use portable extinguishers to which paragraph (c) applies, excluding workplaces exempt under (b)(1) and the non-employee-use situation in (a) where only (e) and (f) apply'
            add('F1', applicable + ', the employer shall assure they are fully charged and operable and kept in designated places at all times except during use.',
                applicable + ', the employer shall assure they are fully charged and operable and kept in designated places at all times.',
                charged, 'requirement', 'must', True, 'Drops the explicit during-use exception.',
                applicable, [scope, exempt_all])
            exemption = 'Where an employer has an emergency action plan meeting section 1910.38 that designates certain employees as the only authorized users of available portable fire extinguishers and requires all other employees in the fire area to immediately evacuate the affected work area when the fire alarm sounds, the employer is exempt from paragraph (d) distribution requirements.'
            add('F2', exemption, exemption, designated, 'exemption', 'not_required', False,
                'All (b)(2) conditions retained; exemption is only from distribution, not paragraph (c).')
            outside = 'Paragraph (d) does not apply to extinguishers provided for employee use on the outside of workplace buildings or structures.'
            add('F3', outside, outside, scope, 'exemption', 'not_required', False,
                'Accurate limited paragraph-(d) exemption, not a blanket exemption.')
        book = compile_candidates(doc, rows, {'id': 'urn:experiment:explicit-audit:' + name})
        assert not book['rejected'], book['rejected']
        assert len(book['accepted']) == 4
        validate_graph(book['graph'])
        for item, claim in zip(expected, book['accepted'], strict=True):
            item['claim_id'] = claim['id']
        books[name], labels[name] = book, expected
        e._save(ROOT / 'inputs' / f'{name}.candidates.json', rows)
    path = REPO / 'examples/document_understanding/consistency-transfer/cells/cell-00/rulebook.json'
    books['seatbelts'] = e._load(path)
    labels['seatbelts'] = [{'claim_id': books['seatbelts']['accepted'][0]['id'],
        'expected_error': True, 'reason': 'Initial takeoff duty omits remote part 121/125/135 exclusions.'}]
    for name, book in books.items():
        e._save(ROOT / 'inputs' / f'{name}.rulebook.json', book)
        assert len(e.plan_windows(book['document'], 24000)) == 1
    e._save(ROOT / 'expected.json', labels)
    cells = [(name, arm) for name in books for arm in ('A', 'B')]
    random.Random(20260910).shuffle(cells)
    inputs = [ROOT / 'PLAN.md', Path(__file__), ROOT / 'expected.json',
              *sorted(sources.glob('*')), *sorted((ROOT / 'inputs').glob('*'))]
    fingerprints = e._freeze(ROOT, [], a.COMPARISON_SCHEMA)
    e._save(ROOT / 'design.json', {'cells': [{'id': f'cell-{i:02d}', 'case': n, 'arm': arm}
        for i, (n, arm) in enumerate(cells)], 'cases': list(books), 'model': e.DEFAULT_MODEL,
        'thinking_level': 'medium', 'temperature': 0, 'max_output_tokens': 32768,
        'max_chars': 24000, 'max_calls': 9, 'max_seconds': 1200,
        'inputs': {str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in inputs},
        'runtime': e._runtime_versions(), 'fingerprints': fingerprints})
    print('Prepared three documents and six paired comparison cells. No provider calls.', flush=True)


def execute(replay=False):
    design = e._load(ROOT / 'design.json')
    for name, digest in design['inputs'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest, name
    assert e._runtime_versions() == design['runtime']
    start = time.monotonic()
    key = '' if replay else e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    count = 0
    books, inventories, labels = {}, {}, {}
    def capture(directory, book, windows, prompts, schema):
        nonlocal count
        if replay:
            return e._load(directory / 'attempts.json')
        if count >= design['max_calls'] or time.monotonic() - start >= design['max_seconds']:
            raise RuntimeError('Experiment bound reached; retain completed attempts')
        count += 1
        attempts = a._capture(directory, book['document'], windows, prompts, schema,
            design['model'], key, None, max_output_tokens=design['max_output_tokens'],
            thinking_level=design['thinking_level'])
        e._save(directory / 'attempts.json', attempts)
        print(f'Call {count}/9: {directory.relative_to(ROOT)} {attempts[0]["status"]}', flush=True)
        return attempts
    for name in design['cases']:
        book = books[name] = e._load(ROOT / 'inputs' / f'{name}.rulebook.json')
        windows = e.plan_windows(book['document'], design['max_chars'])
        directory = ROOT / 'inventories' / name
        prompts = [e._window_prompt(e._prompt_generator([], a.INVENTORY_PROMPT), book['document'], w) for w in windows]
        attempts = capture(directory, book, windows, prompts, a.INVENTORY_SCHEMA)
        inventory = a._inventory(directory, book['document'], windows, attempts)
        label = a._labels(book['document'], inventory, design['model'])
        inventories[name], labels[name] = inventory, label
        if replay:
            assert inventory == e._load(directory / 'inventory.json')
            assert label == e._load(directory / 'labels.json')
        else:
            e._save(directory / 'inventory.json', inventory)
            e._save(directory / 'labels.json', label)
    for cell in design['cells']:
        book, label = books[cell['case']], labels[cell['case']]
        windows = e.plan_windows(book['document'], design['max_chars'])
        directory = ROOT / 'cells' / cell['id']
        with patch.object(a, 'comparison_prompt', lambda: ORIGINAL() + EXTRA) if cell['arm'] == 'B' else nullcontext():
            prompts = [a._comparison_request(book, label, w) for w in windows]
        attempts = capture(directory, book, windows, prompts, a.COMPARISON_SCHEMA)
        for attempt, prompt in zip(attempts, prompts, strict=True):
            if attempt.get('request_file'):
                assert e._load(directory / attempt['request_file'])['contents'] == prompt
        judgments, issues = a._judgments(directory, book, label, windows, attempts, design['model'])
        report = a._assessment(book, label, judgments, inventories[cell['case']]['issues'] + issues)
        if replay:
            assert judgments == e._load(directory / 'judgments.json')
            assert report == e._load(directory / 'report.json')
        else:
            e._save(directory / 'judgments.json', judgments)
            e._save(directory / 'report.json', report)
    if replay:
        e._save(ROOT / 'replay-checks.json', {'nine_captures_replayed': True, 'provider_calls': 0})
    print('Replay matched.' if replay else 'All nine calls completed; raw assessment pending.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'run', 'replay'])
    args = parser.parse_args()
    if args.mode == 'prepare':
        prepare()
    else:
        execute(args.mode == 'replay')
