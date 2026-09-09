# Medium versus high audit thinking

Medium preserved the targeted findings in these three cases while using **79% fewer reported tokens** than high thinking. It is the better candidate for the next audit experiment. This result does not establish full-document accuracy or resolve the complete-case fixture limitation.

## Results

| Case | High tokens | Medium tokens | High request seconds | Medium request seconds | Medium alternatives verdict |
|---|---:|---:|---:|---:|---|
| Complete alternatives | 32,227 | 9,182 | 83.51 | 22.41 | correct |
| Electronic option missing | 29,749 | 4,084 | 88.16 | 5.15 | error |
| Electronic signature missing | 30,340 | 5,990 | 78.15 | 12.42 | error |

High used 92,316 total tokens; medium used **19,256**. Request time is measured from saved attempt timestamps, not whole-pipeline latency. Token reduction is not a dollar-cost ratio: input, answer and thinking tokens can have different pricing treatment.

Medium's raw rationales correctly explain both intended defects: removing the electronic option turns a choice into a paper-only requirement; removing the signature qualification admits unsigned electronic records. Like high, medium accepts one evidence paragraph supporting both alternatives. Full evidence remains present in the defective fixtures, so the model is detecting missing explicit meaning rather than treating quotation coverage as sufficient.

The original broad criteria pass 2/3 cases under both thinking levels. Both flag the complete fixture because its source paragraph includes an adjacent record-content duty whose separate claim is excluded from the isolated test. High calls this a summary error; medium calls it a boundary error and regards the summary as faithful to the delivery duty. All units remain partial. The alternatives verdicts agree with the expected correct/error/error pattern under both thinking levels. Do not report this as an overall 3/3 acceptance result.

All three medium responses end STOP, pass schema, source-evidence and reciprocal-link checks, and replay identically without provider calls. Structural success does not prove semantic correctness. Medium also calls the invented document's requirements statutory in its boundary rationale; that is imprecise wording, not a verified statement about legal authority.

## Controlled comparison

This experiment reuses the clarified-description requests from [the alternatives experiment](../alternative-evidence-experiment/README.md). Only `config.thinking_config.thinking_level` changes from high to medium. Model (`gemini-3.8-flash`), temperature zero, schema, prompt, source, draft, inventory, and omitted numeric thinking budget/output cap are identical. Exact whole-request equality except that setting is checked during acquisition and replay.

Three new comparison calls, no retries, extractions, inventories or repairs. Each arm has one observation per case; high controls were saved earlier. The known fixture limitation remains unchanged to isolate thinking level. These are small comparison-stage tests, not full-document audits or independent gold labels. No production code, schema or default changed in this iteration.

## Next step

Use medium for the next validation experiment. Correct the isolated fixture by supplying the adjacent claim or consistently narrowing its supporting source, then check a representative saved document before considering a default change. The token and timing improvement is promising; broader semantic reliability remains unmeasured.

## Evidence and replay

`design.json` pins the runner, criteria, prior experiment manifest and runtime. The prior manifest binds the reused fixtures, clarified prompt, schema, helper assessment code, high captures and frozen runtime. `runs/` contains the medium requests, responses, attempt metadata, results and per-run hashes. `results.json` retains paired high/medium judgments; `verification.json` records usage and timing; `source-review.json` preserves revisable interpretation. All previous captures remain unchanged.

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/medium-audit-experiment/experiment.py replay
```

Replay requires the pinned runtime and uses no credentials or provider calls. No package tests were rerun because no production implementation changed; verification exercised the actual endpoint and exact saved-response replay. Work remains local and uncommitted.
