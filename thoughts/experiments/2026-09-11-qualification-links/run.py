"""One existing relationship pass; paired checking with/without target aliases."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch

from rulespec_extrapolator import audit as a, extraction as e, refinement as r

ROOT = Path(__file__).resolve().parent
PRIOR = ROOT.parent / '2026-09-11-expanded-inventory'
spec = importlib.util.spec_from_file_location('expanded_inventory', PRIOR / 'run.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
MODEL, CONFIG = prior.MODEL, prior.CONFIG
GUIDANCE = '''
Additional proposed qualifications are fallible, unapproved observations. They
have NOT been applied to the draft. Assess every ORIGINAL C claim and U inventory
unit using the supplied source. Do not assume a proposed qualification repairs
the original claim's wording. Its relation names the proposed effect; qualifies,
when supplied, names proposed affected C aliases, not established correct targets.
Validate any relevant effect and target against source before relying on it.
An omitted qualifies field leaves its targets unspecified. Neither an absent
target list nor an extra proposal establishes a defect by itself.
'''


def save(name, value):
    e._save(ROOT / name, value)


def pins(paths):
    return {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths}


def prepare():
    assert not (ROOT / 'cases.json').exists()
    cases = e._load(PRIOR / 'cases.json')
    for case in cases:
        case['labels'] = e._load(PRIOR / 'inventory' / (case['id'] + '-B') / 'labels.json')
        assert not e._load(PRIOR / 'inventory' / (case['id'] + '-B') / 'inventory.json')['issues']
        case['origin'] = 'frozen development source, original extraction, saved expanded inventory'
    save('cases.json', cases)
    (ROOT / 'PRELABELS.md').write_text((PRIOR / 'PRELABELS.md').read_text() + '''

## Qualification-link experiment additions, before new calls

All cases above are now development data. Existing labels are retained, including
uncertainty; "new" above describes their original selection only.

Generation expectations: equipment (e) exception must target C0000 and preserve
the special-flight-permit limits. Flight (i)(2) and (i)(3) prerequisites must target
C0010; a grouped companion is acceptable if it retains both and the landings
exception. PPE (g) must target C0003-C0006/C0008/C0010-C0013 and preserve the exact
included/excluded sections. Payment precedence should target C0015, without
inventing another standard's content. Other targets require their own source
assessment; similarity or a correct primary target does not validate all targets.

Do not treat every equipment maintenance link as automatically false: (e)'s broad
notwithstanding language requires careful source assessment. Record uncertainty
if the supplied section cannot establish a target's exact effect. Do not count
mere presence of a qualifier elsewhere as fixing the baseline's standalone scope.
''')
    save('schemas.json', {'relationships': r.proposal_schema('relationships'),
                          'comparison': prior.previous.SCHEMA})
    (ROOT / 'relationship-prompt.txt').write_text(r.RELATIONSHIPS)
    (ROOT / 'comparison-prompt.txt').write_text(a.comparison_prompt() + prior.previous.GUIDANCE + GUIDANCE)
    sources = {**e._runtime_sources(), 'application/refinement.py': Path(r.__file__),
               'experiment/expanded.py': PRIOR / 'run.py',
               'experiment/comparison.py': prior.PRIOR / 'run.py'}
    for name, source in sources.items():
        dest = ROOT / 'runtime' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())
    save('runtime-sha256.json', {name: sha256(path.read_bytes()).hexdigest() for name, path in sources.items()})
    save('runtime-versions.json', e._runtime_versions())
    save('precall-pins.json', pins([ROOT / name for name in ('PLAN.md', 'PRELABELS.md', 'run.py',
        'cases.json', 'schemas.json', 'relationship-prompt.txt', 'comparison-prompt.txt', 'runtime-sha256.json')]))
    print('Frozen three development cases; no provider calls', flush=True)


def capture(name, case, prompt, schema, key):
    calls = e._load(ROOT / 'calls.json') if (ROOT / 'calls.json').exists() else []
    usage = e.recorded_usage(ROOT)
    if len(calls) >= 9 or sum(c['seconds'] for c in calls) >= 1800 or usage['tokens'].get('total_token_count', 0) >= 300000:
        save('stopped.json', {'next_call': name, 'reason': 'bound_reached'})
        raise SystemExit('Experiment bound reached')
    save('inputs/' + name + '.json', {'prompt': prompt, 'schema': schema, 'model': MODEL, 'config': CONFIG})
    print('Capture', name, flush=True)
    started = time.monotonic()
    try:
        attempts = a._capture(ROOT / name, case['book']['document'], [case['window']], [prompt],
                              schema, MODEL, key, None, **CONFIG)
        save(name + '/attempts.json', attempts)
        payload, errors = a._read_response(ROOT / name, attempts[0])
        save(name + '/raw-decoded.json', {'payload': payload, 'errors': errors})
        return payload, errors
    finally:
        calls.append({'name': name, 'seconds': time.monotonic() - started})
        save('calls.json', calls)


def proposals(case, payload, errors, packet):
    with patch.object(a, '_source_span', prior.source_span):
        prepared, issues = r._decode_proposals(payload, errors, case['book']['document'],
                                              case['window'], packet, 'relationships')
    return {'prepared': prepared, 'issues': issues}


def observations(prepared, linked):
    result = []
    for p in prepared:
        fields = deepcopy(p['fields'])
        fields.pop('applies_to')
        row = {'id': p['id'], 'operation': p['proposal']['operation'],
               'target': p['proposal']['target'], 'fields': fields}
        if linked:
            row['qualifies'] = p['proposal']['qualifies']
        result.append(row)
    return result


def run():
    assert not (ROOT / 'calls.json').exists(), 'No retries or overwritten observations'
    expected = e._load(ROOT / 'precall-pins.json')
    assert expected == pins([ROOT / name for name in expected])
    key = e._credential(prior.ENV)
    cells = []
    for index, case in enumerate(e._load(ROOT / 'cases.json')):
        packet = r._packet(case['book'], {'book': case['book'], 'labels': case['labels']}, case['window'])
        assert packet['omitted_claim_count'] == 0
        name = 'relationships/' + case['id']
        save(name + '-packet.json', packet)
        payload, errors = capture(name, case, r._proposal_prompt(r.RELATIONSHIPS, packet), r.proposal_schema('relationships'), key)
        decoded = proposals(case, payload, errors, packet)
        save(name + '/proposals.json', decoded)
        if errors or any(x['code'] == 'invalid_proposal_schema' for x in decoded['issues']):
            cells.append({'case': case['id'], 'status': 'skipped_proposal_failure'})
            save('cells.json', cells)
            continue
        draft = a._model_input(a._comparison_input(case['book'], case['labels'], case['window'])[0])
        for arm in (('A', 'B') if index % 2 == 0 else ('B', 'A')):
            cell = case['id'] + '-' + arm
            advisory = observations(decoded['prepared'], arm == 'B')
            prompt = ((ROOT / 'comparison-prompt.txt').read_text()
                + '\nFocus positions: ' + e._canonical({k: case['window'][k] for k in ('start', 'end')})
                + '\nSource material: ' + e._canonical(case['materials']['B'])
                + '\nDraft and inventory: ' + e._canonical(draft)
                + '\nAdditional proposed qualifications: ' + e._canonical(advisory))
            name = 'comparison/' + cell
            save('advisory/' + cell + '.json', advisory)
            capture(name, case, prompt, prior.previous.SCHEMA, key)
            assessment = prior.decode(case, ROOT / name, case['labels'])
            save(name + '/assessment.json', assessment)
            save(name + '/source-evidence.json', prior.evidence_receipt(case['book']['document'], assessment['judgments']))
            cells.append({'case': case['id'], 'arm': arm, 'name': cell, 'status': 'captured'})
            save('cells.json', cells)
    shuffled = [c for c in cells if c['status'] == 'captured']
    random.SystemRandom().shuffle(shuffled)
    mapping = {}
    for index, cell in enumerate(shuffled):
        anonymous = f'review-{index:02d}'
        raw = e._load(ROOT / 'comparison' / cell['name'] / 'raw-decoded.json')
        save('blind/' + anonymous + '.json', {'case': cell['case'], **raw})
        mapping[anonymous] = cell
    save('arm-key.json', mapping)
    save('usage.json', {stage: e.recorded_usage(ROOT / stage) for stage in ('relationships', 'comparison')})
    print('Ready for anonymous comparison review before reading proposals or arm key', flush=True)


def replay():
    checked = []
    cases = {c['id']: c for c in e._load(ROOT / 'cases.json')}
    for name, case in cases.items():
        raw = e._load(ROOT / 'relationships' / name / 'raw-decoded.json')
        packet = e._load(ROOT / 'relationships' / (name + '-packet.json'))
        assert proposals(case, raw['payload'], raw['errors'], packet) == e._load(ROOT / 'relationships' / name / 'proposals.json')
        checked.append('relationships/' + name)
    for cell in e._load(ROOT / 'cells.json'):
        if cell['status'] != 'captured':
            continue
        case = cases[cell['case']]
        directory = ROOT / 'comparison' / cell['name']
        assert prior.decode(case, directory, case['labels']) == e._load(directory / 'assessment.json')
        checked.append('comparison/' + cell['name'])
    save('replay.json', {'equal': True, 'provider_calls': 0, 'cells': checked})
    print('Identical saved-data replay:', len(checked), 'cells', flush=True)


if __name__ == '__main__':
    {'prepare': prepare, 'run': run, 'replay': replay}[sys.argv[1]]()
