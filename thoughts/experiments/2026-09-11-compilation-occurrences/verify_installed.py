"""Verify installed bytes and source/XML/CLI parity without provider calls."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
mode = sys.argv[1]
assert mode in {'isolated', 'working'}
output = HERE / ('delivery-' + mode)
output.mkdir(exist_ok=False)
installed = Path(sysconfig.get_paths()['purelib'])
verified = {}
for item in json.loads((HERE/'wheel-inputs.json').read_text()):
    wheel = Path(item['path'])
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == item['sha256']
    count = 0
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if not name.endswith('.py') or '.dist-info/' in name:
                continue
            data = z.read(name)
            assert (installed/name).read_bytes() == data, name
            for package, source in [('refspec', ROOT.parent/'RefSpec/src'),
                                    ('rulespec_extrapolator', ROOT/'packages/rulespec-extrapolator/src'),
                                    ('rulespec_projection', ROOT/'packages/rulespec-projection/src')]:
                if name.startswith(package+'/'):
                    assert (source/name).read_bytes() == data, name
            count += 1
    verified[wheel.name] = count

commands = []
def run(name, *args):
    cmd = [sys.executable, '-m', 'rulespec_extrapolator.cli', *map(str, args)]
    with (output/(name+'.log')).open('x') as stream:
        result = subprocess.run(cmd, cwd='/tmp', env={**os.environ, 'PYTHONPATH': ''},
                                stdout=stream, stderr=subprocess.STDOUT)
    commands.append({'command': cmd, 'cwd': '/tmp', 'pythonpath': '', 'returncode': result.returncode})
    (output/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    assert result.returncode == 0, name


run('prepare', 'prepare', HERE/'title-18-s798A.xml', '--output', output/'prepared.json')
run('references', 'references', HERE/'title-18-s798A.xml', '--output', output/'references.json')
expected = json.loads((HERE/'xml-results.json').read_text())
assert json.loads((output/'prepared.json').read_text()) == expected['document']
assert json.loads((output/'references.json').read_text()) == expected['references']
from rulespec_extrapolator.discovery import export_discovery
assert export_discovery({'document': expected['document'], 'accepted': []}, include_references=True) == expected['discovery']

source = ROOT/'thoughts/experiments/2026-09-10-parallel-compression/fresh-extraction'
pins = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.glob('*.json')}
if mode == 'isolated':
    run('reprocess', 'reprocess', source, '--output', output/'reprocessed')
    run('replay', 'replay', output/'reprocessed', '--output', output/'replayed')
    assert json.loads((output/'reprocessed/rulebook.json').read_text()) == json.loads((output/'replayed/rulebook.json').read_text())
    processed = output/'reprocessed'
else:
    processed = HERE/'delivery-isolated/reprocessed'
run('discovery', 'discovery-export', processed, '--references', '--output', output/'discovery.json')
book = json.loads((processed/'rulebook.json').read_text())
run_data = json.loads((processed/'run.json').read_text())
assert len(book['accepted']) == 4 and len(book['rejected']) == 0
assert run_data['reprocessing']['provider_calls'] == 0
assert run_data['processing_status'] == 'complete'
assert all(hashlib.sha256(p.read_bytes()).hexdigest() == value for p, value in pins.items())
if mode == 'working':
    assert (output/'discovery.json').read_bytes() == (HERE/'delivery-isolated/discovery.json').read_bytes()
checks = {'status': 'passed', 'python': sys.executable, 'verified_python_files': verified,
          'xml_matches_source': True, 'accepted': 4, 'rejected': 0, 'provider_calls': 0,
          'source_unchanged': True, 'working_matches_isolated': mode == 'working'}
(output/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
print(json.dumps(checks, indent=2))
