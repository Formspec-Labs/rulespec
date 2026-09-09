# Shared evidence for alternatives

The existing CUE descriptions now allow one passage to support several alternatives while requiring all options and qualifications in explicit meaning. The extractor and audit inherit this clarification through generated schemas. No validation constraints changed.

## Results and decision

The clarified description removes the shared-passage alternatives false alarm in this test and retains detection of both deliberately introduced omissions. Keep the small CUE clarification. The broader complete-record acceptance criterion did not pass; see the fixture limitation below.

| Rule version | Old alternatives verdict | Clarified alternatives verdict | Clarified coverage |
|---|---|---|---|
| Both options and signatures retained | error | correct | partial: neighboring record-content duty |
| Electronic option missing | error | error | partial |
| Electronic signature missing | error | error | partial |

The new missing-option rationale correctly explains that paper-only wording removes a permitted option. The new missing-signature rationale correctly explains that it permits unsigned electronic records. Both retain the complete evidence paragraph, so the checker is detecting omissions from meaning rather than assuming quotation coverage is sufficient.

All six responses ended STOP, passed structural/evidence checks and replayed identically. The original broad criteria pass 2/3 cases under each prompt; the complete case fails in both. The alternatives dimension improves from 2/3 to 3/3 expected verdicts in this single small sample. This narrower observation does not replace the predeclared broad result.

Total usage was **167,614 tokens**, including **147,043 thinking tokens (88%)**. Although requests contain only one claim, high thinking remains expensive. The old descriptions used 75,298 tokens; the clarified descriptions used 92,316. Each clarified input is 44 tokens longer. Do not attribute the reasoning-token difference causally to the edit from this sample.

Next: correct the isolated fixture to supply the adjacent record-content claim or trim its source evidence consistently, then test cheaper thinking on the same complete/omission cases. These follow-ups are saved, not executed. No further calls, automatic fixes, UI changes or commits were made.

## Test design

Six Gemini `gemini-3.8-flash` calls compare the old and clarified descriptions on three versions of one saved display rule:

1. Both signed paper and officer-signed electronic options retained.
2. Electronic option removed from summary and choice_text.
3. Electronic signature requirement removed from summary and choice_text.

Every version retains the complete source evidence. All versions leave logic_text empty so the deliberately removed meaning cannot survive there. All other claim fields, the inventory unit and source/context are identical. The source is the saved inspection paragraph plus its governing after-sunset lead-in. The original full draft and source inventory were not edited.

The calls use high thinking, temperature zero, no numeric thinking budget and no application output cap. No retries, new inventories, extraction calls or automatic repairs. There is one observation per cell, so the experiment can demonstrate a behavior but cannot estimate general accuracy or isolate all model variation.

## Limits of the complete case

The source paragraph also contains a second duty about the contents of an inspection record. The saved extraction represents that duty in a separate claim. This isolated test supplies only the alternatives claim, and clears logic_text in every fixture. Therefore the broad predeclared criterion (no errors and covered) can fail on that adjacent content even if the alternatives are complete. The exact original criterion remains recorded; do not silently redefine it as an overall pass.

This is a targeted comparison-stage test. It does not establish end-to-end extraction quality, full-document audit accuracy, or preserved behavior under different thinking levels.

## Verification

Native CUE regeneration and its drift check pass. All 34 focused schema/audit tests pass. Comparing generated schemas with the prior frozen schemas after removing titles/descriptions confirms identical validation constraints.

The design pins fixtures, criteria, prompts, comparison schema, acquisition script and runtime before the calls. Raw requests, responses, judgments and per-run hashes are retained in runs/. The original older experiments retain their original frozen schemas and manifests; changed live schemas intentionally trigger their runtime drift checks.

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/alternative-evidence-experiment/experiment.py replay
```

Replay makes no provider calls and checks pinned inputs/runtime, raw capture hashes, request text, schema validity, source quotes, aliases and reciprocal links, and deterministic result equality. It requires this experiment's pinned runtime. Structural checks do not prove the judgments correct.
