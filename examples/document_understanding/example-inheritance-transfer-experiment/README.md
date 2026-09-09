# Example instruction transfers, but a detached deadline still loses scope

The unchanged instruction improved conditions on new examples and preserved the
difference between recommendation, obligation and descriptive possibility. It
did not pass the full transfer gate: one revised response separated a deadline
from the exemption limiting the underlying duty. Production is unchanged.

## Test

Three newly authored synthetic passages cover:

- A missing inspection report, a valid-exemption exception, a workshop example,
  and a ten-working-day response deadline.
- A recommendation to convert obsolete files where practicable, a spreadsheet
  example, and mandatory retention regardless of conversion feasibility.
- Address verification after an undeliverable notice, a possible temporary move,
  and the statement that an address mismatch alone does not prove false information.

The full texts are in `fixtures/`. They were fixed before calls and were not used
to develop the tested wording. They are invented tests, not an independently
curated benchmark or evaluation of additional real documents.

Control and treatment schemas are byte-identical to those from the
[example-inheritance experiment](../example-inheritance-experiment/README.md).
The treatment says that a separately extracted example inherits its governing
rule's conditions unless the source explicitly changes scope. The only request
difference within each pair is this addition to `meaning.description`.

Twelve calls ran: three passages × two versions × two repeats. Both versions use
the frozen passage-ID source-inventory prototype with `gemini-3.8-flash`, medium
thinking, temperature zero, no numeric thinking budget and no application output
cap. No retries, repairs, instruction revisions, full audits or new extraction
runs were performed.

## Direct source/output review

| Check | Control | Revised instruction |
|---|---:|---:|
| Workshop example retains missing-report condition and exemption | 0/2 | 2/2 |
| Separate deadline retains applicability to the non-exempt request | 0/2 | 1/2 |
| Spreadsheet recommendation retains conversion feasibility | 1/2 | 2/2 |
| Descriptive “may” stays possibility, without new permission or duty | 2/2 | 2/2 |

All four file-conversion calls preserve recommendations as recommendations and
retain the mandatory original-file retention regardless of conversion feasibility.
All four address examples preserve verification before resending and the limit
on what an address mismatch proves. Treatment adds context to the possible move
but does not turn it into an obligation, permission or asserted fact.

The revised workshop example in repeat 2 is complete:

> As an illustrative example, if a workshop permit application lacks a required fire-safety inspection report and the applicant does not hold a valid exemption, the reviewing officer must ask the workshop applicant for its fire-safety inspection report.

But the same response's separate deadline says:

> The request for a missing inspection report must allow the applicant a minimum response period of at least ten working days.

The number and unit are correct. The standalone deadline does not say that it
belongs to the non-exempt application governed by the underlying duty. Treatment
repeat 1 does preserve that link explicitly:

> When a reviewing officer requests a missing inspection report for an application lacking one without a valid exemption, the request must allow at least ten working days for a response.

This distinction follows the predeclared criterion that the deadline must remain
attached to the governed request. It matters when units are consumed independently.
The exemption remains in other units and the full evidence in every response;
it has not disappeared from the document-level inventory. A consumer that always
reconstructs those relationships could recover it, but this test does not prove
that reconstruction.

Treatment repeat 1 also describes the applicant as exempt from the requirement
that the officer request a report. That can mean exemption from the process, but
it obscures the officer as the duty bearer. We record this as wording ambiguity,
not a definite role reversal or new obligation. Its main and example requirements
retain the correct actors. The separate exemption also varies between `exception`
and `exemption`; stable classification was not established.

`source-review.json` preserves all 40 raw unit meanings and revisable per-call
assessments. Scores are agent judgments under the pinned criteria, not gold labels
or general accuracy rates.

## Decision

The example-specific improvement extends beyond the teacher paragraph in these
synthetic cases. The stricter all-criteria gate fails because treatment repeat 2
still drops the deadline's applicability guard. This is a remaining error also
seen in the controls, not evidence that the revised instruction caused a regression.

Keep the wording as a useful candidate; do not describe it as a complete scope
fix. The next useful comparison is to keep a dependent deadline with its governing
duty versus extracting it separately. That can use the existing CUE-derived unit
structure without introducing another schema type. The separate exemption's actor
wording also needs care before turning that record into executable workflow logic.
No follow-up calls or implementation changes ran in this experiment.

## Verification and replay

All 12 responses ended STOP and all evidence resolved without inventory issues.
All 12 inventories and aggregate results replay identically without provider calls.
These structural checks are separate from semantic success. Reported tokens total
**16,594**: 7,809 control and 8,785 treatment. This sample establishes no general
cost effect.

`design.json` pins the runner, schemas, fixtures, criteria, prior prototype manifest
and runtime before acquisition. `runs/` contains request/response captures, attempts,
inventories and manifests. `verification.json` and `decision.json` record the checks
and decision. The outer manifest excludes Python bytecode caches.

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/example-inheritance-transfer-experiment/experiment.py replay
```

Production code, schemas and defaults remain unchanged. No production tests were
rerun. Previous captures are intact. Findings are saved locally and uncommitted.
