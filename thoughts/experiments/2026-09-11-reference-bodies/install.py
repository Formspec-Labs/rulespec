"""Install the changed wheel with the previously verified dependency set."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
mode = sys.argv[1]
pins = json.loads((HERE.parent/'2026-09-11-cfr-ranges/wheel-inputs.json').read_text())
for pin in pins:
    if Path(pin['path']).name.startswith('rulespec_extrapolator-'):
        wheel = ROOT/'dist/reference-integration-20260911-bodies'/Path(pin['path']).name
        pin.update(path=str(wheel), sha256=hashlib.sha256(wheel.read_bytes()).hexdigest())
    assert hashlib.sha256(Path(pin['path']).read_bytes()).hexdigest() == pin['sha256']
if mode == 'isolated':
    (HERE/'wheel-inputs.json').write_text(json.dumps(pins,indent=2)+'\n')
    python = ROOT/'.tools/reference-integration-20260911-bodies/bin/python'
    subprocess.run(['uv','venv','--python',sys.executable,str(python.parent.parent)],check=True)
else:
    python = ROOT/'.tools/document-poc-venv/bin/python'
commands = [['uv','pip','install','--offline','--python',str(python),
    '--constraint',str(HERE.parent/'2026-09-11-uslm-source-links/dependency-constraints.txt'),
    '--reinstall-package','rulespec-extrapolator',*[p['path'] for p in pins]]]
if mode == 'isolated':
    commands.append(['uv','pip','install','--offline','--python',str(python),'pytest=='+importlib.metadata.version('pytest')])
commands.append(['uv','pip','check','--python',str(python)])
(HERE/('install-'+mode+'-commands.json')).write_text(json.dumps(commands,indent=2)+'\n')
for command in commands:
    subprocess.run(command,check=True)
