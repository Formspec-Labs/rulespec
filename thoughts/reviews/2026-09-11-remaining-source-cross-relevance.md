# Remaining source, reference and vocabulary work: shared dependencies

Read-only survey on 2026-09-11 of R3, R7–R13 and R20–R23 in the
[canonical task list](../plans/2026-09-10-reference-integration-task-list.md).
This is an approach review, not a second backlog or a new accuracy measurement.
Production code was inspected in Rulespec, RefSpec, SpicySearch, Spicy Regs,
DocSpec and SpicyDocs. No models, builds, installs, network requests or full
test suites were run. Only this report was written.

**Recommendation: organize the remaining source work around four shared outcomes:
exact source navigation, stated publication metadata, optional shared vocabulary
suggestions, and faithful readable text.** Avoid treating every unchecked task as
an independent implementation. Additional citation syntax and broad corpus
inventory should follow a specific consumer need.

The root agent is editing the eCFR consumer concurrently. At inspection,
`prepare_xml`, `read_xml` and eCFR address integration are present in source;
this survey does not establish their validation or installation. The preceding
delivered checkpoint supports optional USLM sources. The root's new delivery
receipt must establish any later eCFR claim.

## Combine the work by what the user receives

| Shared outcome | Tasks that contribute | Reuse and remaining work | Value / effort judgment |
| --- | --- | --- | --- |
| A reference opens the right source paragraph, with its qualifications intact | R9, R10, R11, R12; representation under R3 and layout under R23 | Build on the native XML index now being connected. Add source-supported omitted-title readings and paragraph addresses to that same index. Relative prose and ranges remain separate, explicit unresolved cases until their required evidence exists. | High value for both discovery and workflow preparation; M–L. Native section lookup is the first independently useful delivery. |
| Published document fields are available without extracting them again | R20, R21, selected R7; R8 if the graph facts path is reused | Use one verified source record and its field evidence. Existing projection functions need closer fit checks; they are not interchangeable with raw metadata observations. | High potential for little model cost; S–M for one source and consumer. |
| The same agency or subject can be found across documents without merging local definitions | R20, R22, R17; R18 for later feedback | Use the existing verified vocabulary reader and exact agency-name resolver. Keep suggestions separate from document-local senses and actor judgments. | High discovery potential; M for a bounded agency pilot, larger for general concepts. |
| Meaningful words, table cells and source boundaries survive preparation | R23, R10, R12, R24 | RefSpec owns the current native XML route; DocSpec owns its general visible-text shortcomings. Fix each demonstrated failure at its owner, then measure the affected downstream use. | High fidelity value; S–M for line breaks, M for a real table consumer. |

These groupings do not close the broad tasks. They identify changes that can
satisfy several acceptance checks without creating several implementations.

## 1. Source navigation should have one address index

Current useful code:

- Rulespec `uslm.SourceIndex` in
  `packages/rulespec-extrapolator/src/rulespec_extrapolator/uslm.py:69`
  replays pinned XML, indexes native identifiers, and shares evidence and targets.
  The current working version obtains eCFR addresses from the RefSpec reader.
- `reference_sources.attach_reference_sources` in
  `packages/rulespec-extrapolator/src/rulespec_extrapolator/reference_sources.py`
  is the existing optional external-source join. Extend this route rather than
  add a retrieval service or place external text in the model response schema.
- RefSpec `citation_grammar.find_cfr_citations` at
  `/Users/mikewolfd/Work/RefSpec/src/refspec/registry/citation_grammar.py:2660`
  deliberately recognizes explicit citations only. Its current API has no
  caller-provided title context. R9 is genuinely missing at that seam.
- Rulespec `source_passages` at
  `packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py:85`
  derives boundaries and parentage from text markers. `with_context` at line 147
  consumes those parents. Changing marker ancestry changes context selection even
  when source characters stay unchanged.

Smallest useful sequence:

1. Finish the root's exact eCFR section lookup and preserve unresolved scopes.
2. Use native TITLE/SECTION evidence to supply title context to a bounded RefSpec
   omitted-title occurrence API. Retain literal spans and separate context
   evidence through the existing `record(..., context=...)` path in
   `references.py:41`. Do not prepend invented title text to the document.
3. Add native paragraph addresses where the publisher actually supplies them.
   Where eCFR stores only textual labels inside `P`, retain that limitation;
   native section structure does not magically solve paragraph ancestry.
4. Implement R11 relative-address/range navigation against that index. A range
   needs source order and known membership, not arithmetic over labels. Missing
   and duplicate labels stay visible.

Keep the failed local-marker experiment as a counterexample set. Do not rewrite
the passage hierarchy independently for R10 and then write another hierarchy for
R11. For prose lacking usable native structure, compare candidate addresses while
leaving passage IDs and existing context behavior intact until the broader gate
passes. Distinguish paragraph labels, exact passage slices and complete referenced
paragraph text; they are not always the same boundary.

There is a scale concern before using full titles as primary extraction inputs:
`source_passages` currently computes a containing-section list for every passage
(`documents.py:106`). That is O(passages × sections). External `SourceIndex`
reuse avoids needing that operation for every target. If primary full-title
ingestion becomes necessary, reuse a sorted interval traversal rather than add
an unrelated cache or reparse the title per citation.

Raw source check: the saved `49 CFR 382.107` opens with
“§§ 386.2 and 390.5T of this subchapter, and § 40.3 of this title, except as
provided in this section—” followed by definitions. See
`thoughts/experiments/2026-09-11-reference-bodies/catalog-probe/alcohol-definition-0.xml:3`.
This supports contextual title recognition, but also shows why a located target
does not establish governing meaning: the introduction carries an explicit
exception, and `390.5T` is not interchangeable with `390.5`.

## 2. Publication metadata and graph-parser cleanup overlap, but are not identical

Already implemented upstream:

- Spicy Regs preserves publisher `publication_date`, `docket_ids_json` and
  `cfr_references_json` in
  `/Users/mikewolfd/Work/spicy-regs/src/spicy_regs/transforms/build_federal_register.py:87`.
  Its Unified Agenda transform preserves `cfr_references_json` and
  `legal_authority_json` at `build_unified_agenda.py:141`.
- DocSpec exposes `SourceCatalogArtifactReader` through
  `/Users/mikewolfd/Work/DocSpec/src/docspec/source_catalog.py:13`.
  `open_snapshot` and `verify_snapshot` in
  `adapters/catalog_artifact/reader.py:33` and `:64` use the shared artifact
  admission machinery and exact source-catalog pins. Reuse this public surface
  when the selected input is a current DocSpec catalog. A legacy Parquet table
  needs its actual owning loader; renaming it a catalog does not make it one.
- Rulespec already has `federal_register_facts` and `unified_agenda_facts` in
  `packages/rulespec-projection/src/rulespec_projection/projection.py:569` and
  `:781`. `PublishedTables` at line 100 is an interface, not an on-disk loader.

**Do not connect the existing graph facts functions indiscriminately as the
metadata solution.** `federal_register_facts` scans every proceedings row and
takes the first row whose document list includes the FR document (`:596`). Its
CFR/RIN/docket relationships primarily come from those derived tables.
`unified_agenda_facts` reparses its JSON strings with
`rulespec_projection.citations` (`:804`, `:811`). Those are R8's live duplicate
graph parsers. Thus the tempting blanket reuse would bring both graph-specific
interpretation and parser migration into an otherwise small metadata feature.

Recommended R21 experiment: select one pinned source record plus its matching
document; retain the stated identifiers and publication fields as source-field
observations, compare them with body occurrences, and expose them in the existing
discovery export. Include a record with absent or disagreeing metadata. Reuse the
native parser only for a field that still contains unparsed text, and keep its
evidence attached to that field. Do not fabricate body quote offsets.

If that consumer needs the existing graph facts, combine its R8 migration and R21
integration as one coordinated change. Preserve structured dictionary/compact
inputs as well as textual grammar cases. Otherwise R8 can proceed independently:
the duplicated readers remain at `citations.py:595` and `:756`, while the
extraction scanner already uses RefSpec. Avoid a Core-to-RefSpec dependency cycle
solely to delete those functions.

The SpicySearch `citation_bridge.UscBridge.parts_for_key` at
`/Users/mikewolfd/Work/spicysearch/src/spicysearch/citation_bridge.py:300` returns
co-occurrence-based CFR part suggestions. It is available, not connected to this
extractor, and not a replacement for source-stated authority. Defer it until a
specific discovery comparison needs that signal; it does not unblock R9–R12.

## 3. Start vocabulary reuse with a small identity problem

Current foundation:

- Rulespec `terms.py:7`, `:95`, `:113` and `:135` retain document-scoped
  definitions, source support, changed/rejected targets and graph relationships.
  Do not replace those identities with a global label key.
- Rulespec `VocabularyConcept` and `concept_assignment` at
  `packages/rulespec-projection/src/rulespec_projection/projection.py:939` and
  `:975` already carry concept/release identities. The helper assumes the caller
  has verified membership; it does not prove that a label match is correct.
- SpicySearch `AtlasSearchView.open` at
  `/Users/mikewolfd/Work/spicysearch/src/spicysearch/atlas_search_view.py:839`
  verifies a pinned view. `read_table` at line 787 supports selected columns and
  bounded filtered reads; it is a verified table reader, not a concept matcher.
- `AgencyProjection.build` and `resolve` at
  `/Users/mikewolfd/Work/spicysearch/src/spicysearch/agency_projection.py:201`
  and `:351` already normalize approved agency names and abstain when multiple
  agency IDs share the same normalized name. `ambiguous_keys` is available at
  line 334. Its supported identity domain is the projection's regulations.gov
  agency IDs, not every governmental office or role mentioned in prose.

Recommended independent pilot: use extracted actor mentions to request optional
agency candidates from one pinned projection, show the matched name and source
release alongside the original mention, and measure useful cross-document
navigation. Keep `Posts`, passport offices, `INs` and `IRLs` as non-global or
potentially unmatched controls. An exact agency-name resolution does not prove
the named organization is the actor of the statement.

For general subjects, filter one relevant vocabulary release and language first;
index only the labels that consumer needs. Avoid invoking the broad
`refspec.atlas.candidate_retrieval.generate_candidate_pairs` (`:586`) merely
because it exists: it proposes cross-vocabulary pairs, a different problem from
linking a document mention to a known release. Preserve ambiguity and relation
types through existing records instead of adding a second taxonomy or mandatory
model-generated vocabulary registry.

Reader cost matters: `AtlasSearchView.read_table` verifies member bytes, and a
filtered read scans the selected table. Do one shared admission/read per input
release and cache the small derived lookup for a run; do not call it for every
mention. The existing agency lookup is bounded enough to try without a full
Atlas rebuild. Actual artifact compatibility remains a required first check,
not proven by this API inspection.

## 4. Keep source-format fixes at their owners

The [direct sibling-reader comparison](../experiments/2026-09-11-ecfr-text/README.md)
already tested the reader alternatives. Repeating that comparison adds little.
DocSpec `XmlVisibleTextExtractor.extract` at
`/Users/mikewolfd/Work/DocSpec/src/docspec/processing/visible_text.py:362`
normalizes text and retains original-byte mapping. Its `<BR>` joins and mixed
parent/child block joins are independent upstream fixes. The native RefSpec route
retains XML nodes and table attributes; these are different useful outputs.

The saved `40 CFR 82.158` table makes the remaining table need concrete:
`refrigerant-equipment-0.xml:19` contains a `rowspan="2"` appliance header and a
`colspan="2"` vacuum heading. The next row splits manufacture dates before and
after November 15, 1993. A following appliance row has values `4` and `10`.
Line-break compensation restores readable words; row/column/header relationships
determine which value applies. Preserve that original structure now. Build a
small table-consumer experiment only when extraction/navigation needs to use the
relationship; do not label tab-separated text a complete table reconstruction.

SpicyDocs already supplies FR XML/text/HTML candidates via
`/Users/mikewolfd/Work/spicy-docs/src/spicy_docs/sources/federal_register/body_sources.py:135`,
publisher granule validation at `:186`, and MODS resolution at `:349`.
These functions perform no network requests and do not choose the preferred
format. Reuse acquisition and identity verification there if R12/R23 needs new
source captures. A supplied URL is not evidence that the body or edition exists.
Keep offline extraction and Core validation usable from captured evidence.

For the saved cross-page PDF citation, source reading order is the missing
capability. Adding another FR/CFR regex does not repair interleaved footnotes.
Prefer the corresponding supported publisher XML when available; otherwise test
the actual page layout at the source-preparation boundary.

## Narrow syntax work and task-list simplifications

- **R7:** RefSpec `parse_federal_register_citations` at
  `citation_grammar.py:4432` already recognizes volume/page values, but returns
  identities without occurrence spans. The small next API change is an occurrence
  view over the same matcher, with source spans/refusals, followed by the existing
  Rulespec `record` route. Do this when an FR-linked discovery/source task needs
  it. Do not enable proclamations, treaties and court-case families as one bundle.
- **R13:** `ActRelativeCitation` at `citation_grammar.py:4082` currently supports
  explicit division, not a bound law number/year. The resolver at
  `act_resolution.py:913` already retains multiple name/law candidates. Add a
  source-supported discriminator there only after an actual ambiguous example
  needs it; reuse existing public-law recognition. Never attach the nearest year
  merely by distance. This can run independently of XML lookup and vocabulary.
- **R3:** Treat disagreement/evidence preservation as a shared acceptance rule
  for every enabled reader. The typed CUE shape is explicitly conditional; no new
  typed reference profile is needed without a consumer that benefits from it.
- **R20:** Keep the existing inventory as an admission checklist for selected
  features, not a requirement to enumerate or import every corpus directory.
  Inspection of a module or presence of a file is neither installation nor user
  value. Record adopt/test/defer decisions in the canonical list.

## Suggested parallel lanes and joins

1. **Root/source navigation:** finish eCFR delivery; then one R9 title-context
   comparison. R10/R11 depend on the address/source decision and should not make
   concurrent incompatible hierarchy edits.
2. **Independent upstream fix:** DocSpec line-break/mixed-block preservation,
   including source-map and changed-identity controls. It need not wait for the
   eCFR application wheel and should not change Rulespec's default input path.
3. **Independent product signal:** one exact agency-candidate pilot using current
   actor output, or one pinned publication-metadata comparison. Choose a named
   consumer and untouched evaluation cases; these need no prompt growth.
4. **Conditional cleanup:** graph-reader R8 migration when the metadata/graph
   consumer needs it; FR occurrences and law/year disambiguation when fresh source
   failures justify them.

Before merging a lane, require its existing reader to be shown active, exact
source/release evidence, a misleading control and a named downstream outcome.
Then join its output into the fresh R24 consumer evaluation. No single reader
comparison establishes extraction completeness, governing scope or general
retrieval quality.
