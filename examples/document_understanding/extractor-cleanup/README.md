# Extractor cleanup — 2026-09-08

The extractor now has one current response format and one meaning/evidence path.
This is a local cleanup; no provider calls, commits, or releases were made.

## Changes

- Parse `unit` / `unit_attributes` with the generated CUE schema. Missing model
  fields are refusals, including missing scope, modality and alternatives.
- Derive string/list field sets from that schema for examples and candidate
  defaults. Local candidates may omit unstated components; compilation always
  records complete meaning and explicit uncertainty.
- Remove per-kind response parsing, context-free window replay, JSON prompt
  examples, reduced review dimensions, old evidence-binding construction and
  dictionary-shaped assertion IDs. The parser version is now `document-understanding-raw/3`.
- Load refinement fields directly from generated JSON. Remove redundant imports,
  lazy Core access, repeated schema-file lists and recursive deep copies during
  schema formatting. Runtime Python is 69 lines shorter.

## Shared schema reuse

Existing Core `ValueAssertion`, `RelationshipAssertion`, `SourceFragment`,
`EvidenceBinding`, `ApplicabilityScope`, `Artifact`, `ExtractionActivity`,
`AILineage` and `Attestation` remain the output representations. Their existing
validation and evidence code stay in use. Both scope/context bindings and
qualification evidence now follow the same path for every compiled claim.

Rechecked `Finding`, assertion, applicability and evidence definitions against
this cleanup. `Finding` describes a detection about an identified subject; it
is not a source inventory or a dimension-by-dimension semantic assessment.
Document-specific fields and audit request structures remain application data.
No shared-schema defect requiring an upstream change was identified. Shared
improvements belong in Core, followed by regeneration, rather than in competing
application definitions.

## Checks

- [240 passing tests](current-tests.txt): parsing, current-format replay and
  reprocessing, audit, refinement, immutable review history, Core validation and
  native schema formatting.
- [181 validation controls](current-verification.json) agree across the former
  candidate schema, native generated JSON Schema and CUE itself. The same check
  confirms 24 saved experiment outputs still compile to identical rulebooks,
  mappings and graphs through their saved experiment adapter. This does not
  restore support for retired response formats in the current parser.
- [Schema comparison](schemas-verification.json): all five model-facing schemas
  retain identical content and ordering. Candidate validation is unchanged;
  only its description drops the legacy wording.
- Native generation `--check` passes. The verification also confirms all 62 Core
  CUE sources and 9,476 protected research/input files remain unchanged.

Historical research and captures remain intact. Strict replay detects changed
runtime inputs; reprocessing accepts the current format without compatibility
branches for retired formats.
