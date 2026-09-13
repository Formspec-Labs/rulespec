# Field-necessity revision: small gain, unresolved medical failure

The refined paragraph improved **28/30 to 29/30** correct judgments while retaining
all unnecessary-edit and legitimate-component controls. It accepted the needed
medical repair once in two attempts, versus neither attempt under the previous
paragraph. It used **29.6% more reported tokens**. The preregistered gate failed;
**production remains unchanged**.

This follows the user's request to iterate specifically on avoiding unnecessary
fields. It does not replace the pending fresh-source evaluation of the earlier
positive shared task.

## What changed

Both arms used the production checker plus a field-necessity paragraph. Arm A
reused the exact earlier paragraph. Arm B replaced it with a criterion based on
added meaning: copying existing default-statement meaning into optional
action/object fields is unnecessary, including cosmetic rewording; supplying a
missing governing condition, exception limit, alternative or timing requirement
is substantive, even when another record or a general label refers to it.

The [exact instructions](instructions.json) were frozen before calls. Both arms
received the same source, draft, proposed changes, evidence, candidate ordering,
schema and model settings. No shared-task instructions from M4b were added. The
paragraph was tested as a whole; individual sentences were not isolated.

## Results

| Measure | Previous paragraph | Refined paragraph |
|---|---:|---:|
| Correct judgments overall | 28/30 | 29/30 |
| Unnecessary action-field filling rejected | 6/6 | 6/6 |
| Field filling plus cosmetic rewording rejected | 6/6 | 6/6 |
| Needed medical repair accepted | 0/2 | 1/2 |
| Corrections to incorrect components accepted | 2/2 | 2/2 |
| Missing exception links accepted | 2/2 | 2/2 |
| Wrong meaning/actor/target rejected | 12/12 | 12/12 |

The cosmetic controls change only equivalent modal phrasing, such as "must" to
"is required to", alongside the existing redundant action fill. Both versions
already reject them. Both allow useful edits with unchanged prose: clearing an
incorrectly assigned action/object pair, and adding the correct exception link.
This supports keeping field necessity distinct from literal text equality.

The single improved medical response explicitly says the draft only generally
labels the confidentiality exceptions and that their specific limits add needed
meaning. The failed repetition still calls the additions paraphrase and credits
companion records as complete coverage. The old paragraph does the latter twice.
The missing details concern necessary work restrictions/accommodations and
appropriateness/emergency-treatment limits on disclosure, not a style preference.

**Decision: bounded gain, not solved.** The explicit distinction sometimes helps,
but it does not reliably keep rejection of unnecessary fields from suppressing a
substantive repair. The data do not support adding this larger paragraph to
production or continuing to append warnings around this same medical example.

## Cost and verification

| Reported usage | Previous paragraph | Refined paragraph |
|---|---:|---:|
| Calls | 12 | 12 |
| Input tokens | 46,998 | 47,742 |
| Visible output tokens | 3,560 | 3,829 |
| Thinking tokens | 18,124 | 37,459 |
| Total tokens | 68,682 | 89,030 |
| Summed provider seconds | 87.0 | 132.7 |

The extra paragraph adds 62 input tokens per call. Most of the observed total
increase comes from reported thinking tokens. These twelve-call arm totals are
observations, not stable cost/latency predictions.

Total: **24 calls, 60 judgments, 157,712 tokens, 219.7 summed provider seconds**.
No retries, missing responses, provider failures or decoder issues occurred.
All fifteen candidate decisions pass the existing source/CUE-field decoder;
all actual request bodies match the frozen shape and all saved responses
re-decode identically with provider access blocked. All paired inputs differ only
in the intended paragraph. Existing source captures and review history are intact.

The [preregistered plan](PLAN.md), [labels](labels.json), [scores and arm costs](scores.json),
[raw review](RAW-REVIEW.md), [cell observations](RAW-OBSERVATIONS.md), and
[verification](verification.json) retain the evidence. Actual prompts and raw
responses are in `inputs/` and `captures/`. `pins.json` binds source/runtime
dependencies; `MANIFEST.json` binds the completed experiment. The runner reuses
the prior experiment's capture implementation and the production schema/decoder.

## Limits and next step

These are five previously used statutory excerpts, with two different notice
controls reusing one excerpt. Fifteen candidate decisions are repeated twice per
arm. The three cosmetic counterexamples are constructed mutations, not fresh
documents. The component-error draft is explicitly constructed from a saved
model mistake, as in the preceding experiment. This is checker evaluation, not
initial extraction or repair generation.

Labels assess independent use of the selected default statement. Medical details
retained in companion records count toward document-level retention, a different
criterion. One failed rationale also cites a real unresolved location for the
repeated quote "may"; the source clearly supplies permission, and both candidates
preserve the field. This does not establish that the proposed disclosure-limit
repair is redundant. The issue and original labels remain visible.

The author reviewed anonymous cells before arm scores but could infer arms from
wording. Labels are revisable agent assessments. Two medical repetitions do not
establish a general success rate or a reliable causal effect.

The next useful decision remains the **unchanged positive shared-task comparison
on fresh sources**, now explicitly including ordinary redundant field fills,
cosmetic variants, useful component corrections and exception links. It already
expresses the distinction without adding this new paragraph. Earlier success
there suggests that the overall definition of the selected reading matters;
these different cohorts do not isolate instruction order or prove that cause.
Keep the field-only revisions as development regressions. No extra default pass,
blanket unchanged-summary filter, new output field or schema is justified here.
