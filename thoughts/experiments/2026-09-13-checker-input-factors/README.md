# Checker input factors: comparison helps here; cause remains unresolved

The standalone checker again rejects complete leave wording for record-status
concerns. Adding current `link_issues` does not change correctness counts in this
test. Keeping competing edits yields **8/8 correct unchanged-reading judgments**;
checking the reading alone yields **6/8**. This is a directional observation on
two known excerpts, not a proven mechanism or a production adoption result.

The preregistered mechanistic-lead gate is **unmet**: neither failing condition
fails in both repetitions. Keep the standalone prototype deferred. No production
code, schema, default extraction behavior or stored review status changed.

## Controlled comparison

The [plan](PLAN.md) crossed competing edited candidates present/absent with
saved raw-book/current review `link_issues`. Each of the four conditions received
the same leave failure and hazard control twice: sixteen fresh, shuffled calls.
Both selected default readings are complete for the supplied source under the
frozen earlier labels. The other candidates test a wrong meaning, an unnecessary
component fill and a cosmetic rewording with an unnecessary fill. This comparison
does not test accepting needed repairs or generating them.

Source, default meaning, component fields, evidence, existing `issues`, existing
`reference_links`, navigation, candidate policy, selected target and schema stay
fixed. The status change adds details without clearing any stored warning. The
unchanged candidate is always `N0000`; the rich requests substitute that identifier
for their earlier no-change ID while retaining the other candidates' relative
order. All candidates remain independent alternatives.

Arm D exactly reproduces the previous integration bridge's actual leave cell 07
and hazard cell 03 requests. Both status interventions change the actual prompt.
[Input checks](input-checks.json) and the saved requests establish these facts;
the comparison is not based only on intended prompt construction.

Settings: `gemini-3.8-flash`, medium thinking, 32,768 output-token limit, supported
API defaults without sampling controls or a thinking budget. All calls completed
without retries. The sixteen-call bound was reached; token and time use stayed
below their bounds. No further calls or prompt changes followed the results.

## Results

Counts below assess the same unchanged reading, not all candidates combined.

| Input condition | Leave correct | Hazard correct | Total correct |
| --- | ---: | ---: | ---: |
| A: competing edits, saved link status | 2/2 | 2/2 | 4/4 |
| B: competing edits, current link status | 2/2 | 2/2 | 4/4 |
| C: unchanged only, saved link status | 1/2 | 2/2 | 3/4 |
| D: unchanged only, current link status | 1/2 | 2/2 | 3/4 |

All **24/24 edited controls** are correctly rejected: eight wrong-meaning edits,
eight plain unnecessary fills and eight cosmetic variants. All forty judgments
decode and select valid supplied passages. Two responses nevertheless disagree
with the unchanged-reading labels:

- **Cell 05, D:** rejects leave because exact actor/modal evidence locations remain
  unresolved, although those meanings are retained and supported by broader source
  evidence.
- **Cell 13, C:** demands that the prose explicitly label external provisions
  unavailable and also rejects the unresolved component locations. The packet
  already records unresolved external references without the extra `link_issues`.

Both are false alarms against the frozen *meaning* criterion. The evidence-location
limitations are real and remain separately recorded. The prompt also asks for
exact evidence and identification of unavailable material; the model may be
interpreting that as requiring a fully resolved record or inline disclaimers.
This is a task-boundary ambiguity, not evidence that the warnings were fabricated.
The [raw review](RAW-REVIEW.md) preserves both rationales and this qualification.

Cell 10 also illustrates a separate limitation: its two correct unnecessary-edit
rejections cite only the final source passage while asserting that the entire
reading is complete. Their references resolve correctly but do not independently
substantiate every aspect of that broad claim. Its unchanged judgment supplies
the full relevant passage set. Rationale coverage is distinct from verdict and
source-location validity.

## What this supports

The extra-status factor shows no correctness difference at either candidate
setting. Removing competing candidates produces the same one-of-two leave loss
with both status settings; the hazard control stays correct. Neither comparison
meets the frozen requirement for two repeated failures against two correct
counterparts. The interaction criterion also fails. See [scores](scores.json).

A plausible explanation is that contrasting edits clarify the comparison, while
a lone unchanged candidate lets the checker switch to auditing the whole record.
The raw rationales fit that explanation, but do not prove the model's internal
process. Two repetitions cannot distinguish an intermittent effect reliably, and
two known excerpts do not establish generalization. In particular, this result
does not show that status information is generally harmless, that standalone
checking is generally worse, or that extra candidates guarantee correct judgment.

## Usage

| Arm | Calls | Prompt tokens | Answer tokens | Thinking tokens | Total tokens | Summed call seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A | 4 | 27,822 | 1,739 | 6,616 | 36,177 | 26.2 |
| B | 4 | 28,520 | 1,629 | 6,303 | 36,452 | 25.5 |
| C | 4 | 18,526 | 756 | 11,929 | 31,211 | 34.4 |
| D | 4 | 19,224 | 724 | 9,371 | 29,319 | 32.3 |
| Total | 16 | 94,092 | 4,848 | 34,219 | 133,159 | 118.3 |

The provider also reports 15,431 cached prompt tokens, already included in prompt
counts. These are recorded token counts, not a dollar-price estimate. Standalone
requests use 16.7% fewer total tokens here, but return eight judgments versus
thirty-two and have two unchanged-reading errors. They also use more thinking
tokens and summed call time in this run. None of these unequal-task totals prove
a general cost or latency advantage. [Usage receipt](usage.json).

## Decision and next work

Stop this diagnostic with the cause unresolved and the original integration gate
still failed. Preserve genuine warnings and sparse optional fields. Do not add
invented edit candidates, force evidence disclaimers into correct prose, or tune
this leave statement again to make standalone checking pass.

The next useful product experiment is actual repair generation, using the earlier
supported candidate-comparison policy as an advisory check. Freeze fresh sources
and manual source-based criteria first; compare full replacements with changes
limited to fields needing correction. Construct before/after candidates from
actual generated repairs and current review records, retaining all status. Include
complete no-change controls, necessary component/link corrections and unavailable
references. Record genuine no-proposal outcomes explicitly; do not manufacture
edits to improve the checker context.

This revises M5's earlier evaluator prerequisite: manual source review must be the
primary quality evidence while the checker remains experimental. Measure checker
agreement separately, especially when generation returns no edit. A successful
generated repair must survive evidence validation and review/export, not merely
receive model support. Any production integration needs that end-to-end evidence;
the standalone command remains deferred. The [active task list](../../plans/2026-09-13-model-input-improvements.md)
records this boundary and next sequence.

## Reproduction and preservation

The plan, requests, labels and dependencies were frozen before calls in
`source-pins.json`. Raw responses were reviewed before opening aggregate scores.
All sixteen inputs and actual requests reconstruct exactly, and all forty
judgments re-decode identically with provider creation blocked. See
[verification](verification.json). Production code was not modified, so this
research checkpoint does not rerun or claim new results for the full unit suite.

From the repository root and the recorded environment:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-checker-input-factors/verify.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-checker-input-factors/score.py
```

The experiment reuses native formatting, decoding, passage resolution and capture
helpers. Runtime/source pins refer to the recorded local checkout and neighboring
experiment artifacts; restore those versions before reproduction after code
changes. `MANIFEST.json` hashes all retained experiment files except itself.
Original experiments and their failed gates remain unchanged.
