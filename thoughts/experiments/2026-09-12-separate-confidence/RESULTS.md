# Separate-pass confidence improved one cohort, but failed the broader gate

Keep this experimental. Scoring a fixed extraction in a separate source-based
call improved review ordering on the 31 records that previously had inline
confidence. It did not provide useful ordering on the 50 ordinary-extraction
records. No extracted statements, production schemas, UI or workflow changed.

The scorer recognized the missing written-parent-agreement/consent dependency
on two IEP rules in one saved version, lowering their scores from 0.99 to 0.95.
In the ordinary version, it missed the same dependency and claimed all conditions
were preserved. All eight clearly flawed records across both cohorts still
received at least 0.95. These scores should not be read as measured correctness
probabilities.

## Results against the declared gate

| Measure | Historical inline scores, same 31 records | Separate pass, same 31 records | Separate pass, 50 ordinary records |
| --- | ---: | ---: | ---: |
| Clear defects / faithful / uncertain | 4 / 24 / 3 | 4 / 24 / 3 | 4 / 42 / 4 |
| Pairwise ranking, uncertain excluded | 0.438 | **0.839** | **0.655** |
| Lowest-20% review budget, rounded up | 7 | 7 | 10 |
| Expected clear defects found, averaging boundary ties | 1.24 / 4 | **3.05 / 4** | **0.91 / 4** |
| Lift over random review at the same budget | 1.37× | **3.37×** | **1.14×** |
| Clear defects still scoring at least 0.90 | 4 / 4 | 4 / 4 | 4 / 4 |

Ranking equals 1 when every flawed record scores below every faithful record;
ties count half and random ordering has expectation 0.5. The gate required
ranking at least 0.70 and review lift at least 2 in both new cohorts, with all
expected scores valid. The primary cohort passes those numeric gates; the
ordinary cohort fails both. **Bounded improvement; broader gate not met.**

The document-level breakdown matters. In ordinary CSBG every record scores
0.95; all clear/faithful ordinary IEP records also score 0.95. Their within-document
rankings are each 0.5. The higher pooled ordinary score comes from faithful LEA
records scoring 0.98, not from discriminating good and bad records inside those
harder documents. Primary IEP's within-document ranking is only 0.556, while its
CSBG counterpart ranks its one clearly flawed record below all eight faithful
records. Do not generalize the pooled 0.839 into a reliable per-document detector.

No faithful record scored below 0.90, but neither did any clear defect. Two
previously uncertain ordinary records received lower scores: a LEA parent pointer
at 0.50 and an IEP writing rule with relative references at 0.65. Both explanations
raise reasonable standalone-usability concerns; their uncertain labels remain.
The manual review also found that the second pass recognized the writing
dependency in only one IEP variant and still praised the lossy CSBG summary.

Post-hoc sensitivity preserves all prior labels but explores assigning uncertain
records to either class: primary ranking ranges 0.563–0.865, ordinary 0.620–0.765.
The primary result depends on the stated treatment of ambiguous cases. The
ordinary cohort already fails under the frozen primary labels. No relabeling
was used to claim a passed gate.

## What changed in the experiment

Six new calls scored all 81 fixed records, with no extraction, rewriting or
automatic repair. Each received the exact original supplied source/context and
ordinary draft fields, including its term index, without prior scores, bases,
manual labels or origin labels. Output required one item ID plus the existing
confidence score/basis object. Inputs stayed in source/extraction order; call
order was randomized. The same model, low thinking, zero temperature, no numeric
thinking budget and 16,384 output cap were held constant.

This tests a separate fixed-output assessment task. It changes the prompt and
provides a completed draft as input; it does not isolate timing alone. Historical
inline scores are from the exact same records, but there is no contemporaneous
inline re-extraction control. There are three selected development sources, two
saved variants per source, and one scoring observation per variant. These are
not six independent documents, repeated trials, or untouched evaluation cases.

## Cost and verification

| Fixed-output cohort | Additional input tokens | Additional generated tokens | Additional total tokens | Recorded call time |
| --- | ---: | ---: | ---: | ---: |
| Previously inline-scored, 31 records | 19,600 | 2,540 | 22,140 | 8.6 seconds |
| Ordinary extraction, 50 records | 22,695 | 3,902 | 26,597 | 13.2 seconds |
| All six scoring calls | 42,295 | 6,442 | **48,737** | **21.8 seconds** |

These costs are in addition to extraction. No separate thinking usage was
reported; the actual request's low-thinking setting was verified. There were no
retries, incomplete responses or missing usage records. The declared bounds were
six calls, 15 minutes and 100,000 reported tokens.

All **81/81** scores have valid IDs, numeric scores/bounds and nonempty bases;
there are no duplicate, unknown or omitted item IDs. Actual SDK request bodies
match the pinned requests and settings. Exact draft fields, term indexes and
source windows match the previous capture. Replay of response decoding and Core
confidence metadata mapping was identical with provider setup blocked. All source,
draft and prior review hashes remained unchanged.

Reused the previous Core-derived confidence schema and metadata mapping, including
its documented bounded workaround for confidence-schema export limitations.
No new confidence semantics or compiler were added. The previous frozen runtime
is referenced and hash-checked rather than copied again. Numeric confidence is
stored as experimental per-item Core `ConfidenceRecord` data; production assertions
and review history are untouched. Mechanical validity did not establish source
fidelity or score calibration.

## What this leaves open

A separate pass can recognize a qualification that inline scoring overlooked,
but it still often approves incomplete meaning. In this pair, the successful
IEP version already named the writing rule's attendance/excusal targets and
included their source references. The other version retained only relative
clause references. Other surrounding fields and model variability remain possible
explanations; target-name causality is untested. Preserve this as a candidate
experiment, not an adopted requirement.

Missing entire source units still have no score. This does not solve coverage,
repair output, or establish independently usable requirements. Any future
adoption needs evidence on ordinary extractions and untouched sources, with
specific source-supported dependency findings assessed separately from a numeric
score. Stop here rather than retuning these six inputs.

Artifacts: `PLAN.md`, `REVIEW.md`, `assessment.json`, `verification.json`,
`precall-pins.json`, `cells.json`, `schema.json`, `captures/`, `decoded/`, and
`manifest.json`. Prior manual labels and exact source/draft paths are pinned
sibling artifacts from `2026-09-12-extractor-confidence`.
