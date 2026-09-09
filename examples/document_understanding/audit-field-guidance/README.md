# Audit with existing CUE field guidance

The checker now uses the existing CUE field descriptions and better recognizes meaning distributed across several claims. This experiment shows useful corrections and new false alarms. Keep high-thinking audit optional; it has not demonstrated a reliable or cheaper default workflow.

## What changed

`audit.comparison_prompt()` reads the generated meaning schema's descriptions for summary, scope, modality, logic and choices. The same prompt is used for requests, saved configuration and replay. Additional instructions explain joint coverage, optional relationship enrichment and the difference between incomplete standalone prose and meaning retained elsewhere in the record. No new schema, extraction change, repair pass or default thinking-level change was introduced.

Four new comparison calls reuse the exact drafts and source inventories from [low extraction → high audit](../low-extract-high-audit/README.md). Each uses Gemini `gemini-3.8-flash`, high thinking and temperature zero, with no application `thinking_budget` or `max_output_tokens`. Only comparison instructions differ from the saved control requests. No retries, new extraction calls or new inventory calls were made. Criteria and input/runtime hashes were saved before acquisition.

## Results

| Saved draft | Control comparison tokens | New comparison tokens | New response | Consistent completed review |
|---|---:|---:|---|---|
| leave-full-low-1 | 92,513 | 86,447 | STOP | yes |
| display-low-1 | 65,364 | 67,700 | STOP | yes |
| leave-full-low-2 | 90,078 | 92,627 | MAX_TOKENS | no |
| display-low-2 | 74,296 | 78,587 | STOP | yes |

The new comparisons used **325,361 tokens**, versus **322,251** for the saved controls: about 1% more. The input guidance adds 891 tokens per request. This is token volume, not a dollar-cost estimate. Reusing the earlier inventory and extraction token counts would give 446,032 tokens for the combined workflow; only the four new comparisons were incurred in this experiment.

Three comparisons returned complete, internally consistent judgments. The second leave response ended `MAX_TOKENS` after 57,181 thinking tokens and 8,340 answer tokens, despite the application omitting a token cap. Its incomplete JSON is preserved. The evaluator records `provider_incomplete`, `malformed_audit_response`, and `invalid_comparison_wrapper`, marks all 28 units unknown and sets `review_complete=false`. We cannot assess its semantic findings.

## What improved

- The first leave comparison still finds the nonconsecutive-month rule missing from accepted output after Core rejected the extraction's kind/modality combination.
- Both display comparisons recognize the parent requirement jointly across its constituent duties. They now call it partial because of individual warnings, rather than demand a duplicate parent record.
- The second display comparison no longer mistakes `alternative_quotes` for an OR operator or requires optional relationship records. Its previous seven inconsistent coverage judgments are gone.

## What remains wrong or uncertain

Both display comparisons introduce a new alternatives warning: a single evidence paragraph contains the paper and electronic inspection-record options instead of separate strings for each option. Both options and the signature qualifications are already explicit in `summary` and `choice_text`. This is not evidence of a missing alternative.

The upstream CUE wording asks for every leaf option, while the provider selects passage IDs. Several options can share a passage. The next small change should clarify that one evidence passage may support multiple explicitly represented options. Do not make the checker demand substring selections the acquisition schema cannot express.

New summary warnings often identify real weaknesses in standalone prose while `scope_text` or `logic_text` preserves the condition. For example, the accounting claim's summary omits the exceptions but its `logic_text` contains the full exception lead-in. The checker still fails to acknowledge that retained meaning consistently. Partial coverage counts therefore mix wording quality, representation complaints and semantic defects; they are not an extraction accuracy score.

Existing inventory weaknesses remain unchanged, including descriptive possibility treated as background and non-prohibition treated as permission. The truncated leave comparison cannot demonstrate continued detection of the teacher wording and future-headcount example. This experiment does not repair any extraction or establish complete coverage.

These observations are a revisable source review, not gold labels. Saved controls were not rerun alongside treatments; one treatment per draft across two documents cannot isolate prompt effects from model variation.

## Next decision

Retain the small CUE guidance integration. Before another expensive whole-document audit, clarify evidence granularity in the existing CUE descriptions and test the inspection-record case in isolation. Keep wording findings distinct from wholly omitted meaning when interpreting the current reports. A smaller audit of specific suspected defects is worth testing, but neither its quality nor its cost has been established here.

## Verification and saved evidence

333 package tests and 11 focused audit tests passed. The existing end-to-end test checks that generated CUE descriptions reach comparison requests and remain absent from inventory requests. All four saved responses replay identically, including the incomplete response; this checks processing reproducibility, not model correctness.

`design.json` pins inputs and runtime; `criteria.json` records the predeclared checks. `runs/` preserves configuration, requests, raw responses, judgments, reports and frozen runtime with per-run hashes. `source-review.json` contains exact selected draft fields and control/treatment judgments for eight revisable findings. `verification.json` contains coverage, issues and usage for each pair; `results.json` totals the experiment.

Run the comparison-only verifier without provider calls:

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/audit-field-guidance/verify.py
```

The original pinned `experiment.py replay` shortcut incorrectly uses the extraction-specific manifest validator, which requires artifacts absent from a comparison-only capture. `verify.py` supplies the correct comparison-only verification: hashes, required artifacts, frozen runtime, source audit, exact request differences and deterministic judgment/report replay. The acquisition script and original captures remain byte-for-byte intact. Use `verify.py` for replay.

Work is local and uncommitted. The surrounding worktree includes earlier changes outside this experiment.
