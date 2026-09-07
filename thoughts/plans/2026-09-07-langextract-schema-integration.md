# Proposed LangExtract integration with Rulespec schemas

Date: 2026-09-07. Status: proposed implementation plan; integration is not built.

## Decision

Rulespec owns the semantic definitions and resulting rulebook. Evaluate LangExtract
as a replaceable producer of candidates through a small model-facing schema.
Do not hand the model the complete Rulespec schema collection or require it to
construct identifiers, hashes, provenance, and release metadata.

Rulespec owns document preparation, processing windows, extraction, evidence
verification, semantic assembly, validation, and review. RefSpec supplies terms,
tags, and thesauri. Ordinary parsing and model libraries are permitted; DocSpec
and SpicyRegs are not runtime prerequisites.

## How the pieces fit

1. Preserve the original document and an addressed text representation, including
   headings, paragraphs, lists, tables, and available page locations.
2. Adapt the preserved SpicyRegs structure-aware segmenter as the first local
   processing-window baseline. These windows are model inputs, not rule identities.
   Evaluate Docling only if the source format requires its parsing capabilities.
3. Use LangExtract with Rulespec-owned instructions, examples, and candidate types
   for requirements, definitions, actors/entities, conditions, and exceptions.
4. Verify candidate quotations against preserved source text using Rulespec's
   existing exact evidence utilities. Record failures and ambiguities explicitly.
5. Assemble claims across passages: attach conditions and exceptions, retain
   heading scope, reconcile duplicate candidates, and preserve unresolved readings.
6. Map the results into Rulespec records, then align vocabulary through RefSpec.
7. Run structural checks and present the source beside the extracted rulebook for
   human review. Preserve raw responses and review decisions for replay.
8. Package exports using existing artifact/release machinery when needed, after
   the local extraction and review workflow works.

The complete workflow is the objective, not a description of current capability.
A referenceable rulebook also does not by itself execute adjudication decisions.

## Two schema roles, one semantic authority

| Schema role | Responsibility |
| --- | --- |
| Model-facing candidate schema | Describe what to find and the supporting quotations. Keep it small enough to guide extraction reliably. |
| Rulespec schema/profile | Define the durable meaning, identities, evidence bindings, provenance, vocabulary assignments, and review records. |

Existing schemas cover much of the representation and provenance. They do not
fully define the intended requirement, grouped-condition, and scoped-exception
structure. Design that small rule-focused profile using worked source examples.

Rulespec's authoritative schema definitions govern semantics. Derive the extraction
view where practical; otherwise maintain an explicit, tested field mapping. Do not
introduce an independently evolving semantic schema inside the LangExtract adapter.
The exact LangExtract API/schema configuration must be verified against the pinned
version during implementation; the example below is a proposed application record,
not a claim about its native response format.

```json
{
  "kind": "requirement",
  "actor": "applicant",
  "action": "submit Document A",
  "evidence_text": "Applicants must submit Document A."
}
```

This invented example illustrates extraction shape only. Real candidates also need
source/window identity, uncertainty handling, and separate evidence for claims that
draw on different passages. Do not force a multi-passage rule into one quotation.

## Mapping responsibilities

| Candidate information | Rulespec representation or responsibility |
| --- | --- |
| Supporting quotation and verified position | `SourceFragment`; preserve original representation identity and exact coordinates. |
| Relationship or factual value | Appropriate `RelationshipAssertion` or `ValueAssertion`, plus rule-profile structure where needed. |
| Support, qualification, or scope evidence | `EvidenceBinding`, potentially referencing several source fragments. |
| Requirement, condition grouping, exception scope | Proposed rule-focused profile; existing `ApplicabilityScope` alone is insufficient for structured logic. |
| Extraction method and model run | Existing origin and extraction-lineage machinery, populated by application code. |
| RefSpec vocabulary match | `ConceptAssignment`; lack of a match must not discard a discovered requirement. |
| Human review decision | `Attestation` and the applicable correction/versioning behavior. |

Application code creates durable identities and evidence records after verification.
An actor/action candidate does not map automatically to a valid assertion: the
profile must define the entities, predicates, and grouping before that conversion
can be considered correct. Schema-valid output remains a candidate interpretation.

## Implementation sequence

1. Select a real representative chapter and hand-author a few expected Rulespec
   examples, including a heading-scoped requirement and a cross-section exception.
2. Define the minimal profile and candidate-to-Rulespec mapping from those examples.
   Keep independently labeled examples held out from model instructions.
3. Pin LangExtract and implement a small producer adapter. First use its existing
   long-document handling; introduce alternate windowing only where the experiment
   identifies a need. Compare against the recovered SpicyRegs baseline when useful.
4. Enforce exact source replay independently of library alignment labels. Prior
   research found fuzzy/partial alignment defaults; verify configuration against
   the selected version and reject or flag non-exact evidence.
5. Implement deterministic conversion for supported candidate types, retaining raw
   outputs, unsupported types, failed mappings, and unresolved relationships.
6. Add source-side review and provider-free replay of saved candidates and decisions.
7. Measure meaning and coverage against the held-out examples before expanding to
   a full manual, additional document families, or release packaging.

## Acceptance checks

- Every supported candidate field has a documented Rulespec destination or an
  explicit reason it is only temporary extraction information.
- Every accepted quotation replays exactly against the preserved representation.
  Repeated text, Unicode coordinates, heading evidence, and window-relative offsets
  have defined handling.
- Conditions and exceptions retain their own evidence and explicit attachment to
  the correct requirement; ambiguous attachments remain unresolved for review.
- Unsupported or invalid candidates remain visible rather than silently vanishing.
- Converted records pass the relevant Rulespec checks; mapping tests detect missing
  fields and unintended semantic changes as the profile evolves.
- Saved raw outputs can be revalidated and converted without another provider call.
- Evaluation reports structural validity, evidence validity, interpretation errors,
  and omissions separately. Retrieval scores are not extraction-accuracy scores.

## Related findings

- [Standalone document-understanding plan](2026-09-06-standalone-document-understanding.md)
- [Reusable segmentation research](2026-09-06-reusable-segmentation-research.md)
- [SpicyRegs recovery and comparison](2026-09-06-spicyregs-segmenter-comparison.md)

This note records the proposed direction from the conversation. It adds no code,
new normative schema, package dependency, or benchmark claim.
