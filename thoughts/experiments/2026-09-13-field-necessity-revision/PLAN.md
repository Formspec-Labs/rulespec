# Distinguish redundant field filling from missing meaning

Decision: whether a revised field-necessity paragraph fixes the medical regression
while retaining useful rejection of redundant action/object filling. This follows
the user's request to iterate on the unnecessary-field treatment specifically;
the broader positive shared-task fresh-source comparison remains pending.

Hypothesis: the earlier paragraph lets the checker equate elaboration of a
statement with filling optional fields. Defining redundancy by semantic change,
and distinguishing missing rule limits from generic mentions, will preserve
substantive repairs. Competing explanation: its general paraphrase-rejection
preference persists regardless of the paragraph. Another risk: any wording change
may become an excuse to approve unnecessary edits. Cosmetic-rewording controls
separate that failure from detecting actual added meaning.

Arms: A = current production CHECK plus the previously tested OPTIONAL paragraph;
B = identical CHECK with that paragraph replaced by the refined criterion in
instructions.json. This tests the paragraph as a whole, not each sentence. Keep
the successful M4b shared task out of both arms. No extra pass or output fields.

Cases: all six original M4a contexts and their original twelve candidates,
including the actual medical omission, component clearing, correct exception link
and wrong meaning/actor/target controls. Add three explicitly constructed
cosmetic-rewording variants of the existing unnecessary action-fill candidates:
inspection permission, jury duty and compensatory-time duty. They change only
modal phrasing, preserving modal force and all meaning, so remain unnecessary.
The original quoted evidence stays verbatim. All are known development sources;
the three new mutations are counterexamples, not fresh documents.

Labels: inherit the original labels unchanged. The medical default names
exceptions without stating their governing restrictions. Under the explicit
independent-use criterion, adding those restrictions is substantive even though
companion records retain them. Removing the saved mismatched action/object pair
and adding a missing correct exception link remain useful with unchanged prose.
The two notice controls have constructed draft/candidate fields, as documented
in the prior experiment. Labels are revisable; statutory text does not mandate
our product's record boundaries.

Held constant: source/draft/evidence, candidates and candidate order within pairs,
production CUE-derived checker schema, Gemini 3.8 Flash, medium thinking, 32,768
max output tokens; no sampling parameters or thinking budget. Two repetitions per
arm/context: 24 calls, 30 judgments per arm. Freeze all inputs, labels, dependency
hashes and instructions before calls. Reuse the prior capture runner and production
decoder; the pinned 24-cell list is the call bound. Its existing launch limits of
450,000 tokens and 1,200 summed provider seconds also apply. No retries or added
cells. Missing or invalid judgments count as failures.

Decision rule: advance B to fresh-source validation only if it accepts both medical
repairs and improves over contemporaneous A on that category; rejects all six
original unnecessary edits and all six cosmetic variants; accepts all four valid
component/link fixes; and rejects all twelve wrong-meaning/actor/target edits.
Report narrower gains or regressions even if the gate fails. If A and B both pass,
report no measured accuracy advantage rather than crediting a historical failure
as a fresh control. No production adoption follows from this diagnostic alone.

Review raw responses by anonymous cell before opening arm scores; the author may
infer arms from wording, so this is not independent human blinding. Assess actual
instruction adherence, source fidelity, completeness, edit necessity, evidence
validity and cost separately. Verify the actual request bodies and provider-blocked
response decoding. Keep all raw results and existing captures. Stop at the result
or bound; preserve fresh sources for the next decision instead of accumulating
prompt patches on the medical example.
