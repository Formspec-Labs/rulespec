# Manual review of separate-pass output

Read all 81 returned scores and bases against the unchanged prior source review,
fixed statements and supplied passages. The earlier labels were pinned before
these calls and remain unchanged. This review interprets what the scorer actually
noticed; it does not turn its assertions or the earlier labels into gold answers.

## Primary cohort: outputs previously scored during extraction

CSBG (`cell-04`, prior `csbg-1`): the lossy combined plan statement R003 remains
0.95. Its basis says it preserves the substantive elements and conditions,
“though heavily condensed in summary form.” It does not identify the lost
service-linkage methods, low-income recipients, emergency/replication details,
or the additional missing qualifications. Lower relative ranking is useful, but
the explanation still incorrectly reassures the reader about completeness.
Other bases correctly recognize the selected designation, duties, hearing,
cause definitions, Secretary permission, revision/submission, inspection and
historical transition meanings. Mixed permission/duty R007 remains uncertain.

IEP (`cell-03`, prior `iep-2`): R004/R005 now score 0.95, down from inline 0.99.
Both bases recognize that independent use depends on the writing requirement
in clause (iii). That qualification exists in source F053 and is absent from
both fixed statements. This is useful, source-supported dependency recognition.
The outputs do not repair those statements. R000 remains 0.98 with an incorrect
claim that the definition is complete, missing the transition-assessment subjects
and rights-transfer qualification. R001/R002 preserve the construction-rule text;
the scorer does not address the uncertain `must_not` classification. The faithful
team definition, writing rule and parent-request invitation remain accurate;
the latter two also receive 0.95, so the score does not isolate the flawed rules
within the IEP output particularly well.

LEA (`cell-02`, prior `lea-1`): all 13 faithful statements receive 0.98. Bases
correctly recognize the governing plan requirement, listed contents, conditional
early-childhood/career provisions and optional examples. No invented criticism
or new requirement found. This does not measure defect detection in LEA because
this saved output has no clearly flawed substantive requirement.

## Ordinary-extraction cohort

CSBG (`cell-00`, prior `csbg-2`): every one of 28 items scores 0.95. The basis for
R006 incorrectly claims thorough capture despite omission of named grassroots
partner categories from F022. It does not mention those missing categories.
The basis for uncertain R019 does not address the Secretary-facilitated-system
qualification. Other bases summarize genuine source meanings. Flat scores
provide no way to prioritize the known error within this document.

IEP (`cell-05`, prior `iep-1`): R000, R004 and R005 all score 0.95 with incorrect
claims of full capture. The scorer misses courses of study (F025) and both
writing conditions (F053). R006 scores 0.65 because its relative clause references
do not name attendance/excusal. That is a reasonable independent-usability
concern already labeled uncertain. It does not propagate that observation to
the two permissions. Faithful construction rules, team definition and transition
invitation also score 0.95. No separation of clear errors from faithful meanings.

LEA (`cell-01`, prior `lea-2`): all 13 substantive requirements receive 0.98 with
accurate bases. The additional parent pointer R000 receives 0.50 because the
statement alone does not enumerate the 13 contents. This concern is reasonable
for standalone use but debatable when explicit child requirements are present;
the original uncertain label remains. It is not counted as a newly discovered
clear defect or a definite false alarm.

## A possible explanation worth preserving

The attendance-exemption statement R004 is exactly identical in the two IEP
inputs, yet only one assessment mentions its missing writing dependency. Both
calls received the same source and the same scoring prompt/schema/settings.
The surrounding extracted material differs. In the version where the dependency
was recognized, R006 names the attendance/excusal targets and supplies source
context references. In the other version it retains only `clause (i)` and
`clause (ii)`. Other surrounding fields differ too.

This is consistent with explicit target names/references helping the scorer
connect an inherited qualification, and also consistent with ordinary model
variability. It is not evidence that the added names alone caused improvement.
A future discriminating test would vary only that already-supported connection
on a fixed input. This experiment did not run that test or adopt another prompt
patch. Reuse existing reference/context facilities if pursuing it.

All eight clearly flawed records across both cohorts still score at least 0.95.
The second pass recognizes two specific qualification dependencies in one saved
version, while giving confident completeness assurances to the other known
omissions. The numeric scores and the concrete dependency observations are
different signals; the latter can be inspected against source text.
