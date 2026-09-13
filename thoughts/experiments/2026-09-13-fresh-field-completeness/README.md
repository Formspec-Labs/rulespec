# Fresh-source completeness and field-necessity comparison

The unchanged positive shared-task checker passes the preregistered gate on
eight fresh source excerpts. It gets **36/36 shared edited-candidate judgments
correct, versus 24/36 for the current checker**. Needed complete repairs improve
from **1/6 to 6/6**, while all redundant-field edits are rejected. This supports
a bounded integration proposal for the optional checker. Production is unchanged;
repair generation has not been tested by this comparison.

## What was compared

Arm A uses production `refinement.CHECK`. Arm B uses the exact `M4b.B` instruction
from the committed [instruction-isolation experiment](../2026-09-13-checker-instruction-isolation/README.md).
No new optional-field paragraph was added. The [instructions](instructions.json)
make the selected `fields.summary` responsible for a complete usable reading,
allow empty optional fields, and distinguish needed corrections from enrichment.

Both arms receive the same source, native draft, schema and shared edited
candidates in the same relative order. B additionally receives explicit selected
aliases and unchanged candidates. This is a policy comparison with a deliberate
task difference, not an isolated test of a sentence, field order or candidate count.
A's absent no-change judgments are reported as unassessed, not wrong shared edits.

The [plan](PLAN.md) and [source criteria](CASE-CRITERIA.md) preceded extraction.
Eight ordinary production extractions then supplied the actual drafts. The
[baseline review](BASELINE-REVIEW.md), candidate labels and requests were frozen
before checker calls. Each arm ran twice per source, followed by a separate
actor/link diagnostic. Candidate edits are constructed around real outputs;
this measures recognition of good and bad changes, not the ability to produce them.

## Results

Counts below include two repetitions per source. They are not independent
documents or a general estimate of extraction accuracy.

| Shared edited candidates | A: current | B: positive shared task |
|---|---:|---:|
| All correct judgments | 24/36 | 36/36 |
| Needed complete repairs accepted | 1/6 | 6/6 |
| Native classification fixes accepted | 2/2 | 2/2 |
| Plain redundant field fills rejected | 0/6 | 6/6 |
| Cosmetic rewording plus field fills rejected | 5/6 | 6/6 |
| Wrong-meaning changes rejected | 16/16 | 16/16 |

B also gets **16/16 no-change judgments** correct: eight complete readings,
six readings missing supplied meaning, and two incorrect-component readings.
A leaves those sixteen decisions unassessed. In the separate constructed
diagnostic, both arms get **8/8**: all four useful actor/link corrections accepted
and all four wrong-actor/target controls rejected.

Six of eight source contexts improve; none regresses. All fourteen checks of the
preregistered gate pass. Excluding the three interpretation-sensitive sources
(debt, jury fees and religious employment) still gives **16/26 to 26/26** shared
edit correctness and **10/10** B no-change judgments. See [scores](scores.json)
for candidate-level results and the sensitivity calculation.

The practical gain is recognizing when meaning really is missing, while leaving
complete statements alone. Five newly accepted needed-repair judgments, six newly
rejected plain fills and one newly rejected cosmetic fill account for the gain.
Populating optional components is not treated as a goal in itself; useful
component and relationship corrections still survive.

## Sources and retained extraction issues

All sources are complete native units from the saved official United States Code
release `119-102`. Original XML, prepared text, source maps and archive digest
are retained in [source receipts](source-receipts.json) and `sources/`.
Freshness searches found no prior use of the selected native identifiers or
distinctive text in the searched experiment/example corpus; this is a local
history check, not proof of absence from model training.

| Native source | Selected native reading |
|---|---|
| 29 USC 2612(e): foreseeable leave | Complete medical-notice rule and earlier-treatment exception |
| 15 USC 1666(a): billing errors | Missing supplied alternatives and repeated-allegation limit |
| 15 USC 2064(b): product-hazard reporting | Complete reporting rule; actor component withheld |
| 15 USC 1692g(a): debt notice | Complete grouped notice, with ambiguous final-exception placement |
| 31 USC 3716(a): administrative offset | Four prerequisites retained only in a neighboring record |
| 29 USC 657(a): workplace inspection | Complete entry permission and credentials condition |
| 28 USC 1871(b): jury fees | Missing supplied base-fee and certification context |
| 42 USC 2000e–2(e): religious employment | Faithful prose, permission classified as absence of duty |

The eight native runs retain 25 accepted statements and zero rejected statements.
Hazard extraction remains partial: an incorrectly copied footnote/thin-space
sequence prevents actor-component evidence from being located. Its complete actor
meaning survives in the default statement. Other repeated-text evidence warnings
also remain. None of these captures was repaired or retried for this test.

The debt exception attachment, jury record boundary and religious classification
interpretation are explicitly uncertain in the frozen labels. The classification
case counts separately from missing-prose repairs. Manual labels are revisable
agent judgments, not independent human ground truth.

## Raw review and verification

All eight sources, all 25 native statements, constructed candidates and all 36
checker responses were read before aggregate scoring. [Raw observations](RAW-OBSERVATIONS.md)
cover every cell; [raw review](RAW-REVIEW.md) records the interpretation limits.
Cell order hid arm names, but wording and candidate counts could reveal the arm.

Correct verdicts do not guarantee faithful explanations. In cell 20 the model
claims that changing classification resolves a modality-evidence issue. An actual
temporary review preview confirms the semantic change but retains
`component_evidence_unresolved`. That status claim is false. Some other rationales
overstate the difference between synonymous modal wording. Conversely, a suspected
missing billing citation was disproved: passage F008 includes the questioned
condition. These checks are retained in [rationale checks](rationale-checks.json).

[Verification](verification.json) confirms all eight native captures replay and
all 36 checker requests and responses reproduce their saved decoding with provider
access blocked. There are no invalid checker judgments, missing responses or
missing usage receipts. Candidate previews preserve the original books/history.
Evidence-location validity and semantic completeness remain separate checks.

A post-score fixture check found one further diagnostic limitation: synthetic
exception C0004 retains its parent statement's top-level offsets (1070–1387),
although its shorter quote and evidence correctly locate 1243–1387. The complete
source is supplied and the semantic link controls remain interpretable, but this
packet is not a native compiled record. Do not count its successful judgments as
end-to-end offset validation. The original inputs and scores remain unchanged;
see [fixture check](diagnostic-fixture-check.json). Integration tests must use
consistent record and evidence positions.

## Usage and limits

Exactly **44 calls** were made: eight extraction, 32 fresh checker and four
diagnostic calls. No retries. Gemini 3.8 Flash used low thinking for extraction
and medium for checking; actual requests contain no deprecated sampling controls
or thinking budget. Output limits were 16,384 and 32,768 respectively.

Total usage is **369,720 tokens**: 233,313 input, 21,258 visible output and 115,149
thinking tokens. The 15,554 cached tokens are part of input, not an additional
chargeable-token count. Summed provider time was **441.1 seconds**, not wall time
for the concurrent experiment.

The fresh A checker calls used 139,390 tokens; B used 164,221, a **17.8% increase**.
B assessed 52 rather than 36 native decisions, a **44.4% increase**. Those unequal
tasks and provider caching prevent treating this as an equal-work price comparison.
The separate diagnostic used 18,132 versus 23,129 tokens. No dollar estimate is made.

The selected eight excerpts and constructed counterexamples do not establish
100% general accuracy, full-document completeness, reliable repair generation,
or automatic workflow correctness. Preserve this cohort as regression evidence;
use untouched sources for the next generation comparison.

## Reproduce and continue

From the repository root, using the recorded environment:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-fresh-field-completeness/verify.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-fresh-field-completeness/score.py
```

The scripts verify pinned local source/runtime dependencies; future source changes
will need this checkout or the recorded versions. The scorer reuses committed
earlier experiment helpers. `extract/leave/frozen` retains the single shared
runtime copy; `verify.py` reconstructs seven byte-identical ignored copies and
checks each original capture manifest. [Shared runtime hashes](shared-runtime.json)
and `MANIFEST.json` identify the retained artifacts. Do not rerun extraction or
checking as part of verification; the experiment has reached its call limit.

The [active implementation list](../../plans/2026-09-13-model-input-improvements.md)
now specifies the optional checker integration, explicit unchanged-target
accounting and separate repair-generation test. No production prompt, schema,
default extraction behavior or review approval changed in this checkpoint.
