"""Retest the full saved chapter through the installed public CLI."""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from rulespec_extrapolator import documents, extraction as e

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE = HERE.parent / '2026-09-12-csbg'
SOURCE = BASE / 'sources/document.json'
CLI = Path(sys.executable).parent / 'rulespec-understand'


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


def prepare():
    doc = json.loads(SOURCE.read_text())
    documents.validate_document(doc)
    src = REPO / 'packages/rulespec-extrapolator/src/rulespec_extrapolator'
    installed = Path(e.__file__).parent
    hashes = {}
    for path in src.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            relative = path.relative_to(src)
            assert path.read_bytes() == (installed / relative).read_bytes(), relative
            hashes[str(installed / relative)] = sha256(path.read_bytes()).hexdigest()
    for name in ('PLAN.md', 'run.py'):
        hashes[str(HERE / name)] = sha256((HERE / name).read_bytes()).hexdigest()
    for path in (SOURCE, BASE / 'cases.json', BASE / 'state-plan-content-review.json', BASE / 'source-receipt.json'):
        hashes[str(path)] = sha256(path.read_bytes()).hexdigest()
    save('pins.json', hashes)
    windows = {arm:e.plan_windows(doc, section_windows=arm == 'B') for arm in ('A','B')}
    assert len(windows['A']) == 6 and len(windows['B']) == 27
    for items in windows.values():
        assert items[0]['start'] == 0 and items[-1]['end'] == len(doc['text'])
        assert all(a['end'] == b['start'] for a,b in zip(items, items[1:]))
    save('windows.json', windows)
    save('setup.json', dict(source=str(SOURCE), source_sha256=doc['sha256'],
        characters=len(doc['text']), passages=len(documents.source_passages(doc)),
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        installed_module=e.__file__, runtime=e._runtime_versions(), cli=str(CLI)))


def verify_pins():
    for name, digest in json.loads((HERE / 'pins.json').read_text()).items():
        assert sha256(Path(name).read_bytes()).hexdigest() == digest, name


def capture(arm):
    assert arm in ('A','B')
    verify_pins()
    command = [str(CLI), 'extract', str(SOURCE), '--env-file',
        '/Users/mikewolfd/Work/spicy-regs/.env', '--output', str(HERE / arm),
        '--model', 'gemini-3.8-flash', '--thinking-level', 'low',
        '--max-chars', '24000', '--max-output-tokens', '16384']
    if arm == 'B':
        command.append('--section-windows')
    env = dict(os.environ)
    env.pop('PYTHONPATH', None)
    started = time.time()
    outcome = {}
    with (HERE / f'{arm}.log').open('x') as log:
        try:
            result = subprocess.run(command, cwd='/tmp', env=env, stdout=log,
                stderr=subprocess.STDOUT, timeout=1200, check=False)
            outcome['exit_code'] = result.returncode
        except subprocess.TimeoutExpired:
            outcome['timeout'] = True
    outcome.update(command=command, started_at=started, seconds=time.time()-started)
    save(f'{arm}-process.json', outcome)
    print(json.dumps(dict(arm=arm, **outcome)), flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'prepare':
        prepare()
    else:
        capture(sys.argv[1])
