"""Aggregate the frozen manual labels and verify what each arm actually sent."""
from collections import Counter
from hashlib import sha256
import json

import run

HERE = run.HERE


def read(path):
    return json.loads((HERE / path).read_text())


def analyze():
    receipt = read('anonymous-review-receipt.json')
    assert sha256((HERE / receipt['review_file']).read_bytes()).hexdigest() == receipt['sha256']
    run.pins('source-pins.json'); run.pins('generation-pins.json')
    cells, key = read('cells.json'), read('arm-key.json')
    # Transcribed from the frozen anonymous table, not labels inferred from arms.
    complete = {'cell-1': ['C0001'], 'cell-2': ['C0002'], 'cell-3': ['C0001']}
    partial = {'cell-6': ['C0002']}
    groups, rows = {}, []
    arms = {arm: Counter() for arm in ('A', 'B')}
    ledger = read('calls.json')
    assert len(ledger) == len({c['name'] for c in ledger}) == 14
    books = read('books.json')
    assert books['pension'] == run.e._load(run.OLD / 'extract/pension/rulebook.json')
    assert books['control'] == run.e._load(run.NAV / 'books.json')['control']
    assert books['notice'] == read('notice-extract/rulebook.json')
    for cell in cells:
        name, arm = cell['id'], key[cell['id']]
        data = read(f'inputs/{name}.json')
        groups.setdefault((cell['case'], cell['repeat']), {})[arm] = name
        d = read(f'decoded/{name}-generation.json')
        check_path = f'decoded/{name}-check.json'
        checks = read(check_path)['judgments'] if (HERE / check_path).exists() else {}
        valid_ids = {p['proposal_id'] for p in d['previews']}
        full_valid_supported = sum(p['proposal']['target'] in complete.get(name, [])
            and p['id'] in valid_ids and checks.get(p['id'], {}).get('verdict') == 'supported'
            for p in d['prepared'])
        for p in d['payload']['proposals']:
            assert p['operation'] == 'edit' and p['target'] in data['selected']
        row = dict(cell=cell, arm=arm, positive_opportunities=3 if cell['case'] == 'notice' else 1,
            raw_proposals=len(d['payload']['proposals']), decoded=len(d['prepared']),
            previews=len(d['previews']), checker_supported=sum(v['verdict'] == 'supported' for v in checks.values()),
            checker_unsupported=sum(v['verdict'] == 'unsupported' for v in checks.values()),
            complete_generated=len(complete.get(name, [])), partial_generated=len(partial.get(name, [])),
            complete_valid_supported=full_valid_supported, observations=len(d['payload']['observations']))
        rows.append(row)
        for k, v in row.items():
            if isinstance(v, int): arms[arm][k] += v
        arms[arm]['generation_calls'] += 1
        arms[arm]['nonempty_generation_calls'] += bool(d['payload']['proposals'])
        for phase in ('generation', 'check'):
            directory = HERE / f'captures/{name}/{phase}'
            if not directory.exists(): continue
            response = run.e._load(directory / 'attempt-0000.response.json')
            request = run.e._load(directory / 'attempt-0000.request.json')
            assert request == read(f'expected-requests/{name}-{phase}.json')
            assert request['model'] == response['model_version'] == 'gemini-3.8-flash'
            assert [c['finish_reason'] for c in response['candidates']] == ['STOP']
            config = request['config']
            assert config['temperature'] == 0 and config['max_output_tokens'] == 32768
            assert config['thinking_config'] == {'thinking_level': 'medium'}
            assert config['response_json_schema'] == read('schemas.json')[phase]
            if phase == 'check': arms[arm]['checker_calls'] += 1
            usage = run.e.recorded_usage(directory)
            for k, v in usage['tokens'].items(): arms[arm][f'{phase}_{k}'] += v
            arms[arm][f'{phase}_seconds'] += next(c['seconds'] for c in ledger if c['name'] == f'{name}/{phase}')
    for pair in groups.values():
        a, b = [read(f'expected-requests/{pair[arm]}-generation.json') for arm in ('A', 'B')]
        assert a['contents'].count(run.CONSTRUCTION) == 0 and b['contents'].count(run.CONSTRUCTION) == 1
        assert {**b, 'contents': b['contents'].replace(run.CONSTRUCTION, '', 1)} == a
        a_data, b_data = [read(f'inputs/{pair[arm]}.json') for arm in ('A', 'B')]
        assert {k: v for k, v in a_data.items() if k != 'prompt'} == {k: v for k, v in b_data.items() if k != 'prompt'}
    for arm in ('A', 'B'):
        repeats = [read(f'expected-requests/{groups[("pension", n)][arm]}-generation.json') for n in (0, 1)]
        assert repeats[0] == repeats[1]
    # Diagnose the failed optional quote without altering or retrying the proposal.
    raw = read('decoded/cell-3-generation.json')['payload']['proposals'][0]
    absent = [name for name, quote in run.e.core.evidence_expectations(raw['fields']).items()
              if quote and quote not in books['pension']['document']['text']]
    assert absent == ['logic_text']
    notice = read('decoded/cell-6-generation.json')
    raw, prepared = notice['payload']['proposals'][1], notice['prepared'][1]
    packet = read('inputs/cell-6.json')['packet']
    assert 'applies_to' not in raw['fields'] and raw['qualifies'] == ['C0000']
    assert prepared['fields']['applies_to'] == [packet['claims']['C0000']['id']]
    check_request = read('expected-requests/cell-6-check.json')
    sent = json.loads(check_request['contents'].split('\nProposed changes: ')[1])
    assert sent[1]['fields']['applies_to'] == prepared['fields']['applies_to']
    total = run.e.recorded_usage(HERE)
    assert total == read('usage.json') and total['recorded_requests'] == 14
    assert total['incomplete_responses'] == total['responses_without_usage'] == total['requests_without_response'] == 0
    result = dict(cells=rows, arms=arms, usage=total,
        fresh_extraction_usage=run.e.recorded_usage(HERE / 'notice-extract'),
        cumulative_capture_seconds=sum(c['seconds'] for c in ledger),
        interpretation='Bounded meaning improvement; full gate failed; no production adoption.',
        checks=dict(requests_differ_only_by_construction=True, pension_repeat_requests_identical=True,
            originals_match_saved_captures=True, optional_quote_failure_fields=absent,
            criticized_identifier_was_application_inserted=True),
        manual_review_sha256=receipt['sha256'])
    run.save('RESULTS.json', result)
    print(json.dumps(dict(arms=arms, total=total, capture_seconds=result['cumulative_capture_seconds']), indent=2))


if __name__ == '__main__':
    analyze()
