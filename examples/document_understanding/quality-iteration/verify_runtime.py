"""Verify new captures, frozen audit replay and the built wheel without a provider.

Replay uses each audit's hash-verified application snapshot because application
changes intentionally invalidate strict replay in a different runtime. These
snapshots were produced by this experiment; do not execute untrusted snapshots.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def main():
    target = REPO / '.tools/quality-v2-final'
    target.mkdir(exist_ok=False)
    e._create_model = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('No provider allowed'))
    extractions = []
    for name in ['names-05', 'photos-03', 'names-excerpts-03', 'names-t02', 'photos-t02', 'names-excerpts-t02', 'fresh-02']:
        source = ROOT / 'runs' / name
        processed = target / 'extraction' / name
        book = e.reprocess_run(source, processed)
        assert e.replay_run(processed, processed.with_name(name + '-replay')) == book
        old = e._load(source / 'run.json')
        new = e._load(processed / 'run.json')
        assert old['temperature'] == new['temperature']
        extractions.append({'run': name, 'temperature': new['temperature'], 'accepted': len(book['accepted']),
                            'reprocessed_and_strict_replayed': True, 'provider_calls': 0})
    audits = []
    sources = sorted((ROOT / 'audits').glob('*/audit.json'))
    sources += sorted((ROOT / 'negative-controls').glob('*/audit.json'))
    sources += sorted((ROOT / 'negative-controls-02').glob('*/audit.json'))
    for source in sources:
        directory = source.parent
        loaded = a.load_audit(directory)
        relative = directory.relative_to(ROOT).as_posix()
        stage = target / 'audit-runtimes' / relative.replace('/', '__')
        package = stage / 'rulespec_extrapolator'
        package.mkdir(parents=True)
        (package / '__init__.py').write_text('"""Verified local experiment snapshot."""\n')
        for name, expected in loaded['run']['sources_sha256'].items():
            frozen = directory / 'frozen' / name
            assert e._digest(frozen.read_bytes()) == expected
            if name.startswith('application/'):
                shutil.copyfile(frozen, package / Path(name).name)
            elif name.startswith('data/'):
                dest = package / '_data' / name.removeprefix('data/')
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(frozen, dest)
        replay = target / 'audits' / relative.replace('/', '__')
        env = {**os.environ, 'PYTHONPATH': str(stage)}
        code = '''import json, sys
from pathlib import Path
from rulespec_extrapolator import audit as a, extraction as e
e._create_model = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('No provider allowed'))
report = a.replay_audit(Path(sys.argv[1]), Path(sys.argv[2]))
print(json.dumps({'status': report['status'], 'review_complete': report['review_complete']}))
'''
        completed = subprocess.run([sys.executable, '-c', code, str(directory), str(replay)],
                                   cwd=stage, env=env, capture_output=True, text=True, check=True)
        receipt = e._load(replay / 'replay.json')
        audits.append({'audit': relative, 'replay': receipt,
                       'assessment': json.loads(completed.stdout), 'runtime': 'original_verified_frozen_application'})
    wheel = REPO / '.tools/quality-v2-wheels/rulespec_extrapolator-0.1.0.dev0-py3-none-any.whl'
    wheel_root = target / 'wheel'
    wheel_root.mkdir()
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(wheel_root)
    code = '''import json, sys
from pathlib import Path
from rulespec_extrapolator import core, extraction as e
from rulespec_extrapolator.documents import prepare_document
assert Path(core.__file__).is_relative_to(Path(sys.argv[1]))
assert core.data_root().is_relative_to(Path(sys.argv[1]))
text = 'Visitors must present a receipt.'
book = core.compile_candidates(prepare_document(text), [{'kind': 'requirement', 'actor': 'Visitors', 'actor_quote': 'Visitors', 'summary': text, 'quote': text, 'modality': 'must', 'modality_quote': 'must'}], {})
assert len(book['accepted']) == 1 and not book['rejected']
core.validate_graph(book['graph'])
assert any(k.startswith('data/') for k in e._runtime_sources())
print(json.dumps({'status': 'verified', 'imported_built_wheel': True, 'packaged_core_data': True, 'compile_and_validate': True}))
'''
    completed = subprocess.run([sys.executable, '-c', code, str(wheel_root)], cwd=wheel_root,
                               env={**os.environ, 'PYTHONPATH': str(wheel_root)}, capture_output=True, text=True, check=True)
    pins = e._load(REPO / '.tools/quality-v2-baseline/before-sha256.json')
    protected = {name: sha for name, sha in pins.items() if name.startswith((
        'examples/document_understanding/manual-slice/',
        'thoughts/reviews/2026-09-07-document-understanding-adversarial/'))}
    changed = [name for name, sha in protected.items() if e._digest((REPO / name).read_bytes()) != sha]
    assert not changed
    e._save(ROOT / 'runtime-verification.json', {
        'created_at': e._now(), 'provider_calls': 0, 'extractions': extractions, 'audits': audits,
        'wheel': {**json.loads(completed.stdout), 'sha256': e._digest(wheel.read_bytes())},
        'protected_original_files': len(protected), 'changed_original_files': changed,
        'runtime_sources_sha256': {name: e._digest(path.read_bytes()) for name, path in e._runtime_sources().items()},
    })
    print(json.dumps({'extractions': len(extractions), 'audits': len(audits), 'wheel': 'verified',
                      'protected_originals': len(protected), 'provider_calls': 0}))


if __name__ == '__main__':
    main()
