"""Offline replay, history, legacy compatibility, wheel and preservation checks.

Historical experiment replays use their hash-verified application snapshots.
These are our local captures; never execute an untrusted frozen application.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.core import validate_graph
from rulespec_extrapolator.review_store import ReviewStore

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def stage_runtime(directory, target, pins):
    stage = target / 'runtimes' / e._digest(pins)[:16]
    package = stage / 'rulespec_extrapolator'
    package.mkdir(parents=True, exist_ok=True)
    (package / '__init__.py').write_text('"""Verified local experiment snapshot."""\n')
    for name, sha in pins.items():
        frozen = directory / 'frozen' / name
        assert e._digest(frozen.read_bytes()) == sha
        if name.startswith('application/'):
            shutil.copyfile(frozen, package / Path(name).name)
        elif name.startswith('data/'):
            dest = package / '_data' / name.removeprefix('data/')
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(frozen, dest)
    return stage


def replay_frozen(directory, target, mode):
    run = e._load(directory / ('refinement.json' if mode == 'refinement' else 'audit.json'))
    stage = stage_runtime(directory, target, run['sources_sha256'])
    relative = directory.relative_to(ROOT).as_posix()
    output = target / 'replays' / relative.replace('/', '__')
    code = '''import json, sys
from pathlib import Path
from rulespec_extrapolator import extraction as e, audit as a, refinement as r
e._create_model = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('No provider allowed'))
fn = r.replay_refinement if sys.argv[1] == 'refinement' else a.replay_audit
report = fn(Path(sys.argv[2]), Path(sys.argv[3]))
print(json.dumps({'status': report['status']}))
'''
    completed = subprocess.run([sys.executable, '-c', code, mode, str(directory), str(output)],
        cwd=stage, env={**os.environ, 'PYTHONPATH': str(stage)}, capture_output=True, text=True)
    if completed.returncode:
        raise RuntimeError(relative + ': ' + completed.stderr[-3000:])
    return {'capture': relative, 'mode': mode, 'receipt': e._load(output / 'replay.json'),
            'assessment_status': json.loads(completed.stdout)['status'],
            'runtime': 'original_verified_frozen_application'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=REPO / '.tools/refinement-verification-complete')
    target = parser.parse_args().output.resolve()
    target.mkdir(exist_ok=False)
    e._create_model = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('No provider allowed'))
    legacy = REPO / 'examples/document_understanding/manual-slice'
    extractions = []
    for name in ['development-01', 'holdout-01', 'holdout-02', 'section-01', 'section-02']:
        processed = target / 'legacy' / name
        book = e.reprocess_run(legacy / 'runs' / name, processed)
        assert e.replay_run(processed, processed.with_name(name + '-replay')) == book
        assert all('modality' not in c for c in book['accepted'])
        extractions.append({'capture': 'legacy/' + name, 'accepted': len(book['accepted']),
                            'reprocessed_and_strict_replayed': True, 'invented_v2_meaning': False})

    workspace = target / 'review-history'
    e.replay_run(target / 'legacy/section-01', workspace)
    store = ReviewStore(workspace)
    before = store.snapshot()
    for index, path in enumerate(sorted((legacy / 'review-demo/actions').glob('*.json'))):
        result = store.apply(e._load(path))
        assert result['revision'] == index + 1
    after = store.snapshot()
    assert ReviewStore(workspace).snapshot() == after
    current = {c['id'] for c in after['accepted']}
    assert all(t in current for c in after['accepted'] for t in c['target_ids'])
    nodes = {n['@id']: n for n in after['graph']['@graph']}
    assert all(nodes[n['@id']] == n for n in before['graph']['@graph'])
    validate_graph(after['graph'])
    e._save(ROOT / 'history-verification.json', {
        'case_id': 'NREG-15', 'status': 'verified', 'actions': len(after['history']),
        'reopened_identically': True, 'original_graph_nodes_preserved': True,
        'current_targets_resolve': True, 'actor_kind': 'aiAgent',
        'source_actions': str(legacy / 'review-demo/actions'), 'workspace': str(workspace),
        'semantic_completeness': 'not_established'})

    for name in ['names', 'photos', 'names-excerpts', 'slopes', 'authorizations', 'marketing']:
        source = ROOT / 'runs-02' / name / 'base-run'
        processed = target / 'extractions' / name
        book = e.reprocess_run(source, processed)
        assert e.replay_run(processed, processed.with_name(name + '-replay')) == book
        original_book = e._load(source / 'rulebook.json')
        assert all(book[k] == original_book[k] for k in ('document', 'accepted', 'rejected', 'unresolved'))
        extractions.append({'capture': 'runs-02/' + name + '/base-run',
                            'accepted': len(book['accepted']), 'reprocessed_and_strict_replayed': True})

    captures = sorted(ROOT.glob('runs-*/**/refinement.json')) + sorted(ROOT.glob('controls/*/refinement.json'))
    captures += [ROOT / name / 'refinement.json' for name in ['slice-01', 'slice-02']]
    replays = []
    for path in captures:
        replays.append(replay_frozen(path.parent, target, 'refinement'))
        for audit in ['initial-audit', 'final-audit']:
            if (path.parent / audit / 'audit.json').exists():
                replays.append(replay_frozen(path.parent / audit, target, 'audit'))
        print(json.dumps({'verified': path.parent.relative_to(ROOT).as_posix()}), flush=True)

    wheel = next((REPO / '.tools/refinement-wheels').glob('*.whl'))
    wheel_root = target / 'wheel'
    wheel_root.mkdir()
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(wheel_root)
    code = '''import json, sys
from pathlib import Path
from rulespec_extrapolator import core, extraction as e, refinement as r
from rulespec_extrapolator.documents import prepare_document
assert Path(core.__file__).is_relative_to(Path(sys.argv[1]))
assert core.data_root().is_relative_to(Path(sys.argv[1]))
text = 'Visitors must present a receipt.'
book = core.compile_candidates(prepare_document(text), [{'kind': 'requirement', 'actor': 'Visitors', 'actor_quote': 'Visitors', 'summary': text, 'quote': text, 'modality': 'must', 'modality_quote': 'must'}], {})
assert len(book['accepted']) == 1 and not book['rejected']
core.validate_graph(book['graph'])
assert 'application/refinement.py' in e._runtime_sources()
assert callable(r.refine_run) and callable(r.replay_refinement)
print(json.dumps({'status': 'verified', 'imported_built_wheel': True, 'packaged_core_data': True, 'compile_and_validate': True, 'refinement_imported': True}))
'''
    completed = subprocess.run([sys.executable, '-c', code, str(wheel_root)], cwd=wheel_root,
        env={**os.environ, 'PYTHONPATH': str(wheel_root)}, capture_output=True, text=True, check=True)
    protected = e._load(REPO / '.tools/refinement-iteration-baseline/protected-sha256.json')
    changed = [name for name, sha in protected.items() if e._digest((REPO / name).read_bytes()) != sha]
    assert not changed, changed
    result = {'created_at': e._now(), 'provider_calls': 0, 'extractions': extractions, 'replays': replays,
        'history': 'history-verification.json', 'wheel': {**json.loads(completed.stdout), 'sha256': e._digest(wheel.read_bytes())},
        'protected_original_files': len(protected), 'changed_original_files': changed,
        'runtime_sources_sha256': {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()}}
    e._save(ROOT / 'runtime-verification.json', result)
    print(json.dumps({'extractions': len(extractions), 'replays': len(replays),
                      'history_actions': len(after['history']), 'protected_files': len(protected), 'provider_calls': 0}))


if __name__ == '__main__':
    main()
