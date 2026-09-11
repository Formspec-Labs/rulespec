# Supplied reference text for discovery

The optional consumer locates exact USC provisions in supplied USLM sources and
keeps their containing section available for reading. It reuses RefSpec's text
reader and section spelling normalizer, plus Rulespec's existing XML, source-map
and evidence records. No model/schema/prompt change or new runtime dependency.

The [declared comparison](design.md) followed two bounded assessments:
[RefSpec bodies/oracle](refspec-probe/README.md) and
[Spicy Regs/catalog/corpora](catalog-probe/README.md). The former already supplies
USC bodies through `uslm.read_text`; the catalog and oracle supply identity or
metadata, not provision text. Actual eCFR XML bodies exist locally, but their
`DIV` format is not supported by the USLM reader. That application connection
remains open rather than being counted as integrated.

## Comparison and decision

| Measure | Installed baseline | Supplied-source consumer |
| --- | --- | --- |
| Three actual `5 U.S.C. 553(b)(B)` occurrences in saved Federal Register 2025-24202 | Mentions preserved; no body | All three locate one exact 243-character provision |
| One additional plain `5 U.S.C. 553` occurrence | Mention only | Exact section located |
| Parent condition, other alternatives, historical/editorial notes | Not available through the reference | One shared 4,352-character section record |
| Existing citation readings, rejections, passages, statements, terms and processing accounting | Baseline | Identical |
| Source version | Requesting source only | Separate XML digest, `Online@119-102` metadata, selectors and source evidence |
| Intended edition/legal applicability | Not established | Still not established |
| Additional model calls | 0 | 0 |

**Decision: adopt the optional navigation feature.** These selected cases support
source lookup and evidence preservation, not a general extraction-accuracy gain.
The earlier failed model-context and combined-retrieval interventions stay
experimental. This feature does not add text to model prompts or a search index.

The original 2025 source does not establish that the supplied 2026 release is its
intended edition. The exact(B) text omits its parent's condition, “Except when
notice or hearing is required by statute”; the containing section preserves that
condition without asserting automatic inheritance. It also preserves historical
notes, including a reference to former Title 5 section 553. A complete section
body is not a set of equally operative rules.

## Implementation and controls

Both `references` and `discovery-export` accept repeatable `--reference-source`
arguments; the API accepts prepared source documents. External targets carry
`source_id` and `record_id`. Source records contain prepared text once, and target
positions select within that source. Discovery evidence lives in the corresponding
source's evidence table, avoiding collisions with the requesting document or
another XML edition with identical readable text. Existing Core `Artifact`,
`SourceFragment`, XPath selectors and digests represent provenance.

Twenty-one focused tests include actual source XML and constructed controls:
missing pinpoints; open-ended citations; ranges/notes; duplicate identifiers;
distinct editions and same readable text from different XML; tampered XML/text/maps;
wrong formats; case-sensitive pinpoints and existing dash normalization; publisher
href/text disagreement; repeated mentions; explicitly resupplied requesting XML;
broad title-level links; and both normal commands. Seven fragments from the full
Title 5 comparison also resolve independently against the original XML tree.

The [independent review](consumer-review.md) caught a variable-shadowing bug,
an overrestrictive native-field check, whole-title materialization, and a
same-document lookup omission. Those were fixed and covered. Original failing
logs remain. The first full-document harness incorrectly expected two pinpoint
mentions; raw review found three. `*-02-incomplete/` retains those outputs, and
`design.md` records the corrected count. An initial harness import failed because
lxml was absent; the comparison uses the standard-library XML reader instead,
without adding a dependency.

## Cost and limits

One full-title source observation took 0.71 seconds to prepare and 1.03 seconds to
scan, versus 0.06 seconds for baseline recognition alone. Discovery took 0.92
seconds with the supplied source versus 0.02 seconds without it. These are single
local observations, not latency guarantees. The reader parses each supplied title
once per scan, rather than once per citation; the focused repeated-mention check
confirms that behavior. Explicitly resupplying the requesting XML also repeats
its publisher preparation; there is no new cache framework.

The reference JSON grows from 33,854 to 63,286 bytes; discovery grows from 179,825
to 213,375 bytes. That includes source/selector metadata and selected context, not
the 19 MB title XML or a full-title dump. The default export is unaffected.
Target quote checks retain the existing source-map scan cost. Whole sections may
still be long, especially notes and tables; visual table fidelity and governing
meaning remain separate concerns.

The CFR probes recovered three bodies, but the available annual 2025 sources and
2026 eCFR target editions differ. Section 390.5 includes an indefinite-suspension
note, while 382.107 refers to 390.5T. Neither is a reason to silently substitute a
modern target. A general eCFR reader/consumer, historical correspondence and
broader reference scope remain R12 work.

## Reproduction and delivery

`compare_consumer.py` records raw normal-API outputs and checks original-source
pins, exact body text, containing context, independent XPath fragments, unchanged
baseline content, and source/installed equality. The small regression fixture
retains the original section and metadata inside a declared constructed USLM
wrapper; its full-title offsets and hashes are in `source/summary.json`.

Source and isolated installed checks: **616 passed each**. Both installed
environments verify all **407 Python files** against the pinned wheels; the
extractor files also agree with the checkout. Full-source reference/discovery
outputs match across source, isolated and working installations. Code is committed
locally as `4dcad37`. The [wheel inputs](wheel-inputs.json) retain the
previous six dependencies and replace only the extractor wheel. Installation
uses those explicit local wheels offline. Final installed/working receipts and
commit status are recorded in `delivery.json`.
