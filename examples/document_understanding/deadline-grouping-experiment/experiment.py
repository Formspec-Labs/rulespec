"""Eight paired calls: change only the inventory meaning-field description."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import rulespec_extrapolator

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'audit-grounding-experiment'


def verify_manifest(directory):
    data = json.loads((directory / 'manifest.json').read_text())
    for name, digest in data['artifacts_sha256'].items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == digest, name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    design = json.loads((ROOT / 'design.json').read_text())
    assert hashlib.sha256((BASE / 'manifest.json').read_bytes()).hexdigest() == design['base_manifest_sha256']
    verify_manifest(BASE)
    # Use preserved prototype code in this process; production is unchanged.
    rulespec_extrapolator.__path__ = [str(BASE / 'frozen/application')]
    from rulespec_extrapolator import audit as a, extraction as e
    from langextract.providers.schemas.gemini import GeminiSchema
    for name, digest in design['inputs_sha256'].items():
        assert e._digest(e._contained(ROOT, name).read_bytes()) == digest, name
    assert {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    key = e._credential(args.env_file) if args.mode == 'run' else None

    def cell(name):
        case, repeat, arm = name.split('/')
        fixture = e._load(ROOT / 'fixtures' / (case + '.json'))
        doc, window = fixture['document'], fixture['window']
        schema = e._load(ROOT / (arm + '-schema.json'))
        prompt = e._window_prompt(e._prompt_generator([], a.INVENTORY_PROMPT), doc, window)
        directory = ROOT / 'runs' / case / repeat / arm
        if args.mode == 'run':
            attempts = a._capture(directory, doc, [window], [prompt], schema, e.DEFAULT_MODEL,
                                  key, None, max_output_tokens=None, thinking_level='medium')
            e._save(directory / 'attempts.json', attempts)
        else:
            verify_manifest(directory)
            attempts = e._load(directory / 'attempts.json')
        assert len(attempts) == 1 and attempts[0] == e._load(directory / 'attempt-0000.json')
        expected = {'model': e.DEFAULT_MODEL, 'contents': prompt, 'config': {
            'temperature': 0, 'candidate_count': 1, 'thinking_config': {'thinking_level': 'medium'},
            **GeminiSchema(schema, _use_json_schema=True).to_provider_config()}}
        if attempts[0].get('request_file'):
            assert e._load(directory / attempts[0]['request_file']) == expected
        result = a._inventory(directory, doc, [window], attempts)
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

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(cell, design['cells']))
    if args.mode == 'run':
        e._save(ROOT / 'results.json', results)
    else:
        assert results == e._load(ROOT / 'results.json')
        print('Eight identical inventory replays; no provider calls.', flush=True)


if __name__ == '__main__':
    main()
