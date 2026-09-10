# Bounded improvement: display 27.5% fewer characters with the same evidence

The preregistered display-compaction gate passed on all six saved cases and all
eight constructed checks. Exact selected character positions, unchanged default
statements, every original span and role, and a reference from each display block
to its original evidence span indices were preserved. Disjoint and adjacent
intervals remained separate. Repeated words at different positions remained
separate. Unicode coordinates matched the source. Invalid evidence was refused.

| Case | Original packet characters | Compacted characters |
| --- | ---: | ---: |
| Passport | 434 | 242 |
| Seatbelts | 2771 | 2354 |
| Recording, experimental extraction | 1256 | 826 |
| First-aid uncertainty | 607 | 332 |
| Separate exemptions, constructed | 418 | 238 |
| AND duty, constructed | 276 | 185 |
| Total | 5762 | 4177 |

Savings: 1585 characters, 27.51%. Read every compacted display against the previous
display. The same Posts permission and recording prerequisite remain visible;
the seatbelt remote exclusions and the AR expansion remain absent. Supplies
scope remains ambiguous. This is a lossless reduction of selected source content,
not a semantic correction. It does not remove the separate extracted statement
even when that statement repeats source wording. Keeping that distinction allows
review of extracted meaning versus source evidence.

All results replayed byte for byte to compaction-replay. No model calls, new
provider charges, production changes, commits or UI changes. These are the same
development captures, not a fresh semantic benchmark. Costs measure displayed
characters, not provider tokens or actual user reading time.

The candidate lives only in compact.py. Production adoption would need a real
consumer of these display blocks; adding a redundant field to the persistent
export would undermine the purpose. Existing evidence records should keep their
own identity and roles. The experiment keeps originals and references them by
index; that index is an experimental view reference, not a new Core identifier.

## Existing support changes the next semantic experiment

Inspected the current CUE profile and callable audit/enrichment code:

- document-understanding.cue already requires complete statements, remote
  governing scope quotations, correct qualification targets and preservation of
  unresolved references. There is no need for a new condition storage schema.
- audit.COMPARISON_PROMPT already asks for a concrete case admitted by the draft
  that the source excludes. Calling that instruction a new scenario-audit idea
  would duplicate existing behavior. Whether the model actually performs that
  check remains an empirical question.
- audit.audit_run already builds a source-first inventory and then compares it
  with claims; it records findings without changing the draft. Reuse that flow.
- structure.enrich_run intentionally fills actors and definition links. It is
  not a general scope-repair pass; expanding it would be a separate design choice.
- The saved seatbelt extraction request contains the remote part 121/125/135
  exclusion text. For that actual failure, missing input is not the explanation.
  This does not establish how other audit windows distribute the same text.

## Proposed next bounded semantic comparison, not yet run

Decision: does requiring an explicit applicability counterexample in the existing
audit rationale improve detection of omitted governing conditions over the current
broad audit request? This tests instruction adherence and diagnostic benefit; it
does not test a new schema or automatic correction.

Arms: current comparison prompt versus the same prompt with a requirement to put
one source-versus-draft applicability contrast (or an explicit statement that none
is supported) in the existing rationale before scope/summary verdicts. Keep all
dimensions and cases in the result; extra rationale may increase cost or distract
from actor, modality and term judgments. Evaluate that possible regression too.

Reuse one frozen source-first inventory per document across both comparison arms,
the existing CUE comparison schema and capture machinery. Freeze claims and
source text. Use fresh comparison calls; saved historical audits are not controls.
Hold model, thinking, temperature, token limit, source catalog and inventory
constant. Randomize the arm order and hide labels for assessment where practical.

Select and pin two untouched official source excerpts before any calls, then
record manually reviewed dependencies and uncertain readings. Include the actual
seatbelt failure as development data. Include clear valid claims and a condition
that governs a different branch as false-positive controls. If using manually
altered claims to create errors, retain originals and label the edits as planted
defects; those do not measure the natural extraction error rate.

Bound: three documents, two arms, one comparison call per arm/document (six
comparison calls); up to one shared inventory call per document if no suitable
frozen inventory exists (three additional calls). Stop at that bound or 20 minutes
of provider time, preserving interrupted/failed attempts. Pin sources, exact
requests, model settings and labels in a separate pre-call plan before execution.

Advance only if the intervention demonstrates adherence, catches at least one
additional confirmed scope/summary defect on each of the two untouched documents,
and introduces no new material false positives or other-dimension regressions.
Report cases where both arms succeed or fail, output cost, and source uncertainty.
One call per arm cannot establish stability. Failure of this broader gate remains
a failure even if the familiar seatbelt case improves. No automatic production
adoption is authorized by an experimental pass.
