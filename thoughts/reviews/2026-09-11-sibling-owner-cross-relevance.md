# Sibling owner survey: connect evidence before adding adapters

**Keep publication-field discovery, optional exact name candidates and DocSpec layout
repair independent.** They share pinned evidence. Reshape the catalog upgrade around
DocSpec's public reader; moving SpicySearch's private import is insufficient.

Static survey of R20–R23 and R8/R17/R18 in the [canonical list](../plans/2026-09-10-reference-integration-task-list.md:1259),
extending [sibling reuse](2026-09-11-sibling-reuse-followup.md). Read current source,
selected manifests, wheel ZIP members and installed distribution files. No imports,
tests, installs, builds, network/model calls, corpus scans or runtime changes.
Only this report was written; suggested benefits remain unmeasured.

## Evidence that changes the next step

| Finding | Practical consequence |
| --- | --- |
| **Source compatibility concern:** [SpicySearch imports the old DocSpec module](../../../spicysearch/src/spicysearch/platform_source_catalog.py:46); live DocSpec exports its [split reader](../../../DocSpec/src/docspec/source_catalog.py:13). | Repair the owning public API before replacing the wheel; avoid a new private-path adapter. |
| **Installed scope:** the vendored and installed SpicySearch DocSpec wheel contains the old module. | Source incompatibility does not establish an installed failure; package version alone does not identify this difference. |
| **Consumer scope:** DocSpec's normal [registry selects `XmlExtractor`](../../../DocSpec/src/docspec/processing/extraction.py:421), whose [result retains XML bytes](../../../DocSpec/src/docspec/processing/extraction.py:243). | Fixing the available visible-text helper alone does not prove a change to normal processing or search. |
| **Candidate scope:** [`suggest`](../../../spicysearch/src/spicysearch/vocabulary_lookup.py:301) and [`resolve`](../../../spicysearch/src/spicysearch/agency_projection.py:351) return `None` for ambiguity. | Retain abstention and input pins; these methods do not return competing identities for a review interface. |

## Lineage, owners and shared foundation

[REF-024](../../../RefSpec/docs/decisions.md:1111) establishes release/package exchange
and vocabulary ownership; [REF-048 and its acquisition update](../../../RefSpec/docs/decisions.md:4014)
assign catalog meaning to DocSpec and source-native acquisition to SpicyDocs.
Current [SpicySearch boundaries](../../../spicysearch/AGENTS.md:279) keep canonical
source/vocabulary authority upstream and search evaluation separate from applicability.

| Shared input or operation | Owner | Consumers in this scope |
| --- | --- | --- |
| Source-native release, original fields and rendition locators | SpicyDocs acquisition; existing Spicy Regs published tables | DocSpec catalog; R20/R21/R23 selected-source work |
| Catalog selection, normalization, located row stream | DocSpec | SpicySearch metadata preparation; optional Rulespec R21 consumer |
| Vocabulary/agency releases and name matching | RefSpec identities; SpicySearch matching | R22 candidate pilot and R17 query interpretation |
| Source occurrences and review observations | Rulespec | Reference feedback; R17 discovery; later candidate review |

Preserve exact source identity, distinct metadata/body coordinates, and separate
observations and claim decisions. R18's local [reference-feedback path](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/cli.py:166)
calls `ReviewStore.apply(action='observe')`; its [capture](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/reference_feedback.py:8)
retains scan, reader/index, target and source evidence. It accepts `document-references/2`;
do not disguise catalog/vocabulary feedback as citation scans. The existing
[observation action](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py:506) and
[discovery issues](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/discovery.py:107) provide broader storage/export.
This work is uncommitted; delivery and tests were not revalidated here.

## 1. Publication-field evidence beside one discovery result — R20/R21/R17

**Owner:** Rulespec discovery; DocSpec normalization/readers. **Outcome:** publisher
date, docket/RIN and available CFR/authority fields beside one pinned source result,
retaining disagreement with body readings.

**Current call path:** DocSpec [policy construction](../../../DocSpec/src/docspec/application/federal_register_catalog.py:296)
retains native fields beside [normalized dates/dockets/RINs](../../../DocSpec/src/docspec/application/federal_register_catalog.py:319);
CFR/authority values need native fields. Its public [reader](../../../DocSpec/src/docspec/adapters/catalog_artifact/reader.py:32)
supplies [`located_items`](../../../DocSpec/src/docspec/ports/source_catalog.py:517) with partition identity.
SpicySearch [metadata ingest](../../../spicysearch/src/spicysearch/metadata_snapshot.py:3701) calls
[`prepare_metadata_subject`](../../../spicysearch/src/spicysearch/source_catalog_metadata.py:2105) for release/member/record/path/value evidence.
Reuse that path for indexing; field display only needs the catalog row and evidence.

Spicy Regs already retains [FR CFR/docket arrays](../../../spicy-regs/src/spicy_regs/transforms/build_federal_register.py:78)
and [Agenda authority/CFR arrays](../../../spicy-regs/src/spicy_regs/transforms/build_unified_agenda.py:128).
The R8 graph path is a different consumer: [`federal_register_facts`](../../packages/rulespec-projection/src/rulespec_projection/projection.py:599)
chooses the first proceedings match after a scan; [`unified_agenda_facts`](../../packages/rulespec-projection/src/rulespec_projection/projection.py:802)
uses its own citation parsers. Avoid routing the field pilot through those joins.

**Acceptance:** pinned record/document association, native/normalized values, paths,
partition identity, reload/export and unchanged source retrieval. Controls: absence,
malformed RIN with `unparseable` outcome, conflicting body text, multiple proceedings.
Read per selected catalog. **Kill/defer:** no useful result/context means defer R21.

## 2. Exact whole-mention candidate pilot — R20/R22/R17/R18

**Owner:** SpicySearch matcher, RefSpec identities, Rulespec evidence. **Outcome:**
optional agency/concept candidates preserving local definitions and roles.
**Current call path:** [`load_agency_projection`](../../../spicysearch/src/spicysearch/agency_projection.py:377)
opens a pinned `AtlasSearchView`, builds one projection, then `resolve` matches a
whole name. [`VocabularyLookup.build`](../../../spicysearch/src/spicysearch/vocabulary_lookup.py:173)
selects a scheme; `suggest` matches a whole label. The existing
[search application](../../../spicysearch/src/spicysearch/search_application.py:907)
already distinguishes that suggestion from `resolve_query_concepts` for query prose.

Retain original source occurrence, lookup/view pins, method and matched label.
Agency results also need their parent [entry evidence](../../../spicysearch/src/spicysearch/agency_projection.py:135).
The agency join domain is [regulations.gov IDs](../../../spicysearch/src/spicysearch/agency_projection.py:182);
DocSpec's [FR `agencyId`](../../../DocSpec/src/docspec/application/federal_register_catalog.py:77)
can be a slug, name or raw heading. A name candidate cannot silently rewrite that ID.
Neither query spans nor `None` supplies a complete ambiguous-candidate record.
If a selected review needs competing identities, expose the existing matching
buckets in SpicySearch; do not duplicate labels or inspect private maps in Rulespec.

**Acceptance:** one pinned view/scheme, supported language scope, distinct repeated
source occurrences, reloadable abstentions, exact unique aliases and unchanged local
term/actor meaning. Controls: colliding acronyms, two concepts sharing a label,
raw-only agency headings, hidden labels and a different concept release.
Build lookup state once; agency `entry_for` currently scans entries for each match,
so a bulk caller must measure that cost before copying an index downstream.
**Kill/defer:** no useful links or false merges means defer adoption. Defer related-topic
expansion, multilingual promises and actor reassignment; feedback stays independent.

## 3. Repair the demonstrated XML joins at their owner — R23, independently

**Owner:** DocSpec visible-text preparation; Rulespec retains its native RefSpec path.
**Current call path:** the saved [probe](../experiments/2026-09-11-ecfr-text/sibling-readers/docspec_probe.py:17)
calls `XmlVisibleTextExtractor.extract` → `_walk_blocks` → `_lay_out` → `_normalized_pieces`.
Current [block traversal](../../../DocSpec/src/docspec/processing/visible_text.py:333)
stops at a text-owning parent and [collects descendant pieces](../../../DocSpec/src/docspec/processing/visible_text.py:250);
empty break elements add no separator. This explains the two distinct joins.
The held [table source](../experiments/2026-09-11-reference-bodies/catalog-probe/refrigerant-equipment-0.xml)
contains `<TH ...>Manufactured or<br/>imported before<br/>November 15, 1993</TH>`
inside a header row; the [saved output](../experiments/2026-09-11-ecfr-text/sibling-readers/refrigerant-equipment-0.defaults.txt:27)
joins those words. The surrounding header rules out an intended inline word.

**Acceptance:** separate break-delimited words/mixed blocks; preserve `<E>re</E>quired`,
entities/Unicode, byte evidence and changed text identity. Retain empty-cell/table limits.
No visible-text-helper caller appears elsewhere in current DocSpec/SpicySearch `src`;
normal extraction is XML passthrough. Name a consumer before claiming benefit beyond
the probe. Rulespec already calls [RefSpec `read_text`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/uslm.py:11).
**Defer:** generic table reconstruction, PDF order repair and a new XML adapter.

## Compatibility and release-reading limits

Read-only `zipfile`/filesystem inspection found `source_catalog_artifact.py` and its
`as_dict` row stream in `spicysearch/vendor/docspec-0.2.11-py3-none-any.whl` and the
SpicySearch `.venv` installation; its `direct_url.json` points to that wheel.
DocSpec's editable `.venv` also says `0.2.11`, with the old module absent; this
establishes file/package differences, not import success or runtime parity.
The [public API request remains unimplemented](../../../DocSpec/docs/history/2026-09-05-reader-api-requests.md:6).
Any replacement must preserve [zero rows delivered before count/tally validation](../../../spicysearch/src/spicysearch/platform_source_catalog.py:247),
located dict streaming and bounded memory. Use the existing sibling-wheel presubmit
after the owner change; its [clean-HEAD check](../../../spicysearch/tools/presubmit.sh:60)
means a run cannot validate uncommitted source simply by pointing at that checkout.

Reuse DocSpec's [SpicyDocs adapter](../../../DocSpec/src/docspec/adapters/spicy_docs_source_native.py:95)
→ [`SourceNativeReleaseReader`](../../../spicy-docs/src/spicy_docs/releases/reader.py:39) → `iter_records`/`iter_renditions`,
retaining blob source, profile, verifier acceptance and artifact pin. The held FR
[manifest](../../../corpora/supply-2026-09-02/releases/fr-slice-2026-04-13/artifact.json) declares `observed-crawl` and producer `spicy-docs`;
neither it nor Atlas's matching `1.1` schema proves admission. No release was opened.
Existing [FR locators](../../../spicy-docs/src/spicy_docs/sources/federal_register/body_sources.py:135)
check date/document identity but do not prove fetched text. Defer acquisition until held
bytes fail the selected use. **Reconsider adapter/consumer assumptions; keep independent value gates.**
