# Extractor confidence did not provide a reliable review-priority signal

Keep confidence reporting out of production. In six live, paired extraction
calls, four clearly flawed records received scores from 0.95 to 0.99. The ranking
and review-budget gates failed. The confidence arm also compressed CSBG much more
aggressively and lost substantive content. This is one observation on each of
three selected development sources, not proof that every confidence approach fails.

The ordinary production extraction prompt, schema and pipeline are unchanged.
The experiment records confidence during extraction, not in a later audit call.

## What the model reported

| Record in confidence arm | Manual source finding | Score | Model's stated basis |
| --- | --- | ---: | --- |
| CSBG row 3 | All 13 plan provisions compressed into one statement; required methods, recipients, alternatives and conditions lost | 0.95 | “Captures the full set of statutory requirements” |
| IEP row 0 | Transition-assessment subjects absent; qualification on transferring rights omitted | 0.98 | “Complete definition of IEP captured directly” |
| IEP row 4 | Attendance exemption omits written parental agreement required elsewhere in the supplied source | 0.99 | “Self-contained statutory attendance exemption with explicit statutory conditions.” |
| IEP row 5 | Excusal permission omits written parental consent; the retained member's written input is a separate requirement | 0.99 | “Permission and governing cumulative conditions for IEP team member excusal are fully specified.” |

The same IEP response separately retained the parent's writing requirement in
row 6. The score did not flag that the two permissions failed to incorporate it.
The confidence bases are model assertions about output quality, not additional
source evidence or measured probabilities.

There was some useful ordering within CSBG: its most compressed record had the
lowest score. That limited signal did not generalize across these three sources.
Faithful LEA records all received 0.98; the two incomplete IEP permissions scored
higher, at 0.99. Observably, several bases cite clear statutory language or exact
capture despite missing meaning. This is consistent with confidence reflecting
surface clarity more than independent completeness, but does not establish the
model's internal mechanism.

## Predeclared measures

Reviewed all 81 emitted rows against the supplied passages with scores, bases and
arm names hidden. Saved and hashed labels before revealing them. Across both
arms: 66 faithful, 8 clearly flawed, 7 uncertain. Confidence arm alone: 31 records,
24 faithful, 4 flawed, 3 uncertain. These are revisable manual labels. A single
lossy parent record can contain many defects, so row percentages are not a
comparison of overall document accuracy.

- Confidence adherence: 31/31 complete numeric-score/basis objects; all scores
  passed the experiment's Core-derived validation. No malformed confidence rows.
- Pairwise ranking, excluding uncertain labels: **0.4375**, versus the required
  **0.70**. Here 1 means every flawed record ranks below every faithful record,
  and ties count half. Random ordering has expectation 0.5.
- All **4/4** clearly flawed scored at least **0.90**. Faithful scores ranged
  0.98–0.99; flawed scores ranged 0.95–0.99.
- Reviewing the lowest 20% of all scored records means 7/31 records. With the
  21-way tie at 0.98 averaged fairly, expected known defects found are **1.24/4**,
  compared with **0.90** from random review: **1.37×**, below the required **2×**.
- Excluding uncertain records from the budget as well gives 6/28 records,
  expected 1.24 defects versus 0.86 random, **1.44×**. Same failed decision.
- Post-hoc label sensitivity: all eight binary assignments of the three uncertain
  B records yield pairwise rankings between **0.313 and 0.569**. None reaches 0.70.

The sample has enough clear positive and negative records for the declared
diagnostic gate. It does not establish general calibration, within-case stability,
or a production-wide error rate. No repeated calls or untouched holdouts were used.

## Extraction quality and cost

| Supplied source | Ordinary records | Confidence records | Ordinary total tokens | Confidence total tokens |
| --- | ---: | ---: | ---: | ---: |
| CSBG section 9908 | 28 | 10 | 15,602 | 11,647 |
| IEP definition/team/attendance | 8 | 8 | 7,095 | 7,375 |
| LEA plan contents | 14 | 13 | 7,212 | 8,135 |
| Total | 50 | 31 | 29,909 | 27,157 |

CSBG ordinary extraction retained separate content requirements and all three
previously missing component groups, though it still omitted named grassroots
partner categories. The confidence arm collapsed all 13 contents into one lossy
record, losing those groups and several previously faithful qualifications.
Grouping is acceptable when complete; these losses make this observation a
regression. One pair does not establish that confidence caused a repeatable
compression effect.

Both IEP arms still omitted writing conditions on the attendance permissions.
Ordinary extraction retained the transition-assessment subjects but omitted
courses of study; the confidence version did the reverse. Both retained all
eight broad definition groups and the qualified team composition. The two
construction rules' force classification in B is uncertain, as documented in
the masked review. Both LEA arms preserved all 13 substantive requirements and
their optional/conditional controls; A added a parent pointer.

Both CSBG arms omitted the supplied 2014-amendment effective-date statement and
editorial/history units. Missing units have no score. Self-confidence on emitted
records cannot establish that the source was completely captured.

Six calls used **57,066 reported total tokens**: 29,566 input and 27,500 generated
candidate tokens. No separate thinking usage was reported; do not infer that
the low-thinking setting was disabled or that thinking has zero cost. Recorded
provider-call time totaled 62.6 seconds; capture plus local processing took
70.6 seconds. B used 9.2% fewer total tokens overall because its CSBG response
omitted detail; this is not a demonstrated efficiency improvement. IEP and LEA
used more tokens with confidence. No dollar estimate or price lookup was needed.

## Reuse, schema limitations and verification

Reused production source windows, prompt/examples, SDK capture, strict response
parsing, passage resolution, candidate compilation and Core graph validation.
The only model-facing change was a trailing confidence object plus its short
instruction. Actual SDK request bodies match the pinned prompts/settings/schemas;
removing that object from B's schema exactly restores A's schema. All six responses
finished normally; 81/81 rows parsed and compiled, with no refusals or rejections,
and all six graphs validated. Saved adapter replay matched exactly with provider
construction blocked. Valid schemas and exact replay did not imply faithful meaning.

Each confidence object maps deterministically to Core `ConfidenceRecord` with
`model-inference`, `uncalibrated`, and the generating model. Records are saved in
an experimental sidecar by raw row index; they are not attached to production
assertions or shown in the UI. Exact row/statement identity through parser and
Core was verified; no fuzzy association was used. Original provider responses
retain confidence, while a separately saved derived response strips it for the
unchanged production parser.

Schema discovery remains relevant to future adoption:

1. The repository's compiled Core confidence schema contains required metadata
   but omits the numeric/categorical score disjunction. It alone cannot validate
   a numeric confidence score.
2. Native CUE retains numeric bounds in the parent disjunction, but the indexed
   application field export loses those bounds. A nonempty list shape was also
   needed to evaluate Core's `list.MinItems(1)` in this isolated export.
3. The experiment reuses the native-generated numeric branch, combines it with
   existing compiled metadata validation, and uses its constraints in the model
   field. It removes only redundant identical `prefixItems`. Positive/negative
   fixtures verify required metadata, score presence/type/bounds, nonempty basis,
   and model-field closure. It does not fix or certify the general Core compiler.

The pre-call CUE probing problems occurred before any model call. Their successful
bounded workaround is recorded in `run.py`, `native-exports.json` and
`schema-checks.json`; no failed model attempt was discarded. Upstream confidence
schema parity needs a focused fix if this capability is pursued later.

## Decision and next useful question

**No adoption. No measured useful confidence signal under the declared gate;
the required completeness outcome is not solved.** Preserve this negative result
instead of tuning its confidence instructions on the same three sources.

The remaining useful question is whether a separate check can identify specific
missing conditions or required components in a fixed statement. Such a checker
would still need to demonstrate that it catches these actual failures. The prior
inventory-audit experiment did not. Treat the score, source evidence and measured
review result as separate information, and keep the current production workflow.

Artifacts: `PLAN.md`, `BLIND-REVIEW.md`, `blind-labels.json`,
`blind-review-pin.json`, `assessment.json`, `label-sensitivity.json`,
`verification.json`, `captures/`, `decoded/`, `frozen/` and `manifest.json`.
Sources are pinned sibling experiment inputs; `precall-pins.json` records hashes.
