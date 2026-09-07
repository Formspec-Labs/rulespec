# Reusable segmentation and extraction for Rulespec

Date: 2026-09-06. Status: source research and proposed evaluation, not a runtime benchmark.

## Decision

Evaluate LangExtract first for typed, evidence-linked extraction. Use existing
Rulespec exact-quote verification. Add Docling only when the source format needs
layout parsing; add semchunk only when source sections exceed processing budgets.
Recover selected local algorithms if their coverage and source-slice handling
prove valuable. Do not restore the old pipeline wholesale.

Rulespec owns the complete workflow. RefSpec supplies vocabulary. DocSpec and
SpicyRegs are sources of potentially adaptable code, not runtime prerequisites.
Docling is an unrelated open-source document library.

Three parallel research agents inspected local implementations, external semantic
tools, and external document-structure tools. Root additionally inspected Docling
Graph. No packages were installed, models invoked, or extraction accuracy measured.
Local tests were inspected but not rerun. This is a targeted survey, not an
exhaustive search of every repository or tool.

## Separate three jobs

1. Source structure: recover headings, paragraphs, lists, tables, and page locations.
2. Processing windows: fit source passages into a model budget without losing text.
3. Semantic extraction: identify requirements, actors, definitions, conditions,
   exceptions, and relationships, with exact evidence for each claim.

Most products called semantic chunkers perform job 2 using topic similarity.
They do not establish that an exception modifies a particular requirement.
Semantic units can overlap and need evidence from several nonadjacent passages.

## External candidates

| Candidate | Useful capability | Limits and disposition |
| --- | --- | --- |
| [LangExtract](https://github.com/google/langextract) (Apache-2.0) | User-defined extraction classes and attributes, source-span alignment, long-document processing, multiple passes, JSONL output and HTML highlighting; Gemini, OpenAI and local Ollama support. | First extraction experiment. Rulespec must define examples, semantic types, relationships and validation. No demonstrated complete passport-rule workflow. |
| [semchunk](https://github.com/isaacus-dev/semchunk) (MIT) | Local token-budget splitting with overlap and source offsets; documents `chunks[i] == text[start:end]`. | Small processing-window baseline. Default separator-based mode needs no model service. Optional Isaacus AI mode is a separate dependency and unnecessary initially. |
| [Docling](https://github.com/docling-project/docling) (MIT code; models have separate licenses) | PDF/Office/HTML parsing, headings, lists, tables, reading order and available page geometry; hierarchical and token-aware chunking. | First parser candidate for PDF. Preserve native document JSON and original file, not just Markdown. Parser/model provisioning adds cost. |
| [Unstructured](https://github.com/Unstructured-IO/unstructured) (Apache-2.0) | Local document partitioning into titles, narrative text, list items and tables; section-aware chunking. | Parser alternative if Docling fails on chosen input. Preserve original elements and their metadata. |
| [Chonkie](https://github.com/feyninc/chonkie) (MIT) | Recursive, sentence, embedding-semantic and model-based chunkers with offsets. | Compare only if basic windows lose relevant context. Topic grouping does not discover rule semantics. |
| [LlamaIndex semantic splitter](https://github.com/run-llama/llama_index/blob/main/llama-index-core/llama_index/core/node_parser/text/semantic_splitter.py) (MIT) | Sentence grouping by embedding dissimilarity. | No clear need for its framework here; default embedding setup uses OpenAI unless supplied another implementation. |
| [Dense X propositionizer](https://huggingface.co/chentong00/propositionizer-wiki-flan-t5-large) (Apache-2.0) | Local 0.8B FlanT5 model produces atomic proposition strings from a title, section and passage. | Research comparator: Wikipedia-oriented, rewrites text, no evidence offsets or explicit exception relationships. |
| [Docling Graph](https://github.com/docling-project/docling-graph) (MIT) | Extracts Pydantic objects and builds relationship graphs; local/API model options, provenance and visualization. | Worth comparing if direct relationship extraction is the bottleneck. Its graph and schema machinery overlap Rulespec; evaluate as a producer, not a replacement schema system. |

### Grounding details that affect the choice

- LangExtract's [resolver](https://raw.githubusercontent.com/google/langextract/main/langextract/resolver.py)
  enables fuzzy and partial alignment by default. Its
  [data model](https://raw.githubusercontent.com/google/langextract/main/langextract/core/data.py)
  permits missing intervals and records alignment status. Disable fuzzy/partial
  acceptance and independently check the quote against preserved source text.
  An extraction interval alone does not prove exact evidence or correct meaning.
  Multiple evidence spans need Rulespec grouping.
- Docling [chunking](https://docling-project.github.io/docling/concepts/chunking/)
  can add heading context and repeat table headers. Chunk text therefore is not
  automatically a contiguous verbatim source range. Retain document-item references,
  original/sanitized text distinctions, and available page/bounding-box provenance.
- Unstructured [chunking](https://docs.unstructured.io/open-source/core-functionality/chunking)
  can consolidate elements from multiple locations. Keep `metadata.orig_elements`
  so consolidation does not erase source locations.
- Chonkie's [semantic chunker](https://docs.chonkie.ai/oss/chunkers/semantic-chunker)
  supports nonconsecutive merging. Avoid that initially and verify exact alignment.
  Its [Slumber implementation](https://raw.githubusercontent.com/feyninc/chonkie/main/src/chonkie/chunker/slumber.py)
  asks for topic-change split points, not requirements.
- Docling Graph's [provenance API](https://docling-project.github.io/docling-graph/reference/provenance/)
  distinguishes document/chunk/span precision. Spans refer to enriched chunk text;
  the locator searches identifiers or other distinctive strings. Locating a name
  does not prove the full relationship or requirement. Rulespec still needs
  claim-level evidence and mapping to its preserved source representation.

The external agents checked current repository/release information. No accuracy
or performance advantage is established by activity, stars, or project claims.
Pin exact versions before an experiment rather than depending on moving `main`.

## Local candidates and recovery evidence

### Existing Rulespec evidence verifier: reuse directly

`packages/rulespec-projection/src/rulespec_projection/evidence.py:44`
defines `resolve_exact_evidence_offsets()`. It verifies supplied offsets or finds
a unique exact occurrence, and refuses absent or ambiguous quotes. It uses Unicode
codepoint offsets and standard-library dependencies. It verifies spans; it does
not discover them. Related fragment verification lives in `projection.py:225`.

### Current DocSpec bounded segmenter: adapt selectively

`/Users/mikewolfd/Work/DocSpec/src/docspec/processing/bounded_segmentation.py:982`
defines `BoundedSegmenter.segment_text()`. It accepts UTF-8 bytes, preserves
under-budget blocks, splits oversized blocks with bounded overlap, retains heading
context, and checks coverage. Focused tests are in
`/Users/mikewolfd/Work/DocSpec/tests/test_bounded_segmentation.py`.

This identifies blank-line blocks and Markdown headings, not semantic rules.
It imports DocSpec helpers, so adapt small mechanics rather than importing DocSpec.
Two important changes would be required: it uses byte offsets while Rulespec uses
codepoints, and it deliberately excludes headings from evidence spans (lines
61–73). Headings can contain operative scope, so Rulespec must allow their evidence.

### Historical SpicyRegs implementation: recoverable, not current checkout code

The Git object exists locally at
`fc24e06ade915ead1209483733b1aec5cd824d1c` in
`/Users/mikewolfd/Work/spicy-regs`. DocSpec's source header documents its adoption.

```sh
git -C /Users/mikewolfd/Work/spicy-regs show fc24e06ade915ead1209483733b1aec5cd824d1c:src/spicy_regs/docpipeline/segments.py
```

At that commit:

- `src/spicy_regs/docpipeline/segments.py:255–418` defines source slices and
  processing segments; `:769–871` builds bounded windows; `:983–1015` checks
  evidence containment/overlap. Supports groups of exact source-field slices,
  Unicode character offsets, neighboring/parent identities and coverage.
- `src/spicy_regs/docpipeline/source.py:844`, `:893`, `:1153`, `:1381`, `:1425`
  implement markup/prose boundaries, structural spans, regions and fragments.
  Useful HTML/XML source-location machinery; the large module carries old
  runtime/source-profile/storage dependencies.
- `src/spicy_regs/docpipeline/extraction.py` contains a structured extraction task
  interface, provider execution, stored requests/responses, rejection handling and
  provider-free rebuilding. Reuse the relevant design or small parts after comparing
  LangExtract; do not restore its entire run/storage system.
- `src/spicy_regs/docpipeline/relation_task.py:105`, `:489`, `:680` handle prompts,
  model schema and semantic checks for polarity, attribution, conditionality,
  temporal scope and competing interpretations. Input supplies a target relation
  and requires one supporting span. It is not open-ended rule discovery.
- Historical tests include `tests/test_docpipeline_segments.py`,
  `tests/test_docpipeline_segments_migration.py`,
  `tests/test_docpipeline_segments_review_fixes.py`, and
  `tests/test_docpipeline_segments_frozen_local.py`. They were not rerun here.

Local searches covered relevant paths in Rulespec, DocSpec, SpicyRegs, SpicyDocs,
RefSpec, RapidATO and PKAF. No actual passport/adjudication example was found in
the candidate paths inspected. Do not infer that none exists elsewhere.

## Proposed first experiment

Use one real chapter or short representative excerpt with independently marked
requirements, definitions, conditions and exceptions. Include a requirement in a
heading, a table, repeated identical wording, Unicode, and an exception across a
section/window boundary. Keep some labels held out from extraction examples.

1. Preserve source bytes, text representation and structure. Use native text/HTML
   if available; evaluate Docling if the actual input is PDF.
2. Give LangExtract a small Rulespec-owned candidate schema and worked examples.
   Try its existing long-document handling before introducing another chunker.
3. Save raw outputs and reject or flag spans that fail Rulespec exact replay.
   Preserve unresolved candidates for review rather than silently losing them.
4. Assemble verified candidates into Rulespec assertions and evidence, including
   condition/exception relationships. Align terms through RefSpec afterward.
5. Compare against labeled source: missed rules, unsupported claims, incorrect
   condition/exception attachment, quote failures, duplicate candidates, cost and
   review effort. Check schema conformance separately from meaning and coverage.

If windows are the problem, compare semchunk with recovered local structure-aware
mechanics. If extraction is the problem, compare prompts/models or Docling Graph.
Do not evaluate all libraries at once. Acceptance requires exact replay of every
accepted quote and explicit accounting for unresolved/unsupported candidates;
semantic accuracy targets should be set against the chosen labeled source.

This experiment answers the immediate decision: can an existing extractor produce
useful Rulespec candidates reliably enough that we only build the domain semantics,
evidence enforcement, and review loop?
