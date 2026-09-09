"""Replay the saved clarified-description cases with medium thinking only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import importlib.util
from pathlib import Path
from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'alternative-evidence-experiment'


def verify_manifest(directory):
    manifest = e._load(directory / 'manifest.json')
    assert manifest['version'] == 1
    for name, digest in manifest['artifacts_sha256'].items():
        assert e._digest(e._contained(directory, name).read_bytes()) == digest, name
    return manifest['artifacts_sha256']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    design = e._load(ROOT / 'design.json')
    for name, digest in design['inputs_sha256'].items():
        assert e._digest(e._contained(ROOT.parent, name).read_bytes()) == digest, name
    verify_manifest(BASE)
    assert {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    spec = importlib.util.spec_from_file_location('saved_alternatives_experiment', BASE / 'experiment.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    key = e._credential(args.env_file) if args.mode == 'run' else None

    def cell(case):
        fixture = e._load(BASE / 'fixtures' / (case + '.json'))
        high = BASE / 'runs/treatment' / case
        expected = deepcopy(e._load(high / 'attempt-0000.request.json'))
        expected['config']['thinking_config'] = {'thinking_level': 'medium'}
        directory = ROOT / 'runs' / case
        if args.mode == 'run':
            attempts = a._capture(directory, fixture['document'], [fixture['window']], [expected['contents']],
                                  a.COMPARISON_SCHEMA, design['model'], key, None,
                                  max_output_tokens=None, thinking_level='medium')
            e._save(directory / 'attempts.json', attempts)
        else:
            artifacts = verify_manifest(directory)
            assert {'attempts.json', 'result.json', 'attempt-0000.json', 'attempt-0000.request.json', 'attempt-0000.response.json'} <= artifacts.keys()
            attempts = e._load(directory / 'attempts.json')
        assert len(attempts) == 1 and attempts[0] == e._load(directory / 'attempt-0000.json')
        if attempts[0].get('request_file'):
            assert e._load(directory / attempts[0]['request_file']) == expected
        result = helper.assess(directory, fixture, attempts[0])
        if args.mode == 'run':
            e._save(directory / 'result.json', result)
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'result.json')
        print(e._canonical({'case': case, 'mode': args.mode, 'criterion_met': result['criterion_met'],
                           'issues': result['issues'], 'finish_reason': result['finish_reason'], 'usage': result['usage']}), flush=True)
        return {'case': case, 'high': e._load(high / 'result.json'), 'medium': result}

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(cell, design['cases']))
    if args.mode == 'run':
        e._save(ROOT / 'results.json', results)
    else:
        assert results == e._load(ROOT / 'results.json')
        print('All three captures replay identically; no provider calls.', flush=True)


if __name__ == '__main__':
    main()
