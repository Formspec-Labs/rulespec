# Existing XML readers and the eCFR preparation decision

**Delivery follow-up:** the native eCFR consumer is now committed and installed
locally. [Application results and limits](application.md) record the final checks.
The comparison below preserves the assessment that preceded adoption.

**DocSpec already solves XML visible-text extraction with original-byte evidence.
The missing piece for this consumer is native eCFR structure: section attributes,
XML locations and table relationships.** The direct sibling comparison supports
extending the existing RefSpec native XML traversal for this bounded need. It does
not support importing another text-stripper or building acquisition, catalog or
segmentation systems in Rulespec.

This assessment used the three pinned eCFR sections from the preceding
[body-source comparison](../2026-09-11-reference-bodies/README.md), plus declared
constructed controls. It checks representation and source preservation, not model
accuracy, a representative corpus, or performance. No network or model calls were
made. At this comparison checkpoint the RefSpec extension was source-tested,
uncommitted and uninstalled; installed XML support still meant USLM.

## Capabilities and fit

| Existing capability | Direct observation | Decision for Rulespec |
| --- | --- | --- |
| DocSpec `XmlVisibleTextExtractor` | Produces normalized paragraphs, configurable headings and UTF-8 byte maps into original XML. Existing `heading_levels={'HEAD': 1}` recognizes eCFR headings. | Reuse for normalized searchable representations where appropriate. It is not a native section/table index and cannot replace the current Unicode-character/XPath evidence path unchanged. No new logical-segmentation dependency. |
| DocSpec `XmlExtractor` and `LocalFileContentFetcher` | Source inspection shows exact XML passthrough; direct local fetch returned identical bytes and refused a too-small size bound. | Reuse source retention/acquisition at that boundary. Neither resolves a cited section within a title. Passthrough was inspected, not separately executed in this probe. |
| SpicyDocs source profiles and FR `body_source_locators` | The CFR profile declares optional body fields. The FR helper derives XML/text/HTML candidates and rejects an eCFR URL on its FR-specific interface. | Reuse publisher-specific discovery and identity helpers when acquiring new inputs. A declared `xml_text` field or derived URL does not establish that a body exists, is fetched, or has the right edition. |
| SpicySearch `document_release_mapper` / `document_content_index` | Code reads and checks text/segments already supplied in a DocSpec release. It does not extract XML or choose new logical boundaries. | Keep it as the downstream search consumer. Do not add a second extraction path through search. |
| SpicySearch `strip_html_to_visible_text` and court `visible_text` | Both strip markup to strings. The experiment helper collapses all whitespace; the court helper retains incidental source whitespace. Neither returns native nodes, section identity or evidence maps. | Do not use these as native XML readers. The experimental helper also is not a production API. Existing Rulespec citation-reader reuse remains in place. |
| SpicySearch `extract_blocks_from_xml_body` | Empty output for the actual eCFR inputs; the explicit `<LSTSUB><P>…` positive returns the subject paragraph. | This is a Federal Register List of Subjects selector, not a general body extractor. Reuse only for that source feature. |
| Candidate RefSpec shared `xml_text.read_text` eCFR profile | Source text, source maps, native attributes and table-cell boundaries survive the selected cases. The copied USLM oracle remains identical. | Preferred bounded native-source extension. Connect through the existing optional reference-source path after title-context, evidence and application checks. Keep acquisition outside it. |

The SpicyDocs check describes directly imported working-tree modules; unrelated
documentation changes already existed there. No files in SpicySearch, DocSpec or
SpicyDocs were changed by this assessment.

## Failures that distinguish the representations

The actual `40 CFR 82.158` header contains line-break elements between words.
DocSpec currently returns `Manufactured orimported beforeNovember 15, 1993`.
Its table output lists cell values as separate paragraphs, without row/column
identity. Heading configuration does not change that layout.

The SpicySearch helpers separate those line-break words, but both turn the
constructed inline word `<E>re</E>quired` into `re quired`. The experiment helper
turns two table rows, `(empty, 20)` and `(A, empty)`, into `20 A`; the court helper
retains spaces without cell identity. Neither rejects the malformed-XML control,
which is consistent with markup stripping rather than XML validation.

DocSpec's separate constructed mixed-content control becomes
`Lead-inChild oneChild two`. Its empty-cell control loses empty positions. These
are diagnostic counterexamples, not measured occurrence rates. Its byte evidence
mapping and suspension-note preservation did work in the sampled source checks.
The candidate RefSpec reader retains native `rowspan`/`colspan` attributes and
cell boundaries, but does not reconstruct a merged-cell grid. Source whitespace
can still make the readable table tall.

## What to implement and what remains separate

1. Continue R12 with the existing native XML path and optional source lookup.
   Require native title context for exact CFR section resolution; preserve
   unresolved pinpoints, ranges, editions and mismatched source context. Measure
   resource use before requiring full-title input. The shared candidate is not
   yet an installed application feature.
2. Keep DocSpec's general `<BR>` and mixed-block shortcomings as upstream fixes
   under R23. They matter to searchable text independently of Rulespec. Changing
   that layout needs its own compatibility checks because prepared-text identities
   can change. No DocSpec production fix is claimed here.
3. Reuse SpicyDocs source-selection/identity helpers if an acquisition consumer
   needs them; do not add speculative fetching to the extractor. Prefer captured
   publisher XML when the needed text is available in a supported format.

R12 and R20 remain partial. The later linked delivery completes the exact eCFR
application connection, while historical correspondence and the broader reuse
backlog remain open. The task list still has 19 open workstreams out of 26.

## Evidence and reproduction

- [Predeclared comparison and amendment](design.md).
- [DocSpec/SpicyDocs findings](sibling-readers/README.md), full raw text outputs,
  byte-map examples and source hashes in that directory.
- [SpicySearch direct-import results](sibling-readers/spicysearch-results.json),
  with actual and constructed input hashes, exact module paths/hashes and output
  files. Invoked offline from SpicySearch with:
  `uv run --no-sync python /Users/mikewolfd/Work/rulespec/thoughts/experiments/2026-09-11-ecfr-text/sibling-readers/spicysearch_probe.py`.
- [Candidate RefSpec findings and freeze](upstream/README.md), with the focused
  validation command, copied-oracle comparisons and complete native-reader output.

Root inspected the actual table output, counterexample strings and relevant
implementation paths in all three named repositories before this decision. Source
inspection and direct calls are distinguished above; no whole-repository test or
service availability claim follows from this check.
