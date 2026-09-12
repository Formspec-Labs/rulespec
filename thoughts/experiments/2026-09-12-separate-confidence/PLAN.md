# Confidence in a separate pass over fixed extractions

Decision: Does a separate source-based confidence pass merit further evaluation
for review prioritization? No production adoption is authorized by this test.

Observation: In the preceding experiment, four flawed records received inline
scores of 0.95–0.99; the scored CSBG output also compressed away required content.
Hypothesis: Assessing a fixed output in a new call separates the assessment task
from generation and produces lower scores for incomplete meanings. Alternatively,
the second call may repeat confidence in clear source language without checking
what the extracted meaning omitted. Low scores on the actual omissions distinguish
these predictions; this does not reveal the model's internal reasoning.

Comparison: Historical inline scores versus new separate-pass scores on the
EXACT SAME 31 records (CSBG-1, IEP-2, LEA-1 in the preceding experiment). Secondary
check: separately score the 50 ordinary-extraction records (CSBG-2, IEP-1, LEA-2),
which have no historical confidence score. Both cohorts include faithful controls
and real omissions. Do not regenerate or edit any extracted field. The separate
call receives the full original supplied source/context and ordinary extracted
fields/term index, with confidence, bases, labels, origins and prior critiques
removed. Required item IDs preserve association. Same order within each document;
randomized call order and opaque call names.

Cases and labels: Reuse all 81 rows and the prior source-grounded masked review,
including its seven uncertain judgments. Primary cohort has four clear defects,
24 faithful records and three uncertain; ordinary cohort has four clear defects,
42 faithful and four uncertain. Pin labels before new calls; do not relabel to
fit scores. CSBG losses, transition details and written parent agreement/consent
remain the actual failure cases. LEA's optional/conditional provisions are controls.
These are three selected development sources, not fresh holdouts. Each document
has two saved output variants, not two independent documents. No repetitions;
zero temperature is not a determinism guarantee.

Held constant: Same gemini-3.8-flash model, temperature 0, low thinking, no numeric
thinking budget, 16,384 output-token maximum. Reuse the already tested confidence
schema and Core metadata mapping verbatim; only an item-ID/list wrapper is new.
Use existing SDK capture and strict response reading. The deliberate intervention
is a separate fixed-output assessment task; it changes prompt and available draft
input as well as timing. Do not attribute the result to timing alone. Inline
baseline is historical, not a contemporaneous re-extraction control.

Bound: Six new scoring calls (three sources times two fixed-output cohorts), no
retries, tuning, rewriting, extraction, inventory or additional audit calls. Stop
before the next call at six attempts, 15 minutes of capture, or 100,000 reported
total tokens. A running call may exceed a time/token boundary. Preserve failures
and missing/duplicate/unknown IDs; do not silently exclude noncompliant calls.

Measures: Score presence/type/bounds, exactly one score per expected ID, unchanged
input meaning, brief basis grounded in supplied evidence, token usage and latency.
Use frozen labels for pairwise ranking (lower scores should predict flaws, ties
half; exclude uncertain labels), lowest-20% review budget rounded up (including
uncertain records, average ties), lift over random review, and clear defects still
scoring at least 0.90. Compare primary metrics to the historical inline scores;
report ordinary-cohort metrics separately. Missing source units have no score and
are outside the discrimination denominator, not fixed by this method. Manually
review all bases for detected omissions, mistaken criticisms and unsupported
certainty; never count a plausible basis as ground truth.

Decision rule: Further evaluation is justified only if all expected scores are
valid, primary ranking reaches at least 0.70, primary review-budget lift reaches
at least 2, and the ordinary cohort also reaches both thresholds. Report an effect
on just one cohort as bounded/partial, not a passed broader gate. Passing merits
fresh-case evaluation, not production adoption or claims of calibrated confidence.
Failures to reach the gate leave production unchanged. Report false alarms on
faithful controls and sensitivity to the pre-existing uncertain labels separately.

Verification: Pin exact prompts, schemas, runtime hashes, source/draft/label
artifacts and historical scores before calls. Match actual recorded SDK requests
to those inputs and replay decoding/metadata mapping with provider setup blocked.
Reuse the preceding frozen runtime rather than making another copy. Keep all
raw responses and derived records in this experiment directory.
