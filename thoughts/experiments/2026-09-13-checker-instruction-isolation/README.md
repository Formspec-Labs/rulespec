# Positive completeness wording merits a fresh-source test

Replacing one ambiguous sentence in the experimental shared task improved checker
judgments from **25/32 to 32/32** on the saved failures and controls. All three
target contexts improved. The separate optional-field instruction reduced noise
but lost a medical-repair acceptance. **Production remains unchanged.**

These are selected development cases and constructed candidate decisions. They
test the checker, not fresh document extraction or generation of the repairs.
Two repetitions per arm measure within-case variability, not additional documents.
The sources comprise six saved statutory excerpts and one synthetic control;
the two new notice controls reuse the same excerpt.

## M4a: reject unnecessary action/object filling

Added one paragraph to the current production checker, allowing empty optional
action/object fields while preserving corrections to incorrect populated fields
and missing qualification links. Everything else in each pair stayed identical.

| Measure | Current checker | With field instruction |
|---|---:|---:|
| All correct judgments | 17/24 | 22/24 |
| Unnecessary field edits rejected | 0/6 | 6/6 |
| Needed medical repairs accepted | 1/2 | 0/2 |
| Actual component fixes accepted | 2/2 | 2/2 |
| Needed exception links accepted | 2/2 | 2/2 |
| Wrong meaning/actor/target rejected | 12/12 | 12/12 |

The field-noise benefit survives in isolation, including controls with unchanged
prose that still need a component correction or exception link. However, both
treatment responses call the missing medical disclosure restrictions a paraphrase
duplicate. The contemporaneous baseline accepts one of two repairs; its earlier
saved result was two of two. This variability is why we used fresh paired calls.

**Decision: bounded improvement with a regression; gate failed.** Do not adopt this
paragraph alone. The original component error was transplanted into an explicitly
constructed complete draft for the clearing control. Success there does not prove
the checker consistently identifies that error in its original presentation.

## M4b: positively name what must be in the selected statement

Both arms used the prior experimental shared task. The only change replaced:

> A full quotation or another record retaining a condition does not incorporate it
> into this statement.

with:

> Assess completeness in the selected statement's fields.summary: include every
> supplied condition that governs that statement, including those recorded in
> quotations or other records.

M4a's paragraph was absent from both arms. Source, draft, candidate order, output
schema and settings were identical within each pair.

| Measure | Previous shared task | Positive sentence |
|---|---:|---:|
| All correct judgments | 25/32 | 32/32 |
| Complete repairs accepted | 5/8 | 8/8 |
| Incomplete no-change decisions rejected | 4/8 | 8/8 |
| Complete no-change decisions accepted | 2/2 | 2/2 |
| Wrong meaning/target rejected | 10/10 | 10/10 |
| Unnecessary or incomplete component-only edits rejected | 4/4 | 4/4 |

| Context | Previous shared task | Positive sentence |
|---|---:|---:|
| Privacy access exclusion | 4/6 | 6/6 |
| Medical disclosure limits | 2/6 | 6/6 |
| Notice waiver and surviving duty | 7/8 | 8/8 |
| Synthetic request/inspection controls | 12/12 | 12/12 |

All preregistered diagnostic gates passed: seven additional correct judgments,
improvements in three target contexts, and no lost wrong-edit or complete-no-change
controls. The two arms each have 16 distinct candidate decisions repeated twice.

The raw privacy response under the old wording calls incorporating the exclusion
an improper edit because it is separately recorded. Both positive-wording responses
identify it as a governing section-wide exclusion. For medical rules, both positive
responses name the omitted work restrictions/accommodations and conditional
emergency-treatment purposes. Both accept the repair and reject the incomplete
default. Both notice responses detect the incoming infeasibility exception.

**Decision: advance this unchanged positive-wording task to new sources.** The
comparison supports the instruction change on these cases. It does not establish
a universal effect of negation or reveal hidden model reasoning. The old wording
also succeeded on some repetitions, so failure was not inevitable.

## Evidence and limitations

- 40 fresh checker calls, 112 judgments, no retries or provider failures. Every
  judgment has mechanically valid source selections. The original source captures
  and review history remain untouched.
- Model: `gemini-3.8-flash`; medium thinking; 32,768 maximum output tokens. Sampling
  parameters and thinking budget omitted. All actual requests match the frozen
  expected shape; every response re-decodes identically with provider access
  blocked. The paired-input check confirms only the declared instruction differs.
- Usage: **286,274 tokens**: 180,552 input, 13,689 visible output, 92,033 thinking.
  Summed provider time: **350.7 seconds**. Stayed within the 40-call, 450,000-token
  and 1,200-second launch limits.
- In M4b, reported total tokens fell from 78,682 to 71,784 (8.8%), and summed
  provider time from 97.1 to 86.1 seconds. The positive sentence added 15 input
  tokens per call; fewer thinking tokens account for the overall decrease.
  These are observed costs in eight calls per arm, not a stable performance claim.
  Both comparisons' arm totals are retained in [costs.json](costs.json).
- Two correct verdicts contain an additional rationale problem: demanding
  resolution of an unavailable provision, and calling an any-one-sufficient
  mutation mutually exclusive. These remain documented separately from verdict
  accuracy in [the raw review](RAW-REVIEW.md).
- Medical details are also retained in companion extraction records. The labels
  assess independent use of the selected default statement. This is an explicit
  product criterion; document-level completeness is a different measure.
- These cases are known development data. The reviewer authored the instructions,
  reviewed anonymized cells before aggregate scoring, and could infer likely arms
  from wording. Labels are revisable assessments, not independent human ground
  truth. Counterexamples are deliberate diagnostic mutations.

The [preregistered plan](PLAN.md), [exact instructions](instructions.json),
[labels](labels.json), [scores](scores.json), [verification](verification.json),
[raw observations](RAW-OBSERVATIONS.md), and actual `inputs/`, `captures/` and
`decoded/` files preserve the comparison. `pins.json` binds the input/runtime and
prior-source dependencies; `MANIFEST.json` binds the final retained experiment.

## Next bounded decision

1. Compare the unchanged positive shared task directly with the current production
   checker on eight previously unused source excerpts. Freeze source-based labels
   before checker calls and include complete controls, incoming exceptions,
   separate duties and unavailable references. Keep constructed candidate checking
   distinct from model-generated repairs.
2. Measure needed repairs, missed conditions, unnecessary edits, wrong-target
   acceptance, no-change judgments, rationale fidelity and cost separately. Score
   production's unassessed no-change targets explicitly, outside shared-edit
   denominators. Freeze comparative thresholds before collecting that cohort.
3. Do not append M4a's paragraph or tune the winning sentence during that test.
   The positive shared task already passed the current component-noise controls.
   Preserve M4a's medical regression as a separate development check.
4. Adopt only if that new comparison supports it, through the existing optional
   refinement/check path. Repair-generation response-size work and its untouched
   holdout remain later tasks. No default extra pass or new schema is justified
   by this diagnostic.
