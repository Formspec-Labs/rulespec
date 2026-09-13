# Focused checker integration bridge

Decision: expose the successful completeness policy as an optional check of
explicitly selected current statements, recording assessments through existing
review history. Keep repair generation and the existing broad refinement behavior
separate until their own comparison. This is a narrower first integration of
M9a–d; it avoids asking an unvalidated generator to supply the evaluator's inputs.

Implementation: reuse the refinement runner, source catalog, CUE-derived fields,
checker result schema, recorded requests and replay. Build unchanged candidates
deterministically from current records. A `check --claim ID` command selects at
most eight exact current revisions. It performs no inventory, generation or
meaning edits. It records supported/unsupported/unknown assessments, preserves
approval and evidence warnings, and identifies unassessed or stale targets.
The shared candidate builder also accepts validated selected edits for the future
generation comparison, but this command supplies only unchanged readings.

Hypothesis: removing the constructed competing edits from the checker request
does not impair assessment of the same unchanged reading. Alternative: the
earlier correct judgments depended on being shown an explicit repair or wrong
counterexample. A new failure on an unchanged source would weaken adoption.

Arms: A is the exact saved positive-policy input from the previous fresh-source
experiment, sent again; B is the actual integrated check-only request. Both use
the same native draft and available source. B intentionally has only the
unchanged candidate, generated through the new production path. Compare the
shared no-change decisions; A's other edit judgments are additional diagnostics.
Preserve the independent-candidate instruction and reference navigation that
appear in the actual saved requests, not just the nominal policy constant.

Pre-call clarification from input preparation: opening a native extraction through
ReviewStore populates `link_issues` that were null in the raw-book experiment.
Retain these current status facts in B and save every difference; assert all other
source and claim fields match. This evaluates the actual integration bundle
(candidate removal plus current review status), so a difference cannot isolate
which of those two factors caused it. No source, meaning or label changes.

Cases: leave and hazard are complete controls; billing and offset have supplied
governing meaning missing from the selected reading. Reuse the frozen previous
labels and original native records. Hazard's actor evidence issue remains. These
are known regression sources, not a new generalization cohort. No ambiguous debt,
jury-fee or religious-classification labels are in the primary decision.

Held constant: Gemini 3.8 Flash, medium thinking, 32,768 output limit, current API
defaults without sampling parameters or thinking budget. Use a 24,000-character
window cap to retain the same complete native excerpt as the earlier requests;
the longest excerpt is 3,110 characters. Two repetitions per
arm/source, shuffled order. Maximum 16 calls, 200,000 reported tokens and 1,200
summed provider seconds before starting another call. No retries. Pin actual
requests and expected labels before calls; retain all responses and failures.

Decision rule: integrate this selected-statement check if B gets all eight
unchanged decisions correct with no regression against contemporaneous A, every
judgment has valid source evidence, and runtime tests pass for no mutation,
preserved warnings/approval, exact selection, stale revisions, missing judgments
and offline replay. If B fails, retain the implementation evidence but do not
present its changed request as an adopted quality improvement. Do not tune the
prompt to these cases. Record tokens, latency and rationale errors separately;
this is not an equal-work total-cost comparison or a test of repair generation.

Review raw responses in anonymous cell order before scoring. The reviewing agent
can infer arms from candidate counts; labels are revisable, not independent human
ground truth. Preserve all prior captures and their failed gates.
