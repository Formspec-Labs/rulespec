# Document understanding proof of concept

The current runnable workflow is the
[manual-section slice](manual-slice/README.md), implemented in
[`rulespec-extrapolator`](../../packages/rulespec-extrapolator/README.md).
It adds persistent review, raw-response replay, and independent source evaluation.
The scripts and results below remain the historical POC baseline.

Historical: [v2 meaning and shared-scope results](V2-FINDINGS.md). Use `--profile v2`
for authority/threshold distinctions, typed conditions and multiple qualification
targets. `v1` remains the default for compatibility with the original experiment.

This experiment runs LangExtract on Article I, Section 5 of the Constitution,
checks every candidate quotation, and converts grounded candidates into existing
Rulespec Core records. It produces a standalone HTML review and can replay saved
candidates without a model call. It is an experiment, not an adjudication engine
or a complete requirement schema profile.

## Run

From the Rulespec root, create an isolated environment:

```sh
uv venv .tools/document-poc-venv
uv pip install --python .tools/document-poc-venv/bin/python -r examples/document_understanding/requirements.txt -e packages/rulespec-projection
```

The Core JSON schemas must exist under `compiled/json-schema/core/`. If they are
absent, generate only the JSON Schema target from the authoritative CUE sources:

```sh
for name in artifact source-fragment value-assertion relationship-assertion evidence-binding ai-lineage; do
  .tools/document-poc-venv/bin/python tools/constraints_compile.py --in "constraints/core/$name.cue" --target json-schema --out "compiled/json-schema/core/$name.schema.json"
done
```

Use a new output directory for each run. Existing directories are never overwritten.

```sh
# GEMINI_API_KEY comes from the environment, or an explicitly supplied --env-file.
.tools/document-poc-venv/bin/python examples/document_understanding/poc.py extract --model gemini-3.5-flash --output .tools/document-poc-gemini

# Optional local model path; download the model separately with ollama pull.
.tools/document-poc-venv/bin/python examples/document_understanding/poc.py extract --model qwen3:4b --output .tools/document-poc-local

# No provider credentials, server or model needed for replay.
.tools/document-poc-venv/bin/python examples/document_understanding/poc.py replay --input examples/document_understanding/runs/gemini-3.5-flash-03 --output .tools/document-poc-replay

.tools/document-poc-venv/bin/python -m pytest examples/document_understanding/test_poc.py -q
```

## What is implemented

- Original National Archives HTML, selected text, extraction method and source
  digests are retained in `source/`. `manifest.json` identifies the source URL.
  This is a historical transcription; no current-law reconciliation is attempted.
- The entire 1,026-character excerpt fits in one processing window. This does
  **not** test or adopt the recovered SpicyRegs segmenter, PDF extraction, long
  documents, or cross-window assembly.
- LangExtract extracts requirements, permissions, prohibitions, conditions and
  exceptions. Worked prompt examples use invented visitor/board rules, not labels
  from the source document. Later prompt changes informed by observed failures
  make this a development example, not a held-out benchmark.
- Gemini receives a JSON response schema generated from the worked LangExtract
  examples, configured explicitly on its model adapter. It does not receive the
  complete Core schemas. Candidate validation and Core conversion remain separate.
- `poc.py` defines and validates a small experimental candidate shape. Existing
  compiled Core schemas validate `Artifact`, `SourceFragment`, `ValueAssertion`,
  `RelationshipAssertion`, `EvidenceBinding`, and `AILineage`. Nested selectors
  are checked explicitly; unknown emitted Core types cannot be silently skipped.
  Existing SHACL shapes check the resulting JSON-LD graph as well.
- The application supplies identities, hashes, evidence positions and lineage.
  All claims are `aiSuggested`, `statisticalInference`, and `reviewQueueOnly`.
  Prohibitions are affirmed claims about prohibited conduct, not denied assertions.
- `summary` becomes the assertion's literal value; `kind` selects an experimental
  predicate in `urn:rulespec:document-poc:`. These predicates do not establish a
  normative rule profile. `actor` remains unreviewed text on the candidate/review
  card, not a resolved entity assertion. `applies_to` yields a relationship only
  when it identifies exactly one grounded main-rule candidate.
  In v2, each entry in the target list must resolve uniquely, and the relationship
  predicate records scope, prerequisite, trigger or exception rather than a generic
  qualification. Conditions can therefore govern several main statements.
- Quotes use existing `rulespec_projection.evidence` exact matching. LangExtract
  fuzzy/partial alignment is disabled. A missing library interval can still be
  recovered if the quotation appears exactly once. Repeated text requires a valid
  explicit position. Offsets count Unicode codepoints in half-open intervals.
- Missing, altered, invalid and duplicate candidates remain in rejection records.
  Missing or ambiguous relationship targets remain unresolved. No RefSpec matching
  is implemented yet; no sibling product is required to execute the experiment.
- Requests and provider responses are recorded without credentials. Run records
  identify source, prompt, model and relevant hashes. Gemini versions are provider
  managed; their response metadata is retained. Ollama records its model digest.
  Replay recompiles saved candidates; it does not rerun LangExtract's response
  parser. Newer runs check candidate/request/response digests before replay.

## Outputs and limits

Each extraction directory contains the source, instructions, request/response
records, LangExtract annotations, and candidates. Successful conversion adds
`rulebook.json`, `graph.jsonld`, `review.html`, `validation.json`, and the SHACL
report. Early failed conversions are retained; their raw candidates can be
replayed with the corrected converter. Review HTML escapes source and model text.

The HTML supports inspecting each claim's quotation and following qualification
links. It does not yet edit claims or create human attestations. A short quote may
need surrounding context to support the model's full summary or implied actor;
the page shows the complete source for review. Schema validity and exact quotations
do not establish semantic accuracy or completeness.

Tests cover altered/ambiguous evidence, Unicode offsets, source tampering,
relationship target failures, unknown candidate types, provisional AI restrictions,
and HTML escaping. See `FINDINGS.md` for observed model results and review limits.

Provider adapters use small version-specific recording hooks, pinned to LangExtract
1.6.0. This is deliberate experiment code, not a general provider framework.
