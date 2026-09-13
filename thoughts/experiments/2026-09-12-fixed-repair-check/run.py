"""Challenge fixed positive/negative repairs with the existing checker unchanged."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import random
import sys
import tempfile
import time
from unittest.mock import patch

from rulespec_extrapolator import audit as a, extraction as e, refinement as r

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / '2026-09-12-navigation-repair'
spec = importlib.util.spec_from_file_location('navigation_repair', PRIOR / 'run.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
MODEL, CONFIG = prior.MODEL, prior.CONFIG
RATIONALE = 'Assess whether this edit makes the selected statement independently usable while preserving its source meaning.'


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert e._load(path) == value, name
    else:
        e._save(path, value)


def specifications():
    return {
        'iep': [
            ('I1', 4, 'The parent’s agreement under this attendance provision must be in writing.', 6, 'supported'),
            ('I2', 5, 'The parent’s consent under this excusal provision must be in writing.', 6, 'supported'),
            ('I3', 4, 'Both the parent’s agreement and the local educational agency’s agreement under this attendance provision must be in writing.', 6, 'unsupported'),
            ('I4', 5, 'The member’s written input satisfies the requirement for written parental consent.', 6, 'unsupported'),
            ('I5', 3, 'Every team member’s participation requires prior written parental consent.', 6, 'unsupported'),
            ('I6', 7, 'This invitation may occur only after written parental consent.', 6, 'unsupported'),
        ],
        'control': [
            ('T1', 0, 'An electronic request must include the applicant’s name and reference number.', 1, 'supported'),
            ('T2', 0, 'Applicants may submit the request only after the agency has published its annual request statistics.', 2, 'unsupported'),
            ('T3', 3, 'The applicant must supply their name and reference number before inspecting public records.', 1, 'unsupported'),
            ('T4', 0, 'Applicants must publish annual statistics on electronically submitted requests.', 2, 'unsupported'),
        ],
    }


def prepare():
    assert not (HERE / 'cells.json').exists()
    books = e._load(PRIOR / 'books.json')
    labels, cells, all_prepared, mechanics = {}, [], {}, []
    rng = random.Random(91281)
    for case, specs in specifications().items():
        book = books[case]
        window, packet = prior.packet(book)
        rng.shuffle(specs)
        proposals = []
        for index, (name, target, addition, support, expected) in enumerate(specs):
            claim = book['accepted'][target]
            fields = {k: deepcopy(claim[k]) for k in r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']}
            fields['summary'] += ' ' + addition
            fields['context_quotes'] = list(dict.fromkeys([*fields['context_quotes'], book['accepted'][support]['quote']]))
            proposals.append(dict(operation='edit', target=f'C{target:04d}', qualifies=[],
                                  rationale=RATIONALE, quote=claim['quote'], fields=fields))
            labels[f'{case}/P{index:04d}'] = dict(case_id=name, target_row=target, support_row=support, expected=expected)
        prepared, issues = r._decode_proposals(dict(proposals=proposals, observations=[]), [], book['document'], window, packet, 'recovery')
        assert not issues and len(prepared) == len(specs), issues
        with tempfile.TemporaryDirectory() as directory:
            store = prior.temporary_store(directory, book)
            before = store.snapshot()
            for proposal in prepared:
                preview = store.preview(r._action(proposal, before, MODEL))
                target = next(c for c in before['accepted'] if c['id'] == proposal['target_id'])
                new = next(c for c in preview['accepted'] if c['rule_id'] == target['rule_id'])
                assert (new['quote'], new['kind'], new['modality']) == (target['quote'], target['kind'], target['modality'])
                assert not new['target_ids']
                assert not any(i['code'] == 'component_evidence_unresolved' for i in new['issues'])
                assert store.snapshot() == before
                mechanics.append(dict(case=case, proposal_id=proposal['id'], preview_valid=True,
                    source_requirement_unchanged=before['accepted'][6] in preview['accepted'] if case == 'iep' else True,
                    evidence_fields=[v['field'] for v in new['evidence']], preview_only=True))
        all_prepared[case] = dict(window=window, packet=packet, prepared=prepared)
    combinations = [(case, order) for case in books for order in ('forward', 'reverse')]
    rng.shuffle(combinations)
    for index, (case, order) in enumerate(combinations):
        name = f'cell-{index + 1}'
        data = all_prepared[case]
        prepared = data['prepared'][::1 if order == 'forward' else -1]
        prompt = r._challenge_prompt(data['packet'], prepared, books[case]['document'])
        save(f'inputs/{name}.json', dict(prompt=prompt, case=case, order=order, prepared=prepared,
                                       window=data['window'], model=MODEL, config=CONFIG))
        cells.append(dict(id=name, case=case, order=order))
    save('prepared.json', all_prepared)
    save('labels.json', labels)
    save('mechanical-proof.json', mechanics)
    save('cells.json', cells)
    save('schema.json', r.CHECK_SCHEMA)
    save('runtime-versions.json', e._runtime_versions())
    paths = [HERE / n for n in ('PLAN.md', 'run.py', 'prepared.json', 'labels.json', 'cells.json', 'schema.json')]
    paths += sorted((HERE / 'inputs').glob('*.json')) + [PRIOR / 'books.json', PRIOR / 'run.py']
    paths += list(e._runtime_sources().values())
    save('precall-pins.json', {os.path.relpath(p, HERE): sha256(p.read_bytes()).hexdigest() for p in paths})
    print('Ten constructed repairs decode/preview; four checker requests frozen; no model calls.')


def pins():
    for name, expected in e._load(HERE / 'precall-pins.json').items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name


def decode(cell):
    directory = HERE / 'captures' / cell['id']
    attempt = e._load(directory / 'attempt.json')
    payload, errors = a._read_response(directory, attempt)
    data = e._load(HERE / f'inputs/{cell["id"]}.json')
    frozen = e._load(HERE / 'prepared.json')[cell['case']]
    book = e._load(PRIOR / 'books.json')[cell['case']]
    judgments, issues = r._decode_checks(payload, errors, data['prepared'], book['document'], frozen['packet'])
    return dict(payload=payload, errors=errors, judgments=judgments, issues=issues)


def capture():
    pins()
    assert not (HERE / 'captures').exists()
    key = e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    books = e._load(PRIOR / 'books.json')
    start = time.monotonic()
    for index, cell in enumerate(e._load(HERE / 'cells.json')):
        usage = e.recorded_usage(HERE / 'captures').get('tokens', {}).get('total_token_count', 0)
        if index >= 4 or time.monotonic() - start >= 900 or usage >= 120000:
            save('stopped.json', dict(completed=index, reason='predeclared_bound')); break
        data = e._load(HERE / f'inputs/{cell["id"]}.json')
        directory = HERE / 'captures' / cell['id']
        begin = time.monotonic()
        attempts = a._capture(directory, books[cell['case']]['document'], [data['window']], [data['prompt']],
            r.CHECK_SCHEMA, MODEL, key, None, max_output_tokens=CONFIG['max_output_tokens'], thinking_level=CONFIG['thinking_level'])
        save(f'captures/{cell["id"]}/attempt.json', attempts[0])
        save(f'captures/{cell["id"]}/timing.json', dict(seconds=time.monotonic() - begin))
        result = decode(cell)
        save(f'decoded/{cell["id"]}.json', result)
        print(f'{cell["id"]}: {len(result["judgments"])} judgments, {len(result["issues"])} issues', flush=True)
    save('usage.json', e.recorded_usage(HERE / 'captures'))
    pins()


def verify():
    pins()
    books, fixed = e._load(PRIOR / 'books.json'), e._load(HERE / 'prepared.json')
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected model call')):
        for cell in e._load(HERE / 'cells.json'):
            assert decode(cell) == e._load(HERE / f'decoded/{cell["id"]}.json')
            data = e._load(HERE / f'inputs/{cell["id"]}.json')
            assert data['prompt'] == r._challenge_prompt(fixed[cell['case']]['packet'], data['prepared'], books[cell['case']]['document'])
            attempt = e._load(HERE / 'captures' / cell['id'] / 'attempt.json')
            req = e._load(HERE / 'captures' / cell['id'] / attempt['request_file'])
            assert req == dict(model=MODEL, contents=data['prompt'], config=dict(temperature=0, max_output_tokens=32768,
                candidate_count=1, response_mime_type='application/json', response_json_schema=r.CHECK_SCHEMA,
                thinking_config=dict(thinking_level='medium')))
    print('All four exact requests and response decodes verified; provider creation blocked; pinned originals unchanged.')


if __name__ == '__main__':
    {'prepare': prepare, 'capture': capture, 'verify': verify}[sys.argv[1]]()
