# Original teacher paragraph: reminder did not fix condition loss

The original omission reproduced in all four calls. Both control and treatment
preserved the inaccurate-record condition in the general employer burden, then
omitted it from the separate teacher requirement. The extra schema instruction
provided no observed benefit. Production remains unchanged.

## Comparison

This test reuses the byte-identical `burden.json` fixture from the saved
[audit-grounding experiment](../audit-grounding-experiment/README.md), including
its original surrounding context. Both arms use that experiment's frozen
passage-ID prototype. The control here is that prototype's unchanged schema,
not the older quotation-based control used in the audit-grounding experiment.

The treatment is byte-identical to the schema from the
[same-passage test](../same-passage-scope-experiment/README.md). It adds only this
text to `meaning.description`:

> Include every governing condition in meaning, even when it appears inside the selected main passage. Empty scope_refs means no additional evidence passage is needed—not that the rule is unconditional.

Two repetitions per arm used `gemini-3.8-flash`, medium thinking, temperature
zero, no numeric thinking budget, and no application output cap. Four calls
completed; no retries, repairs, comparison audits, or full-document calls ran.
The source, prompt, field order, validation constraints and other settings were
identical within each pair. Saved requests confirm the description was the
only request difference. Inputs and review criteria were pinned before calls.

## Source and output

The source begins:

> In the event an employer does not maintain an accurate record of hours worked by an employee ... the employer has the burden of showing that the employee has not worked the requisite hours.

The next sentence illustrates that burden:

> An employer must be able to clearly demonstrate, for example, that full-time teachers ... did not work 1,250 hours during the previous 12 months in order to claim that the teachers are not eligible for FMLA leave.

In all four responses, the first extracted requirement retains the inaccurate-record
condition. Every separate teacher requirement begins with the employer's intent
to claim ineligibility and omits the inaccurate-record condition. For example,
treatment repeat 2 says:

> To claim that full-time teachers (as defined in § 825.102) of an elementary or secondary school system, institution of higher education, or other educational establishment or institution are not eligible for FMLA leave, an employer must be able to clearly demonstrate that the teachers did not work 1,250 hours during the previous 12 months, taking into account that they often work outside the classroom or at their homes.

That captures the teachers, institutions, hours, time period and work-location
detail. It does not carry forward the condition governing the burden being
illustrated. A separate condition-bearing rule and a link to the whole source
paragraph do not make this independently usable statement complete.

| Check | Control | Revised description |
|---|---:|---:|
| Teacher statement retains inherited condition | 0/2 | 0/2 |
| General employer burden retains condition | 2/2 | 2/2 |
| Teacher details and definition reference retained | 2/2 | 2/2 |
| Aircrew special-rule reference retained as background | 2/2 | 2/2 |
| Evidence resolves without inventory issues | 2/2 | 2/2 |

All calls returned three units: two requirements and one background cross-reference.
No unrelated condition transferred from the adjacent context. Treatment repeat 2
slightly strengthens the parenthetical about work locations into “taking into
account”; this is a secondary wording concern, separate from the repeated scope
loss. Full raw units and revisable agent assessments are in `source-review.json`.

## Decision and next useful test

Do not adopt this reminder as a demonstrated fix. Unlike the previous synthetic
test, this comparison reproduces the problem, so its failure is informative:
explicitly repeating the instruction to preserve governing conditions is
insufficient here.

The outputs are consistent with treating “for example” as a separate standalone
duty and losing the relationship to the general conditional rule. That is a
hypothesis about the failure, not evidence of the model's internal reasoning.
Empty `scope_refs` alone cannot explain it: the preceding synthetic test retained
conditions with the same empty lists.

The next narrow test would make the example relationship explicit in the
instructions: examples inherit the conditions of the rule they illustrate unless
the source changes scope. Pair the original paragraph with a case that explicitly
changes scope, so indiscriminate inheritance does not pass. This follow-up is
proposed only; no further calls ran and no production change was made.

## Verification and replay

All four responses ended STOP. All four inventories and aggregate results replay
identically without provider calls. Reported tokens total **12,585**: 5,558 control
and 7,027 treatment. Four calls on one paragraph do not establish a general
accuracy or cost effect. Both arms report 1,189 input tokens per call despite the
changed description; request captures verify its presence, and the token counts
do not establish how the provider accounts for schema descriptions.

`design.json` pins fixtures, schemas, criteria, runner, the original prototype
manifest and runtime hashes. `runs/` retains requests, responses, attempt metadata,
inventories and per-run manifests. `verification.json` records checks;
`decision.json` records the result and proposed follow-up. The outer manifest
covers the experiment's saved artifacts, excluding Python bytecode caches.

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/teacher-scope-experiment/experiment.py replay
```

The runner loads the preserved prototype within its process. Production code and
defaults are unchanged, so no production test suite was rerun. These results are
local and uncommitted.
