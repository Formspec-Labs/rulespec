"""Replay the completed trial with its saved application code, without model calls.

The installed dependencies and Core artifacts must still match recorded hashes.
The later partial-enrichment check uses current production code separately.
"""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temp:
        package = Path(temp) / 'rulespec_extrapolator'
        shutil.copytree(ROOT / 'cells/cell-00/frozen/sources/application', package)
        (package / '__init__.py').write_text('')
        subprocess.run([sys.executable, '-c', '''
from contextlib import nullcontext
from pathlib import Path
import runpy
import sys
from unittest.mock import patch
from rulespec_extrapolator import extraction as e, audit, structure
root, output = map(Path, sys.argv[1:])
trial = runpy.run_path(str(root / 'experiment.py'))
design = trial['verify']()
output.mkdir(parents=True, exist_ok=False)
for cell in design['cells']:
    with patch.object(e, 'passage_catalog', trial['sentences']) if cell['arm'] == 'S' else nullcontext():
        e.replay_run(root / 'cells' / cell['id'], output / cell['id'])
structure.replay_enrichment(root / 'integration/enrichment', output / 'enrichment')
audit.replay_audit(root / 'integration/audit', output / 'audit')
e._save(output / 'checks.json', {'extraction_replays': 10, 'enrichment_replay': 'passed',
    'audit_replay': 'passed', 'provider_calls': 0, 'runtime': 'saved application, verified installed dependencies'})
print('10 extraction cells, enrichment and audit replayed with no provider calls.')
''', str(ROOT), str(args.output.resolve())], check=True,
            env={**os.environ, 'PYTHONPATH': temp})
