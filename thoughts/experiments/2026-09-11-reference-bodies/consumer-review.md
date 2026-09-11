# Independent optional reference-source consumer review

**Completed: no remaining serious correctness gap found in the reviewed optional consumer after the fixes below.** No production/test edits or full-suite execution by this reviewer. Inline probes construct small sources and call existing production functions; they do not establish general retrieval accuracy.

## Findings sent during implementation

1. **Blocking runtime regression, initial SourceIndex refactor.** The local SourceIndex variable `index` was overwritten by the anchor enumeration loop; final `index.artifact()` called a method on an integer. Root changed the source-object variable to `publisher`; current reading confirms that correction.
2. **Blocking text-reference lookup, initial external adapter.** `_identifier` allowed only `usc_title`, `usc_section`, `pinpoint`, while the actual native USC reading includes `authority_type`, `parse_status`, and default false qualifier flags. A direct `scan_references(prepare_document('5 USC 553(b)(B).'))` plus `_identifier` returned None. The accepted native occurrence reports parse_status partial, so merely requiring ok would also suppress this positive. Preserve substantive qualifiers, while tolerating normal metadata/default flags.
3. **Unbounded publisher target materialization.** A native href `/us/usc/t5` matched both USLM root and title identifiers. The no-containing-section fallback serialized the full title twice. A direct two-section fixture produced two identical full-title records and an ambiguous target. This contradicts the declared no-whole-title output bound; broad title/chapter targets need an explicit unsupported-body result or another deliberately bounded behavior.
4. **Scaling concern to measure.** `SourceIndex.support` calls `_evidence` for each original source slice; `_evidence` scans the whole title source map. Containing-section context currently asks for that support and discards the returned text evidence. Large notes/table sections may incur title-map-size times selected-slice work despite indexing once. No full-corpus timing claim from this observation; measure the real5USC positive before deciding whether a small reuse fix is needed.

Source identity review so far: external tables key by XML digest rather than readable-text digest, so equal text in distinct XML can remain distinct editions/artifacts. External discovery evidence takes its source document from that XML identity instead of the requesting document, which addresses the main coordinate-boundary risk. Further review pending finalized code and target probes.

## Follow-up checks against revised implementation

- Text-reference metadata gate fixed: the ordinary5USC553(b)(B) occurrence now locates its exact target. Notes and ranges acquire no target; `et seq.` remains rejected with its existing refusal.
- Broad publisher title fixed: direct repeat now returns `target_scope_not_supported`, zero targets and zero containing records.
- Containing-section context now calls shared support with `include_text=False`, avoiding generation of discarded quote evidence. Target-piece `_evidence` still has its existing full source-map check; measure real workloads before claiming a general scaling guarantee.
- External discovery evidence reconstructs exactly from its own source containing-section record. The constructed parent condition remains in that record.
- An altered originalXML with unchanged pin is refused.
- Same readable text in distinctXML artifacts keeps two source IDs and two target IDs, with ambiguous resolution; no silent merge by text-document ID.
- Publisher href/text disagreement remains unresolved at the publisher target; the accepted text interpretation is retained without promoting its different553 target.

## Additional finding

**Explicitly resupplying the requesting XML can falsely report target absence.** The external-source adapter skips indexing any source whose XML identity matches the requesting publisher source. That avoids duplicate native targets, but native publisher processing does not resolve plain text occurrences lacking `<ref>` markup. Constructed direct call: requesting USLM contains plain text `5 USC 553` and a real553 target section; `scan_references(document, reference_sources=[document])` reports `not_in_selected_sources`. The bytes and identifier are present in the explicitly supplied source. Either reuse the same source index for these accepted plain text occurrences or report the narrower unsupported behavior rather than false absence.

## Final check

The same-requesting-XML finding was corrected by retaining the explicitly supplied source in the identifier lookup. Repeated direct scan now locates the unmarked `5 USC 553` occurrence, and discovery exports its source-qualified target successfully. All reproduced correctness findings above are fixed in the reviewed code.

This is a bounded code and constructed-input review, not a general CFR/USC resolver certification. The source reader remains USLM-only; edition correspondence remains unestablished. Whole containing sections may be large because statutory/editorial notes are intentionally preserved. Each source should be prepared/indexed once where possible; supplying the requesting XML again currently duplicates reader work between publisher-link scanning and external indexing, although it no longer loses the target. No evidence here justifies a new cache framework.

No full suite was run by this reviewer. Root owns integration tests, real captured-source checks, and final adoption.

Reviewed module snapshots:

- `uslm.py`: `55381108d433794345bc11386f8f20f876d1df1f954511e06447ff0d97322c5d`
- `reference_sources.py`: `3699e2219e55df231cbce310e68fc9b52151bf4cf70ee67fb38f2ee9a16e9010`
- `references.py`: `0130db5ad18f04fedfa718a9fe4fc77232cd18402bceb1a8816e69ca9c619585`
- `discovery.py`: `06f4cc98d7a101323940544ca62caf77fdad552cb57615eee0742ab6a9ce3b5d`
- `cli.py`: `08d12e8b69b01fa888e04865ea8ef37049055bb5de7b4f1b1f7df9bd46a957ae`

Final reread after root reported the real Title5 probe: confirmed the native metadata gate, no-containing-section refusal, same-source indexing, source-qualified discovery handling and runtime capture inclusion of `reference_sources.py`, `uslm.py` and RefSpec reader modules. No additional serious correctness concern found. Root-reported real-source timings and sevenXPath checks are not represented as independently rerun by this reviewer. Ready for root's full-suite gate.
