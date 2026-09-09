# Existing schema reuse in document extraction

The extractor uses Rulespec's evidence and assertion foundation, but several
existing schema families could support its discovery and workflow use cases.
Originally inspected after rich-schema adoption on 2026-09-07. Updated on
2026-09-08 as shared-schema integrations are implemented. This is the active
reuse checklist; moving the model schema to CUE did not complete these integrations.

For current settings and the completed extraction handoff, use the
[operating guide](../../packages/rulespec-extrapolator/README.md) and
[final checkpoint](2026-09-09-extraction-handoff.md). The table below tracks
schema capabilities, not a requirement to add every optional field to extraction.

The normal extraction pass now selects complete statements, modal force, scope,
context, alternatives, references and exact evidence from this same CUE profile.
Concepts, attribution, typed values, effectivity, actor/action/object components
and explicit relationship records remain connected through Core and optional
refinement. They are not requested on every first pass. `meaning.schema.json`
keeps the full generated field definitions independent of `provider.schema.json`.
The [adoption record](2026-09-08-meaning-first-adoption.md) explains the measured
tradeoff. `discovery-export` now connects the source/scope/context view without
additional model inference and retains unlinked passages and pending review state.

## What is connected now

[`build_graph` and `validate_graph`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py)
emit or validate sixteen concrete Core record types: `Artifact`, `SourceFragment`,
`ValueAssertion`, `RelationshipAssertion`, `EvidenceBinding`, `AILineage`,
`ExtractionActivity`, `Attestation`, `ApplicabilityScope`, `Finding`, `SourceClaimant`,
`ConceptScheme`, `LocalConcept`, `ConceptAssignment`, `ReferenceResourceRelease`,
and `EffectivePeriod`. Audit
findings ship in `findings.jsonld`, separately from the source rulebook graph. Optional records
appear only when their inputs exist. Shared CUE definitions and enums are also
used through those generated schemas; sixteen record types is not a count of every
reused CUE definition. There are 40 Core CUE source files, many containing several
definitions.

The earlier capability assessment is stale in two places: `definesScope` and
`providesContext` evidence functions are now connected, and the graph accepts
`ApplicabilityScope`. Supported scope text and quotations now produce a Core
scope even without territorial evidence: its jurisdiction list is empty, making
no territorial assertion. Unsupported jurisdiction text remains flagged on the
claim. Explicit effectivity now links the meaning through its applicability scope to
`EffectivePeriod`; relative deadlines remain typed values. Subject-specific
applicability is still retained in scope text. The full meaning assertion and
its scope evidence remain intact.

## Available but unused, or only partly used

| Existing definitions | Current extraction use | Practical use and remaining work |
| --- | --- | --- |
| [LocalConcept, RegisteredConcept, ConceptScheme](../../constraints/core/concept.cue), [ConceptAssignment](../../constraints/core/concept-assignment.cue) | Connected: source-supported local concepts and role-specific assignments to source fragments, pinned to actual content-derived releases. `vocabulary.annotate` remains a separate label-suggestion path. | Concepts come first in the full meaning schema used for refinement. The producer derives local identity from document, label and distinguishing definition. Shared labels do not establish cross-document identity or RefSpec registration. |
| [ConceptMapping](../../constraints/core/concept-mapping.cue), [ConceptResolutionResult](../../constraints/core/concept-resolution-result.cue), [ReferenceResourceRelease](../../constraints/core/reference-resource-release.cue) | Local concept releases now have real membership, content distributions and verified RDFC-1.0 digests. External mapping/resolution remains unconnected; the optional RefSpec label snapshot is not an identity decision. | Connect local concepts to RefSpec, retain exact/close/broader/narrower/related mappings, and preserve unresolved or conflicting identity. Release membership and evidence must support each selected mapping; matching labels alone is insufficient. |
| [SourceClaimant](../../constraints/core/source-claimant.cue) | Connected: separate source text, attribution role and exact evidence, linked to the complete meaning. | Distinguishes source claimant, actor, extractor and reviewer. Audit now assesses attribution explicitly. Live review found two incorrect model attributions despite exact text grounding. |
| [Authority](../../constraints/core/authority.cue), [Warrant](../../constraints/core/warrant.cue), [Justification](../../constraints/core/justification.cue) | Unused as graph records. `kind: authority` currently creates a text assertion, not an authority chain. | Represent an explicitly supported statutory, regulatory, or delegated basis and its justification. Source quotations and citations must establish the chain; a schema does not infer legal authority. |
| [ValueAssertion](../../constraints/core/value-assertion.cue) typed datatypes | Connected: typed literals use the Core datatype enum and lexical validation. Source comparator, unit and relative reference event remain attached through a retained JSON descriptor; complete meaning includes the original structured interpretation. | Invalid lexical values or unsupported comparator/unit/anchor wording remain visible with issues and are not emitted as typed components. Source normalization still requires semantic assessment; these values are not executable workflow conditions. |
| [EffectivePeriod](../../constraints/core/effective-period.cue), additional [ApplicabilityScope](../../constraints/core/applicability-scope.cue) fields | Connected: explicit in-force timestamps produce EffectivePeriod and an applicability link. Subject-specific applicability remains in source-supported scope text. | Date-only effectivity remains a typed date without invented time or timezone. Relative deadlines and validity durations do not create in-force periods. Multiple effectivity branches require separate semantic units. |
| [Finding](../../constraints/core/finding.cue) | Connected: audit meaning errors, missing/partial units and audit processing issues emit Core Findings, with an audit Artifact, timestamp and affected subject. The detailed report remains the evidence behind these derived records. | Stable references for feedback and graph consumers. Findings retain model-assisted wording and warning status; schema validity does not certify the judgments. Raw extraction refusals are still local records. |
| [ConfidenceRecord](../../constraints/core/confidence-record.cue) | Unused. | Requires a method, basis, producer and calibration status. Connect when measured uncertainty is available; do not manufacture confidence scores. |
| [GeneratedWorkProduct](../../constraints/core/generated-work-product.cue), [RevalidationEvent](../../constraints/core/revalidation-event.cue), [LifecycleEvent](../../constraints/core/lifecycle-event.cue) | Unused by the extractor; no workflow/form generation is implemented here. | Link a generated form field or workflow step to its justifying assertion and track which derived elements need reconsideration after a source change. These records support traceability; they do not create the Formspec or WOS artifact themselves. |
| [RelationComparisonContext](../../constraints/analysis/relation-comparison-context.cue), [RelationFinding](../../constraints/analysis/relation-finding.cue), [ResolverProofRecord](../../constraints/analysis/resolver-proof-record.cue) | Analysis module records are not emitted by the extraction pipeline. | Later compare explicit opposing assertions across document versions under a defined context and retained proofs. `RelationFinding` is specifically an affirmed/denied discrepancy, not a general omission diagnostic. |

## Callable code worth reusing

- [`rulespec_projection.verify_candidate_rows` and `assemble`](../../packages/rulespec-projection/src/rulespec_projection/projection.py)
  already verify tag evidence and emit `ConceptAssignment` with concept-release
  pins and evidence bindings. They operate on existing source/profile/model
  records; a generic semantic-unit adapter would be needed. Novel concepts absent
  from the normalized vocabulary are refused by this path, not registered.
  The shared `concept_assignment` constructor now serves both the existing
  producer and this extractor. New local concepts reuse `verify_fragment` for
  source grounding and supply actual releases rather than pretending to be
  normalized RefSpec entries.
- [`rkaf-runtime::concept::evaluate`](../../crates/rkaf-runtime/src/concept.rs)
  evaluates supplied concepts, mappings, releases, trust, and conflict state. It
  is a reference runtime over a supplied graph/test case, not a text-to-concept
  discovery model or an automatic RefSpec network client.
- [`reference_release_digest`](../../src/rulespec_conformance/reference_release_digest.py)
  computes and verifies reference release manifests. The release validators also
  check concept assignments/evidence, but their release-specific document inputs
  should not become a dependency of standalone semantic extraction. The extractor
  now calls the packaged digest implementation and shared Core validation data
  through `rulespec-conformance`, without a duplicated validation-data bundle.
- Existing runtime modules implement
  [temporal evaluation](../../crates/rkaf-runtime/src/temporal.rs),
  [dependency cascades](../../crates/rkaf-runtime/src/cascade.rs), and
  [consumer-state reduction](../../crates/rkaf-runtime/src/reducer.rs).
  These are future integration points for derived products, not extraction calls.

## Adoption rule and next integrations

Use an existing schema whenever it improves faithful representation, validation,
discovery or downstream use. Shared meaning belongs in Core; if Core needs a
better definition, improve that definition and regenerate its outputs. Keep
only document-specific interpretation and model request shaping in the profile.

The completed integration adds jurisdiction-independent applicability, audit
Findings, actual request temperature, local concepts and assignments, source
attribution, typed values and explicit effectivity. Native CUE imports the Core
attribution, role, datatype and period definitions directly at build time.
The model-facing collections remain document interpretation fields; all graph
records use the existing Core schemas. No Core schema needed a competing copy.

The [execution record](../plans/2026-09-08-finish-schema-reuse.md) and
[verification artifacts](../../examples/document_understanding/schema-reuse-finish/README.md)
cover exact evidence, semantic uncertainty, review correction, native generation,
installed wheels, live Gemini extraction, and strict replay.

The remaining integrations need their actual inputs:

1. RefSpec mapping/resolution requires a trusted vocabulary release and a
   supported semantic mapping. Local concept labels alone do not supply it.
2. Subject-specific applicability can move beyond scope text when a consumer
   needs a defined subject vocabulary. Source-supported scope is already retained.
3. Authority chains and calibrated confidence require supporting authority
   evidence and measured confidence methods respectively.

Generated-product and revalidation records become useful when an actual form or
workflow consumer is connected. The source review above remains the inventory
for each integration, rather than a requirement to invent data for every type.

## Priorities and boundaries

For discovery, prioritize concepts and assignments, followed by explicit RefSpec
mapping/resolution where needed. Keep topical association separate from the
actor/object identity errors found in the ID experiment.

For workflow preparation, prioritize faithful typed values and applicability,
then generated-product links and source-change tracking when a consumer exists.
Source attribution helps both use cases. Findings can standardize feedback when
those records need to travel outside the local audit files.

Core governance, registry administration, access/retention, consumer bridge, and
US-rulemaking-specific schemas serve other tasks; using all of them is not an
extraction objective. `PointInTimeException` governs retained historical use in a
lifecycle packet; it is not the representation for every exception in prose.
[ClosureClaim](../../constraints/analysis/closure-claim.cue) is explicitly disabled
and cannot establish that an extraction omitted nothing.

These definitions should inform the planned CUE-owned extraction profile and
its mapping to Core. They provide reusable representations and checks; choosing
the right concepts, governing conditions, and complete source meanings remains
document-understanding work.
