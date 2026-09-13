# Separate checker input factors

Decision: identify a useful explanation for the standalone checker's leave false
alarm before changing instructions or integrating the candidate command.

Cases: the exact failed input from focused-check-integration cell 07 (leave),
and its unaffected complete-reading control from cell 03 (hazard). Both default
readings are complete for the supplied source under the frozen earlier labels.
Unresolved evidence/reference status remains real and separate from meaning.
The rich candidate sets retain the earlier wrong-meaning, redundant-field and
cosmetic-edit counterexamples. These are known diagnostic sources, not a new
generalization benchmark or a test of repair generation.

Factors, crossed independently:

| Arm | Other edited candidates | `link_issues` in the draft |
|---|---|---|
| A | Present | Saved raw-book value (null) |
| B | Present | Current review warnings |
| C | Absent; unchanged candidate only | Saved raw-book value (null) |
| D | Absent; unchanged candidate only | Current review warnings |

All four arms keep existing `issues`, `reference_links`, source passages, default
meaning, component fields, evidence, navigation, checker policy and output schema.
Only the additional `link_issues` field changes in the status factor. Do not erase
warnings from the stored records. Keep the unchanged candidate's ID `N0000` and
wording constant across all arms. Hold the relative rich-candidate order constant.
D must reproduce the saved actual failing/control requests exactly. Candidate
renaming in the rich inputs is disclosed; this experiment isolates the two factors
from the same fixed standalone input rather than reproducing every earlier arm.

Hypotheses and observable predictions:

- Extra link-status detail contributes to false alarms: B performs worse than A,
  and/or D worse than C, with the warnings cited in a faulty necessity rationale.
- Removing contrasting edits contributes: C performs worse than A, and/or D worse
  than B, while the meaning and statuses are otherwise identical.
- Both changes interact: repeated failures concentrate in D.
- Variability or an untested factor: failures do not repeat or differ inconsistently.

Settings: Gemini 3.8 Flash, medium thinking, 32,768 output limit, supported API
defaults without sampling controls or thinking budget. Two identical repetitions
per source/arm: sixteen calls in shuffled order. Before calls, freeze sources,
requests, labels, code hashes and the actual-request equality checks. No retries
or replacement cases. Stop at sixteen calls, 250,000 reported tokens or 1,200
summed call seconds before launching another request.

Decision rule: a factor provides a bounded mechanistic lead if a matched condition
is wrong in both repetitions while its one-factor counterpart is correct in both,
and the hazard control does not show a new loss of correct meaning judgments.
For an interaction lead, D must fail twice while B and C each pass twice. Mixed
results or no repeated failure remain unresolved; they do not establish that the
standalone checker is fixed. Report smaller directional differences without
claiming causality. With two repetitions, absence of a false alarm is weak evidence
against an intermittent problem. A mechanistic lead guides a separate comparison;
it does not authorize suppressing true status information or adopting a new prompt.

Read anonymized responses against the source and frozen criteria before aggregate
scoring. Candidate counts and warning text may reveal conditions, so this is not
independent human blinding. Score unchanged judgments, edited controls, rationale
fidelity, source validity and usage separately. Preserve prior failures and stop
without further tuning when the experiment reaches its decision or bound.
