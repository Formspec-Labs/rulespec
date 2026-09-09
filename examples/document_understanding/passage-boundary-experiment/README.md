# Larger passages retain context but do not fix standalone meaning

**The target remains unsolved.** Joining a layout break inside the governing
sentence preserves the missing lead-in in the notice permission's selected
evidence in both treatment runs. All four notice outputs still produce the same
unqualified statement. One treatment run partially improves scope. The declared
semantic gate is unmet; no production boundary policy is adopted.

This follows the [description experiment](../standalone-qualification-experiment/README.md),
which found no target improvement from stronger standalone-statement wording.
The [preregistered plan](PLAN.md) tested a different explanation using the current
production schema and normal extraction/capture/replay functions.

## What changed

The baseline splits the notice's governing sentence at a blank line into F003
and F004. The experimental catalog replaces those two entries with one F003
covering the original offsets 3315–4360. All source bytes, including the blank
line, remain unchanged. The model receives the same complete 4,360-character
source, instructions, schema and examples. Only catalog granularity and its ID
presentation change. Source records in the document itself are not rewritten.

Two repeated notice pairs and two constructed control pairs used eight fresh
`gemini-3.8-flash` calls, temperature 0, low thinking, and no application output
cap or numeric thinking budget. There were no retries, audits or repairs.
Actual requests match their frozen catalogs and otherwise unchanged configuration.

## Outcomes

| Target field or control | Baseline | Joined passages |
|---|---|---|
| Notice statement contains complete governing qualifications | 0/2 | 0/2 |
| Notice scope contains unforeseeability | 0/2 | 1/2 |
| Notice scope contains all required qualifications | 0/2 | 0/2 |
| Notice selected logic includes the governing lead-in | 0/2 | 2/2 |
| Both simple controls preserve independent meanings | 2/2 | 2/2 |

Every notice run emits this same statement:

> An employer may require employees to call a designated number or a specific individual to request leave.

The first treatment scope is empty. The second says:

> When the need for leave is not foreseeable, as an example of an employer's usual and customary notice and procedural requirements

That is partial improvement: the unusual-circumstance and emergency limits are
still absent from the scope, and the statement is unchanged. Both treatment
logic quotations now include the complete subsection. Because passage selection
returns the whole chosen passage, the larger quotation is an expected mechanical
effect of the intervention, not proof that the model understood more of it.

All four preserve the separate general notice duty, unusual-circumstance exception,
information alternatives, first/subsequent leave distinction, and emergency
exemption with stabilization **and** access **and** ability to use a phone. The
simple controls retain staff's signing duty separately from an optional blue pen,
and visitors' notice-on-arrival duty separately from staff's remote-work permission.
Neither joined control invents a dependency or waiver. This does not establish
that arbitrary paragraphs can safely be joined.

Modality remains variable: notice treatment 1 labels emergency written advance
notice `possible`; the other three label it `not_required`, while preserving the
same source wording. The two “expected” clauses are `should` in baseline 1 and
`not_stated` in the other three. These are unresolved classification differences,
not successful repairs. The [masked source review](blind-review.md) preserves
the field-specific judgments and other details. It preceded opening the arm key,
but the reviewer designed the experiment and longer quotations reveal its shape;
this is not independent blind validation.

## Verification and cost

All eight extractions completed with **80 accepted records, zero rejected records
and zero parser refusals**. All 314 retained evidence spans match exact source
offsets. Raw statements, scopes, choices, kinds and modalities survive conversion
unchanged; logic selections resolve unchanged under each saved experimental
catalog. Component warnings and unresolved references remain in the captures.
Fewer warnings or retained spans in a run do not establish higher quality.

All eight full replays and result metadata match without provider calls. Replay
must use this harness because it reinstates the experimental catalog; ordinary
production still uses the original catalog. The captures retain the normal frozen
runtime, and `design.json` additionally pins this harness and its explicit override.

| Pair | B reported total tokens | T reported total tokens |
|---|---:|---:|
| Notice 1 | 6,392 | 6,345 |
| Notice 2 | 6,382 | 6,435 |
| Same actor | 1,846 | 1,831 |
| Different actors | 1,865 | 1,865 |
| Total | 16,485 | 16,476 |

The experiment used **32,961 provider-reported tokens**. The nine-token difference
between arms is negligible; no cost advantage is established. Summed attempt
durations were 37.48 seconds for B and 25.82 seconds for T. These observations
are saved, but this small sequential run is not a general latency benchmark.
Provider usage has no separate thinking count; no dollar estimate is made.
Detailed counts and raw target records are in [verification.json](verification.json)
and provider metadata is in [results.json](results.json).

To verify replay from the repository root with the captured runtime:

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/passage-boundary-experiment/run.py replay
```

The preparation and live-run modes are historical capture tools; do not rerun
them over these artifacts. Replay is local processing evidence; the two fresh
notice repeats measure within-case behavior, not generalization to new documents.
All semantic labels here are revisable engineering judgments on selected
development material and constructed controls, not legal authority.

## Decision and next direction

The strong boundary hypothesis did not meet its predicted standalone-meaning
outcome. The narrower context-retention prediction did: joining made the complete
governing source available in the selected quote twice. The experiment cannot
distinguish different hidden reasons for the unchanged statement. It does show
that fixing this boundary alone is insufficient on this case, and confirms the
omission exists in the model response before Rulespec conversion.

Stop here at the eight-call bound. Across this and the preceding description
experiment, neither intervention justifies a production change. Keep full source
evidence available for discovery and review; do not treat the short statement
as a complete independently executable rule.

The next useful decision concerns the existing audit: can it distinguish a
qualification missing from the statement but present in its evidence from a
qualification absent from both? Use these saved field-specific failures and a
clearly labeled constructed complete version as controlled inputs. Measure that
distinction before adding another extraction instruction or automatic repair.
This audit comparison has not been run here. A generic sentence-boundary policy,
new schemas, fuzzy matching and automatic condition inheritance remain unjustified
by this diagnostic. Research is saved locally; no commit, push or release was made.
