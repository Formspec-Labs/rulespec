"""Paired inventory grounding experiment; no extraction or repair calls."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
from pathlib import Path
from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    design = e._load(ROOT / 'design.json')
    for name, digest in design['inputs_sha256'].items():
        assert e._digest(e._contained(ROOT, name).read_bytes()) == digest, name
    assert {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    spec = importlib.util.spec_from_file_location('rulespec_extrapolator._inventory_control', ROOT / 'control-audit.py')
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    key = e._credential(args.env_file) if args.mode == 'run' else None

    def cell(name):
        arm, case = name.split('/')
        module = control if arm == 'control' else a
        fixture = e._load(ROOT / 'fixtures' / (case + '.json'))
        doc, window = fixture['document'], fixture['window']
        prompt = e._window_prompt(e._prompt_generator([], module.INVENTORY_PROMPT), doc, window)
        directory = ROOT / 'runs' / arm / case
        if args.mode == 'run':
            attempts = a._capture(directory, doc, [window], [prompt], module.INVENTORY_SCHEMA,
                                  e.DEFAULT_MODEL, key, None, max_output_tokens=None, thinking_level='medium')
            e._save(directory / 'attempts.json', attempts)
        else:
            artifacts = e._load(directory / 'manifest.json')['artifacts_sha256']
            assert {'attempts.json', 'inventory.json', 'attempt-0000.json', 'attempt-0000.request.json', 'attempt-0000.response.json'} <= artifacts.keys()
            for path, digest in artifacts.items():
                assert e._digest(e._contained(directory, path).read_bytes()) == digest, path
            attempts = e._load(directory / 'attempts.json')
        assert len(attempts) == 1 and attempts[0] == e._load(directory / 'attempt-0000.json')
        from langextract.providers.schemas.gemini import GeminiSchema
        expected = {'model': e.DEFAULT_MODEL, 'contents': prompt, 'config': {
            'temperature': 0, 'candidate_count': 1, 'thinking_config': {'thinking_level': 'medium'},
            **GeminiSchema(module.INVENTORY_SCHEMA, _use_json_schema=True).to_provider_config()}}
        if attempts[0].get('request_file'):
            assert e._load(directory / attempts[0]['request_file']) == expected
        result = module._inventory(directory, doc, [window], attempts)
        if args.mode == 'run':
            e._save(directory / 'inventory.json', result)
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'inventory.json')
        raw = e._load(directory / attempts[0]['response_file']) if attempts[0].get('response_file') else {}
        row = {'cell': name, 'accepted': len(result['units']), 'issues': result['issues'],
               'finish_reason': raw.get('candidates', [{}])[0].get('finish_reason'), 'usage': raw.get('usage_metadata')}
        print(e._canonical(row), flush=True)
        return row

    with ThreadPoolExecutor(max_workers=3) as pool:
        results = list(pool.map(cell, design['cells']))
    if args.mode == 'run':
        e._save(ROOT / 'results.json', results)
    else:
        assert results == e._load(ROOT / 'results.json')
        print('Six identical inventory replays; no provider calls.', flush=True)


if __name__ == '__main__':
    main()
