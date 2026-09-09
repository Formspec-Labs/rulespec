"""Two full-window source inventories; preserve current complete-meaning guidance."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
from pathlib import Path
import secrets
import rulespec_extrapolator

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'audit-grounding-experiment'
CAPTURE = ROOT.parent / 'low-extract-medium-audit'


def verify(directory):
    for name, expected in json.loads((directory / 'manifest.json').read_text())['artifacts_sha256'].items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == expected, name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    design = json.loads((ROOT / 'design.json').read_text())
    for name, directory in (('base', BASE), ('capture', CAPTURE)):
        assert hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest() == design[name + '_manifest_sha256']
        verify(directory)
    for name, expected in design['inputs_sha256'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    rulespec_extrapolator.__path__ = [str(BASE / 'frozen/application')]
    from rulespec_extrapolator import audit as a, extraction as e
    from langextract.providers.schemas.gemini import GeminiSchema
    spec = importlib.util.spec_from_file_location('rulespec_extrapolator._quote_comparison', BASE / 'control-audit.py')
    quote = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quote)
    assert {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    config = e._load(ROOT / 'configuration.json')
    fixture = e._load(ROOT / 'fixture.json')
    doc, window = fixture['document'], fixture['window']
    key = e._credential(args.env_file) if args.mode == 'run' else None

    def cell(arm):
        setting = config[arm]
        prompt = e._window_prompt(e._prompt_generator([], setting['prompt']), doc, window)
        if arm == 'quote':
            assert config['current_quote_request'] == {'model': e.DEFAULT_MODEL, 'contents': prompt}
            assert setting['schema'] == quote.INVENTORY_SCHEMA
        directory = ROOT / 'runs' / arm
        if args.mode == 'run':
            attempts = a._capture(directory, doc, [window], [prompt], setting['schema'], e.DEFAULT_MODEL,
                                  key, None, max_output_tokens=None, thinking_level='medium')
            e._save(directory / 'attempts.json', attempts)
        else:
            verify(directory)
            attempts = e._load(directory / 'attempts.json')
        assert len(attempts) == 1 and attempts[0] == e._load(directory / 'attempt-0000.json')
        expected = {'model': e.DEFAULT_MODEL, 'contents': prompt, 'config': {
            'temperature': 0, 'candidate_count': 1, 'thinking_config': {'thinking_level': 'medium'},
            **GeminiSchema(setting['schema'], _use_json_schema=True).to_provider_config()}}
        if attempts[0].get('request_file'):
            assert e._load(directory / attempts[0]['request_file']) == expected
        module = quote if arm == 'quote' else a
        inventory = module._inventory(directory, doc, [window], attempts)
        if args.mode == 'run':
            e._save(directory / 'inventory.json', inventory)
            e._write_manifest(directory)
        else:
            assert inventory == e._load(directory / 'inventory.json')
        payload, errors = module._read_response(directory, attempts[0])
        raw = e._load(directory / attempts[0]['response_file']) if attempts[0].get('response_file') else {}
        result = {'arm': arm, 'accepted': len(inventory['units']), 'issues': inventory['issues'],
                  'finish_reason': raw.get('candidates', [{}])[0].get('finish_reason'), 'usage': raw.get('usage_metadata')}
        review = {'parse_errors': errors, 'units': [{'raw_row': i, 'kind': u.get('kind'), 'meaning': u.get('meaning')}
                  for i, u in enumerate(payload.get('units', []))]}
        return result, review

    with ThreadPoolExecutor(max_workers=2) as pool:
        output = list(pool.map(cell, design['arms']))
    results = [x[0] for x in output]
    reviews = {x[0]['arm']: x[1] for x in output}
    if args.mode == 'run':
        e._save(ROOT / 'results.json', results)
        arms = list(design['arms'])
        secrets.SystemRandom().shuffle(arms)
        mapping = dict(zip(('A', 'B'), arms, strict=True))
        e._save(ROOT / 'review-key.json', mapping)
        e._save(ROOT / 'blind-review-input.json', {label: reviews[arm] for label, arm in mapping.items()})
    else:
        assert results == e._load(ROOT / 'results.json')
        mapping = e._load(ROOT / 'review-key.json')
        assert {label: reviews[arm] for label, arm in mapping.items()} == e._load(ROOT / 'blind-review-input.json')
    print('Two inventories saved.' if args.mode == 'run' else 'Two identical inventory replays; no provider calls.', flush=True)


if __name__ == '__main__':
    main()
