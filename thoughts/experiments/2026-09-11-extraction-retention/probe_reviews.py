"""Compare unchanged and current readers on the same preserved review runs."""
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile

from rulespec_extrapolator import extraction as ex
from rulespec_extrapolator.review_store import ReviewStore

HERE = Path(__file__).resolve().parent
roots = [HERE.parents[2] / 'examples/document_understanding/actor-term-integration/extract',
         HERE.parent / '2026-09-10-parallel-compression/fresh-extraction']
rows = []
for root in roots:
    row = {'path': str(root), 'manifest_sha256': ex._digest((root / 'manifest.json').read_bytes())}
    try:
        with tempfile.TemporaryDirectory(prefix='rulespec-review-probe-') as temporary:
            copied = Path(temporary) / 'run'
            shutil.copytree(root, copied, ignore=shutil.ignore_patterns('review.sqlite3*'))
            if (root / 'review.sqlite3').exists():
                with sqlite3.connect(f'file:{root / "review.sqlite3"}?mode=ro', uri=True) as source:
                    with sqlite3.connect(copied / 'review.sqlite3') as target:
                        source.backup(target)
            store = ReviewStore(copied)
            snapshot = store.snapshot()
            assert snapshot == ReviewStore(copied).snapshot()
            row.update(status='passed', accepted=len(snapshot['accepted']),
                       snapshot_sha256=ex._digest(snapshot))
    except Exception as error:
        row.update(status='failed', error_type=type(error).__name__, error=str(error))
    rows.append(row)
ex._save(HERE / (sys.argv[1] + '-reviews.json'), rows)
print(json.dumps(rows))
