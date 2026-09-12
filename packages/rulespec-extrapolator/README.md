# Rulespec document understanding

Turn a document into individually referenceable rules, requirements, permissions,
definitions and qualifications, linked to their source passages. Use the drafts
for search, tagging and knowledge discovery; use the same records as a starting
point for reviewing a future workflow or form.

## Extract and use the result

From the repository root, with the local environment installed:

```sh
.tools/document-poc-venv/bin/rulespec-understand extract manual.txt --output my-run
.tools/document-poc-venv/bin/rulespec-understand discovery-export my-run --output discovery.json
.tools/document-poc-venv/bin/rulespec-understand usage my-run
```

Supply `GEMINI_API_KEY` in the environment or add `--env-file /path/to/local.env`
to `extract`. Use a new output directory for each run. Extraction accepts plain
text, prepared document JSON, and supported USLM/eCFR XML; XML needs the
optional verified RefSpec reader. GovInfo annual CFR XML currently needs a
separately prepared text rendition; its native XML structure is not supported.
Separate `prepare` is useful for source metadata
or inspecting text before extraction, but is not required.

The default is `gemini-3.8-flash`, low thinking, temperature 0, 24,000 focus
characters and a 16,384-token generation allowance. Extraction makes one model
request per planned window, with no automatic retries. `discovery-export` and
`usage` make no model calls. Optional overrides are documented in the
[operating reference](OPERATIONS.md#settings-and-advanced-examples).

`my-run/rulebook.json` contains the extracted records. `discovery.json` retains
source passages, including passages without extracted statements, with IDs,
evidence and processing/review status. The run keeps the original text, requests,
responses and refusals for inspection and replay. Usage reports provider-recorded
tokens, not a billing invoice; local JSON copies are not additional output tokens.

## Installation

For a fresh environment, compile the required Core schemas and install the local
packages:

```sh
uv venv --python 3.12 .tools/document-understanding
for source in constraints/core/*.cue; do
  .tools/document-understanding/bin/python tools/constraints_compile.py \
    --in "$source" --target json-schema \
    --out "compiled/json-schema/core/$(basename "$source" .cue).schema.json"
done
uv pip install --python .tools/document-understanding/bin/python \
  -e packages/rulespec-artifacts -e . \
  -e packages/rulespec-projection -e packages/rulespec-extrapolator
uv pip check --python .tools/document-understanding/bin/python
```

Use that environment's `bin/rulespec-understand` for subsequent commands.

## When to go further

- **Inspect or correct:** use `serve`, `review` and `export` with the current run.
- **Locate references or context:** use `references` or `context-export`. These
  deterministic outputs are separate from the normal model request.
- **Investigate possible omissions:** optionally run `audit`. It adds an independent
  source inventory and a comparison, two model requests per audit window.
- **Repair or add structure:** `refine` and `enrich` are optional operations that
  append AI-attributed changes through existing review history.
- **Revisit saved responses:** `replay` verifies the original processing;
  `reprocess` applies current code to a new run while preserving the original.

See the [command table and operating reference](OPERATIONS.md#choose-an-operation)
for inputs, outputs, costs, review effects and examples.

## What the checks establish

Rulespec checks structure, source evidence and recorded processing. It can still
miss a governing condition, attach an exception incorrectly, or overstate a
permission. Keep complete source passages available alongside the draft;
`semantic_completeness=not_established` remains an explicit limit. Human review
can arrive over time for discovery, or before using the records to build an
executable workflow. This package does not generate Formspec/WOS artifacts.

The CUE application profile owns model-facing fields and their generated schemas.
Ordinary extraction keeps one complete statement, kind, modality, nullable actor
assessment and a source-backed term index; additional fields should add information.
See [schema ownership](OPERATIONS.md#schema-ownership-and-reuse) for extension and
build instructions, and [research evidence](EVIDENCE.md) for tested alternatives.

The [current task list](../../thoughts/plans/2026-09-10-reference-integration-task-list.md)
records the bounded next work and remaining defects.
