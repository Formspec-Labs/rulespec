"""Bounded live check; replay retains exact requests and original raw responses."""
import argparse
from pathlib import Path
import random
import shutil
import tempfile
from unittest.mock import patch

from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import extraction as e, audit as a

ROOT = Path(__file__).resolve().parent
CELLS = [case + '/' + arm for case in ('passport', 'waste', 'notice') for arm in ('B', 'T')]
random.Random(20260909).shuffle(CELLS)


def prepare():
    assert not (ROOT / 'design.json').exists()
    baseline = e._load(ROOT / 'baseline.json')
    prompts = {}
    for case in ('passport', 'waste', 'notice'):
        fixture = e._load(ROOT / 'fixtures' / (case + '.json'))
        prompts[case + '/B'] = baseline['cases'][case]['prompt']
        assert baseline['cases'][case]['schema'] == a.COMPARISON_SCHEMA
        prompts[case + '/T'] = a._comparison_request(fixture['book'], fixture['labels'], fixture['window'])
    sources = e._runtime_sources()
    for name, path in sources.items():
        target = ROOT / 'frozen' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    e._save(ROOT / 'design.json', {'cells': CELLS, 'prompts': prompts, 'model': e.DEFAULT_MODEL,
        'temperature': 0, 'thinking_level': 'medium', 'max_output_tokens': None,
        'runtime_sha256': {name: e._digest(path.read_bytes()) for name, path in sources.items()},
        'fixtures_sha256': {str(p.relative_to(ROOT)): e._digest(p.read_bytes()) for p in (ROOT / 'fixtures').glob('*.json')},
        'comparison_schema': a.COMPARISON_SCHEMA, 'baseline_commit': '88f4da3', 'max_provider_calls': 8})


def execute(mode, env_file):
    if mode == 'replay':
        artifacts = e._load(ROOT / 'manifest.json')['artifacts_sha256']
        assert set(artifacts) == {str(p.relative_to(ROOT)) for p in ROOT.rglob('*')
                                 if p.is_file() and p != ROOT / 'manifest.json'}
        for name, digest in artifacts.items():
            assert e._digest((ROOT / name).read_bytes()) == digest
    design = e._load(ROOT / 'design.json')
    assert design['runtime_sha256'] == {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()}
    for name, digest in design['fixtures_sha256'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest
    key = e._credential(env_file) if mode == 'run' else None
    results = {}
    for case in ('passport', 'waste'):
        directory = ROOT / 'extraction' / case
        document = e._load(ROOT / 'fixtures' / (case + '.json'))['book']['document']
        if mode == 'run':
            book = e.extract_run(document, directory, env_file=env_file)
        else:
            with tempfile.TemporaryDirectory(prefix='rulespec-sparse-replay-') as tmp:
                with patch.object(e, '_create_model', side_effect=AssertionError('Replay called provider')):
                    book = e.replay_run(directory, Path(tmp) / 'run')
        print('extraction', case, book['run']['status'], len(book['accepted']), flush=True)
    for cell in design['cells']:
        case, arm = cell.split('/')
        fixture = e._load(ROOT / 'fixtures' / (case + '.json'))
        book, labels, window = (fixture[k] for k in ('book', 'labels', 'window'))
        prompt = design['prompts'][cell]
        if arm == 'T':
            assert prompt == a._comparison_request(book, labels, window)
        directory = ROOT / 'comparison' / case / arm
        if mode == 'run':
            attempts = a._capture(directory, book['document'], [window], [prompt], a.COMPARISON_SCHEMA,
                design['model'], key, None, max_output_tokens=None, thinking_level='medium')
            e._save(directory / 'attempts.json', attempts)
        else:
            artifacts = e._load(directory / 'manifest.json')['artifacts_sha256']
            assert set(artifacts) == {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file() and p.name != 'manifest.json'}
            for name, digest in artifacts.items():
                assert e._digest((directory / name).read_bytes()) == digest
            attempts = e._load(directory / 'attempts.json')
        attempt, = attempts
        if attempt.get('request_file'):
            assert e._load(directory / attempt['request_file']) == {'model': design['model'], 'contents': prompt,
                'config': {'temperature': 0, 'candidate_count': 1, 'thinking_config': {'thinking_level': 'medium'},
                **GeminiSchema(a.COMPARISON_SCHEMA, _use_json_schema=True).to_provider_config()}}
        judgments, issues = a._judgments(directory, book, labels, [window], attempts, design['model'])
        report = a._assessment(book, labels, judgments, issues)
        response = e._load(directory / attempt['response_file']) if attempt.get('response_file') else {}
        result = {'judgments': judgments, 'issues': issues, 'report': report, 'usage': response.get('usage_metadata')}
        if mode == 'run':
            e._save(directory / 'result.json', result)
            e._write_manifest(directory)
        else:
            assert result == e._load(directory / 'result.json')
        results[cell] = result
        print(cell, report['status'], len(issues), 'issues', result['usage'], flush=True)
    if mode == 'run':
        e._save(ROOT / 'results.json', results)
    else:
        assert results == e._load(ROOT / 'results.json')
        print('All eight captures replay identically; no provider calls.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['prepare', 'run', 'replay'])
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    prepare() if args.mode == 'prepare' else execute(args.mode, args.env_file)
