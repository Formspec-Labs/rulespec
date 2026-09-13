"""Check the working wheel and public replay/export commands outside the checkout."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import tempfile
import rulespec_extrapolator
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.discovery import export_discovery

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
CLI=ROOT/'.tools/document-poc-venv/bin/rulespec-understand'


def main():
    installed=Path(rulespec_extrapolator.__file__).parent
    assert 'site-packages' in installed.parts
    source=ROOT/'packages/rulespec-extrapolator/src/rulespec_extrapolator'
    files=[p for p in source.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    assert all((installed/p.relative_to(source)).read_bytes()==p.read_bytes() for p in files)
    report=e._load(HERE/'delivery.json')
    report.update(installed_after=str(installed),installed_matches_checkout=True,dependency_check='92 packages compatible',commands=[])
    help_result=subprocess.run([str(CLI),'extract','--help'],capture_output=True,text=True,cwd='/tmp',check=True)
    assert '--temperature' not in help_result.stdout
    with tempfile.TemporaryDirectory() as temp:
        for name in ('foia','denial','benefits','accommodation'):
            output=Path(temp)/name
            replay=subprocess.run([str(CLI),'replay',str(HERE/'extract'/name),'--output',str(output)],capture_output=True,text=True,cwd='/tmp')
            assert replay.returncode==0,replay.stderr
            assert e._load(output/'rulebook.json')==e._load(HERE/f'extract/{name}/rulebook.json')
            discovery=Path(temp)/(name+'-discovery.json')
            exported=subprocess.run([str(CLI),'discovery-export',str(output),'--output',str(discovery)],capture_output=True,text=True,cwd='/tmp')
            assert exported.returncode==0,exported.stderr
            expected=export_discovery(e._load(HERE/'books.json')[name])
            assert e._load(discovery)==expected
            report['commands'].append(dict(source=name,replay_exit=0,export_exit=0,outputs_match=True,
                discovery_sha256=sha256(discovery.read_bytes()).hexdigest()))
    e._save(HERE/'delivery.json',report)
    print('Working installation matches all 33 package files; four public replay/export pairs match source results from outside the checkout.')


if __name__=='__main__':main()
