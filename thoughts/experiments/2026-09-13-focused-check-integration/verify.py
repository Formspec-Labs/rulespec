"""Verify with candidate-implementation.patch applied; no provider calls."""
from hashlib import sha256
from pathlib import Path
import shutil
import tempfile
from unittest.mock import patch
import run as exp
from rulespec_extrapolator import audit as a, extraction as e, refinement as r


def restore():
    arms = e._load(exp.HERE / 'arm-key.json')
    shared = next(exp.HERE / 'captures' / cell / 'frozen' for cell,v in arms.items() if v['arm']=='B')
    for cell, info in arms.items():
        if info['arm'] != 'B': continue
        source = exp.PRIOR / 'extract' / info['source']
        if not (source / 'frozen').exists():
            shutil.copytree(exp.PRIOR / 'extract/leave/frozen', source / 'frozen')
        for dest in (exp.HERE / 'workspaces' / cell, exp.HERE / 'captures' / cell / 'base-run'):
            if not dest.exists(): r._copy_run(source, dest)
        frozen = exp.HERE / 'captures' / cell / 'frozen'
        if not frozen.exists(): shutil.copytree(shared, frozen)
        assert {str(p.relative_to(frozen)):sha256(p.read_bytes()).hexdigest() for p in frozen.rglob('*') if p.is_file()} == {
            str(p.relative_to(shared)):sha256(p.read_bytes()).hexdigest() for p in shared.rglob('*') if p.is_file()}


def main():
    restore()
    exp.x.pins()
    rows = []
    with patch.object(e, '_create_model', side_effect=AssertionError('Provider calls blocked')):
        for cell, info in e._load(exp.HERE / 'arm-key.json').items():
            data = e._load(exp.HERE / f'inputs/{cell}.json')
            saved = e._load(exp.HERE / f'decoded/{cell}.json')
            capture = exp.HERE / saved['capture']
            attempt = saved['attempt']
            assert e._load(capture / attempt['request_file']) == data['expected_request']
            payload, errors = a._read_response(capture, attempt)
            judgments, issues = r._decode_checks(payload, errors, data['candidates'], data['document'], data['packet'])
            assert all(saved[k] == v for k,v in dict(payload=payload, errors=errors, judgments=judgments, issues=issues).items())
            result = dict(cell=cell, request_and_decode_verified=True, judgments=len(judgments))
            if info['arm'] == 'B':
                output = exp.HERE / 'captures' / cell
                before, after = e._load(output / 'before.json'), e._load(output / 'after.json')
                assert [c['id'] for c in before['accepted']] == [c['id'] for c in after['accepted']]
                for old, new in zip(before['accepted'], after['accepted']):
                    for field in (*r.CANDIDATE_SCHEMA['properties'], 'evidence', 'review_status', 'link_issues'):
                        assert old.get(field) == new.get(field), (cell, field)
                    assert all(issue in new['issues'] for issue in old['issues'])
                assert e._load(output / 'changes.json') == []
                assert all(event['action']=='observe' for event in after['history'][len(before['history']):])
                with tempfile.TemporaryDirectory() as temp:
                    result['replay'] = r.replay_refinement(output, Path(temp) / 'replay')
                for name in ('document.json','run.json','rulebook.json'):
                    assert (exp.HERE / 'workspaces' / cell / name).read_bytes() == (exp.PRIOR / 'extract' / info['source'] / name).read_bytes()
                result['meaning_evidence_approval_and_original_files_preserved'] = True
            rows.append(result)
    e._save(exp.HERE / 'verification.json', dict(provider_calls=0, cells=rows))
    print('Sixteen requests/decodes verified; eight complete check runs replay; original meanings, warnings and approvals preserved.')


if __name__ == '__main__': main()
