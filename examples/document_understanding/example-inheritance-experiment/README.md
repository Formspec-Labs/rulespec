# Explicit example inheritance: promising result on the teacher paragraph

The revised instruction preserved the teacher example's governing condition in
both runs; both controls lost it. When a synthetic variant explicitly changed
the example's scope, both versions respected the change. This supports the
specific instruction on this passage. It does not establish general accuracy or
justify adopting the whole passage-ID prototype.

## What changed

Both arms use the frozen passage-ID source-inventory prototype from the
[audit-grounding experiment](../audit-grounding-experiment/README.md). This is a
test of the audit's source inventory, not a full extraction or downstream workflow.
The control is its unchanged CUE-generated schema. The treatment adds only this
to `meaning.description`:

> When a passage gives an example of a rule (for example, signaled by 'for example' or 'such as'), preserve that relationship: if you extract the example as its own unit, include the governing rule's conditions in that unit's meaning. Do not turn an illustration into an unconditional duty. If the source explicitly changes the example's scope, use that scope instead; do not inherit a condition the source overrides.

The unsuccessful generic reminder from the
[previous teacher test](../teacher-scope-experiment/README.md) is not included.
This isolates the specific example instruction against the original baseline.
Saved request comparisons confirm that this description is the only difference
within each pair. Source, prompt, field order, schema constraints and other
settings remain identical.

Eight calls ran: two cases × two arms × two repeats. Settings: `gemini-3.8-flash`,
medium thinking, temperature zero, no numeric thinking budget, no application
output cap. No retries, repairs, comparison audits or full-document calls ran.

## Cases and results

The original fixture is byte-identical to the saved teacher/burden fixture,
including surrounding context. Its general employer burden applies when accurate
hours records are not maintained. The teacher duty follows as an example.

The synthetic counterexample changes only the teacher sentence's opening to:
“Regardless of whether the employer maintains accurate records of hours worked,
an employer must be able to clearly demonstrate, for example, that full-time
teachers ...”. Its document metadata labels it invented, and it carries no
source URL. The adjacent context text is unchanged. This is a test fixture,
not a statement of the actual regulation.

| Primary semantic check | Control | Revised instruction |
|---|---:|---:|
| Original teacher duty retains inaccurate-record condition | 0/2 | 2/2 |
| Synthetic teacher duty respects explicit scope override | 2/2 | 2/2 |

The revised original outputs begin:

- Repeat 1: “As an example under the rule placing the burden of proof on employers who do not maintain accurate hours records ...”
- Repeat 2: “As an illustration under the condition that an employer does not maintain an accurate record of hours worked ...”

Both then preserve the teacher-specific proof, 1,250 hours, previous 12 months,
institutions, teacher-definition citation and outside-classroom/home work detail.
Both revised counterexamples instead begin “Regardless of whether ...”, retaining
the explicit override without imposing the inaccurate-record condition.

Every call also preserves the condition on the general employer burden, including
its application to employees exempt from recordkeeping requirements. All preserve
the aircrew special-rule reference as background. No adjacent USERRA, accounting
or timing condition transfers into these rules. Original control repeat 2 also
omits the outside-classroom/home work detail; all other calls retain it.

All calls produce two requirements and one background reference. No new substantive
error was observed in the treatment outputs under the pinned criteria. All raw
unit meanings and revisable agent assessments are saved in `source-review.json`;
these are not independent gold labels.

## What the result supports

The predeclared narrow gate passes: both original controls reproduce the omission,
both revised originals retain the condition, and both revised counterexamples
respect the override without new substantive errors observed.

The earlier generic instruction said to retain governing conditions but failed
on this same paragraph. The specific instruction tells the model how an example
relates to its governing rule. That difference is consistent with the failure
arising when an illustrative example becomes a separate standalone duty. It does
not reveal the model's internal reasoning or establish that this is the only cause.

The scope override is deliberately explicit and the source remains very close
to the original teacher paragraph. Success here does not demonstrate handling of
subtle scope changes or other documents. Two repeats per case are a narrow check,
not a general accuracy estimate.

Next useful step: one small comparison on previously untested illustrative rules,
including a descriptive example that must not become a new obligation. If that
also improves scope without introducing obligations or omissions, carry the
successful wording into the authoritative CUE definition and regenerate derived
schemas. Keep this wording decision separate from adopting the passage-ID
prototype, whose other semantic failures remain unresolved. No follow-up calls
or production changes were made in this experiment.

## Verification and replay

All eight responses ended STOP, all evidence references resolved without inventory
issues, and all eight inventories plus aggregate results replay identically without
provider calls. These structural checks are separate from the semantic review.
Reported tokens: **26,241** total, comprising 12,530 control and 13,711 treatment.
This sample does not establish a general cost effect.

The provider reports identical input-token counts within each pair despite the
changed description. Captured requests verify that the instruction is present;
those counts do not establish how schema descriptions are accounted for.

`design.json` pins the fixtures, schemas, criteria, runner, prior prototype manifest
and runtime hashes before acquisition. `runs/` retains requests, responses,
attempt metadata, inventories and per-run manifests. `verification.json` records
checks; `decision.json` records the narrow result and proposed next step. The
outer manifest covers saved artifacts and excludes Python bytecode caches.

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/example-inheritance-experiment/experiment.py replay
```

Production code, schemas and defaults remain unchanged; no production test suite
was rerun. Research and findings are local and uncommitted. Previous captures
remain intact.
