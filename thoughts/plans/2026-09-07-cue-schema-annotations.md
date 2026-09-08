# Preserve schema guidance in the CUE projector

**Current decision after the settings recheck:** test native CUE generation
for the extraction application schema before building a general source reader.
The official explicit-open migration fixes the small composition failure, and
`matchIf` preserves the small conditional example. Full Core export still fails
the saved cases, so retain the existing production build during a staged change.
The extraction profile now uses native generation; its exact rich model schema
and saved-output checks pass. The legacy Core parser and annotation changes are
not implemented. See [the delivered application migration](2026-09-07-native-extraction-schema.md).
See [results and revised sequence](../reviews/2026-09-07-native-cue-assessment.md).
The unfinished custom annotation parser was saved under
`examples/document_understanding/cue-projector-verification/` and removed from
the active compiler. The sections below preserve the earlier scope and the
investigation that led to this decision. They are historical scope, not a
requirement to implement a new general parser first.

The user directed fixing the CUE projector before continuing schema
consolidation. This change preserves CUE documentation as JSON Schema
descriptions and supports explicit `@title("...")` and
`@description("...")` annotations. Existing validation constraints and property
order must remain unchanged.

Scope: definitions and fields, inherited property guidance, local/cross-file
named references, and quoted text containing URLs, escapes, or punctuation.
Descriptions are annotations, not validation rules. Explicit descriptions
override nearby comments; derived field guidance overrides inherited guidance.
Malformed explicit annotations must produce a compilation error.

Check real CUE syntax, compiler regressions, representative validation behavior,
and annotation-stripped parity against schemas produced before the change.
Preserve prior model captures and review history. The extraction-profile
migration and concept integration follow this projector fix; neither is part
of its acceptance claim.

## Native compiler assessment after the user's challenge

The user interrupted implementation to ask why Rulespec maintains its own CUE
compiler. Investigate that choice before extending the text parser further.

Verified on 2026-09-07:

- The original ADR, `docs/adr/2026-05-12-rkaf-constraint-source-cue.md`, calls
  for native CUE export to drive JSON Schema generation. The initial compiler
  commit, `99c21eb`, instead introduces a Python structural parser. Neither
  that commit's explanation nor the searched plans documents a comparison
  justifying this departure.
- The installed compiler is CUE v0.10.0. Its `cue def --out openapi` command
  exports the actual `UsageEligibility` definition with its full documentation
  comment as `description`. It rejects `--out jsonschema` as unsupported.
- Exporting all 40 Core files together through the installed OpenAPI exporter
  fails on an unresolved disjunction in `AssertionEnvelope`. Both ordinary
  and strict export fail. Native export is therefore not a verified drop-in
  replacement for the current complete build.
- Current upstream documentation describes direct Draft 2020-12 output with
  `cue def --out jsonschema`. That newer route has not been tested locally.
  See https://cuelang.org/docs/concept/how-cue-works-with-json-schema/ and
  https://github.com/cue-lang/cue/releases.

Saved native commands and outputs:
`examples/document_understanding/cue-projector-verification/native-export/`.

The right next assessment is to test a separately installed current CUE
compiler against existing conditions, composition, annotations, property order,
and valid/invalid fixtures. Preserve Rulespec's deliberate JSON-LD conventions
and its target-specific generators where needed. A limitation in native schema
export does not require a separate CUE text parser: upstream's parser and Go API
are another integration route.

Before the native assessment, the local annotation patch's initial regression
run had 143 passing tests and one exact schema comparison failing because it
gained a description. That unfinished patch is now checkpointed outside the
active compiler. No compiled artifacts, source constraints, model captures,
or review history were replaced.
