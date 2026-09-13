# Repair iteration closed; verified extraction/review baseline retained

**Decision: do not adopt sparse repair output. Close this iteration.** Neither
format repaired the selected fresh-document meaning gaps. The local installed
tool has been refreshed to the already committed provider/identifier fixes and
verified through tests and saved-run replay/export. No new repair behavior,
standalone checker, default pass or application schema was added.

The usable baseline remains document → source-linked draft records → review and
export. It supports discovery and review of future workflows; it does not certify
that every statement contains all governing meaning. Use concrete documents and
feedback to decide whether to reopen repair work. No further experiment is queued
by this closeout.

## What was tested

The [frozen plan](PLAN.md) compared full replacement fields with optional changed
fields derived from the same CUE-generated schema. Sparse edits retain omitted
values deterministically before the existing decoder and review checks. The
semantic task, source, selected statements, navigation, warnings, model and
settings stayed fixed. This tests a scoped repair request, not the entire existing
multi-pass `refine` command. Both arms include the positive complete-reading task
alongside the original recovery guidance.

Four previously unused archived US Code excerpts produced ordinary extractions:
FOIA timing, denial notice, pension benefit statements and accommodation. They
yielded 43 accepted records and one rejected kind/modality contradiction. No
source or extraction was replaced. Five fresh default-meaning gaps, two complete
controls and two uncertain readings were selected before repair generation.
The accommodation subtree lacks its ancestor's force-setting introduction;
its readings were excluded from decisive scores before generation. That is a
limitation of this excerpt selection, not evidence that the production reader
dropped an ancestor from a supplied complete document.

The exact saved pension carryover failure and a constructed wrong-actor field
completed six case inputs. Every input ran twice per format: 24 generation calls
after four ordinary extraction calls. Repairs used `gemini-3.8-flash`, medium
thinking and 32,768 output tokens, with provider-managed sampling. Initial
extractions used production low-thinking defaults. See [baseline criteria](BASELINE-REVIEW.md)
and [source receipt](source-receipt.json); this is an archived-source study, not
a claim about current law or overall extraction accuracy.

## Results

| Outcome after native validation | Full replacement A | Sparse edit B |
| --- | ---: | ---: |
| Complete fresh meaning repairs | 0/10 | 0/10 |
| Complete controls preserved | 4/4 | 4/4 |
| Known pension repair | 2/2 | 2/2 |
| Constructed actor correction | 1/2 | 2/2 |
| Uncertain accommodation readings | 4 excluded | 4 excluded |
| Proposals returned / valid previews | 4 / 3 | 6 / 6 |
| Proposals emitting every meaning field | 4/4 | 5/6 |

The ten fresh repair opportunities per arm are **five selected readings repeated
twice across three excerpts**, not ten documents. The fourth excerpt supplies
the uncertainty cases. Raw responses were manually read before aggregate scoring,
with no model-checker verdicts available to influence the labels. The experiment
designer performed that review; shape can reveal the arm. Preserve this limitation
and the source-bound criteria rather than treating the labels as gold answers.

Examples from the [raw review](RAW-GENERATION-REVIEW.md):

- FOIA: neither format incorporated the supplied start of the twenty-day clock,
  its narrow tolling situations or the response that ends tolling. Several
  responses discussed unavailable external references instead.
- Denial: full replacement returned no edit because required grounds/exceptions
  existed in another record. Sparse output made two modality/evidence edits while
  leaving the selected default meaning incomplete. These narrowed the selected
  evidence without deleting the original source or the other record.
- Benefits: both formats called the three-year duty and annual-notice alternative
  complete while leaving their mutual meaning behind paragraph references.
- Actor counterexample: both formats generated the right Secretary correction.
  One full replacement also generated non-verbatim optional `logic_text`, causing
  refusal of that correction. Sparse output avoided that refusal in this small
  constructed case, but still emitted full fields and unnecessary enrichment.
- Sparse pension cell 10 returned only three fields and complete prose, but
  populated action/object without their quotes and added no direct evidence for
  the incorporated eligibility text. Native preview preserved explicit unresolved
  component warnings. Mechanical validity and complete evidence remain distinct.

The fresh-repair requirement fails for both the quality-gain and cost-gain adoption
routes. The narrower actor result cannot substitute for it. Neither interpretation
of the uncertain accommodation force, nor excluding the debatable breadth of the
denial content criterion, can produce a fresh repair gain: there were no proposals
for the FOIA or benefits meaning gaps either.

## Costs and the stopping decision

| Generation measure | A | B |
| --- | ---: | ---: |
| Calls | 12 | 12 |
| Prompt tokens | 117,230 | 117,686 |
| Answer tokens | 5,356 | 4,089 |
| Thinking tokens | 38,819 | 54,013 |
| Total tokens | 161,405 | 175,788 |
| Summed call seconds | 128.4 | 166.6 |

Sparse output used 23.7% fewer answer tokens but **8.9% more total generation
tokens**, with more thinking. It emitted 111 unchanged fields versus 72 in A,
partly because it made two additional denial edits. Smaller answer size did not
establish cheaper useful repairs. These are recorded tokens, not invoice prices;
cached prompt tokens are already included in prompt counts.

All 28 calls completed without retries: **358,675 total tokens**, including the
four initial extractions, and 324.9 summed call seconds. At the completed manual
generation review, neither adoption route could pass regardless of checker
verdicts. Stop there under the plan's decision rule. The optional 24 advisory
checker calls were skipped; checker agreement and generation-plus-check cost
remain **unmeasured**, not zero. [Scores](scores.json), [usage](usage.json),
[stop receipt](check-skipped.json).

The old recovery language discourages duplicate meaning and describes later
relationship work, while the added task asks for independently complete selected
statements. Some responses explicitly follow the former interpretation. That is
a plausible instruction conflict, not an isolated causal finding. The response
format comparison does not justify another prompt patch or more tuning here.

## Validation and actual local delivery

All four native extractions replay identically. All 24 generation inputs, actual
requests, responses and decodes reproduce with provider access blocked. All nine
valid proposals also apply through the existing review/export path in disposable
workspaces, with exact deterministic replay of the resulting records and export
hashes. Original source and unselected records remain intact; the resulting
records are not approved. This is a **mechanical application rehearsal**, explicitly
including the incomplete denial edits, not semantic approval or checker acceptance.
See [verification](verification.json) and `applied/`.

The relevant source refinement/schema tests passed 60 tests. Delivery checks then
found that the working command-line installation predated the already committed
Gemini request-setting and identifier fixes: eight packaged files differed.
The current wheel was built and installed with dependencies unchanged. All **33
package files match the checkout**; 92 installed packages pass dependency checks.
The complete installed application suite passed **709 tests** from outside the
checkout. Four public CLI replay/export pairs match the source results. See
[delivery receipt](delivery.json) and [installed test log](installed-tests.log).
The wheel remains local; no package publication, push or deployment occurred.

One instrumentation issue is preserved: a mutable call ledger was accidentally
included in generation pins. The run stopped locally after cell 01, before a
second provider call. Only the pin-file selection/exclusion was corrected; every
request, source, setting and label stayed fixed. The original pins and runner
remain alongside the [correction note](INSTRUMENTATION.md). Cell 01 was retained,
not retried.

## Reproduce the saved result

From the repository root, using the recorded dependencies:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-repair-finish/verify.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-repair-finish/score.py
```

The experiment is closed; do not rerun `prepare`, `generate` or the unused optional
`check` stage against its immutable inputs. Source/runtime pins refer to the
recorded checkout and neighboring saved captures. `MANIFEST.json` identifies all
retained artifacts; the installed wheel's receipt identifies its exact bytes.
The [closed task list](../../plans/2026-09-13-model-input-improvements.md) and package
[operating guide](../../../packages/rulespec-extrapolator/README.md) distinguish
usable behavior from deferred research.
