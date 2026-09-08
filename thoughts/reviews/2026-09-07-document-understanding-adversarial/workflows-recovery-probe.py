"""Check normal entry points against the already recorded numeric-overflow run."""
import hashlib
import json
from pathlib import Path

from rulespec_extrapolator import extraction, review_store

PACKET = Path('/Users/mikewolfd/Work/rulespec/.tools/blind-review-20260907/code/repo')
REPORT = Path(__file__).resolve().parent
ROOT = Path('/Users/mikewolfd/Work/rulespec/.tools/blind-review-20260907/workflows-artifacts/workflows-runs')
RUN = ROOT / 'numeric-overflow'
for module in (extraction, review_store):
    assert Path(module.__file__).resolve().is_relative_to(PACKET)


def hashes():
    return {str(p.relative_to(RUN)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in RUN.rglob('*') if p.is_file()}


before = hashes()
observed = {}
for name, action in (
    ('review', lambda: review_store.ReviewStore(RUN)),
    ('replay', lambda: extraction.replay_run(RUN, ROOT / 'overflow-replay')),
    ('reprocess', lambda: extraction.reprocess_run(RUN, ROOT / 'overflow-reprocess')),
):
    try:
        action()
        observed[name] = {'returned': True}
    except Exception as exc:
        observed[name] = {'error_type': type(exc).__name__, 'message': str(exc)}
observed['original_artifacts_unchanged'] = before == hashes()
observed['created_review_database'] = (RUN / 'review.sqlite3').exists()
observed['created_replay_directory'] = (ROOT / 'overflow-replay').exists()
observed['created_reprocess_directory'] = (ROOT / 'overflow-reprocess').exists()
(REPORT / 'workflows-recovery-observed.json').write_text(json.dumps(observed, indent=2) + '\n')
print(json.dumps(observed, indent=2))
