"""Integrator rerun of W1/W2 against the sealed code copy; no providers.

The reviewer's inputs are reused, so this confirms reproducibility rather than
providing a second independent discovery. Original review evidence is untouched.
"""
import importlib.util
import json
from pathlib import Path
import tempfile


REPORT = Path(__file__).resolve().parent
SCRATCH = Path("/Users/mikewolfd/Work/rulespec/.tools/blind-review-20260907")
module_spec = importlib.util.spec_from_file_location("blind_workflow_probes", REPORT / "workflows-probes.py")
probes = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(probes)
scratch = Path(tempfile.mkdtemp(prefix="integrator-confirm-", dir=SCRATCH))
probes.REPORT = scratch
probes.RUNS = scratch / "runs"
probes.RUNS.mkdir()

overflow = probes.overflow_failure()
omissions = probes.omission_accounting()
run = json.loads((probes.RUNS / "numeric-overflow" / "run.json").read_text())
recovery = {}
for name, action in (
    ("review", lambda: probes.review_store.ReviewStore(probes.RUNS / "numeric-overflow")),
    ("replay", lambda: probes.extraction.replay_run(probes.RUNS / "numeric-overflow", scratch / "replay")),
    ("reprocess", lambda: probes.extraction.reprocess_run(probes.RUNS / "numeric-overflow", scratch / "reprocess")),
):
    try:
        action()
        recovery[name] = {"returned": True}
    except Exception as exc:
        recovery[name] = {"error_type": type(exc).__name__, "message": str(exc)}

assert overflow["raised"]["type"] == "ValueError"
assert run["status"] == "running"
assert not overflow["final_artifact_exists"]["manifest.json"]
assert all("error_type" in entry for entry in recovery.values())
assert omissions["status"] == "failed"
assert omissions["review_complete"] is False
assert omissions["coverage"]["missing"] == 1
assert omissions["coverage"]["unknown"] == 0
assert not omissions["issues"]

result = {
    "reviewer": "Integrator; not blind",
    "method": "Rerun the blind workflow reviewer's W1/W2 inputs against the sealed code copy.",
    "production_edits": False,
    "provider_calls": 0,
    "scratch": str(scratch),
    "overflow": overflow,
    "recorded_run_status": run["status"],
    "recovery": recovery,
    "total_omission": omissions,
}
(REPORT / "integrator-workflows-confirmed.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
