# Do explicit qualification targets improve checking?

Decision: decide whether the existing relationship pass supplies useful rule
associations, and whether exposing those associations to the checker merits a
fresh-document evaluation. This is a diagnostic experiment, not adoption.

Observation: the preceding expanded-inventory experiment found the equipment
override and all simulator conditions separately but still approved incomplete
individual statements. PPE scope associations helped, while payment precedence
remained detached. Source availability and whole-book coverage are different
from the completeness of an independently reusable statement.

Hypotheses and distinguishable predictions:

- H1: explicit target aliases are useful missing input. Given identical proposed
  qualification meaning and evidence, the linked arm catches more actual missing
  qualifications without attaching them to the wrong rules.
- H2: the checker still treats one necessary condition as sufficient permission,
  or separately captured exceptions as repairing another statement. It approves
  incomplete claims even when a supported proposal explicitly targets them.
- H3: automatic association discovery is the bottleneck. The existing relationship
  pass omits, refuses, or misdirects the needed proposals. Those cases cannot test
  H1 under a faithfully supplied correct association; they remain workflow failures.
- Both arms improving would not establish a target-alias benefit. Added meanings,
  the common advisory instruction, or call variability could explain a difference
  from historical results. This experiment cannot separate those explanations.

Arms: generate relationships once per frozen book with the unchanged
`refinement.RELATIONSHIPS`, its CUE-derived `proposal_schema('relationships')`, and
existing decoder. A and B receive identical mechanically accepted proposal fields
and original source evidence. A omits `qualifies`; B includes the generated target
aliases. Both retain the proposed relation type. Remove generator rationale from
both comparison inputs so explicit C aliases in the explanation do not bypass
the intervention. Preserve raw rationale in captures for later manual review.
Natural-language target descriptions can still make associations inferable in A;
this measures the incremental value of aliases, not total absence of association.

The same common instruction treats proposals as fallible advisory data, never
applied corrections. Both arms assess every ORIGINAL claim and inventory unit.
Neither proposal inclusion nor schema validity establishes semantic truth. No
human target labels or defect answers are sent. All mechanically accepted proposals
are supplied, including possible wrong links; no selection based on semantic success.
Do not run a separate challenge stage in this diagnostic: manually assess every
proposal and every target after the comparison review. Production refinement's
proposal/challenge/apply sequence is not being evaluated in full here.

Cases: exact saved equipment, flight-review and PPE books plus their expanded B
inventories from `../2026-09-11-expanded-inventory/`. All are now development data;
no claims about general accuracy or new-document success. Copy the preceding
PRELABELS unchanged and append explicit target expectations before calls.
Primary outcomes: E1, F1's two necessary conditions, P1's nine affected statements
(one shared scope rule). Secondary P2: other-standard payment precedence.
Counterexamples: limited ground-hour exemption; approved-landings exception does
not cancel course/rating requirements; PPE (g) does not govern (a)/(b)/(c)/(e)/(h);
payment exemptions do not remove maintenance duties or permit compelled purchase.

Held constant: all source material, extraction bytes, expanded inventories,
comparison prompt/schema, passage catalogs, windows, model and settings. Reuse
the prior experiment's context-ID decoder and original-evidence whitespace adapter
in both arms; no production edits. `gemini-3.8-flash`, temperature 0, medium thinking,
32,768 output allowance, no thinking budget. One relationship generation and one
comparison per arm per case. Alternate comparison order A/B, B/A, A/B. Nine calls
maximum, 30 minutes accumulated capture time, 300,000 recorded tokens; stop before
starting another call after a bound is reached. No retries. Failed calls count and
remain unresolved. Failed proposal generation skips that pair. Partial valid
proposal sets remain eligible. No patching prompts after observing results.

Decision rule: investigate a fresh-document test only if supported generated links
exist for E1 and both F1 conditions, B catches both defects, B improves at least one
over A, preserves the PPE scope findings when available, and adds no confirmed
false qualification inheritance. Record P2 separately. Missing target generation
means H3 remains a bottleneck; correct supplied targets with missed effects support
H2. Failure of the broad gate is not success because one narrow case improves.
No outcome authorizes production adoption or editing original captures/reviews.

Review: randomize and mask six comparison outputs; assess all rationales against
raw source, including correct judgments and counterexamples. Save and hash this
review before opening the arm key or generated proposal targets. Masking may be
imperfect when the checker mentions proposed links. Then review every raw proposal,
its refusal/grounding and each target, separate generation adherence from checker
accuracy, inspect actual requests/settings/pair differences, and replay saved data.
Report mechanical validity, semantics, uncertainty, tokens/time and user benefit
separately. Agent labels are revisable, not authoritative legal conclusions.
