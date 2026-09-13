# Quoted narratives for fixed-output judgments

Decision: Does composing source quotations and extracted meaning into each
question justify a broader test of this optional second pass? Research only.

Hypothesis: Repeating source text inside each judgment makes omitted conditions
and detail easier to detect than a shared source block. A competing explanation
is that the boolean task still accepts plausible paraphrases regardless of where
evidence appears. This tests a composition/repetition bundle, not prose alone.

Arms: A is the preceding experiment's shared plain-text source and item layout.
B composes each question into a paragraph: given quoted source, does quoted
statement faithfully assign quoted actor, kind and force, including quoted
scope and supporting text? B resolves support passage IDs into actual quotations
and repeats the full supplied source within every question. It also repeats the
proposed term catalog. No separate source or field blocks in B. The complete
source is a deliberate superset of relevant context: this avoids testing an
unproven relevance selector at the same time. It is not the proposed efficient
production input. No source text outside the original window is introduced.

Cases: Fixed iep-1 (8 items) and lea-1 (13 items) from the original confidence
experiment: 3 clearly flawed, 17 faithful, 1 uncertain. These include omitted
transition detail, missing written parental agreement/consent, and valid
conditional/optional requirements as counterexamples. Preserve the previously
pinned, revisable labels. These repeatedly reviewed cases are development data.
Other saved outputs are outside this small test, not failed cases discarded
after calling the provider.

Held constant: Both arms use the same concise boolean instruction, exact source
availability, fixed extracted meaning, item order, model gemini-3.8-flash,
temperature 0, low thinking, no numeric thinking budget, plain-text responses,
16,384 output cap. One fresh call per arm/document, shuffled opaque cell IDs.
No retries or tuning after capture. No numeric confidence or rewriting output.
Null fields need no prose; all nonempty meaning/support fields are represented.

Bound: Four calls, ten minutes, or 75,000 reported total tokens; check before
each call (one active call may cross the bound). Retain incomplete/failed calls.

Decision rule: Investigate on fresh documents only if B detects at least 2/3
clear defects, improves on A, and raises no more than one false alarm on the
17 faithful controls. Report uncertain items separately. Do not adopt on this
small test even if the gate passes. If it fails, save the finding and stop this
format iteration. More tokens are acceptable for this diagnostic but must be
reported; no claim of cost efficiency is intended.

Checks: Pin exact prompts, runtime, fixed inputs and labels before calls; use
existing provider capture and passage resolution. Check that every B question
contains every supplied source passage, its unchanged statement and all populated
meaning/support fields, with no earlier labels/scores. Verify actual requests and
replay verdict parsing offline. Allow balanced brackets around output IDs as
already observed; refuse unknown/duplicate/missing IDs and false without a reason
and supplied source ID. Inspect raw verdicts and explanations against source.
