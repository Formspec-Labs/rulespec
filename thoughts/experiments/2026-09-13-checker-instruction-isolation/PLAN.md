# Isolate field necessity and condition wording

Decision: identify which, if either, narrow checker instruction merits a new-source
validation. Keep production unchanged in this diagnostic.

Observed: the shared task rejected 6/6 unnecessary action-field edits, but lost
2/2 correct medical repairs. Its privacy rationales inverted the sentence about
conditions retained elsewhere. The same checker still approved incomplete notice
readings. These observations do not establish the model's internal reasoning.

## M4a: optional action/object fields

Hypothesis: explicitly distinguishing filling empty optional components from
repairing incorrect components will reduce unnecessary edits without discouraging
substantive fixes. Competing explanation: the earlier benefit requires the larger
shared task, or the instruction induces indiscriminate rejection of any edit with
unchanged prose. The component and qualification controls separate these outcomes.

Arms: A = current production CHECK; B = the identical CHECK plus the single
field-necessity paragraph saved in instructions.json. No no-change candidates in
either arm. Same source, draft, schema, candidate order and settings within a pair.

Cases: the saved inspection, jury and compensatory-time unnecessary action filling
and wrong-meaning edits; the actual medical needed repair and wrong conjunction;
two diagnostic controls based on the saved notice source. The first transplants
the saved model's bad action/object pair into the complete constructed notice
reading, then tests clearing those fields versus substituting the Commission as
actor. The second adds the missing exception link to the original notice draft,
with a wrong-target counterpart. These two drafts/candidates are constructed,
not fresh extraction results. Original sources and outputs remain untouched.

Decision rule: advance only if B rejects all six unnecessary-edit judgments,
outperforms A on that category, accepts both medical repairs and all four genuine
component/link fixes, and introduces no additional known wrong-edit acceptance.
A failure can still reveal a bounded gain; report categories independently.

## M4b: positively state completeness of the selected reading

Hypothesis: the ambiguous negative wording contributes to the privacy inversion
and crediting conditions retained outside the selected statement. Replacing only
that sentence with a positive direction will improve completeness judgments.
Competing explanations: the problem is a persistent preference for separate
records, or the broader necessity instruction suppresses needed elaboration.
If the inversion disappears but omissions remain, wording alone is insufficient.

Arms: A = the previous shared CHECK_TASK; B = exactly the same text with one
sentence replaced, as saved in instructions.json. Both judge the same edits and
no-change candidates. M4a's paragraph is absent from both arms.

Cases: unchanged saved privacy, medical, notice and synthetic request/inspection
control packets and candidate groups. Include incoming exceptions, medical
disclosure restrictions, the notice waiver and separate surviving duty, an
unrelated agency reporting duty, correct no-change inspection and wrong targets.
Keep prior labels, including the explicit requirement to make the selected default
reading independently usable. Complete document-level retention is a different
criterion. The source does not itself prescribe our product's record boundaries.

Decision rule: advance to untouched sources only if B gains at least three correct
judgments across privacy/medical/notice, improves at least two of those contexts,
and loses no correctness on known wrong edits or the complete no-change control.
Report needed repairs and incomplete no-change decisions separately. Do not
require perfection or reinterpret labels after calls.

## Common limits and evidence

Use production capture, CUE-derived CHECK_SCHEMA and passage resolution. Run two
fresh calls per arm/context: 24 calls for M4a and 16 for M4b, maximum 40. Use
gemini-3.8-flash, medium thinking, max_output_tokens=32768; omit sampling settings
and thinking budget. No retries, replacements, repair generation or additional
source extraction. Stop launching at 450,000 recorded tokens or 1,200 summed
provider seconds; an in-flight call may exceed a bound. Missing/invalid judgments
count as failures. Repeats measure within-case variability, not new documents.

Freeze all inputs, labels, runtime hashes, instructions and source dependencies
before calls. Randomize cell names and order; review raw responses before opening
the arm key. This is an agent review, not independent human blinding: instruction
wording may reveal the treatment. Preserve all requests, raw responses, usage,
nonadherence and label uncertainty. Verify actual SDK request bodies and re-decode
all saved responses with provider access blocked. No production adoption or broad
accuracy claim follows from this selected development set. Stop and consolidate
at the decision or cap; a successful diagnostic gets a separate fresh-source test.
