# Qualification and evidence regressions

These are saved provider outputs with revisable source-review labels. Use them
to assess a proposed change against actual failures, alongside fresh documents.
They are development data. The semantic failures remain unresolved; ordinary unit
tests verify deterministic evidence and consistency behavior, not model accuracy.

The immutable [cases](../../../thoughts/experiments/2026-09-11-qualification-links/cases.json)
contain each complete source, original rulebook, expanded inventory and actual
passage catalog. `C0000` etc. are request-local aliases for the indexed original
claims; use their saved IDs when evaluating records. Reuse these artifacts rather
than rewriting the original statements or duplicating their schemas.

| Case | Required finding | Counterexample |
| --- | --- | --- |
| `equipment`, C0000 | § 91.213(e)'s special-flight-permit route qualifies the opening prohibition; C0013's separate existence does not repair C0000 | Preserve permit conditions and the limited (d) route; do not invent unconditional operating permission |
| `ecfr-14-61-56`, C0010 | Simulator permission also requires (i)(2)'s landing-recency condition/exception and (i)(3)'s aircraft-rating condition | Approval for landings does not remove course or rating requirements; (f) waives only the ground-training hour |
| `ecfr-29-1910-132`, C0003-C0006, C0008, C0010-C0013 | Paragraph (g)'s included/excluded sections limit the (d)/(f) duties | Do not attach this restriction to independent provision, maintenance, design, damaged-equipment or payment duties |
| `ecfr-29-1910-132`, C0015 | The final note's other-standard payment precedence qualifies the general payment statement | Do not infer the contents of unavailable external standards or release maintenance duties through payment exceptions |

For complete criteria and uncertainties, read the frozen
[prelabels](../../../thoughts/experiments/2026-09-11-qualification-links/PRELABELS.md).
Inspect both the individual statement and whole-book coverage; these are different
outcomes. A found quotation, existing identifier or passing schema does not establish
that the statement preserves the qualification's effect.

Two deterministic regressions are now exercised in the package tests:

- Native PPE evidence spanning inserted formatting must retain its original
  pieces through inventory, comparison and refinement. The
  [source-evidence receipt](../../../thoughts/experiments/2026-09-11-expanded-inventory/comparison/ecfr-29-1910-132-B/source-evidence.json)
  preserves the original affected spans. Inserted substantive words remain refused.
- Equipment B returned U0006/U0007/U0008 with incorrect C0006/C0007/C0008 aliases,
  while the corresponding claim-side mappings named C0005/C0006/C0007. The
  [saved assessment](../../../thoughts/experiments/2026-09-11-qualification-links/comparison/equipment-B/assessment.json)
  must remain `needs_review`, with three unknown coverage results, when reevaluated.

The [expanded-inventory results](../../../thoughts/experiments/2026-09-11-expanded-inventory/RESULTS.md)
and [qualification-link results](../../../thoughts/experiments/2026-09-11-qualification-links/RESULTS.md)
retain raw requests, refusals, failures, settings, cost and replay receipts. Neither
experiment justified an additional default model pass. Historical runtime copies
remain pinned; the evidence fix belongs to the current application, not a rewrite
of those captures.
