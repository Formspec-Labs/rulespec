# Deadline grouping: one complete result, inconsistent instruction following

The grouped strategy preserved the duty, deadline and exemption together in one
of two same-scope runs. The other ignored the grouping instruction and emitted
an incomplete standalone deadline. Both versions retained the broader deadline
scope in the explicit counterexample. The predeclared grouping gate does not
pass; no new instruction was adopted.

## Comparison

Eight calls compared two segmentation strategies on two synthetic passages, with
two repetitions per pair. Both schemas start from the successful example-inheritance
schema and add identical dependency guidance. Only the final strategy differs:

- Split: “Represent a deadline separately from the duty it qualifies.”
- Group: “Represent a deadline together with the duty it qualifies, unless their scopes differ; in that case, represent them separately.”

The shared guidance requires complete conditions, exceptions, modal force and time
limits, distinguishes deadlines from duties to act, and preserves explicitly
different scopes. This comparison tests the strategies against each other, not
the entire addition against the current production prompt.

The permit fixture is byte-identical to the
[previous transfer experiment](../example-inheritance-transfer-experiment/README.md).
It requires a missing-report request unless an exemption applies, gives a workshop
example, then sets a ten-working-day response period. The counterexample changes
only the deadline sentence to:

> Every request for an inspection report, including requests made voluntarily for exempt applicants, must allow at least ten working days for a response.

The fixtures are invented and labeled as such. Requests used the frozen passage-ID
inventory prototype, `gemini-3.8-flash`, medium thinking, temperature zero, no
numeric thinking budget and no application output cap. No retries, repairs,
instruction revisions or full-document calls ran. Captured request comparisons
confirm that only the strategy sentence differs within each pair.

## Raw-output findings

| Check | Split | Group |
|---|---:|---:|
| Same-scope deadline retains governed non-exempt applicability | 0/2 | 1/2 |
| Same-scope grouping instruction followed | — | 1/2 |
| Explicit broader deadline scope retained | 2/2 | 2/2 |
| New mandatory request duty for exempt applicants | 0/2 | 0/2 |

The successful grouped main rule says:

> If a permit application lacks a required inspection report, the reviewing officer must request the missing report, allowing at least ten working days for a response, unless the applicant holds a valid exemption.

Its workshop example likewise includes the missing-report condition, deadline and
exemption. Existing fields can represent this complete meaning without a separate
threshold record or a new schema type.

The other grouped run produces the same weakness as both split controls:

> A request for a missing inspection report must allow at least ten working days for a response.

The number survives, but the standalone deadline omits the exemption limiting
the governed request. The exemption remains elsewhere in the inventory and in
the exact source evidence. The main duty and separate workshop example also omit
the deadline in these three runs. These findings use the pinned independently
usable meaning criterion, not a claim that the information vanished everywhere.

All four counterexample outputs preserve the express broader scope, including
voluntary requests for exempt applicants, and keep the mandatory request rule
conditional. One split output additionally turns mention of voluntary requests
into an explicit permission record; that interpretation deserves review because
the source does not separately state a grant of authority. Another uses ambiguous
wording about the applicant being exempt from the officer's requirement. Neither
creates a mandatory request duty for exempt applicants.

`source-review.json` contains every raw unit and the per-call assessments. These
are revisable agent judgments, not independent gold labels. Classification of a
deadline as `requirement` versus `threshold` also varies across strategies.

## Decision

Grouping is a viable representation, but the description did not reliably make
the model use it. The failed grouped response is a failure to follow the strategy;
it does not demonstrate that a faithfully grouped representation loses scope.
One compliant run does not establish a general advantage over complete separate
records. Two repeats and closely related synthetic passages limit the conclusion.

Do not add this grouping sentence to production. Retain the successful output as
a regression example. Prioritize the already-planned deterministic check of the
four original refused audit evidence rows. If grouping is revisited, test guidance
about how to identify whole rules in the inventory task and measure adherence
separately, instead of adding more reminders to the meaning-field description.
No additional calls were made.

## Verification

All eight responses ended STOP, all evidence references resolved, and all eight
inventories plus aggregate results replay identically without provider calls.
Reported tokens totaled **16,556**: 8,306 split and 8,250 group. This small sample
does not establish a general cost difference.

`design.json` pins schemas, fixtures, criteria, runner and the prior frozen runtime
before acquisition. `runs/` preserves requests, responses, attempt metadata,
inventories and manifests. `verification.json` records paired-request and replay
checks; `decision.json` records the non-adoption decision. The outer manifest
covers experiment files excluding Python bytecode caches.

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/deadline-grouping-experiment/experiment.py replay
```

The existing production example-inheritance update remains in place. This
experiment changed no implementation or defaults; only the active handoff and
operating guide were updated afterward. No production tests were rerun. Research
and existing implementation changes remain local and uncommitted.
