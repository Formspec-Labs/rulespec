# Does extractor confidence identify incomplete meanings?

Decision: Decide whether extractor self-confidence merits a broader evaluation
as a review-priority signal. This experiment does not authorize production adoption.

Hypothesis: Confidence emitted in the extraction response ranks incomplete or
incorrect individual meanings below faithful ones. Competing explanations are
that scores track surface clarity instead of completeness, or that requesting
confidence improves the extraction itself. The first predicts confident errors;
the second predicts better meanings without necessarily useful score separation.

Arms: A is the current extraction request. B adds one confidence object AFTER
each unit's ordinary fields: a numeric score and brief, externally checkable
basis. Both are generated in the extraction call. The schema and its short
instruction form one intervention; do not attribute an effect to either alone.
Reuse Core ConfidenceRecord's constraints through native CUE, with deterministic
model-inference, uncalibrated and generatedBy metadata. Preserve raw responses;
strip only this experimental object in a derived copy for the existing parser.

Cases: Reuse exactly the supplied CSBG section 9908 window, 20 USC 1414(d)(1)
(IEP), and 20 USC 6312(b) (LEA). These are selected development cases, not fresh
holdouts. All source and context boundaries stay fixed. Prior failures are CSBG
emergency/replication detail, service methods and low-income recipients; IEP
transition subjects/courses and written parent agreement/consent on attendance
permissions. LEA is a faithful control with optional and conditional provisions.
Review every new record against its source, including additional defects.

Labels: A meaning is flawed if its statement loses or changes a substantive
condition, alternative, actor, force, quantity, required component or exception
needed to use that meaning independently. Verbatim evidence elsewhere does not
repair missing meaning. A faithfully separated rule may still fail independent
usability when the governing condition is absent. Record uncertain judgments
separately and exclude them from the primary ranking. Check wholly omitted units
separately: records that were never emitted have no confidence score. Labels are
revisable manual judgments, not gold answers or legal advice.

Held constant: gemini-3.8-flash, temperature 0, low thinking, no numeric thinking
budget, 16,384 maximum output tokens, same examples/source/parser/Core. One call
per arm per case (six total), randomized call order and arm-masked review names.
Hide scores and bases during manual review; save/hash labels before revealing
them. Stop at six attempts, 15 minutes of capture time, or 150,000 reported total
tokens, whichever is reached first; a running call may cross the boundary.
No retries, prompt tuning, automatic repair, additional audit calls or UI changes.
Zero temperature does not guarantee identical results. One observation cannot
estimate within-case variability.

Measures: Strict parsing and grounding, confidence adherence, source fidelity,
wholly omitted content, record counts, input/output/thinking tokens and latency.
For B, report score distributions for faithful/flawed records, pairwise ranking
(lower confidence should predict a flaw; ties count half), and the fraction of
flaws scoring at least 0.90. At a review budget of the lowest 20% of B records
(rounded up), report detected flaws. Resolve boundary ties by averaging over the
tied group rather than pretending arbitrary record order is a signal. Compare
against the random-review expectation of that same budget. Do not call these
scores calibrated probabilities on this small selected sample.

Decision rule: Investigate further only if there are at least three clearly
flawed and three faithful B records, pairwise ranking is at least 0.70, and the
lowest-20% review budget detects at least twice the random expectation, without
new substantive regressions in the named faithful controls. Otherwise retain
the current production pipeline: a weak ranking is no measured useful signal;
insufficient defects or ambiguous labels is unresolved. Any extraction-quality
change is a separate bounded observation, not evidence of confidence calibration.

Verification: Compare actual SDK request bodies against the pinned requests and
settings, and replay the experimental derived parsing/Core compilation with
provider construction blocked. This adapter replay is not normal CLI replay.
Validate generated confidence constraints with positive/negative fixtures. Keep
all failures and invalid confidence objects in the accounting.
