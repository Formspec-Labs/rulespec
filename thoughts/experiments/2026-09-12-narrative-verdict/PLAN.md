# Compact narrative input with a boolean fidelity decision

Decision: Can concise narrative input make the fixed-output source check useful
and cheaper? No production adoption, automatic corrections or new confidence
scores. The user requested narrative text, boolean true/false, minimal JSON/noise,
and a clear goal.

Hypothesis: Presenting source and meaning in readable text while removing nulls,
offsets and repeated evidence strings reduces input cost without losing the
information needed to identify omissions. Competing prediction: the source
comparison remains superficial, so shorter formatting saves tokens but misses
the same conditions. A shared boolean task separates format effects from the
earlier probability-scoring task.

Arms: A uses the prior JSON source/draft representation with a new concise
boolean instruction. B uses the SAME instruction and source/draft content in
a plain-text narrative, omitting nulls, offsets, redundant quotes, the section
index outside the supplied passages, and a scope statement only when it is an
exact substring of the statement. All statement/actor/kind/modality content,
nonredundant scope/choice text, term IDs, references and support passage IDs remain.
No prose paraphrasing by another model. Full supplied passage text remains in
order. This is a representation/filtering bundle, not punctuation removal alone.
Both answer in plain text: ID true, or ID false — specific defect (source IDs).
No provider JSON response schema or numeric confidence. The HTTP capture itself
remains JSON for replay; that is not the model-facing data format of B.

Cases: Exactly the same 81 fixed records across six saved outputs of three sources.
Use frozen source-grounded labels: eight clearly flawed, 66 faithful, seven
uncertain. The ordinary-extraction cohort has four clear defects and 42 faithful
records; the previously inline-scored cohort has four and 24. Prior CSBG partner,
methods/recipients/qualifiers and IEP transition/writing omissions are the actual
failures. LEA conditional/optional provisions are faithful controls. Unknown-label
items are reported separately. Labels are revisable, remain hidden from requests,
and are not changed after observing these verdicts. These are development cases,
not independent holdouts. Two variants of one document are not independent cases.

Held constant: Same shared goal, answer format, source availability, fixed
statements, record order, gemini-3.8-flash, low thinking, temperature 0, no numeric
thinking budget, 16,384 output cap, one call per arm/output. Randomize call order
and use opaque capture IDs. No repetitions, tuning, model rewrites or retry calls.
The earlier numeric-confidence pass is historical context, not this experiment's
contemporaneous format control.

Bound: 12 fresh assessment calls, 15 minutes or 120,000 reported total tokens;
check before each call, allowing one active call to cross a time/token bound.
Retain all failures. Stop after this comparison rather than tuning the same cases.

Measures: Exactly one parseable decision per expected ID, no unknown/duplicate
IDs, a source-supported specific reason on false verdicts, clear-defect detection,
false alarms on faithful controls, uncertain-item decisions, input/output tokens
and latency. Review every negative explanation and known-error approval manually.
True/false is a fallible fidelity judgment, not a ConfidenceRecord probability.

Decision rule: Narrative merits broader evaluation only with valid complete
output, at least 6/8 clear defects detected including at least 3/4 in ordinary
extractions, at most 3/66 false alarms, no more false alarms than A, and at least
20% fewer input tokens than A. If both variants fail usefulness but B is cheaper,
report cost improvement and unresolved fidelity, not a production-ready checker.
Passing only a narrower cohort is not a passed broader gate. No adoption on
these repeatedly reviewed sources; retain untouched cases for any next evaluation.

Verification: Freeze exact prompt files, source/draft/label/runtime hashes and
arm key before calls. Verify all original source passages/statements remain in
B, that every nonempty semantic/support field has a render or explicit redundant
representation, and that no previous score or critique enters either request.
Verify actual SDK contents/config (plain text, no response schema) and replay
the small line decoder with provider setup blocked. Reuse existing model setup
and raw capture; do not modify production code or prior experiment artifacts.
