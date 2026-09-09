"""Bounded, separate inventory-guidance and coverage-order comparisons."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import secrets

from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent


def verify(directory):
    for name, digest in e._load(directory / 'manifest.json')['artifacts_sha256'].items():
        assert e._digest(e._contained(directory, name).read_bytes()) == digest, name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    design = e._load(ROOT / 'design.json')
    for name, digest in design['inputs_sha256'].items():
        assert e._digest(e._contained(ROOT, name).read_bytes()) == digest, name
    runtime = {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()}
    if args.mode == 'run':
        assert runtime == design['runtime_sources_sha256']
    else:
        verify(ROOT)
    config = e._load(ROOT / 'configuration.json')
    key = e._credential(args.env_file) if args.mode == 'run' else None

    def cell(spec):
        task, case, repeat, arm = spec
        fixture = e._load(ROOT / 'fixtures' / (case + '.json'))
        doc, window = fixture['document'], fixture['window']
        setting = config[task][arm]
        prompt = e._window_prompt(e._prompt_generator([], setting['prompt']), doc, window)
        if task == 'order':
            prompt += '\nDraft and inventory: ' + e._canonical(a._model_input(
                a._comparison_input(fixture['book'], fixture['labels'], window)[0]))
        directory = ROOT / 'runs' / task / case / str(repeat) / arm
        if args.mode == 'run':
            attempts = a._capture(directory, doc, [window], [prompt], setting['schema'],
                design['model'], key, None, max_output_tokens=None, thinking_level='medium')
            e._save(directory / 'attempts.json', attempts)
        else:
            verify(directory)
            attempts = e._load(directory / 'attempts.json')
        assert len(attempts) == 1 and attempts[0] == e._load(directory / 'attempt-0000.json')
        attempt = attempts[0]
        expected = {'model': design['model'], 'contents': prompt, 'config': {
            'temperature': 0, 'candidate_count': 1, 'thinking_config': {'thinking_level': 'medium'},
            **GeminiSchema(setting['schema'], _use_json_schema=True).to_provider_config()}}
        if attempt.get('request_file'):
            request = e._load(directory / attempt['request_file'])
            # Canonical equality ignores object order; this comparison deliberately cannot.
            assert request == expected
            if task == 'order':
                actual_schema = request['config']['response_json_schema']
                assert list(actual_schema['properties']['unit_judgments']['items']['properties']) == list(
                    setting['schema']['properties']['unit_judgments']['items']['properties'])
        payload, parse_issues = a._read_response(directory, attempt)
        if task == 'inventory':
            parsed = a._inventory(directory, doc, [window], attempts)
            result = {'inventory': parsed, 'parse_issues': parse_issues}
        else:
            judgments, issues = a._judgments(directory, fixture['book'], fixture['labels'],
                [window], attempts, design['model'])
            report = a._assessment(fixture['book'], fixture['labels'], judgments, issues)
            claims, units = judgments['claim_judgments'], judgments['unit_judgments']
            if len(claims) == len(units) == 1:
                dimensions, status = claims[0]['dimensions'], units[0]['status']
                passed = (dimensions['summary'] == dimensions['scope'] == 'correct' and status == 'covered'
                    if case == 'complete' else
                    dimensions['summary'] == 'error' and dimensions['scope'] == 'error' and status == 'partial')
                passed = passed and report['review_complete']
            else:
                passed = False
            result = {'judgments': judgments, 'report': report, 'parse_issues': parse_issues,
                      'criterion_met': passed, 'output_unit_field_order': [list(r) for r in payload.get('unit_judgments', [])]}
        raw = e._load(directory / attempt['response_file']) if attempt.get('response_file') else {}
        result.update(usage=raw.get('usage_metadata'),
                      finish_reason=raw.get('candidates', [{}])[0].get('finish_reason'))
        if args.mode == 'run':
            e._save(directory / 'result.json', result)
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'result.json')
        print('/'.join(map(str, spec)), 'recorded' if args.mode == 'run' else 'replayed', flush=True)
        return {'cell': spec, **result}

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(cell, design['cells']))
    if args.mode == 'run':
        e._save(ROOT / 'results.json', results)
        shuffled = list(range(len(results)))
        secrets.SystemRandom().shuffle(shuffled)
        mapping = {f'R{i:02d}': j for i, j in enumerate(shuffled)}
        e._save(ROOT / 'review-key.json', mapping)
        packet = {}
        for label, index in mapping.items():
            row = results[index]
            if row['cell'][0] == 'inventory':
                packet[label] = {'task': 'inventory', 'units': [
                    {'meaning': u['meaning'], 'kind': u['kind']} for u in row['inventory']['units']],
                    'issues': row['inventory']['issues']}
            else:
                packet[label] = {'task': 'order', 'case': row['cell'][1],
                    'claim_judgments': row['judgments']['claim_judgments'],
                    'unit_judgments': row['judgments']['unit_judgments'],
                    'criterion_met': row['criterion_met']}
        e._save(ROOT / 'blind-review-input.json', packet)
        e._write_manifest(ROOT)
    else:
        assert results == e._load(ROOT / 'results.json')
        print('Identical replay; no provider calls. Runtime drift:', runtime != design['runtime_sources_sha256'])


if __name__ == '__main__':
    main()
