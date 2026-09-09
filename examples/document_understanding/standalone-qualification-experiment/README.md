# Standalone qualification: description change did not improve the target cases

Keep the current production schema. This eight-call experiment found no incremental
qualification benefit from replacing the general statement description with a
concrete standalone-consumer check. Both versions preserve the passport duty's
local-adaptation qualification; both omit the notice permission's governing
conditions from its statement and scope. The preregistered adoption gate is unmet.

## What was tested

One documentation paragraph in native CUE `#Summary` changed. The existing CUE
generator produced the experimental schema; no parallel schema implementation or
new fields were introduced. The existing example-inheritance paragraph stayed.
Saved requests verify that this one statement description is the only provider
schema difference. Prompts, field order, examples, model settings, parsing and Core
conversion stayed fixed. Production files were not edited.

Each arm extracted three full saved documents and one constructed control document
once: `gemini-3.8-flash`, temperature 0, low thinking, no numeric thinking budget or
application output cap. All fit one window. There were eight calls, no audit,
repair, retry or post-result tuning. See [PLAN.md](PLAN.md),
[schema-change.json](schema-change.json), and [design.json](design.json).

## Source review

| Check | Baseline B | Treatment T | Interpretation |
|---|---|---|---|
| Passport cleared-language duty retains authorized local adaptation | Pass | Pass | Earlier failure not reproduced; no measured improvement |
| Notice designated-number permission retains governing conditions in statement and scope | Fail | Fail | Target omission remains |
| Waste exception tree, both label components, three-day alternatives and interim duties | Pass | Pass | No material meaning regression identified in these groups |
| Three constructed independent-rule scenarios | Pass | Pass | No condition contamination observed |

The [masked review](blind-review.md) was written before opening
[review-key.json](review-key.json). This was a self-review with masked labels, not
an independent blind assessment: the reviewer knew the treatment and call counts.
The labels are revisable engineering judgments, not legal authority or evaluation
gold. These selected development cases and one sample per cell establish neither
general accuracy nor repeatability.

Passport's complete duty statement is identical in both arms. Both also keep the
local-adaptation permission separately. Their duty scopes identify posts but do
not repeat the adaptation qualification; `logic_text` is empty. Statement success
does not imply perfect adherence across every field.

Notice row 14 is **identical in the raw responses**, including all its fields:

> An employer may require employees to call a designated number or a specific individual to request leave.

Both select `F004` for the unit and logic, with no scope selection or scope text.
`F004` begins “the employer's usual and customary notice…” after the governing
unforeseeability lead-in in `F003`. Its retained text includes unusual circumstances
and emergency exceptions, but the short statement does not. The separate general
duty and emergency exemption remain complete. The latter preserves stabilization
**and** phone access **and** ability to use the phone. The problem is incomplete
standalone meaning and missing selected context, not a converter deleting text.

Treatment labels two notice “expected” clauses `should`; baseline labels them
`not_stated`. Both preserve their prose. This unplanned classification difference
requires a separate rubric decision; it is not evidence of qualification repair.
Both label emergency written advance notice `not_required` in this pair.

Waste T groups the opening permissions, accounting for its lower record count.
Their meanings survive. T also produces **two new `scope_evidence_incomplete`
warnings**: small- and large-generator scopes have no dedicated `scope_quotes`.
The statements and their main evidence retain those actor conditions. This is an
evidence-binding regression, even though the selected semantic checks pass. Neither
arm satisfies every possible standalone-context expectation for every waste row.

## Processing, source grounding and cost

All eight runs completed: **106 accepted records, zero rejected records, zero
parser refusals**. All 420 retained evidence spans match their original source
offsets. The model's statements, scope wording, choices, kinds and modalities
survive conversion unchanged; all selected logic passages resolve unchanged.
Component warnings and unresolved references remain preserved in the captures.
These mechanical checks do not establish complete meaning or coverage.

| Case | B records | T records | B reported total tokens | T reported total tokens |
|---|---:|---:|---:|---:|
| Passport | 16 | 15 | 5,084 | 4,897 |
| Notice | 18 | 18 | 6,282 | 6,264 |
| Waste | 14 | 13 | 8,517 | 8,643 |
| Controls | 6 | 6 | 2,587 | 2,577 |
| Total | 54 | 52 | 22,470 | 22,381 |

All calls used **44,851 provider-reported tokens**. Treatment used 0.4% fewer total
tokens and 0.7% fewer output tokens in this sample, too little evidence for an
efficiency recommendation. Summed attempt durations were 41.608 seconds for B and
33.477 seconds for T; these sequential single observations are not a latency
benchmark. The provider reported identical input-token counts per pair despite the
schema-description change and no separate thinking-token count. Do not infer exact
schema billing or zero thinking from that metadata. No dollar estimate is made.

Eight local full-workflow replays reproduce the saved rulebooks and result metadata
exactly, without provider calls. [metrics.json](metrics.json) records warning counts,
unresolved counts, grounding checks, tokens and timings. To reproduce verification
under the saved runtime (the harness checks source hashes):

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/standalone-qualification-experiment/run.py replay
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/standalone-qualification-experiment/measure.py
```

The second command prints the saved metrics. The original live-run and preparation
commands are historical capture tools; do not rerun them over these saved artifacts.
Raw requests, responses, exact sources, generated schemas, frozen runtime, Core
records and refusal history are retained under this directory. No production
change, commit, push or release is included in this iteration.

## Next useful hypothesis

Stop this description-tuning line. Existing guidance already asks for complete
meaning, and the concrete replacement did not change the persistent notice row.

A better focused diagnostic is whether a **layout boundary inside a governing
sentence** contributes to losing its condition. Current `documents.source_passages`
splits at blank lines; the saved notice contains such a break between “comply with”
and “the employer's…”. The model receives both pieces and can select `F003:F004`,
but chooses `F004` for the permission in both arms. This observation motivates a
hypothesis; it does not prove the boundary caused the omission, especially because
exceptions already within F004 are also absent from the statement.

Proposed next experiment, not yet executed: retain source bytes, offsets, prompt,
schema and model settings, but compare the existing catalog with a diagnostic
catalog that joins only this known sentence break. Repeat the notice pair twice;
also compare one same-actor and one different-actor independent-rule control
document with separate versus joined adjacent passages, for eight calls total.
Require both notice treatment runs to preserve the full standalone qualifications,
with an improvement over baseline in each pair and no fabricated dependency in
either control. Check statement, scope and selected evidence separately. If only
the quote gets longer, count grounding improvement only. Save all failures and
stop after eight calls. A successful diagnostic would still need a general boundary
policy and new-source checks before changing production; no automatic sentence
joining, inferred condition links or fuzzy matching is justified by this result.
