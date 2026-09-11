# RefSpec provision-body lookup probe

**USC bodies are already accessible through RefSpec's native USLM reader. The missing piece is choosing a supplied pinned source document and exposing its target safely across documents.** No additional parser, model pass, network call, dependency or production edit was needed for this probe.

## Directly exercised

| Reference/control | Result | Important boundary |
| --- | --- | --- |
| Actual `5 U.S.C. 553(b)(B)` in saved Federal Register 2025-24202 | Exact `/us/usc/t5/s553/b/B` node, 243 readable characters, canonical identifier, XPath, decoded-source offsets and source map | Returned release 119-102; equivalence to the citing 2025 source's edition is not established |
| Actual `38 U.S.C. 4301, et seq.` in saved leave source | Exact anchor `/us/usc/t38/s4301`, 26,316 characters including editorial/statutory notes | Section 4301 is an anchor only; this does not resolve the open-ended `et seq.` target |
| Constructed pinpoint `/us/usc/t38/s4301/a/1` | Exact 169-character paragraph | Tests native identifier selection; this pinpoint was not written in the cited leave source |
| Constructed missing `/us/usc/t38/s4301/z` | No node; oracle reports subsection absent in its selected release | No fallback to a neighboring paragraph or fabricated text |
| Historical 1990 question for 4301 | Oracle returns unknown, `edition_outside_oracle_window` | Current text must not be labeled 1990 text |
| Wrong archive digest | Existing pin reader refuses | Preserves expected/observed digest and length in saved failure |

The first row is the viable explicit body-lookup positive; the open-ended row is not counted as complete reference resolution.

## Interfaces and fit

| Existing callable | What it returns | Fit for R12 |
| --- | --- | --- |
| `refspec.input_pin.read_verified_file_pin(path, expected_sha256="sha256:…", expected_byte_length=n)` | Authenticated raw bytes; rejects changed, unsafe or mismatched files | Use before reading a selected local archive/document |
| Standard-library `ZipFile(...).read("usc05.xml")` | Exact title member from authenticated archive | Archive chooses title, not paragraph; member digest recorded separately |
| `refspec.registry.uslm.read_text(xml: bytes)` | `text`, decoded `source_text`, `source_map`, and `nodes` keyed by XPath; node values include canonical `identifier`, tag and both text coordinate ranges | Reuse for target bodies. No new XML-to-text implementation needed |
| `refspec.registry.uslm.section_identifiers(xml)` | Section identifiers only | Identity/existence inventory; no body or paragraph text |
| `UscSectionOracle.from_repository(root)` then `section_verdict(title, section, edition_year)` | Pinned existence, statuses, annual attestation, coverage caveats and recodification evidence | Useful lookup uncertainty. Does not supply edition-specific text |
| `oracle.subsection_verdict(title, section, sub)` | Current-release subsection existence/coverage | Not a body reader; detailed native XML identifiers preserve case and deeper hierarchy |
| Rulespec `uslm.prepare_uslm`, `read_uslm`, `attach_publisher_links` | Existing original-XML pinning, text replay, publisher references, target identities and Core XPath/text evidence inside one supplied document | Reuse source/evidence design. Existing same-document target lookup is the nearest consumer implementation |
| RefSpec `inspect_ecfr_part_sources(...)` | Specialized subject-list metadata inspection of titles/agencies/structure/Part 11 full text | Not a general eCFR provision reader; it requires a part-shaped root and the subject-list requirement |
| `CfrAuthorityNotes.from_repository(...)` and Atlas explorer resource/identifier/evidence views | Authority notes, resource metadata, provenance and identity relations | Not demonstrated complete CFR/USC provision bodies; do not equate label or authority note with target text |

RefSpec current checkout was `61bb05d09e9bed4041b48e35f5edcefd19cc10aa`. The Rulespec virtual environment's installed `refspec` version is `0.1.0.dev0`; its `uslm.py` bytes exactly match the probed checkout. [Compatibility receipt](installed-compatibility.json) includes hashes. Direct imports used the RefSpec source checkout and existing virtual environment.

The source archive is local salvage `usc-annual-2026-08-24/xml_uscAll_119-102.zip`, 108,610,077 bytes, SHA-256 `55c8d19543c4a972a33e33532b592ac3984c83fdcb04de9f5a64ef1f8483d300`. Its retained fetch log pin agrees with RefSpec's tracked oracle README. Existing pin code authenticated the bytes before ZIP member access. Original title metadata says `Online@119-102`; Title 38 was created 2026-05-04 and Title 5 was created 2026-07-16. These are not 2024/2025 text-edition assurances.

## Raw-source findings

[5 USC 553(b)(B) raw XML with surrounding context](raw-s553-b-B-context.xml.txt) shows a real named subparagraph, not a TOC mention or authority citation. The returned body says the agency must find good cause and incorporate its finding and reasons in the issued rules. Immediately before sibling(A), the source says: **“Except when notice or hearing is required by statute, this subsection does not apply—”**. That parent continuation is outside the exact(B) target. Body lookup therefore supports navigation; it does not by itself deliver complete governing context or an executable exception.

[Section 4301 raw XML](raw-s4301-context.xml.txt) shows actual section/subsection/paragraph nodes. Its whole section includes lengthy editorial and statutory notes; the full section's 26,316 characters are not all operative text. [Readable body](s4301.txt) preserves those notes rather than silently stripping them. The 2025 amendment listed there further demonstrates why existence in 2024 does not prove this captured body is 2024 text.

Original decoded XML text coordinates are Unicode codepoints, not XML byte offsets. Source-map entries distinguish original decoded text from inserted layout separators. Archive digest + member name/digest + canonical identifier + XPath distinguish source identity, edition and target. A title-relative text offset alone is unsafe outside that title.

## Cost and consumer boundary

`read_text` parses the entire selected title each time it is called. ZIP member selection avoids loading all titles, but does not avoid parsing one whole title per call. The measured Title 38 parse took 0.70 seconds for 18.6 MB XML/200,408 nodes; Title 5 took 0.69 seconds. These are single local observations, not latency guarantees.

The positive probe built an identifier→list-of-nodes index once in 0.016 seconds after reading Title 5. Reusing that prepared title/index supports further lookups without reparsing. Preserve lists rather than silently selecting one node if identifiers repeat. A consumer can hold this bounded per supplied document/version; no new persistent corpus rebuild is required for a small selected-source session. Rebuilding the index or scanning every node per reference would unnecessarily scale with title size times reference count.

Do not attach these external offsets to the requesting Rulespec document's evidence array. `discovery.verified` checks evidence against `book.document`; externally sourced bodies need their own source identity/document plus target evidence. The existing Rulespec publisher-target shapes and Core XPath fragments should guide that small consumer addition. Retrieval-pilot separately inspects local eCFR bodies; this report does not claim USLM parsing supports eCFR `DIV` XML.

## Artifacts and reproduction

- [Explicit actual positive](explicit-positive.json), [original open-ended source occurrence](source-reference.json)
- [Source pins/reader results](results.json), [identity and edition controls](oracle-results.json)
- Exact target texts and source-map selections alongside those results
- `probe.py` and `explicit_positive.py` directly import existing implementations; they neither alter production nor fetch/rebuild sources.

```sh
PYTHONPATH=/Users/mikewolfd/Work/RefSpec/src /Users/mikewolfd/Work/RefSpec/.venv/bin/python thoughts/experiments/2026-09-11-reference-bodies/refspec-probe/probe.py
PYTHONPATH=/Users/mikewolfd/Work/RefSpec/src /Users/mikewolfd/Work/RefSpec/.venv/bin/python thoughts/experiments/2026-09-11-reference-bodies/refspec-probe/explicit_positive.py
```

No integration or commit. This bounded result supports optional source-body navigation, with pinned edition and unresolved scope visible; it does not support making external-text ingestion a mandatory extraction pass.
