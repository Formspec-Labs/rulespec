"""Installed-only delivery checks. No provider calls; original captures stay read-only."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
mode = sys.argv[1]
assert mode in {'isolated', 'working'}
attempt = sys.argv[2] if len(sys.argv) > 2 else mode
assert attempt.replace('-', '').isalnum()
environment = ('reference-integration-20260911-retention' if mode == 'isolated'
               else 'document-poc-venv')
python = ROOT / '.tools' / environment / 'bin/python'
cli = [str(python), '-m', 'rulespec_extrapolator.cli']
output = HERE / ('cli-' + attempt)
assert not output.exists(), 'Keep earlier attempts; choose a separate retry directory explicitly.'
lock = Path('/Users/mikewolfd/Work/spicysearch/compositions/measurement.lock')
record = {'holder': 'rulespec-retention-delivery', 'pid': os.getpid(), 'purpose': attempt + '-delivery'}
deadline = time.monotonic() + 600
while True:
    try:
        if os.getloadavg()[0] >= 4:
            raise BlockingIOError('load')
        record.update(start=datetime.now(timezone.utc).isoformat(), start_load=os.getloadavg())
        with lock.open('x') as stream:
            json.dump(record, stream)
        break
    except (FileExistsError, BlockingIOError):
        if time.monotonic() >= deadline:
            raise TimeoutError('Measurement start conditions not met')
        print('Waiting for measurement slot; load', os.getloadavg()[0], flush=True)
        time.sleep(10)

commands = []


def run(name, args, *, pythonpath=''):
    env = os.environ.copy()
    env['PYTHONPATH'] = pythonpath
    row = {'name': name, 'command': list(map(str, args)), 'cwd': '/tmp', 'pythonpath': pythonpath}
    with (output / (name + '.log')).open('x') as stream:
        result = subprocess.run(row['command'], cwd='/tmp', env=env,
                                stdout=stream, stderr=subprocess.STDOUT)
    row['returncode'] = result.returncode
    commands.append(row)
    (output / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    print(name, result.returncode, flush=True)
    if result.returncode:
        print((output / (name + '.log')).read_text()[-5000:], flush=True)
    assert result.returncode == 0, name


try:
    output.mkdir()
    run('dependency-check', ['uv', 'pip', 'check', '--python', python])
    run('runtime', [python, '-c', 'import rulespec_extrapolator.extraction as e; print(e.__file__)'])
    if mode == 'isolated':
        run('review-boundary', [python, '-m', 'pytest', '-q', HERE / 'test_review_reprocessing.py'],
            pythonpath=str(ROOT / 'packages/rulespec-extrapolator/tests'))
        source = HERE.parent / '2026-09-10-parallel-compression/fresh-extraction'
        run('reprocess', cli + ['reprocess', source, '--output', output / 'reprocessed'])
        run('replay', cli + ['replay', output / 'reprocessed', '--output', output / 'replayed'])
    source = output / 'reprocessed' if mode == 'isolated' else HERE / sys.argv[3] / 'reprocessed'
    for command, extra in [('references', []), ('discovery-export', ['--references']), ('export', [])]:
        run(command, cli + [command, source, *extra, '--output', output / (command + '.json')])
    run('usage', cli + ['usage', source])
    record['status'] = 'passed'
finally:
    record.update(end=datetime.now(timezone.utc).isoformat(), end_load=os.getloadavg(), commands=commands)
    (HERE / (attempt + '-delivery-command.json')).write_text(json.dumps(record, indent=2) + '\n')
    if lock.exists() and json.loads(lock.read_text()).get('pid') == os.getpid():
        lock.unlink()
