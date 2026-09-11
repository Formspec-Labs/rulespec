# Retrieval representation pilot

**Do not adopt the tested combined index.** Extracted meanings help retrieve useful grouped context, but appending every linked meaning to every source item creates repetition and loses relevant results. Keep source retrieval available; investigate selecting context after ranking and combining separately ranked result sets as distinct future experiments.

This was a zero-API, frozen-output comparison using the existing lexical BM25 diagnostic and `discovery.records`. Four saved provider-extracted legal sources, 16 new agent-authored source questions, no tuning or retries. These are development sources and synthetic queries, not fresh held-out documents or a real-user benchmark. Production is unchanged.

| Measure | Source passages | Statement summaries | Source + linked meanings/context |
|---|---:|---:|---:|
| Indexed rows | 85 | 53 | 85 |
| Indexed text characters | 15,928 | 14,923 | 99,415 |
| Selected relevant source fragment retrieved @3 | 14/16 | 14/16 | 13/16 |
| All selected source fragments retrieved @3 | 9/16 | 14/16 | 13/16 |
| Same under 6,000 unique-source-character cap | 9/16 | 14/16 | 13/16 |
| Mean reciprocal first-support rank | .777 | .769 | .805 |
| Unique returned evidence characters, all queries | 15,477 | 20,533 | 24,029 |
| Repeated returned evidence characters, all queries | 0 | 5,290 | 57,276 |
| Pairs of returned hits with overlapping evidence | 0 | 11 | 22 |

The cap never bound; these results do not show equal-cost context delivery. No individual hit contained the entire source. First-support rank counts evidence attached to a hit, which can be broader than the displayed statement. **All-selected-fragments is not complete-answer accuracy:** manual review found that the refrigerant de minimis question's labels omitted compliance alternatives. Its source-only result passes the small fragment check but lacks those conditions. Original labels/scores are preserved, not repaired after seeing results.

The preregistered gate fails: combined loses two source-only successes (chlorine scope and refrigerant service duties), despite gaining the shipment exception. It also trails statement-only in both support counts. Higher aggregate reciprocal rank conceals these regressions.

The main mechanisms are visible in raw results:

- **Source fallback matters:** the nonconsecutive-employment provision is absent from the saved extracted summaries. Source and combined retrieve it; statement-only cannot.
- **Grouped meaning helps:** `Can a truck carry beer as cargo?` finds the shipment exception through the grouped statement. Source-only finds the possession rule but not the separate shipment list item.
- **Blindly concatenating context hurts:** chlorine's any-quantity scope falls from rank 1 to rank 20 in combined. Short placard list items inherit the same long classification statement and crowd the results.
- **Retrieval needs more than lexical matching:** all arms miss the long-break military-service employment rule at rank 3 for an everyday paraphrase.

Reuse available code before building more: source-only ranking with context attached afterward is already represented by `discovery.records(..., 'packets')` and the old `discovery_trial` packets arm. That is a sensible next controlled comparison, not implemented here. Separate source and statement ranking with source-span deduplication is another candidate. Neither embeddings benefit nor legal-answer accuracy was tested, and no production retrieval service was built.

Artifacts: [preregistered plan](PLAN.md), [frozen queries](queries.json), [source/run hashes](freeze.json), [actual indexed text](indexes.json), [all ranks and evidence](results.json), [manual raw review](RAW-REVIEW.md), [exact replay receipt](replay.json).

Reproduce without network or a model, without overwriting saved artifacts:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python - <<'PYTHON'
import importlib.util, json
from pathlib import Path
root = Path("thoughts/experiments/2026-09-10-design-retrieval")
spec = importlib.util.spec_from_file_location("trial", root / "run.py")
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)
rows, result = trial.execute()
assert rows == json.loads((root / "indexes.json").read_text())
assert result == json.loads((root / "results.json").read_text())
print("Replay matched")
PYTHON
```

Existing `replay.json` records the successful first replay. Runtime hashes are captured in `results.json`. Preparation paths preserve provenance to historical provider books; they were generated under different past extraction versions/settings, held fixed here to isolate retrieval representation. Source paragraph parsing, historical extraction granularity, query authorship and the unchanged homemade BM25 diagnostic limit generalization. No external BM25 package was installed, and no sealed holdout labels were opened.
