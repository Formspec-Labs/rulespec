# Reference bodies: local catalog and publisher XML probe

**The provision bodies already exist locally. The sampled SpicyRegs catalog does not supply them, and a located body is not automatically the right edition or operative rule.** Reuse pinned publisher XML for optional reference navigation; do not add a service or sibling import to Rulespec validation.

This read-only probe used three actual reference occurrences from saved Rulespec inputs, no network or model calls, and no production changes. It directly imported existing SpicyRegs and SpicySearch functions and used the standard library XML parser to select native publisher `TYPE="SECTION"` / `N` nodes. It did not introduce a text parser, segmentation method, dependency, build or service. Native XML remains authoritative; the accompanying `.txt` files are only `Element.itertext()` renderings.

## Directly exercised paths

| Existing capability | Observed output | What can be reused |
|---|---|---|
| `spicy_regs.sources.cfr_sections.CfrSectionsReader` | Keyless call yields no records. Constructed existing-test-style granule passed through `_iter_granules` and `_shape` produces metadata/citation fields, no body. | Publisher identity, annual edition, heading and source URL. The constructed reader control is not a live provider response. |
| Saved `mixed-real-data-corpus-v2/cfr_sections.parquet` via PyArrow | 40,000-row historical sample, eleven metadata columns, no full text; zero hits for the three exact title/part/section filters. | Bounded catalog lookup, not proof that targets do not exist. This sample is not a current complete catalog. |
| `spicysearch.cfr_citations.extract_citations(..., strict=True)` | Explicit full citations preserve title/part/section and raw surface. Bare `§ 390.5` returns no citation. `.key` is deliberately **part-level**, so both `390.5` and `390.5T` yield `49 CFR 390`. | Citation discovery with provenance. Do not use its tagging key as a section-body lookup key; preserve the section and document-title context. |
| Existing publisher eCFR XML under durable corpus salvage | All three target sections found exactly once, with full-title SHA-256 matching the per-title manifest and original section byte offsets saved. | Complete dated target XML for navigation, including tables and editorial/effective-date notes. No ready-made general eCFR body lookup service was found in the inspected APIs. |

Paths checked without a corpus-wide scan: `~/corpora` does not exist; `~/Work/corpora` does. The body corpus is `~/Work/corpora/_salvage-2026-08-28/refspec-output/ecfr-title-xml-2026-08-24/`. This probe opened only its manifest and titles 40/49; it did not claim the integrity of every title. The manifest records publisher endpoint dates and fetch times separately.

## Actual references and source cautions

| Saved source reference | Retrieved local section | Corpus publisher date | Important raw content |
|---|---|---|---|
| Railroad stop exception: business district, `§ 390.5` | `49 CFR 390.5`, Definitions | 2026-08-19 | Includes the business-district frontage definition **and an Effective Date Note saying the section was again suspended indefinitely**. |
| Driver alcohol prohibition: alcohol, `§ 382.107` | `49 CFR 382.107`, Definitions | 2026-08-19 | Defines alcohol, alcohol concentration and alcohol use separately; lead-in also refers to `390.5T`, `386.2` and `40.3`. |
| Refrigerant recovery equipment: `§ 82.158` | `40 CFR 82.158`, Standards for recovery and/or recycling equipment | 2026-08-20 | Contains equipment manufacture/import dates, certification duties, exceptions, two native tables and referenced appendices. |

The saved Rulespec source captures are annual 2025 GovInfo excerpts. The recovered corpus is later dated eCFR text. No equivalence comparison with the 2025 targets was performed, so results are **different-edition discovery candidates**, not resolved source-edition dependencies. These pinned dates do not establish present-day currency.

The railroad example makes the distinction concrete: recovering the exact `390.5` body is mechanically successful while its own suspension note prevents an unsupported claim that this is the operative definition. Do not silently redirect to `390.5T`; preserve the citation, edition question and note for navigation/review.

Missing controls queried nonexistent section `999999.999999` in both opened titles and returned zero matches. Ambiguous controls explicitly leave titleless and editionless requests unresolved. Those control dispositions are probe policy declarations, not behavior claimed of an existing general resolver.

## Smallest reusable path and remaining gap

1. Preserve the original citation occurrence plus source document identity/edition/context.
2. Select a pinned publisher title file and exact native section identifier. Return the complete section XML plus original file digest, byte range and publisher date. This probe demonstrates the underlying existing data/library path.
3. Show the referenced body as a separate navigation destination with edition mismatch or unresolved status. Keep original evidence and interpretation unchanged.

The missing production component is a **thin optional reference-body lookup with explicit edition selection and unresolved results**. It should consume immutable local artifacts, not import a sibling's mutable source tree. The probe's direct imports inspect current capabilities only. Rulespec validation continues to work entirely from its saved documents/evidence without this optional lookup. No DocSpec segmentation is involved.

Do not replace raw XML with flattening: table cell boundaries and effective-date notes affect interpretation. Nor does this probe establish transitive dependency closure; the definitions body itself cites further provisions. No automatic expansion, legal resolution or model-context injection was tested.

## Evidence and reproduction

- `results.json`: exact source contexts, all catalog outcomes, source/title/file hashes, publisher manifest receipts, native section matches and byte offsets.
- `citation-results.json`: current imported SpicySearch module path/hash and full returned citation records.
- `*-0.xml`: exact original bytes sliced from the pinned title XML; `*-0.txt`: labelled text rendering, not replacement source.
- `probe.py`, `citation_probe.py`: bounded scripts; network connections disabled and outputs created exclusively.

Commands executed from Rulespec:

```sh
uv run --project /Users/mikewolfd/Work/spicy-regs --no-sync python \
  thoughts/experiments/2026-09-11-reference-bodies/catalog-probe/probe.py
uv run --project /Users/mikewolfd/Work/spicysearch --no-sync python \
  thoughts/experiments/2026-09-11-reference-bodies/catalog-probe/citation_probe.py
```

No timing or corpus-wide coverage claims are made. Existing outputs are preserved; scripts intentionally refuse replacement of their results. Original corpus bytes remain at the recorded immutable-source paths. See `replay.json` for independent local byte/hash reconstruction checks.
