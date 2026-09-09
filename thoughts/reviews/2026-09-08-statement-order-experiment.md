# Statement-first experiment: useful local gains, no adoption

The output-order-only follow-up to the
[meaning-consistency experiment](2026-09-08-meaning-consistency-experiment.md)
is complete. Keep the current extractor default. Twelve live Gemini 3.8 Flash
calls compared two observations per variant on baggage, leave eligibility and
invented negative wording. Only the position of `statement` within the existing
CUE-generated schema changed. All 107 raw rows followed the requested order.

The treatment preserved the full firearm declaration in both repeats versus one
control repeat, and correctly avoided the ammunition absence-of-duty label in
both repeats versus neither control. It did not fix the invented ban exception:
all four observations still labeled it `exemption/not_required`.

These gains coexist with regressions. One treatment leave statement dropped the
proviso while retaining it in scope; another part of that output lost the
outside-US reference topic, retaining only its citation and original source.
One treatment baggage result selected partial logical evidence where both
controls selected complete lists. Another correctly stated the loaded-firearm
ban but attached only the introductory source passage, omitting the passage
that names loaded firearms from every evidence field.

The evidence supports a narrower diagnosis than "the model summarizes badly."
It can produce a correct statement with a wrong classification, a correct scope
with an incomplete statement, or a correct statement with insufficient attached
evidence. These are distinct failures. Moving one field first does not reliably
correct the others. This describes observed output; it does not establish the
model's internal mechanism.

All twelve runs replayed to identical compiled books with no provider calls.
All passed Core graph validation and had no rejected candidates or extraction
refusals. Raw statement, scope, kind and modality survived conversion unchanged.
Recorded usage was 80,290 tokens including thinking. There were no retries,
repair calls or model reviews. Production code and prior captures remain
unchanged.

The next high-value candidate is a narrow assessment of these specific defects,
using the existing audit/refinement path and saved cases before changing default
extraction. Evaluate detection and correction separately: a concern should be
recorded with evidence, and a proposed correction must preserve other meaning.
Avoid another broad prompt addition without evidence that it improves both.
This is a proposed next step, not an adopted implementation or a claim that the
existing audit already detects every case.

[Experiment results](../../examples/document_understanding/statement-order-experiment/README.md)
link the frozen design, criteria, raw captures, twelve source-review findings and
replay verification. Reviews remain revisable agent judgments. Two observations
per variant on selected development cases do not establish overall accuracy.
