# The audit does not reliably distinguish incomplete wording from retained logic

The current audit **missed the original notice failure in both repeats**. It
detected a scope problem in both versions with more complete source logic, but
only one of those also received a summary error. Neither rationale explicitly
distinguished qualifications retained in `logic_text` from incomplete standalone
wording. Both complete-statement controls passed. The preregistered gate is unmet.

These are misses against the declared standalone-use criterion, not claims that
the bare permission is universally legally false. The source, user-facing use case
and application field definitions determine the required level of completeness.

## Controlled inputs

Six fresh comparisons used the same full 4,360-character notice source, all 18
draft claims, the same 18 fallible inventory units, the current comparison prompt
and schema, and `gemini-3.8-flash` at temperature 0 with medium thinking. No numeric
thinking budget or application output cap was set. Two repeats per input ran in
randomized order: C1, A1, B2, B1, C2, A2. No new inventory, extraction, repair or
retry was performed. See the [preregistered plan](PLAN.md).

- **A — historical failure:** C0014 has a short unqualified statement and empty
  scope. Its 884-character logic includes unusual/emergency circumstances but
  starts after the unforeseeability lead-in.
- **B — complete logic:** the same statement and empty scope, with the source
  selection and logic extended to the exact 1,045-character F003:F004 range.
  Corresponding main/logic evidence offsets change together. This is a constructed
  source-selection bundle, not an isolated single-field change.
- **C — complete statement:** B with only the statement changed to explicitly
  retain unforeseeability, unusual circumstances and the emergency exemption
  until stabilization AND phone access AND ability. This is a constructed control,
  not a new provider extraction or authoritative legal interpretation.

Every other model-facing claim and inventory field stayed identical. A and B
both retain this statement:

> An employer may require employees to call a designated number or a specific individual to request leave.

The original fixture and Core graph remain untouched. Experimental draft views
contain document/claim data for comparison only, with a separate target identity.
Their source and authorship are recorded in `design.json`; they are not newly
validated Core graphs, approvals or review-history changes. No Core Findings were
written for these constructed views. The comparison used the existing input,
capture, parser and accounting functions without prompt/schema/runtime changes.

## Results against the declared criteria

| Input | Summary error | Scope error | Complete field-specific explanation | Audit report |
|---|---:|---:|---:|---|
| A: original failure | 0/2 | 0/2 | 0/2 | passed twice |
| B: same wording, full logic | 1/2 | 2/2 | 0/2 | failed twice |
| C: complete statement | 0/2 | 0/2 | Not an omission case | passed twice |

Both C summaries were judged correct, as expected. Both A summaries were also
judged correct, contrary to the declared criterion. For example, A1's rationale
says the claim “correctly captures the example of employer policy options.”
B1 flags an unconstrained permission and missing unforeseeable-leave context,
but does not say that this context is already present in explicit logic.
B2 accepts the summary while criticizing empty `scope_text`.

All six target judgments select **F003:F004**, including the governing lead-in.
Thus the auditor can select the complete supporting source even while overlooking
the draft's incomplete wording. The problem is not refusal of audit evidence.
The result does not establish why the model treated A and B differently; input
presentation and run variability remain plausible. More complete logic was not
credited consistently according to the existing field instructions.

The unchanged first-time exemption, subsequent-notice alternative and emergency
exemption received correct verdicts in all six calls. Their abbreviated rationales
do not prove each emergency prerequisite was individually checked. B2 also flags
the two previously known `not_stated` versus should/expected classifications;
keep those disputed label decisions separate from the primary result. There were
no other claim error verdicts. The [masked review](blind-review.md) was saved before
opening the arm key. It is a primary-agent self-review with known design and
revisable labels, not independent validation.

## Verification, failures and cost

Every call returned 18 claim and 18 inventory judgments: **216 judgments total**,
with no parsing/accounting issues. All 216 selected evidence spans match original
source offsets. Reciprocal accounting completed in all six reports. Actual
requests match the frozen input variants, schema and settings. All six comparisons,
derived judgments and reports replay identically without provider calls.

The first replay command failed with `ReplayDriftError: The run manifest omits a
required artifact`. This was a harness error: `run.py` used an extraction-specific
manifest verifier on comparison-only captures. The original frozen runner and all
observations remain intact. `replay.py` supplies a complete-file-set/hash verifier
for the comparison capture format, then runs the same request reconstruction,
judgment parsing and accounting. This does not waive any artifact hash or semantic
check. The failed attempt and correction are recorded in `verification.json`.

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/audit-field-distinction/replay.py
```

Preparation and live-run modes are historical capture tools; do not rerun them
over these saved artifacts. Replay requires the pinned runtime, saved once under
`frozen/`. Full requests/responses, inputs, derived reports and metrics are retained.

| Input | First call reported tokens | Second call reported tokens |
|---|---:|---:|
| A | 51,651 | 52,656 |
| B | 63,361 | 53,594 |
| C | 52,209 | 53,060 |

The six comparisons used **326,531 provider-reported tokens**. Each request reports
roughly 45,000 input tokens because the audit input repeats source evidence across
claims and inventory. Several calls report cached input; cached counts are subsets
of input, not additional tokens. Reported thinking varied from 1,088 to 12,580
tokens despite fixed medium thinking and temperature 0. Do not treat total token
counts as billed dollars or infer hidden reasoning quality from thinking volume.
Per-call timing, usage and exact target judgments are in [metrics.json](metrics.json).

## Decision

The current audit can produce useful review findings, but this experiment does
not support using it as an automatic guarantee that standalone rules preserve
their conditions. A `passed` report with valid evidence can still miss this known
profile failure. The existing `semantic_completeness: not_established` limitation
is therefore material, not boilerplate. No production change is adopted.

Stop the six-call comparison here. The prior wording and passage experiments plus
this audit test do not justify more instruction patches on the same sentence.
A useful next evaluation would test the audit on independently selected, materially
different losses of negation, alternatives, actors and deadlines, with exact sources
and clearly labeled constructed controls. That would distinguish a general audit
reliability problem from this context-inheritance criterion. Keep current findings
advisory and preserve source review before deriving executable workflows. This
broader evaluation is proposed, not executed; the overall research endpoint is
awaiting the user's requested outcome. Research remains local and uncommitted.
