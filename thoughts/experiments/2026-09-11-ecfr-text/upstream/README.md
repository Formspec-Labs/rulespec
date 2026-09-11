# Candidate shared eCFR text reader

**The existing USLM traversal can support readable eCFR text without a second XML engine. This is an uncommitted, uninstalled candidate pending the sibling-reader comparison.** No production adoption, wheel build, network call, model call or corpus rebuild occurred.

## API and ownership

In RefSpec:

- `uslm.read_text(xml)` retains its existing output, including method `uslm-block-boundaries/1`.
- New `ecfr.read_text(xml)` returns the same text/source-map/node shape with method `ecfr-block-boundaries/1`. Each node retains native `tag` and `attributes`, including `N`, `TYPE`, `VOLUME`, table spans and classes. It emits no invented legal identifier, paragraph identity, title or edition.
- `xml_text.read_text(xml, profile=None)` is the shared implementation. It parses once and chooses the supported profile from the root. The explicit wrappers fix their respective profiles. Unsupported/malformed roots refuse.

The application can distinguish an `ECFR`/`DIV1 TYPE=TITLE` source from a bare `DIV8 TYPE=SECTION` through the native nodes. A section-only source does not acquire title context from its number, filename or volume. Title/edition source selection remains the application's responsibility.

## Evidence

**93 focused tests passed.** Existing USLM native-reference and XPath tests were included. The replaced text implementation is copied into `tests/uslm_text_oracle.py`, without importing the replacement. Three real USLM fixtures under five conditions each—original, newline removal, inline text, empty table cells, added notes—produce identical complete result dictionaries: text, source text, maps, nodes and method. Mutation execution is asserted; there are no declared USLM divergences.

Three actual eCFR section fixtures were copied byte-for-byte from the preceding pinned catalog probe. `tests/fixtures/ecfr-text/pins.json` retains their hashes, original title receipts and byte ranges. All original decoded text and every node's source interval reconstruct exactly.

| Actual source | Native nodes | Readable characters | Inserted separators | Observed contents retained |
| --- | ---: | ---: | ---: | --- |
| 49 CFR 390.5 | 275 | 35,397 | 6 | Definitions, editorial note, indefinite suspension history |
| 49 CFR 382.107 | 89 | 12,518 | 2 | Definitions and exact references to 390.5T and other provisions |
| 40 CFR 82.158 | 137 | 11,839 | 53 | 56 table cells, caption, row/column span attributes, before/after date headings, values |

Small controls separately verify headings/paragraph adjacency, inline emphasis, mixed-case line breaks, leading/middle/trailing empty cells, existing source tabs, multiple paragraphs inside cells, notes, empty nodes and wrong formats. Compact raw `<TD>0</TD><TD>0.</TD>` text has no cell delimiter; the eCFR profile supplies tabs rather than joining values. Existing source whitespace remains unchanged, with only layout separators inserted.

The actual table text was read beside its XML. The before/after manufacture headings, values such as `4` and `10.`, row labels and exceptions remain distinct. The actual 390.5 source's `EFFDNOT` still says the section was repeatedly suspended indefinitely. Nothing turns that captured body into a current applicability assertion.

## Limits and decision

This passes the bounded source-preservation/readability gate. It does not establish that RefSpec is the best owner while SpicySearch, DocSpec and SpicyDocs are being checked. Keep the candidate frozen until those findings are compared.

The readable table is source order with tabs and preserved original whitespace, not a reconstructed grid. Merged-cell layout is retained as native attributes; it is not expanded into inferred cells. Empty nodes retain source positions and have no invented source text. Original pretty-print newlines can still make a table visually tall. The source map distinguishes inserted separators from decoded publisher text; offsets address Unicode codepoints, not original XML bytes.

The shared traversal and source mapping cost is linear in XML/text size plus per-node source-map lookup. It builds the complete supplied tree and maps; this probe measured selected sections only. No full-title memory or latency promise follows. Root owns that assessment before requiring full-title input.

## Saved artifacts and freeze

[results.json](results.json) records per-source counts and exact-map checks. The `*.readable.txt` and `*.reader.json` files retain complete candidate outputs. [source-freeze.json](source-freeze.json) pins the candidate source and tests; no further feature changes are intended before the sibling comparison.

Reproduce the offline comparison:

```sh
PYTHONPATH=/Users/mikewolfd/Work/RefSpec/src /Users/mikewolfd/Work/RefSpec/.venv/bin/python thoughts/experiments/2026-09-11-ecfr-text/upstream/compare.py
```

Focused validation, from RefSpec:

```sh
PYTHONPATH=src .venv/bin/python -m pytest tests/test_uslm_text.py tests/test_ecfr_text.py tests/test_uslm_source_paths.py tests/test_extract_uslm_reference_edges.py -q
```
