"""Installed positive reference export from a manifest-complete saved model response."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
mode = sys.argv[1]
assert mode in {'isolated', 'working'}
python = ROOT / '.tools' / ('reference-integration-20260911-usc-open-ended' if mode == 'isolated' else 'document-poc-venv') / 'bin/python'
output = HERE / ('cli-positive-' + mode)
output.mkdir(exist_ok=False)
source = ROOT / 'examples/document_understanding/context-budget-experiment/runs/leave-24000-16384-1'
original = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir() if p.is_file()}
(output / 'input.json').write_text(json.dumps({'source': str(source), 'sha256': original}, indent=2) + '\n')
commands = []


def run(name, args):
    cmd = [str(python), '-m', 'rulespec_extrapolator.cli', *map(str, args)]
    with (output / (name + '.log')).open('x') as stream:
        result = subprocess.run(cmd, cwd='/tmp', env={**os.environ, 'PYTHONPATH': ''},
                                stdout=stream, stderr=subprocess.STDOUT)
    commands.append({'command': cmd, 'cwd': '/tmp', 'pythonpath': '', 'returncode': result.returncode})
    (output / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    print(name, result.returncode, flush=True)
    assert result.returncode == 0, name


if mode == 'isolated':
    run('reprocess', ['reprocess', source, '--output', output / 'reprocessed'])
    run('replay', ['replay', output / 'reprocessed', '--output', output / 'replayed'])
    processed = output / 'reprocessed'
    assert json.loads((processed / 'rulebook.json').read_text()) == json.loads((output / 'replayed/rulebook.json').read_text())
else:
    processed = HERE / 'cli-positive-isolated/reprocessed'
run('references', ['references', processed, '--output', output / 'references.json'])
run('discovery', ['discovery-export', processed, '--references', '--output', output / 'discovery.json'])
scans = [json.loads((output / 'references.json').read_text()),
         json.loads((output / 'discovery.json').read_text())['reference_scan']]
for scan in scans:
    assert not [row for row in scan['candidates'] if row['kind'] == 'usc']
    row, = [row for row in scan['rejected'] if row['kind'] == 'usc']
    assert row['value'] == '38 U.S.C. 4301, et seq.'
    assert row['code'] == 'usc_open_ended_reference_unresolved'
    assert row['reading']['usc_section'] == '4301' and 'usc_section_end' not in row['reading']
assert all(hashlib.sha256((source / name).read_bytes()).hexdigest() == value for name, value in original.items())
if mode == 'working':
    for name in ('references.json', 'discovery.json'):
        assert (output / name).read_bytes() == (HERE / 'cli-positive-isolated' / name).read_bytes()
run_data = json.loads((processed / 'run.json').read_text())
assert run_data['reprocessing']['provider_calls'] == 0
(output / 'checks.json').write_text(json.dumps({'status': 'passed', 'provider_calls': 0,
    'source_unchanged': True, 'open_ended_wording_and_refusal_retained': True,
    'working_matches_isolated': mode == 'working'}, indent=2) + '\n')
