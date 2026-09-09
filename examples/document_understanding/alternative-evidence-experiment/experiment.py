"""Six isolated audit comparisons; replay checks saved requests and raw judgments."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from jsonschema import Draft202012Validator
from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent


def prompt(arm, fixture):
    generator = e._prompt_generator([], (ROOT / (arm + '-prompt.txt')).read_text())
    return e._window_prompt(generator, fixture['document'], fixture['window']) + '\nDraft and inventory: ' + e._canonical(fixture['model_input'])


def assess(directory, fixture, attempt):
    payload, issues = a._read_response(directory, attempt)
    errors = list(Draft202012Validator(a.COMPARISON_SCHEMA).iter_errors(payload))
    if errors:
        issues.append('invalid_comparison_schema')
    if not issues:
        claims, units = payload['claim_judgments'], payload['unit_judgments']
        if (len(claims) != 1 or len(units) != 1 or claims[0]['claim_id'] != 'C0006'
                or claims[0]['unit_ids'] != ['U0006'] or units[0]['unit_id'] != 'U0006'
                or units[0]['claim_ids'] != ['C0006']):
            issues.append('unexpected_ids_or_links')
        for row in claims + units:
            try:
                if not row['quotes']:
                    raise ValueError()
                for quote in row['quotes']:
                    a._span(fixture['document'], quote, fixture['window'])
            except ValueError:
                issues.append('invalid_source_evidence')
    observed = None
    if not issues:
        dimensions = payload['claim_judgments'][0]['dimensions']
        coverage = payload['unit_judgments'][0]['status']
        observed = (dimensions['alternatives'] == 'correct' and coverage == 'covered'
                    and not any(v in ('error', 'unknown') for v in dimensions.values())) if fixture['expected'] == 'complete' else (
                    dimensions['alternatives'] == 'error' and coverage == 'partial')
    raw = e._load(directory / attempt['response_file']) if attempt.get('response_file') else {}
    return {'criterion_met': observed, 'issues': issues, 'judgments': payload,
            'usage': raw.get('usage_metadata'),
            'finish_reason': raw.get('candidates', [{}])[0].get('finish_reason')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    design = e._load(ROOT / 'design.json')
    for name, digest in design['inputs_sha256'].items():
        assert e._digest(e._contained(ROOT, name).read_bytes()) == digest, name
    assert {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    key = e._credential(args.env_file) if args.mode == 'run' else None

    def cell(name):
        arm, case = name.split('/', 1)
        fixture = e._load(ROOT / 'fixtures' / (case + '.json'))
        directory = ROOT / 'runs' / arm / case
        if args.mode == 'run':
            attempts = a._capture(directory, fixture['document'], [fixture['window']], [prompt(arm, fixture)],
                                  a.COMPARISON_SCHEMA, design['model'], key, None,
                                  max_output_tokens=None, thinking_level='high')
            e._save(directory / 'attempts.json', attempts)
        else:
            manifest = e._load(directory / 'manifest.json')['artifacts_sha256']
            assert {'attempts.json', 'result.json', 'attempt-0000.json', 'attempt-0000.request.json', 'attempt-0000.response.json'} <= manifest.keys()
            for path, digest in manifest.items():
                assert e._digest(e._contained(directory, path).read_bytes()) == digest, path
            attempts = e._load(directory / 'attempts.json')
        assert len(attempts) == 1 and attempts[0] == e._load(directory / 'attempt-0000.json')
        request = e._load(directory / attempts[0]['request_file'])
        assert request['contents'] == prompt(arm, fixture)
        result = assess(directory, fixture, attempts[0])
        if args.mode == 'run':
            e._save(directory / 'result.json', result)
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'result.json')
        print(e._canonical({'cell': name, 'mode': args.mode, 'criterion_met': result['criterion_met'],
                           'issues': result['issues'], 'finish_reason': result['finish_reason'], 'usage': result['usage']}), flush=True)
        return {'cell': name, **result}

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(cell, design['cells']))
    if args.mode == 'run':
        e._save(ROOT / 'results.json', results)
    else:
        assert results == e._load(ROOT / 'results.json')
        print('All six captures replay identically; no provider calls.', flush=True)


if __name__ == '__main__':
    main()
