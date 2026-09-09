# Statement-first output experiment

Keep the current default. Generating the statement first improved the firearm
declaration and ammunition classification in these repeated runs, but did not
reliably preserve conditions, cross-reference topics or sufficient evidence.
This experiment changed no production code.

## What changed

The experiment moves `statement` from last to first within `unit_attributes` in
the current CUE-generated provider schema. All other property positions, field
definitions, descriptions, required fields, instructions, examples, source text,
parser and Core conversion remain unchanged. It adds no parallel schema or
`propertyOrdering` setting. The source reference `unit` still precedes the
attributes.

Gemini 3.8 Flash processed three sources twice under each order: 12 calls at
temperature 0, with a 16,384 output-token allowance and no retries. The first
repeat runs control before treatment; the second reverses them. The three
sources run independently, with at most three concurrent requests. This is a
small development experiment, not a representative or blinded quality benchmark.
Photos were omitted to bound cost.

[design.json](design.json) pins the inputs and runtime before the calls;
[criteria.json](criteria.json) records the source-review criteria.

## Observed meaning

These are selected checks against source, not overall accuracy scores. Each
column contains two observations. Full evidence and qualifications are in
[source-review.json](source-review.json).

| Selected check | Current order | Statement first |
| --- | ---: | ---: |
| Firearm declaration statement retains all specified details | 1/2 | 2/2 |
| Ammunition non-prohibition avoids absence-of-duty label | 0/2 | 2/2 |
| Invented ban exception avoids absence-of-duty label | 0/2 | 0/2 |
| Invented baseline rules retain their exceptions in statement and scope | 2/2 | 2/2 |
| Leave proviso appears in both statement and scope | 2/2 | 1/2 |
| Leave definition retains both cross-reference topics | 2/2 | 1/2 |
| Three baggage lists have complete selected logical evidence | 2/2 | 1/2 |

The clearest regression is the second statement-first leave result. It says:

> The 12 months an employee must have been employed by the employer need not be consecutive months.

The source continues with **provided** and the following rules. The result puts
that limit in `scope_text` but omits it from the statement. Moving the statement
first did not prevent meaning from being distributed unevenly across fields.

Another statement-first result correctly describes the loaded-firearm ban but
selects only `F009` as its main, scope and logical evidence. That passage is the
checked-baggage introduction; **“Any loaded firearm(s).”** is in `F010`, which no
selected field includes. The source supplied to the model contains the right
text, but the record's attached evidence does not substantiate the object.

Other recurring gaps remain: the weapons exception still receives
`exemption/not_required`, its scope omits complete qualifying-person tests, and
some scope fields refer to numbered conditions instead of retaining their
meaning. Controls also have defects: one scope writes `14 CFR` while its own
statement writes `49 CFR`. The treatment is not being compared to perfect
outputs.

Some grouping changes preserve meaning. Both statement-first baggage runs
combine ammunition non-prohibition with its additional-requirements explanation.
That reduces independent referenceability but retains the explanation and its
citation; it is not counted as an omitted explanation.

## Processing and usage

| Source | Order | Repeat 1: statements / tokens | Repeat 2: statements / tokens |
| --- | --- | ---: | ---: |
| Baggage | Current | 7 / 5,611 | 7 / 6,065 |
| Baggage | Statement first | 6 / 5,126 | 6 / 5,016 |
| Leave | Current | 11 / 8,185 | 9 / 11,283 |
| Leave | Statement first | 10 / 16,431 | 10 / 5,868 |
| Invented contrasts | Current | 11 / 4,621 | 10 / 4,066 |
| Invented contrasts | Statement first | 10 / 3,850 | 10 / 4,168 |

Total reported usage: **80,290 tokens**, including thinking. Token totals include
input and thinking as well as output, so they are not compared directly with
the output allowance. All calls ended with `STOP`. There were no repair or
model-review calls.

All 107 raw rows followed the requested attribute order. All 12 runs replayed
to identical books without provider calls, passed Core graph validation and had
no extraction refusals or rejected candidates. Raw statement, scope, kind and
modality matched their compiled values. These checks establish processing
integrity, not semantic correctness. Existing review issues remain attached.

[verification.json](verification.json) records the checks and usage. Verification
compares exact request structure, restoring only the statement property position,
because ordinary dictionary equality and canonical schema hashes ignore object
order. File-byte hashes preserve the recorded schema and request order.

Replay one capture using a new output directory:

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/statement-order-experiment/experiment.py \
  replay baggage statement-first 1 --output .tools/statement-first-replay
```

## Next decision

These observations support targeted checks of statement/scope agreement,
negative classifications and evidence completeness more than another broad
instruction block. Existing `audit.py` and `refinement.py` already provide
recorded assessment and proposed corrections; reuse them when testing a narrow
check. A check must demonstrate that it detects these defects without rewriting
correct outputs or treating a review flag as proof of error. No such new check
or correction was implemented in this experiment.

The internal reason for the model's failures remains uncertain. Reordering
changed some outcomes, but the source review does not establish a universal
causal explanation or a generally better order.
