"""Check the delivered files and recorded command results, not semantic accuracy."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


environments = {name: next((ROOT / '.tools' / directory / 'lib').glob('python*/site-packages'))
                for name, directory in [('isolated', 'reference-integration-20260911-retention'),
                                        ('working', 'document-poc-venv')]}
files = {}
source_files = {}
for wheel in read(HERE / 'wheel-inputs.json'):
    path = Path(wheel['path'])
    assert sha(path) == wheel['sha256'], path
    with ZipFile(path) as archive:
        for name in archive.namelist():
            if name.endswith('/') or '.dist-info/' in name or '.data/' in name:
                continue
            expected = hashlib.sha256(archive.read(name)).hexdigest()
            assert all(sha(site / name) == expected for site in environments.values()), name
            files[name] = expected
            if name.startswith('rulespec_extrapolator/'):
                source = ROOT / 'packages/rulespec-extrapolator/src' / name
                if '/_data/' not in name:
                    assert sha(source) == expected, source
                    source_files[name] = expected

commands = {}
for mode in ('isolated-retry', 'working'):
    receipt = read(HERE / (mode + '-delivery-command.json'))
    assert receipt['status'] == 'passed'
    assert all(c['returncode'] == 0 for c in receipt['commands'])
    commands[mode] = sha(HERE / (mode + '-delivery-command.json'))
for name in ('references.json', 'discovery-export.json', 'export.json', 'usage.log'):
    assert (HERE / 'cli-isolated-retry' / name).read_bytes() == (HERE / 'cli-working' / name).read_bytes(), name
isolated = HERE / 'cli-isolated-retry'
assert read(isolated / 'reprocessed/rulebook.json') == read(isolated / 'replayed/rulebook.json')
review = read(isolated / 'export.json')
assert not review['attestations'] and all(c['review_status'] == 'pending' for c in review['accepted'])

inputs = read(HERE / 'input.json')
parent = Path(inputs['source_experiment'])
assert sha(parent / 'manifest.json') == inputs['manifest_sha256']
for name, digest in read(parent / 'manifest.json')['files'].items():
    assert sha(parent / name) == digest, name
for pins in ('baseline-pins.json', 'range-pins.json', 'evidence-application-pins.json', 'combined-application-pins.json'):
    for name, digest in read(HERE / pins).items():
        assert sha(HERE / name) == digest, name
normal = HERE.parent / '2026-09-10-parallel-compression/fresh-extraction'
assert sha(normal / 'manifest.json') == read(HERE / 'old-review-check.json')['runs'][-1]['manifest_sha256']
for name, digest in read(normal / 'manifest.json')['artifacts_sha256'].items():
    assert sha(normal / name) == digest, name

result = {'status': 'passed', 'wheel_package_files': files, 'source_package_files': source_files,
          'command_receipts': commands, 'normal_capture_unchanged': True,
          'parent_capture_unchanged': True, 'comparison_snapshots_unchanged': True,
          'normal_replay_equal': True, 'installed_exports_equal': True,
          'new_review_pending': True}
(HERE / 'delivery-checks.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'wheel_files': len(files), 'source_files': len(source_files)}))
