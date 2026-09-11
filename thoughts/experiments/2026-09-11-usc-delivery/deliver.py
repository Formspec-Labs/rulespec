"""Exercise installed packages and normal commands outside both source checkouts."""
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
mode, attempt = sys.argv[1:3]
assert mode in {'isolated', 'working'} and attempt.replace('-', '').isalnum()
python = ROOT / '.tools' / ('reference-integration-20260911-usc' if mode == 'isolated' else 'document-poc-venv') / 'bin/python'
python = Path(os.environ.get('RULESPEC_USC_TEST_PYTHON', python))
output = HERE / ('cli-' + attempt)
output.mkdir(exist_ok=False)
env = {**os.environ, 'PYTHONPATH': ''}
commands = []


def run(name, args):
    args = list(map(str, args))
    with (output / (name + '.log')).open('x') as stream:
        result = subprocess.run(args, cwd='/tmp', env=env, stdout=stream, stderr=subprocess.STDOUT)
    commands.append({'name': name, 'command': args, 'cwd': '/tmp', 'pythonpath': '', 'returncode': result.returncode})
    (output / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    print(name, result.returncode, flush=True)
    assert result.returncode == 0, name


run('dependencies', ['uv', 'pip', 'check', '--python', python])
run('packages', [python, HERE / 'verify_packages.py', attempt + '-packages.json'])
run('comparison', [python, HERE / 'verify_scan.py', attempt + '-comparison'])
cli = [python, '-m', 'rulespec_extrapolator.cli']
if mode == 'isolated':
    run('application-suite', [python, '-m', 'pytest', '-q', ROOT / 'packages/rulespec-extrapolator/tests'])
    run('upstream-usc-suite', [python, '-m', 'pytest', '-q', ROOT.parent / 'RefSpec/tests/test_usc_occurrences.py'])
    saved = HERE.parent / '2026-09-10-parallel-compression/fresh-extraction'
    run('reprocess', cli + ['reprocess', saved, '--output', output / 'reprocessed'])
    run('replay', cli + ['replay', output / 'reprocessed', '--output', output / 'replayed'])
    source = output / 'reprocessed'
else:
    source = HERE / sys.argv[3] / 'reprocessed'
for name, extra in [('references', []), ('discovery-export', ['--references']), ('export', [])]:
    run(name, cli + [name, source, *extra, '--output', output / (name + '.json')])
run('usage', cli + ['usage', source])
