# Simplify the entry path; keep the shared implementation

The main workflow now appears first in the package README: direct source
extraction, source-preserving discovery export, and recorded usage. CLI help
points to the same sequence. The operating reference lists each command's inputs,
outputs, model calls and review effects. Chronological research and the old pinned
installation recipe moved to an evidence index; the recipe is explicitly historical.
Native annual CFR XML is correctly described as unsupported, with a separately
prepared text rendition used in the fresh experiment.

## Bounded duplication trace

| Concern | Existing owner and callers | Decision |
|---|---|---|
| Source grounding | `core.evidence_parts` composes the existing exact resolver, source slices and fragment identities; `audit._source_span` now delegates to it. Inventory, comparison and refinement use that route. | Keep the recently integrated shared helper. No new resolver. |
| Schema fields | `schemas.load_schema` checks packaged generated data and digests. Core/extraction/audit/refinement/structure consume the shared CUE views. | Keep generated views; they serve different requests and validation. Frozen snapshots are evidence, not live duplicate definitions. |
| Model requests and usage | `extraction._record_window` records actual requests/responses, errors and settings. `audit._capture` and `refinement._call` delegate to it; structure/enrichment uses `audit._capture`. | Keep one provider recorder. |
| Stage setup | Audit captures multiple windows; refinement creates one proposal/challenge capture and returns a decoded payload. Their setup/error wrappers look similar but have different directory and result semantics. | No new abstraction for this small similarity. This review found no additional duplication worth changing in the bounded scope. |
| Replay versus reprocess | Extraction verifies original runtime/bytes separately from applying current code to a new result. Review workspace exports also annotate existing unresolved references. | Preserve these differences; document them instead of hiding them behind one command. |

Trace: [Core](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py),
[schema loader](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/schemas.py),
[extraction](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py),
[audit](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/audit.py),
[refinement](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/refinement.py),
[structural enrichment](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/structure.py).

Only CLI descriptions/help changed in production Python. Model prompts, schemas,
defaults, extraction semantics, evidence rules and review behavior are unchanged.
The [fresh comparison](../experiments/2026-09-12-simple-path/PLAN.md) uses existing
operations to test the optional layers; it does not add a production model pass.

Validation: 689 package/schema tests passed (11,307 dependency warnings, no test
failures); all relative file links in the three operating documents resolve.
The rebuilt wheel is installed locally without dependency upgrades, its CLI source
matches the checkout, and all 92 installed packages pass dependency checking.
Fresh capture/replay and consumer checks are recorded with the experiment.
