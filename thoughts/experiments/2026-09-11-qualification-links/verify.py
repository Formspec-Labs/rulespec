"""Receipts for fixed inputs, actual requests and deterministic saved-data replay."""
from hashlib import sha256
import run as x

a, e, r = x.a, x.e, x.r
root = x.ROOT
frozen = e._load(root / 'precall-pins.json')
assert frozen == x.pins([root / name for name in frozen])
for name, digest in e._load(root / 'runtime-sha256.json').items():
    assert sha256((root / 'runtime' / name).read_bytes()).hexdigest() == digest

old = {c['id']: c for c in e._load(x.PRIOR / 'cases.json')}
pairs, generation = [], []
for case in e._load(root / 'cases.json'):
    name = case['id']
    assert case['book'] == old[name]['book']
    assert case['materials'] == old[name]['materials']
    assert case['labels'] == e._load(x.PRIOR / 'inventory' / (name + '-B') / 'labels.json')
    directory = root / 'relationships' / name
    decoded = e._load(directory / 'proposals.json')
    document = case['book']['document']
    evidence = []
    for p in decoded['prepared']:
        fields = p['fields']
        span = {'source_id': document['id'], **{k: fields[k] for k in ('quote', 'start', 'end')}}
        evidence.append(x.prior.evidence_receipt(document, span))
    e._save(directory / 'source-evidence.json', evidence)
    generation.append({'case': name, 'accepted': len(decoded['prepared']),
        'target_count': sum(len(p['qualification_ids']) for p in decoded['prepared']),
        'issue_codes': [i['code'] for i in decoded['issues']]})
    apath = root / 'advisory' / (name + '-A.json')
    if not apath.exists():
        continue
    av, bv = e._load(apath), e._load(root / 'advisory' / (name + '-B.json'))
    assert av == [{k: v for k, v in row.items() if k != 'qualifies'} for row in bv]
    delimiter = '\nAdditional proposed qualifications: '
    requests = [e._load(root / 'inputs' / 'comparison' / (name + '-' + arm + '.json')) for arm in ('A', 'B')]
    assert requests[0]['schema'] == requests[1]['schema']
    assert requests[0]['prompt'].split(delimiter)[0] == requests[1]['prompt'].split(delimiter)[0]
    assert requests[0]['prompt'].split(delimiter)[1] == e._canonical(av)
    assert requests[1]['prompt'].split(delimiter)[1] == e._canonical(bv)
    pairs.append({'case': name, 'only_difference': 'qualifies target arrays', 'proposals': len(av)})

requests = []
for call in e._load(root / 'calls.json'):
    name = call['name']
    directory = root / name
    intended = e._load(root / 'inputs' / (name + '.json'))
    for attempt in e._load(directory / 'attempts.json'):
        if not attempt.get('request_file'):
            requests.append({'name': name, 'status': attempt['status'], 'no_recorded_request': True})
            continue
        actual = e._load(directory / attempt['request_file'])
        assert actual['contents'] == intended['prompt']
        assert actual['model'] == x.MODEL
        assert actual['config']['response_json_schema'] == intended['schema']
        config = {k: v for k, v in actual['config'].items() if k != 'response_json_schema'}
        assert config == {'temperature': 0, 'max_output_tokens': 32768,
            'response_mime_type': 'application/json', 'candidate_count': 1,
            'thinking_config': {'thinking_level': 'medium'}}
        requests.append({'name': name, 'status': attempt['status'], 'model': actual['model'], 'config': config})

comparisons = []
for cell in e._load(root / 'cells.json'):
    if cell['status'] != 'captured':
        continue
    result = e._load(root / 'comparison' / cell['name'] / 'assessment.json')
    judgments = result['judgments']
    comparisons.append({'case': cell['case'], 'arm': cell['arm'],
        'claim_count': len(judgments['claim_judgments']), 'unit_count': len(judgments['unit_judgments']),
        'issues': result['issues'], 'evaluation_issues': result['report']['issues'],
        'status': result['report']['status'], 'review_complete': result['report']['review_complete'],
        'source_refs': sum(len(j['source_spans'])
            for group in ('claim_judgments', 'unit_judgments') for j in judgments[group])})
x.save('mechanical-results.json', {'fixed_inputs_equal': True, 'runtime_pins_equal': True,
    'pairs': pairs, 'generation': generation, 'requests': requests, 'comparisons': comparisons})
x.replay()
print('Verified frozen inputs, actual requests, pair differences and evidence')
