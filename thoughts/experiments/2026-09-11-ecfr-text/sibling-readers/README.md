# Existing DocSpec and SpicyDocs readers

**DocSpec already has a reusable XML-to-visible-text reader with original-byte evidence mapping. It does not currently preserve the table and native structural information needed for the proposed eCFR reader. SpicyDocs supplies acquisition and source-identity helpers, not an alternative eCFR text renderer.** These are complementary capabilities; do not add a DocSpec segmentation dependency to Rulespec.

This assessment directly imported current local modules and exercised three pinned native eCFR sections from the reference-body probe, plus explicitly constructed controls. No production edits, new dependencies, wheels, network/model calls, segmentation or corpus rebuilds. Current module paths/hashes are in the result files. SpicyDocs has unrelated uncommitted work; findings describe the imported working-tree bytes, not a published release.

## What exists and was exercised

| Capability | Verified behavior | Fit and limitation |
|---|---|---|
| `docspec.processing.visible_text.XmlVisibleTextExtractor.extract(bytes)` | All three actual sections produce visible text with blocks and byte-range mapping runs. Existing `heading_levels={'HEAD': 1}` recognizes the eCFR heading without changing code. | Useful deterministic visible text, source-byte evidence and configurable heading vocabulary. Output has no native XPath/node attributes, section index or table row/cell structure. |
| `VisibleText.rendition_range(start, end)` | Selected actual business-district, suspension, alcohol and equipment text maps back to captured XML; constructed entity/unicode control maps `Alpha & beta` back across `&amp;`. | Representation offsets are UTF-8 **bytes**. Collapsed whitespace/entities resolve conservatively to source runs. This differs from a decoded-source-character/XPath map and cannot be exchanged without an explicit coordinate conversion. |
| `docspec.adapters.content_fetchers.LocalFileContentFetcher` | Selected XML file streamed byte-identically; a one-byte-too-small limit refused. | Existing contained local file acquisition with size/stat checks. It fetches a whole chosen file, not a section within a title. Its fetch method does not itself verify `expected_digest`; downstream acquisition owns digest validation. |
| `spicy_docs.catalog.profiles.declared_profile_for_table('cfr_sections')` | Returns a profile listing heading/citation and optional `text`, `full_text`, `xml_text` fields. | A field/profile declaration, not proof body text is populated or a body reader exists. |
| `spicy_docs.sources.federal_register.body_sources.body_source_locators` | Constructed valid FR metadata produces format URL candidates; eCFR URL passed to this FR-specific API refuses. | Source-specific discovery/identity helper. Derivation does not establish remote availability. Not a CFR reader. |

Also traced, without an additional invocation: `docspec.processing.extraction.XmlExtractor` validates XML then `_passthrough_result` retains the exact original bytes with identity evidence mapping. That is deliberately source-native preservation, not readable-text extraction. `Extractor` and `ContentFetcher` protocols separate those operations; neither requires semantic/logical segmentation. SpicyDocs' FR MODS resolver parses source metadata to select a granule/access ID; it does not render the regulation body.

## Actual source findings

The probe produced default and `HEAD`-configured outputs for:

- `49 CFR 382.107`: all observed definition paragraphs remain readable; configured heading recognized.
- `49 CFR 390.5`: business-district definition and final indefinite-suspension note remain present; configured heading recognized. Retention of the note does not interpret whether the section is operative.
- `40 CFR 82.158`: prose remains readable, but the two native tables become streams of individual cell paragraphs. Column relationships and row identities are absent. The actual header becomes `Manufactured orimported beforeNovember 15, 1993` because its `<BR>` elements add no separator.

The source structures expose specific gaps, not just a preference for formatting:

| Constructed diagnostic | Existing DocSpec output | Consequence |
|---|---|---|
| Header `Type, Limit`; row `(empty), 20`; row `A, (empty)` | `Type`, `Limit`, `20`, `A`, each separated by blank lines | Empty cells disappear, so row/column positions cannot be reconstructed from the returned text/blocks. Original XML is still available. |
| `<DIV8>Lead-in<P>Child one</P><P>Child two</P></DIV8>` | `Lead-inChild oneChild two` as one block | The generic rule emits a text-owning ancestor with its descendants; it does not respect nested block boundaries. This is a constructed format counterexample, not a measured frequency in eCFR. |
| Entity plus thin space | Entity decoded, whitespace normalized; source run retained | Mapping is useful, but normalization differs from preserving all original decoded characters plus inserted separators. |
| Malformed XML | `extraction.unparseable-source` | Failure is explicit in both configuration arms. |

The actual section defaults produce 57/157/93 blocks respectively and no recognized headings; configuring `HEAD` recognizes one heading in each with the same block counts. Counts describe these three files only. Raw results, all blocks/runs and sampled source fragments are in `docspec-results.json`; every output text is saved separately.

## Recommendation for the candidate engine

**Do not claim there is no existing XML reader, but do not substitute this reader for faithful native eCFR output as-is.** DocSpec's current reader covers generic visible text and original-byte evidence. The pending RefSpec candidate reportedly covers native section attributes/XPath, row/cell boundaries and original decoded character preservation; the direct DocSpec probe demonstrates those are not redundant outputs.

Before establishing a second generic XML implementation, make the coordinate/layout requirement explicit:

- If the consumer needs only searchable normalized paragraphs with original-byte links, reuse DocSpec's existing reader and heading configuration at an optional document-preparation boundary.
- If the consumer needs exact native section/table navigation, the eCFR-specific structural profile remains necessary. Prefer extending an existing shared traversal already in the relevant package; do not build a second acquisition/catalog/segmentation stack around it.
- A future general fix to DocSpec's `<BR>` and table layout should improve that owner directly; this probe does not implement that extension. It would need its own compatibility checks because layout/configuration contributes to recorded identities.

SpicyDocs should continue to own acquisition and publisher response identity when fresh bytes are needed. Neither its CFR field profile nor FR body URL helper replaces native eCFR reading. No direct sibling-source import or required service is recommended for Rulespec validation. Consume pinned input artifacts and retain evidence so saved validation remains self-contained.

## Reproduce the direct checks

Commands executed from Rulespec (result files are created exclusively; preserve them before a separate rerun):

```sh
uv run --project /Users/mikewolfd/Work/DocSpec --no-sync python \
  thoughts/experiments/2026-09-11-ecfr-text/sibling-readers/docspec_probe.py
uv run --project /Users/mikewolfd/Work/spicy-docs --no-sync python \
  thoughts/experiments/2026-09-11-ecfr-text/sibling-readers/spicydocs_probe.py
```

`docspec-results.json` records configurations, source hashes, all output blocks/runs and sampled source ranges. `spicydocs-results.json` records profile/locator results and failures. The input section XML, source-edition caveats and full-title pin verification remain in `../../2026-09-11-reference-bodies/catalog-probe/`. No comparison claims rely on a fresh service response or an inferred source edition.
