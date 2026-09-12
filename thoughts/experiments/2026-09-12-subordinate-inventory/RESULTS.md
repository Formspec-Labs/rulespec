# Explicit passage accounting does not improve defect detection

**Decision: no measured detection improvement; do not adopt the checklist.**
The treatment made a decision for every supplied passage, but both audit arms
missed all three saved CSBG gap groups and all three prelabelled fresh IEP checks.
Both preserved the faithful local education plan control. Production is unchanged.

This is a completed, bounded hypothesis test, not evidence that extraction is
generally accurate or that no audit design could help. It tests one change to
inventory allocation with the existing comparison unchanged.

## What was compared

The [plan](PLAN.md) was saved before provider calls. A used the existing inventory
prompt; B added a source-ordered checklist requiring an explicit decision for every
nonempty focus passage. Headings could be background; substantive units used the
same existing CUE inventory schema and scope evidence. Sources, focus/context,
model settings and downstream comparison were identical within each pair.

We reused the saved focused CSBG draft and made two new, untouched extractions
from pinned USLM release 119-102: 20 USC 1414(d)(1), IEP definitions/team/attendance,
and 20 USC 6312(b), local education agency plan provisions. These complete selected
subsections were unused in the targeted experiment-note search. They are now
development data, not an independent benchmark or current-law advice.

Both fresh extractions completed without refusals or rejections: eight IEP records
and thirteen local-plan records. The [pre-audit review](PRELABELS.md) identified a
transition-detail omission and two standalone-permission qualification defects
in IEP. The local-plan draft retained the selected details and served as a natural
faithful control. No artificial errors, repairs or replacement cases were introduced.

## Results by layer

| Measure | A: ordinary inventory | B: passage checklist |
| --- | ---: | ---: |
| Explicit single-passage decisions / supplied passages | 72 / 147 | 147 / 147 |
| Total inventory units | 92 | 147 |
| Substantive inventory units | 88 | 116 |
| CSBG target gap groups detected | 0 / 3 | 0 / 3 |
| Fresh IEP target checks detected | 0 / 3 | 0 / 3 |
| Faithful local-plan claims falsely flagged | 0 / 13 | 0 / 13 |
| Inventory + comparison tokens across three cases | 106,696 | 128,564 |

The single-passage decision measure checks adherence to B's instruction, not
semantic coverage. A may legitimately use ranges and has no obligation to make
one decision per passage. Likewise, more substantive units do not prove fuller
or better meaning. The treatment's required behavior occurred, so the failure
cannot be explained simply as ignoring the checklist.

**Recognition does not ensure detection.** Both inventories name the four CSBG
gap-filling methods: information, referrals, case management and followup
consultations. Both comparisons call C0010 covered, although its explicit meaning
only describes linkages to fill gaps. Both retain emergency immediate/urgent-needs
and urban-intervention/replication detail in inventory but approve C0006 without
it. Both still omit low-income recipients within the single (b)(5) passage.

On the new IEP source, both inventories name training, education, employment,
where-appropriate independent living, and courses of study. Both approve C0000
without those details. Both separately record written parental agreement/consent
but approve the attendance exemption and excusal without those prerequisites.
The writing requirement survives elsewhere in the draft; the individual
permissions remain incomplete. These are different failures from unavailable
source or a missing passage identifier.

**The checklist also introduces representation risk.** Some B CSBG units recast
requirements for the plan to describe intended outcomes as direct mandates that
activities must enable outcomes or partnerships must document best practices.
Their source evidence remains present, but their explicit meanings change the
role of the requirement. B's IEP inventory also splits excusal into a permission
pointing to subclauses plus separate conditions, recreating a reference-only
permission. These units should not be treated as ready-to-use rules.

The named faithful controls receive no false alarms in either comparison. This
includes optional examples, qualified duties and the IEP rule against unnecessary
duplicate information. That alone is weak evidence of discrimination because the
same comparisons approve the known omissions. A additionally identifies a missing
2014-amendment effective-date note, supported by supplied text. That historical
finding is separate from the primary requirement targets; B does not identify it.

**Contemporaneous controls mattered.** This test's ordinary CSBG inventory retained
more detail than the preceding audit, despite an identical actual request. The
[request check](input-and-cost-checks.json) confirms equality. Crediting that gain
to the checklist using only the old inventory as a control would have been wrong.
One observation per arm cannot estimate stable variability or success rates.

The [manual review](BLIND-REVIEW.md) was hashed before the arm key was opened.
Unit counts reveal likely arms, so masking was partial. Judgments remain revisable
assistant labels. No predeclared outcome rule changed after viewing outputs.

## Cost and verification

All 14 calls completed with `STOP`, no retries, no incomplete responses and no
missing usage receipts. Total consumption was **249,618 provider-reported tokens**:
154,461 input, 69,229 candidate output and 25,928 thinking. Reported cached input
is included in input consumption, not added again. Two extractions used 14,358
tokens; the twelve inventory/comparison calls used 235,260.

| Case: inventory + comparison | A tokens | B tokens |
| --- | ---: | ---: |
| CSBG | 54,828 | 65,056 |
| Fresh IEP | 26,785 | 34,607 |
| Fresh local education plan | 25,083 | 28,901 |

B used about **20.5% more tokens** in this observation, with no target-detection
gain. This is not a billing invoice or a stable expected-cost estimate. Capturing
the two extractions took 19.8 seconds; the audit experiment took 207.1 seconds.
All predeclared call/time/token bounds were respected.

All inventories and comparisons pass their parsing/source checks; the full
comparison observations assess 98 claim appearances and 204 substantive unit
appearances with consistent reciprocal links. Both fresh extraction graphs
validate. All twelve audit requests match their schemas, source/prompt and actual
SDK settings. Their processing and both original extractions replay identically
with provider setup disabled. Runtime and schemas remained unchanged. See
[verification](verification.json), [input/cost checks](input-and-cost-checks.json),
[captures](comparison/) and [source receipts](source-receipt.json).

## Practical conclusion

Do not add more inventory output or a mandatory audit pass on this evidence.
The next useful decision concerns direct comparison of each substantive source
component with explicit draft meaning, including conditions that must attach to
a permission. It should demonstrate actual missing-detail detections against
faithful controls before any implementation. Another generic inventory expansion
does not address the observed comparison failure.

Stop this test here. Preserve the current extraction path, source evidence and
optional audit for its demonstrated uses. The broader completeness problem
remains open; no new production behavior is proposed for adoption from this run.
