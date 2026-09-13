# Fresh-source test of complete readings and field necessity

Decision: whether the unchanged positive shared-task checker is ready for a
bounded production integration proposal. Previous field-only revisions reduced
noise but still rejected necessary meaning. This is a policy comparison against
production, not another wording revision on the medical development case.

Hypothesis: explicitly evaluating the selected independently usable statement
will improve recognition of missing conditions while retaining rejection of
redundant fields. Competing explanations: earlier gains depend on familiar cases,
or the policy imports unrelated duties and suppresses useful component/edge edits.

Arms: A = current production CHECK; B = exact M4b/B instruction from the committed
instruction-isolation experiment. No new field paragraph. Same source, draft,
schema and relative ordering of shared candidates. A judges edits, matching
production; B additionally judges no-change candidates. This deliberate task
difference is part of the policy. Compare shared edits directly and report A's
unassessed no-change targets separately. Do not attribute the whole effect to one
sentence, candidate count or instruction placement.

Sources: eight previously unused native excerpts selected for source structure,
not model performance. Preserve their complete native units and prepared text.
Source-based criteria are saved separately before extraction. Use ordinary
production extraction, then manually assess the selected default readings before
constructing or submitting checker candidates. Choose the claim closest to the
predeclared target; explain ties or legitimate splitting before checker calls.

For each source, retain an unchanged candidate, a complete repair if meaning is
missing, and one materially wrong edit. On complete readings with empty optional
action/object fields, also construct a redundant fill and equivalent modal
rewording plus fill. Use at least three complete-reading contexts for that test,
including a complete sibling reading if the primary is incomplete. Do not invent
a natural omission or replace an inconvenient source. If coverage is insufficient,
report that limitation. All diagnostic edits are constructed answers around the
native outputs; this does not test repair generation.

Add one separate fresh-source diagnostic packet with a deliberately wrong actor
component and missing exception link, using the clearest available source. Test
correcting each without rewriting correct prose, plus wrong-actor and wrong-target
controls. Report these constructed draft results separately from natural output
accuracy. Preserve original drafts and history; never apply mutations to them.

Freeze exact candidate labels, uncertainties, source/runtime hashes and requests
before checker calls. The source-based selection rule precedes extraction; the
candidate-level labels necessarily follow seeing the actual draft. Keep these
stages distinct. Labels assess independently usable selected readings, not just
meaning retained somewhere in the document. Unavailable references stay explicit;
do not invent their contents or treat them as a reason to ignore supplied limits.

Settings and bound: 8 initial extraction calls, low thinking, default 16,384 output
limit; 32 fresh checker calls plus 4 separate diagnostic calls, medium thinking,
32,768 output limit. Gemini 3.8 Flash, supported provider defaults, no sampling
parameters or thinking budget. Two repetitions per checker arm/context. Reuse the
existing bounded runner: maximum 44 calls, 500,000 reported tokens and 2,400 summed
provider seconds before starting another call. No retries or replacement sources.
Keep invalid/partial captures and count missing judgments as failures. Repetitions
measure within-source variability, not additional independent sources.

Decision rule, frozen before model calls:

- B shared-edit correctness >=85%, with >=10 percentage-point gain over A and
  improvement in at least three source contexts.
- B accepts >=80% of needed complete repairs, with no loss against A. Require at
  least two naturally incomplete target contexts; otherwise this remains untested.
- B no-change correctness >=85%, with at least two complete and two incomplete
  native target contexts represented. A's unassessed no-change targets are not
  scored as erroneous shared edits.
- B rejects every known wrong-meaning/target control; both plain redundant fills
  and cosmetic variants reach >=90% rejection over at least three complete
  contexts. All four useful actor/link corrections in the separate diagnostic
  must be accepted, and its wrong controls rejected.

Report meaningful partial gains even if a gate fails. Passing justifies a concrete
integration proposal and its validation, not automatic adoption, automatic review
approval or a claim of general legal completeness. Judge rationale fidelity,
mechanical validity, prompt adherence, cost and source selection separately.
Review anonymized raw outputs before opening arm scores; the author may infer
arms from wording/counts, so this is not independent human blinding. Stop after
the decision or bound. Preserve this cohort as evidence and leave generation
holdouts untouched.
