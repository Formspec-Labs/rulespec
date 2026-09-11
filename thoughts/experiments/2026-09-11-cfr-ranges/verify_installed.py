"""Check source/installed reference and discovery parity, including USLM input."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
import zipfile

from rulespec_extrapolator.documents import load_document
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.references import scan_references

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
mode = sys.argv[1]
assert mode in {'source', 'isolated', 'working'}
out = HERE/('delivery-'+mode)
out.mkdir()
verified = 0
if mode != 'source':
    site = Path(sysconfig.get_paths()['purelib'])
    for pin in json.loads((HERE/'wheel-inputs.json').read_text()):
        wheel = Path(pin['path'])
        assert hashlib.sha256(wheel.read_bytes()).hexdigest() == pin['sha256']
        with zipfile.ZipFile(wheel) as z:
            for name in z.namelist():
                if not name.endswith('.py') or '.dist-info/' in name:
                    continue
                data = z.read(name)
                assert (site/name).read_bytes() == data, name
                for package, source in [('refspec', ROOT.parent/'RefSpec/src'),
                                        ('rulespec_extrapolator', ROOT/'packages/rulespec-extrapolator/src')]:
                    if name.startswith(package+'/'):
                        assert (source/name).read_bytes() == data, name
                verified += 1

inputs = [HERE/'source-paragraphs.txt', HERE.parent/'2026-09-11-compilation-occurrences/title-18-s798A.xml']
commands = []
for source in inputs:
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    doc = load_document(source)
    expected = scan_references(doc)
    result = out/(source.stem+'-references.json')
    command = [sys.executable, '-m', 'rulespec_extrapolator.cli', 'references', str(source), '--output', str(result)]
    environment = dict(os.environ)
    if mode != 'source':
        environment['PYTHONPATH'] = ''
    with (out/(source.stem+'.log')).open('x') as f:
        subprocess.run(command, cwd='/tmp', env=environment, stdout=f, stderr=subprocess.STDOUT, check=True)
    commands.append(command)
    assert json.loads(result.read_text()) == expected
    discovery = export_discovery({'document':doc,'accepted':[]}, include_references=True)
    discovery_path = out/(source.stem+'-discovery.json')
    discovery_path.write_text(json.dumps(discovery,ensure_ascii=False,indent=2)+'\n')
    if mode != 'source':
        for produced in (result,discovery_path):
            assert json.loads(produced.read_text()) == json.loads((HERE/'delivery-source'/produced.name).read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
checks = {'mode':mode,'python':sys.executable,'status':'passed','verified_wheel_python_files':verified,
          'normal_cli_and_api_agree':True,'source_and_installed_agree':mode!='source',
          'inputs':[str(p) for p in inputs],'commands':commands,'model_calls':0}
(out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
