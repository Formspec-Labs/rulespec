# Sibling reuse follow-up: metadata, vocabulary and source preparation

**Recommendation:** test one publication-metadata consumer and one optional
agency/subject lookup through existing readers. Keep DocSpec's demonstrated text
fixes independent, but validate the SpicySearch–DocSpec source pair before replacing
its wheel. General vocabulary expansion and graph-facts migration can wait for a
consumer that needs them.

This read-only follow-up covers R20–R23 and their R8/R17/R18 dependencies. It extends
the [prior survey](2026-09-11-remaining-source-cross-relevance.md); the
[canonical task list](../plans/2026-09-10-reference-integration-task-list.md) remains
the backlog. I inspected current code and selected manifests in `rulespec`,
`spicysearch`, `DocSpec`, `spicy-docs`, `RefSpec`, `spicy-regs`, and `corpora` under
`/Users/mikewolfd/Work`. The actual paths are `DocSpec` and `spicy-docs`.
Only this report was written. No installs, builds, models, network calls, runtime
tests or broad corpus text scans were performed; source compatibility below does
not establish installed behavior or artifact admission.

## Existing integration versus available reuse

| Capability | Current relationship to Rulespec | Smallest useful next check |
| --- | --- | --- |
| SpicySearch identifiers / RefSpec citation and XML readers | Connected through [references.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/references.py:19); earlier task receipts establish delivered slices | Preserve those adapters; this survey does not revalidate their latest delivery |
| Local term identities and shared concept assignments | [terms.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/terms.py:7) is in extraction; [concept_assignment](../../packages/rulespec-projection/src/rulespec_projection/projection.py:975) constructs shared graph records after caller verification | Add optional, evidenced candidates to a named discovery use without replacing local terms |
| DocSpec catalog rows / SpicySearch metadata preparation | Both exist upstream; no catalog connection in the current [discovery export](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/discovery.py:48) | Compare one pinned document and its matching catalog record, including absent/conflicting fields |
| Atlas agency and vocabulary lookups | Existing SpicySearch implementations; extractor-to-vocabulary connection remains open | One pinned view, one selected scheme or agency projection, fresh mentions and collision controls |
| DocSpec visible text / SpicyDocs source locators | Previously exercised in the [sibling-reader comparison](../experiments/2026-09-11-ecfr-text/README.md); available as preparation/acquisition capabilities | Repair demonstrated owner defects; use held source bytes before acquiring replacements |

## R21: preserve the catalog's own field evidence

DocSpec already separates the raw record from its interpretation.
[FederalRegisterCatalogPolicy](../../../DocSpec/src/docspec/application/federal_register_catalog.py:297)
copies the publisher record into `sourceNativeFacts[*].fields`, then stores
`normalizedMetadata` and normalization decisions separately. Its
[normalization](../../../DocSpec/src/docspec/application/federal_register_catalog.py:319)
records original `sourcePaths`, absent/unparseable outcomes, and whether a value
comes from source or policy; `language=en`, for example, is explicitly policy.
The normalized fields include dates, dockets and RINs, but omit CFR and authority
fields. Read those from the preserved native record when present. Spicy Regs also
preserves [FR CFR/docket fields](../../../spicy-regs/src/spicy_regs/transforms/build_federal_register.py:87)
and [Agenda CFR/authority fields](../../../spicy-regs/src/spicy_regs/transforms/build_unified_agenda.py:141).

SpicySearch's [prepare_metadata_subject](../../../spicysearch/src/spicysearch/source_catalog_metadata.py:2105)
already produces searchable fields, identifier values and facets from a verified
catalog row. Its evidence includes release/digest, member, record, JSON pointer
and value digest, in `decoded-json-value-utf8-byte` coordinates
([construction](../../../spicysearch/src/spicysearch/source_catalog_metadata.py:2157)).
This can support R17 metadata discovery without inventing document-body offsets.
It does not produce CFR/authority reference candidates. Reusing its whole search
policy merely to display a publication date would add unnecessary behavior.

**Pilot:** show stated publication date, docket/RIN and native CFR/authority fields
beside the existing document/source result, preserving each field's record pin and
normalization status. Compare body readings separately. Keep malformed RINs and
absent metadata as controls; DocSpec already has a
[malformed-RIN retention test](../../../DocSpec/tests/test_source_catalog_policy.py:240).
Use the [located row stream](../../../DocSpec/src/docspec/ports/source_catalog.py:517)
to retain the supplying partition; reading `.items` alone discards that locator.
The stream is single-pass, so admit/read once per selected catalog, not per mention.

R8 remains conditional. [federal_register_facts](../../packages/rulespec-projection/src/rulespec_projection/projection.py:595)
still selects the first matching proceedings row and scans proceedings per document;
bulk use scales with documents × proceedings. [unified_agenda_facts](../../packages/rulespec-projection/src/rulespec_projection/projection.py:804)
still invokes the projection's citation parsers. Neither is the minimal raw-field
adapter. Migrate these parsers and joins together only when that graph consumer is
selected; otherwise the metadata pilot need not wait for R8.

## R22/R17: use the matcher that fits the question

[VocabularyLookup.build](../../../spicysearch/src/spicysearch/vocabulary_lookup.py:173)
selects one scheme from a verified `AtlasSearchView`; [suggest](../../../spicysearch/src/spicysearch/vocabulary_lookup.py:301)
matches a whole normalized mention to preferred/alternate labels and abstains on
multiple concepts. It preserves release, matched label, source record and view
pins. Hidden labels are excluded. The current builder selects by scheme, with no
language parameter; preferred display labels use deterministic ordering. A
multilingual pilot therefore needs an explicit supported language policy or a
demonstrably suitable selected scheme before promising language-specific results.

For query prose, reuse [build_lookup_label_index](../../../spicysearch/src/spicysearch/concept_resolution.py:171)
and [resolve_query_concepts](../../../spicysearch/src/spicysearch/concept_resolution.py:195).
They provide stopped/ambiguous outcomes and longest-label matching without another
alias registry. Build the index once per lookup. This is the useful R17 route;
whole-mention `suggest` is the simpler R22 route for already extracted mentions.

**R18 limitation:** [ResolvedConceptSpan](../../../spicysearch/src/spicysearch/concept_resolution.py:82)
contains normalized text and concept IDs, not original byte/character offsets or a
source occurrence identity. Its receipt alone cannot distinguish repeated source
mentions or preserve release provenance. Retain the original Rulespec source
fragment and lookup pin beside each suggestion. Existing
[ReviewStore.observe](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py:500)
accepts observations without claim targets; test reload/export there before adding
another store or transferring approvals to newly matched concepts.

[AgencyProjection.resolve](../../../spicysearch/src/spicysearch/agency_projection.py:351)
is suitable for exact agency-name candidates. Retain the parent lookup's pin and
entry evidence: the returned resolution itself contains only agency/name fields.
Also preserve source agency IDs separately: the projection's exact join domain is
regulations.gov, while DocSpec's [FR normalization](../../../DocSpec/src/docspec/application/federal_register_catalog.py:77)
uses slug-or-name and still promotes raw-only headings to agency IDs. That live
mechanism makes unresolved headings a useful control; the dated
[catalog findings](../../../DocSpec/docs/history/2026-09-09-catalogue-cleaning-findings.md)
provide captured examples, not a refreshed corpus-quality claim.

Defer [RelatedTopicsIndex](../../../spicysearch/src/spicysearch/related_topics.py:429)
until exact matching improves a named task. It preserves native intra-scheme
`skos:related` evidence and bounded suggestions, but building it scans/materializes
selected columns from the entire Statement table. Pass the existing lookup to
avoid another label read. Related concepts remain suggestions, not identity merges.
The located `corpora/atlas-3.1-parquet-search-view-2026-08-21d` manifest declares
agency tables and omits `SourceRecord.nativePayload`; raw publisher inspection
therefore needs its upstream evidence. Presence and manifest inspection here do
not establish compatibility with [AtlasSearchView.open](../../../spicysearch/src/spicysearch/atlas_search_view.py:839).

## R20/R23: validate the source pair before an upstream wheel change

**Verified source mismatch; installed impact untested.** SpicySearch
[platform_source_catalog.py:46](../../../spicysearch/src/spicysearch/platform_source_catalog.py:46)
imports `SourceCatalogArtifactVerifier`, `_iter_located_catalog_rows` and
`source_catalog_producer` from `docspec.adapters.source_catalog_artifact`.
That module is absent from live DocSpec. The definitions now live in
[verification.py:56](../../../DocSpec/src/docspec/adapters/catalog_artifact/verification.py:56),
[rows.py:158](../../../DocSpec/src/docspec/adapters/catalog_artifact/rows.py:158), and
[rules.py:158](../../../DocSpec/src/docspec/adapters/catalog_artifact/rules.py:158).
The public [source_catalog facade](../../../DocSpec/src/docspec/source_catalog.py:13)
exports `SourceCatalogArtifactReader`, but no admitted-artifact/plain-dict streaming
API. The [API request](../../../DocSpec/docs/history/2026-09-05-reader-api-requests.md:6)
still says unimplemented. SpicySearch's comment claiming a future `0.2.12` export
is not implementation evidence; both current pins still say `0.2.11`.

Keep the installed/vendored pair until a selected upgrade has its focused sibling
wheel checks, using SpicySearch's existing `tools/presubmit.sh`. This matters if
DocSpec's [XML preparation](../../../DocSpec/src/docspec/processing/visible_text.py:362)
fix is delivered as a replacement wheel. The source fix can proceed independently
of Rulespec's native XML navigation; no general logical-segmentation dependency is
needed. Check changed prepared-text identities and source-map evidence under R18.

For additional captures, SpicyDocs supplies both the previously checked
[FR body locators](../../../spicy-docs/src/spicy_docs/sources/federal_register/body_sources.py:135)
and [SourceNativeReleaseReader](../../../spicy-docs/src/spicy_docs/releases/reader.py:36).
The latter requires a source profile, accepted verifier implementation IDs, blob
source and artifact pin; a release directory alone is insufficient. Prefer the
existing selected releases under `corpora/supply-2026-09-02/releases` and held XML.
Source profiles describe supported fields/access; they do not prove a fetched
body, meaningful table structure, or applicability of its content.
