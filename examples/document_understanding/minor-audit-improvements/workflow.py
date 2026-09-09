"""Run the existing full-workflow harness on the reserved new document."""
import importlib.util
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
harness = ROOT.parent / 'low-extract-medium-audit/experiment.py'
design = json.loads((ROOT / 'fresh/design.json').read_text())
assert hashlib.sha256(harness.read_bytes()).hexdigest() == design['harness_sha256']
spec = importlib.util.spec_from_file_location('full_workflow', harness)
workflow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)
workflow.ROOT = ROOT / 'fresh'

if __name__ == '__main__':
    workflow.main()
