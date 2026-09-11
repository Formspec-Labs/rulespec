"""Check pinned wheel bytes, both installations, changed sources and CLI output."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
envs = {name: ROOT / '.tools' / folder / 'bin/python' for name, folder in
        [('wheel', 'reference-integration-20260911-readings'), ('current', 'document-poc-venv')]}
site = {name: Path(subprocess.check_output([str(py), '-c', 'import sysconfig; print(sysconfig.get_path("purelib"))'], text=True).strip()) for name, py in envs.items()}
sha = lambda data: hashlib.sha256(data).hexdigest()
inputs = json.loads((HERE / 'wheel-inputs.json').read_text())
files, errors = [], []
for wheel in inputs:
    path = Path(wheel['path'])
    if sha(path.read_bytes()) != wheel['sha256']:
        errors.append('Wheel changed: ' + str(path))
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name.endswith('/') or '.dist-info/' in name or '.data/' in name:
                continue
            raw = archive.read(name)
            row = {'file': name, 'wheel_sha256': sha(raw)}
            for installed, base in site.items():
                target = base / name
                row[installed + '_matches'] = target.is_file() and target.read_bytes() == raw
                if not row[installed + '_matches']:
                    errors.append(installed + ' differs: ' + name)
            if name.endswith('.py') and name.startswith(('refspec/', 'rulespec_extrapolator/')):
                source = (Path('/Users/mikewolfd/Work/RefSpec/src') if name.startswith('refspec/') else ROOT / 'packages/rulespec-extrapolator/src') / name
                row['source_matches'] = source.is_file() and source.read_bytes() == raw
                if not row['source_matches']:
                    errors.append('Source differs: ' + name)
            files.append(row)
artifacts = []
for folder in sorted((HERE / 'application-source').iterdir()):
    if not folder.is_dir(): continue
    for source in sorted(folder.glob('*.json')):
        relative = source.relative_to(HERE / 'application-source')
        expected = json.loads(source.read_text())
        row = {'artifact': str(relative)}
        for name in envs:
            actual = HERE / ('application-' + name) / relative
            row[name + '_matches'] = actual.exists() and json.loads(actual.read_text()) == expected
            if not row[name + '_matches']: errors.append(name + ' CLI differs: ' + str(relative))
        artifacts.append(row)
reviews = json.loads((HERE / 'application-current/review.json').read_text())
if any(row['residual_overlaps'] or row['remaining_text_candidates'] for row in reviews):
    errors.append('Real source retains a duplicate or unsupported RIN candidate')
if sum(row['remaining_rejected'] for row in reviews) != 1:
    errors.append('Expected amendment refusal is missing or extra refusals appeared')
report = {'wheel_files': files, 'cli_artifacts': artifacts, 'errors': errors,
          'package_file_count': len(files), 'changed_package_python_files': sum('source_matches' in r for r in files),
          'cli_artifact_count': len(artifacts), 'source_review': reviews,
          'source_module_hashes': {str(path): sha(path.read_bytes()) for path in
              [ROOT/'packages/rulespec-extrapolator/src/rulespec_extrapolator/references.py',
               ROOT/'packages/rulespec-extrapolator/src/rulespec_extrapolator/uslm.py',
               Path('/Users/mikewolfd/Work/RefSpec/src/refspec/registry/iri_minting.py')]}}
with (HERE / 'delivery-verification.json').open('x') as f:
    json.dump(report, f, indent=2); f.write('\n')
print(json.dumps({key: report[key] for key in ('package_file_count', 'changed_package_python_files', 'cli_artifact_count', 'errors')}, indent=2))
if errors: raise SystemExit(1)
