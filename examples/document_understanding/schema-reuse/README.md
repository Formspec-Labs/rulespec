# Shared schema integration — 2026-09-08

Three existing Core capabilities now improve the extractor's output:

- `ApplicabilityScope` represents grounded conditions even when no territory is
  asserted. An empty jurisdiction list uses the existing Core schema; unsupported
  territorial evidence remains flagged. The complete meaning and scope evidence
  remain unchanged.
- `Finding` gives audit-detected omissions, suspected meaning errors and audit
  processing problems referenceable Core records in `findings.jsonld`. Each
  record identifies the affected document or claim, the audit Artifact and its
  completion time. The detailed report retains evidence and diagnostic fields.
  These model-assisted findings are warnings, not authoritative conclusions.
- `AILineage.temperature` records the actual request value, normalized to the
  float representation required by the existing graph validation.

No new Core schemas or copies of their definitions were introduced. The existing
JSON Schema and SHACL checks validate the emitted records. The model-facing
extraction schema and prompts are unchanged.

[246 tests pass](final-tests.txt). The [final verification](verification.json)
records seven scope nodes, eight applicability links, temperature 0.2, and six
Core audit findings. Both the reprocessed extraction and final live audit replay
without provider calls.

The original live extraction is preserved. Its documentation unit was refused
for a non-verbatim nested-list quotation. Two live Gemini audit trials detected
that missing requirement and its document alternatives. The first represented
the omissions as seven units; the final trial grouped the court-order options
and represented them as six. Both agreed on the substantive missing content.
These are observations about this sample, not accuracy or completeness scores.

Use `final-names`, `final-audit` and their replay directories for the final code.
Earlier trial directories retain the intermediate runtime and captures.
Reprocessing made no new extraction request; each live audit used two Gemini
requests. This work made no commits or releases.

The [active schema reuse checklist](../../../thoughts/reviews/2026-09-07-document-understanding-schema-usage.md)
tracks the remaining concept/assignment, source-attribution, typed-value and
consumer integrations. Shared definition improvements belong upstream in Core;
document-specific model instructions belong in the application profile.
