# The audit catches explicit contradictions in these four controls

The existing audit identified **all four planted errors** and accepted their four
original counterparts. It did not propagate those errors into the named neighboring
correct rules. The preregistered sensitivity criterion passes on these selected
cases. This does not resolve its earlier misses of inherited qualifications or
establish a general detection rate.

## What was compared

Four fresh comparisons used the complete saved passport introduction and Ohio
waste rule, their full draft records and frozen source inventories. Each document
had one original-draft control and one constructed corrupted draft containing two
changes. All original source text, quotations, logic and evidence offsets remained
intact; only the declared meaning fields changed. Exact edits are recorded in
[mutations.json](mutations.json).

Current production comparison instructions, schemas and processing stayed fixed:
`gemini-3.8-flash`, temperature 0, medium thinking, no numeric thinking budget or
application output cap. Randomized order was passport/B, waste/A, waste/B,
passport/A. There were no extra inventory/extraction calls, retries or repairs.
See [PLAN.md](PLAN.md). Original captures and Core graphs remain untouched; the
diagnostic views are not newly approved or rewritten Core records.

| Planted change | Audit finding | Original control |
|---|---|---|
| Assign agencies/centers' IRL restriction to posts | Names the wrong actor and scope; summary/actor/support/scope errors | Correct |
| Turn INs' no-response exemption into a response duty | Names the reversed exemption; summary/modality/support/action errors | Correct |
| Replace both label components with either component | Identifies the AND-to-OR mismatch; summary/alternatives errors | Correct |
| Replace three calendar days with thirty | Names the wrong deadline in summary and choice text; summary/threshold errors | Correct |

All four altered summaries received errors with specific reasons. The corresponding
inventory units became partial. The correct nearby IN-change restriction and
closed-container exception tree remained correct. No additional claim error
verdicts appeared. Both original documents received `passed`; both corrupted
documents received `failed`, all with complete mechanical review accounting.

One explanation overreaches: the waste-label rationale calls either/or “mutually
exclusive.” The planted wording makes either component sufficient but does not
clearly prohibit providing both. The AND-to-OR detection is correct; the exclusivity
claim is unsupported. Preserve that distinction instead of treating the entire
rationale as gold.

The [masked review](blind-review.md) was saved before opening the arm key. The
primary agent knew the design, and rationales revealed the likely mutations. These
are revisable judgments on constructed changes and already-used development
sources. One call per arm, two coupled errors per corrupted document and only two
documents limit conclusions about repeatability, isolated causes and generalization.

## What this changes about the recommendation

Correct source quotations do **not always** hide faulty extracted meaning: the
auditor caught these direct contradictions despite intact original evidence.
That supports using the existing audit for review triage of wrong actors, reversed
force, changed alternatives and incorrect deadlines.

It does not establish complete rule meaning. Both passport runs still accepted
the known short cleared-language duty without identifying its standalone local-
adaptation qualification issue. The preceding
[field-distinction experiment](../audit-field-distinction/README.md) also missed
the original notice scope failure twice despite selecting the correct governing
source. The observed distinction is between these explicit planted contradictions
and the tested context-inheritance failures; it does not prove a hidden model
mechanism or universal boundary between easy and hard errors.

Keep low extraction for discovery with source passages and logic available. Use
the existing medium audit when its findings help prioritize review. For executable
workflows, a passed audit does not replace source review of governing conditions,
exceptions and affected actors. No new schema, prompt patch, fuzzy matcher or
automatic approval rule follows from this experiment.

## Verification and cost

All four comparisons returned complete, reciprocal judgments with no parsing or
accounting issues: **60 claim judgments and 72 inventory judgments**, supported by
225 exact source spans. All recorded requests match the frozen inputs/settings.
Every comparison, parsed judgment and report replays identically without provider
calls. Actual counts, target rationales, evidence references, usage and timings are
saved in [metrics.json](metrics.json).

| Call | Provider-reported total tokens |
|---|---:|
| Passport, original | 25,103 |
| Passport, corrupted | 28,832 |
| Waste, original | 54,210 |
| Waste, corrupted | 55,557 |
| Total | 163,702 |

These counts include reported input/output/thinking usage; any cached-input count
is a subset of input, not additional tokens. This is not a billed-dollar estimate
or a latency benchmark.

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/audit-mutation-sensitivity/run.py replay
```

Preparation and live-run modes are historical capture tools; do not rerun them
over saved observations. Replay verifies the full comparison file sets and hashes
before reconstructing requests and rerunning the existing parser/accounting.
Runtime source files are pinned once under `frozen/`.

The four-call experiment is complete. Its result supports preserving the current
workflow with a clearer understanding of what the audit can help detect. The
[consolidated recommendation](../../../thoughts/reviews/2026-09-09-extraction-quality-decision.md)
combines this result with the three preceding experiments. Research is local and
uncommitted; no production change, approval or release was made.
