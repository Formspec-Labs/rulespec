"""Verify native captures and checker requests without making provider calls."""
from hashlib import sha256
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch
import run as exp
from rulespec_extrapolator import audit as a, extraction as e, refinement as r


def restore_frozen(directory):
    if not (directory / 'frozen').exists():
        shutil.copytree(exp.HERE / 'extract/leave/frozen', directory / 'frozen')


def main():
    exp.x.pins()
    exp.x.pins('check-pins.json')
    report = dict(extractions=[], checks=[])
    with patch.object(e, '_create_model', side_effect=AssertionError('Provider calls blocked')):
        with tempfile.TemporaryDirectory() as temp:
            for name in exp.x.NAMES:
                directory = exp.HERE / 'extract' / name
                restore_frozen(directory)
                book = e._load(directory / 'rulebook.json')
                assert e.replay_run(directory, Path(temp) / name) == book
                request = e._load(directory / 'attempt-0000.request.json')
                assert not {'temperature', 'top_p', 'top_k', 'candidate_count'} & request['config'].keys()
                assert request['config']['thinking_config'] == dict(thinking_level='low')
                report['extractions'].append(dict(name=name, status=book['run']['status'], claims=len(book['accepted']), replayed=True))
        for cell in e._load(exp.HERE / 'cells.json'):
            data = e._load(exp.HERE / f'inputs/{cell}.json')
            directory = exp.HERE / 'captures' / cell
            attempt = e._load(directory / 'attempt.json')
            expected = dict(model=e.DEFAULT_MODEL, contents=data['prompt'], config=dict(max_output_tokens=32768,
                response_mime_type='application/json', response_json_schema=r.CHECK_SCHEMA,
                thinking_config=dict(thinking_level='medium')))
            assert e._load(directory / attempt['request_file']) == expected
            payload, errors = a._read_response(directory, attempt)
            judgments, issues = r._decode_checks(payload, errors, data['candidates'], data['document'], data['packet'])
            assert dict(payload=payload, errors=errors, judgments=judgments, issues=issues) == e._load(exp.HERE / f'decoded/{cell}.json')
            report['checks'].append(dict(cell=cell, judgments=len(judgments), issues=issues, redecoded=True))
        # Seven identical native runtime copies may be reconstructed after checkout.
        shared = exp.HERE / 'extract/leave/frozen'
        shared_hashes = {str(p.relative_to(shared)): sha256(p.read_bytes()).hexdigest() for p in shared.rglob('*') if p.is_file()}
        for name in exp.x.NAMES[1:]:
            directory = exp.HERE / 'extract' / name / 'frozen'
            assert {str(p.relative_to(directory)): sha256(p.read_bytes()).hexdigest() for p in directory.rglob('*') if p.is_file()} == shared_hashes
        with tempfile.TemporaryDirectory() as temp:
            sparse = Path(temp) / 'sparse'
            shutil.copytree(exp.HERE / 'extract/hazard', sparse, ignore=shutil.ignore_patterns('frozen'))
            restore_frozen(sparse)
            assert e.replay_run(sparse, Path(temp) / 'replayed') == e._load(exp.HERE / 'extract/hazard/rulebook.json')
        report['shared_runtime_reconstruction_verified'] = True
    e._save(exp.HERE / 'shared-runtime.json', dict(retained='extract/leave/frozen', files=shared_hashes,
        duplicates=[f'extract/{name}/frozen' for name in exp.x.NAMES[1:]],
        restore='verify.py restores missing identical trees; each original capture manifest checks the restored bytes.'))
    report['usage'] = exp.x.usage()
    report['provider_seconds'] = sum(c['seconds'] for c in e._load(exp.HERE / 'calls.json'))
    e._save(exp.HERE / 'verification.json', report)
    print('Eight native captures and all checker requests/responses verified with provider access blocked.')


if __name__ == '__main__': main()
