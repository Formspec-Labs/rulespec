"""Run or replay the existing full workflow on one frozen transfer source."""
import importlib.util
from pathlib import Path
import sys
from rulespec_extrapolator import extraction as e

ROOT=Path(__file__).resolve().parent
design=e._load(ROOT/'design.json')
for name,digest in design['inputs_sha256'].items():
    assert e._digest((ROOT/name).read_bytes())==digest,name
harness=ROOT.parent/'low-extract-medium-audit/experiment.py'
assert e._digest(harness.read_bytes())==design['harness_sha256']
case=sys.argv.pop(1)
assert case in ('passport','waste')
spec=importlib.util.spec_from_file_location('transfer_workflow',harness)
workflow=importlib.util.module_from_spec(spec)
spec.loader.exec_module(workflow)
workflow.ROOT=ROOT/case
workflow.main()
