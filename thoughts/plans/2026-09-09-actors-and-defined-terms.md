# Connect actors and defined terms

User authorized deciding and implementing the useful actor/definition workflow.
Fresh evidence is in examples/document_understanding/fresh-structure-check.
Choose combined first-pass structure for new drafts, fixed enrichment for existing
material. Neither promises completeness; do not add explanation fields or tune
source-specific prompts. Preserve all prior experiment manifests and UI history.

Implementation:
1. Reuse tested model-facing index/actor fields in canonical CUE; add a generated
   enrichment response for existing claim IDs. Reuse actor field types. Add only
   the small application fields needed to carry definitions and usage links.
2. Deterministically resolve registry aliases to source-bound term identities;
   connect definition/mention fields to Core LocalConcept, ConceptScheme,
   RelationshipAssertion and EvidenceBinding. Preserve distinct senses; refuse
   invalid IDs, unsupported names/evidence and unavailable definition targets.
3. First pass fills actors instead of unconditionally clearing them. Separate
   enrichment uses an allowlisted edit through existing review history, preserving
   statement, source and modal fields and existing populated components.
4. UI shows defined names/aliases and compact clickable usage links to definitions;
   actor appears in existing place. Missing actor means not recorded, not an
   assertion that source contains no actor. Export useful structure for discovery.
5. Meaningful tests: source evidence, duplicate/dangling references, distinct senses,
   definition changes/rejections, no rewrite/no overwrite, history, replay and
   generated CUE. Run live extraction/enrichment and inspect rendered navigation.

Pre-implementation checkpoint: all six fresh-source calls finished and reviewed;
production edits had not yet started. See completed checkpoint below. Existing worktree also contains two prior uncommitted
experiments, result hypotheses and handoff additions. Retain those exact captures.
No push/deployment requested. Do not read credentials into tool output.

## Completed implementation checkpoint

- Canonical CUE now generates term-index and fixed-enrichment schemas. First-pass
  parsing retains supported actor fields and resolves temporary term IDs.
- Definitions/aliases/uses map to existing Core concepts, relationships and
  evidence bindings. Current links report unavailable definitions; historical
  assertions remain. Qualification revision families remain separate.
- `enrich` / `enrich-replay` use existing review edits, never overwrite populated
  fields, retain raw refusals and require exact claim IDs/current revisions.
- UI and discovery exports show actors and navigable definitions. The review
  loader now honors optional modality quotes consistently with extraction.
- Live extraction produced 15 claims, six actors and two definitions. Live fixed
  enrichment preserved all 14 original statements while adding six actors/two
  definitions. Original and final-code reproduction are saved in
  examples/document_understanding/actor-term-integration.
- The fresh extraction repeated the known standalone local-modification caveat
  loss. The visible UI uses fixed enrichment of the intact original statements.
  No explanation fields or new source-specific prompt tuning were introduced.
- Browser inspection exercised both term links and keyboard focus. The Mac was
  locked, so a separate Playwright browser verified the page. Server port 63694.
- No commit or push in this continuation. Earlier experiment files retain their
  original manifests. All source and review changes remain locally reviewable.
