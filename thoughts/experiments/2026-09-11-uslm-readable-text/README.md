# Readable USLM source and publisher navigation: installed and verified

RefSpec's readable-text reader and Rulespec's XML preparation, publisher-reference
scan and discovery export are installed in the working environment. The new
conformance wheel includes the XPath selector shape and corrected plain-string
SHACL generation. The source, isolated-wheel and working command results match.
This is a bounded navigation/preparation improvement; context-assisted extraction
quality remains unmeasured. The broader reuse objective remains open.

The second preparation candidate preserves all 107 publisher reference texts and
all decoded source characters across the three selected cases. Eleven controls
and independent XPath checks pass. The first candidate failed the readability
gate on “FunctionsThe Secretary”; its code and outputs remain saved. B2 adds a
generic heading-to-text separator and fixes that join without rewriting source
characters. This is a bounded source-preparation result, not extraction accuracy.

The fresh case pairs 5 U.S.C. 302 with 5 U.S.C. 5721. The operative reference in
302(a) supplies a definition of “agency”; its target is present in the captured
pair. Selection followed the fixed source-order rule before changed outputs.
The target retains the listed agencies and the exclusion of a Government controlled
corporation. The earlier two cases have locally located editorial-note targets.

| Source | Decoded characters | Prepared characters, B2 | References retained |
| --- | --- | --- | --- |
| Title 5 section 423 | 4,340 | 4,370 | 30 |
| Title 42 section 242c | 9,921 | 9,973 | 40 |
| Title 5 sections 302 / 5721 | 5,120 | 5,152 | 37 |

Discovery's existing source-map handling preserves all original decoded characters
as evidence and excludes inserted separators. Inline words, punctuation, entities,
Unicode, repeats, empty references, duplicate identifiers, cell boundaries and
footnotes have controls. Tables retain source order and cell separation; this does
not reproduce full visual table layout. Original inter-element blank runs remain.

## Reuse assessment

- Reuse the shared RefSpec `iter_edges` and Python XML parser for occurrence
  identity. The [publisher schema/stylesheet archive](https://uscode.house.gov/download/resources/schemaandcss.zip)
  is captured and hashed here. Its block/table rules inform the preparation;
  heading separation is an explicit plain-text rule, not a full CSS renderer.
- The inspected Spicy Regs attachment transform reuses already extracted
  Mirrulations text. It supplies neither USLM node positions nor this source map.
- SpicySearch `text_units.py` provides evidence-bound UTF-8 text segments for search.
  It is a possible downstream R17 consumer, not an XML formatter. Rulespec already
  has codepoint evidence and passage identities; replacing them would add another
  representation without solving the observed XML problem.

## Implementation and delivery

- Added `read_text` to RefSpec's existing `registry/uslm.py`, with the pure native
  text/map/node result. It has no dependency on the Rulespec extraction application.
  Source checks pass **62 tests** including the previous 52 link/path tests and
  10 new text tests. Three frozen source-text expectations live beside their XML
  fixtures upstream. Existing link-reader default behavior remains unchanged.
- Added a thin Rulespec `uslm.py` consumer that builds the existing prepared
  document, retains original UTF-8 XML once, and verifies replay before trusting
  publisher coordinates. `load_document` routes `.xml` input through it. Publisher
  occurrences, shared local targets, text readings and discovery evidence are now
  connected. The initial source suite passed 508 tests; the new nested-refusal
  control brings the installed package suite to **509 passing tests**, in both
  the isolated environment and the working installation.
- Core already named `oa:XPathSelector` but lacked its payload shape. Added the
  CUE definition and regenerated the canonical outputs, including Rust. Compilation
  and CUE vetting completed, and `reference-corpus-check.log` reports PASS. The
  initial selector suite had four passes and one failure. The runtime comparison
  confirmed that a numeric XPath value passed SHACL while failing JSON Schema.
  A 20-line generator change uses the existing JSON-LD mapping to check plain
  strings without retyping identifiers, dates or language values. All **146 compiler
  tests**, **47 Rust tests**, and **299 parity cases** now run successfully at the
  Core gate: zero Core divergences, with two separately reported adversarial findings.
  The [validation comparison](xpath-validation-design.md) preserves the failure,
  result and limited scope. The model-facing schemas are unchanged; only their
  source manifest needed regeneration.
- Rebuilt conformance, RefSpec and extractor wheels, installed all seven pinned
  local dependencies in a fresh environment, and then updated the working
  environment. **1,031 package files** match source, wheel and both installations.
  **24 JSON artifacts** from the three real-source CLI runs match in all three
  environments; three earlier command outputs remain byte-identical. The combined
  upstream wheel checks pass **62 tests**. Dependency checks pass.
- An independent lxml XPath engine verifies all **110 exported XML fragments**
  against the original XML and content digests. It is a test tool, not a production
  dependency. The [raw review](raw-review.md) records the three targets, four
  residual overlapping readings and the false RIN candidate `1998—Pars.`.
- No new model fields, model calls, commits or published releases. The source
  changes and local installation are complete for this bounded slice.

The first isolated-wheel suite attempt used pytest's `importlib` mode and failed
collection because existing tests import sibling test helpers. The retry uses the
suite's normal import mode from `/tmp`; all application imports come from installed
packages. Both logs remain saved. This was a test invocation correction, not a
runtime repair. Earlier failed preparation/selector/schema-drift observations also
remain intact.

The [wheel inputs](wheel-inputs.json), [install commands](install-commands.json),
[package comparison](wheel-verification.json), [independent XPath check](application-xpath-verification.json),
and [final verification](verification.json) preserve the build and checks. The
working environment is `.tools/document-poc-venv`; the isolated installation is
`.tools/reference-integration-20260911-uslm-text`. The extractor README contains
the exact seven-wheel installation command and dependency constraint path.

## Remaining work

1. Test the false RIN reading upstream using the real amendment heading and valid
   identifier controls. Preserve permissive query semantics where intentional.
2. Compare broader containment-based association for the four residual overlaps,
   retaining separate observations, nested-anchor ambiguity and rejected readings.
3. Select fresh consumer cases for bounded context/comprehension work under R15/R16.
   These three captures are now development evidence. External target bodies,
   unmarked local paragraph references, qualified USC and vocabulary reuse remain
   separate open work in the [canonical task list](../../plans/2026-09-10-reference-integration-task-list.md).

`design.md`, `fresh-case.json`, `first-layout-review.json`, `baseline.json`,
`prepared.json`, `v2/`, `counterexamples.log` and `upstream-source.log` retain the
comparison. `prepare-v1.py` and `run-v1.py` retain the first implementation;
`prepare.py` and `run.py` produced B2. Production uses the shared native reader
once integrated; experimental captures remain research evidence.
