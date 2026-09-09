# Rulespec document understanding

Rulespec turns exact document text into individually referenceable statements of
rules, requirements, permissions, definitions and qualifications. It retains the
source, evidence, model responses, rejected suggestions and review history.

Use the resulting drafts for search, tagging, embeddings and knowledge discovery,
with corrections arriving over time. For a form or executable workflow, use the
same records as a source-linked starting point for human review. This package
does not generate Formspec or WOS artifacts or certify complete rule coverage.

This is the current operating guide. Earlier experiment reports preserve the
settings and conclusions of their own runs.

## Current recommendation and evidence

Start with **low-thinking extraction**. Add a **medium-thinking audit** when its
diagnostic feedback is useful. Keep full source passages available to downstream
search alongside the extracted statements. Relationship refinement and structured
concept/value enrichment are optional; ordinary extraction preserves complete
meaning in prose without requiring those extra passes.

The [final full-section run](../../examples/document_understanding/low-extract-medium-audit/README.md)
used a saved 6,919-character leave-eligibility regulation:

- Low extraction produced 19 accepted statements with no rejected candidates.
- Medium inventory and comparison completed, but four inventory entries failed
  exact-evidence checks. The audit correctly reports `review_complete=false`.
- Direct review found the main conditions, alternatives and examples retained,
  plus remaining weaknesses in standalone wording that the audit missed.
- The three calls used 64,117 reported tokens and about 48 seconds of request
  time. This is one measured run, not a typical-document cost estimate.
- Extraction, audit and discovery export replay identically. All 333 package
  tests, six schema-generator tests and native CUE generation checks pass.

The [small medium/high comparison](../../examples/document_understanding/medium-audit-experiment/README.md)
retained detection of two deliberate omissions while reducing token volume by
79%. Its fixture limitation and single samples prevent a general accuracy claim.
The full-section result confirms that a completed model response can still leave
an incomplete review. Neither experiment justifies automatic approval or repair.

## Run the workflow

From the repository root, the existing experimental environment exposes
`.tools/document-poc-venv/bin/rulespec-understand`. With its `bin` directory on
`PATH`, run:

```sh
rulespec-understand prepare manual.txt --title "Manual section" \
  --source-url https://example.org/manual --output prepared.json

rulespec-understand extract prepared.json --model gemini-3.8-flash \
  --thinking-level low --temperature 0 --max-chars 24000 \
  --max-output-tokens provider --env-file /path/to/local.env --output my-run

# Optional: inventory the source before comparing it with the extracted draft.
rulespec-understand audit my-run/rulebook.json --model gemini-3.8-flash \
  --thinking-level medium --max-chars 24000 --max-output-tokens provider \
  --env-file /path/to/local.env --output my-audit

# Retain source passages and links, including passages without an extracted rule.
rulespec-understand discovery-export my-run --output discovery.json

# Reproduce the saved processing without provider calls.
rulespec-understand replay my-run --output my-replay
rulespec-understand audit-replay my-audit --output my-audit-replay
```

Supply `GEMINI_API_KEY` through the environment or the explicitly selected env
file. Each new run needs a new output directory. The commands above select the
evaluated settings explicitly; library defaults remain unchanged:

| Setting | Extraction default | Audit default | Recipe above |
|---|---|---|---|
| Focus characters | 24,000 | 3,000 | 24,000 for both |
| Generation allowance | 16,384 tokens | 32,768 tokens | provider limit |
| Thinking level | provider default | provider default | low / medium |
| Temperature | 0 | 0 | 0 |

`--max-output-tokens provider` omits the application's cap; provider limits still
apply. `--thinking-level` accepts low, medium or high and sends no numeric
`thinking_budget`. Requests allow up to five minutes, with no automatic retries.
Settings and actual SDK requests are recorded and checked during replay. Fresh
calls can differ even at temperature zero.

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
```

Use that environment's `bin/rulespec-understand` for subsequent commands.

## What goes in, what happens, what comes out

**Input:** UTF-8 text or prepared JSON with exact text, its SHA-256 digest and
named section coordinates. Newlines remain intact; offsets count Unicode
codepoints in half-open intervals, `text[start:end]`. Optional source maps
identify inserted separators. Preparation does not discover a manual's section
hierarchy. PDF, OCR and layout extraction are outside this package.

**Processing:** the application indexes paragraphs and list items, plans bounded
windows, and supplies parent/neighbor context. Fitting list groups stay together;
larger groups can split. Structural parents are clues, not proven governing
conditions. The model emits complete statements, scope, modal force, choices and
source references using the CUE-generated schema. LangExtract supplies its Gemini
adapter; Rulespec supplies evidence resolution, validation, identities and Core
records.

`unit` selects a focus passage such as `F003` or a contiguous range such as
`F003:F009`. Supporting fields can also select context passages (`C000`). The
application resolves those selections to exact original text. `logic_quote`
becomes verbatim `logic_text`; model `statement` becomes candidate `summary`.
One passage can support several meanings or alternatives. Every option and
qualification must still survive in the explicit meaning; a quotation alone is
not proof of semantic completeness.

Invalid main references refuse a row. Invalid supporting references withhold the
component and preserve the statement, raw suggestion and field-specific refusal.
Schema and kind/modality contradictions can reject candidates. The application
does not silently guess replacements. Optional component uncertainty can remain
on accepted records.

**Output:** `rulebook.json`, a Core JSON-LD graph, exact source, requests,
responses, candidates, refusals, validation results and frozen runtime inputs.
The discovery export retains every source paragraph/list item, linked statements,
exact evidence and review/processing status. It makes no model calls and creates
no embeddings or inferred legal relationships.

**Audit:** a separate source-first inventory, followed by a draft comparison,
produces raw judgments, a detailed report and existing Core `Finding` records in
`findings.jsonld`. It does not modify the draft. Inventories and judgments remain
fallible observations; missing or invalid inventory entries limit what was checked.

## How to interpret the checks

| Result | What it establishes |
|---|---|
| Accepted candidate | Passed compiler checks; meaning may still be wrong |
| Exact evidence | The cited text exists at the saved offsets |
| Schema / SHACL validation | Records and graph satisfy structural constraints |
| Processing complete | Planned work reached its recorded terminal outcome |
| Review complete | Audit judgments passed its accounting and consistency checks |
| Covered inventory units | The checker assessed those accepted units as covered |
| Identical replay | Saved responses reproduce the same processing results |

None establishes that every source meaning was discovered. Read `audit_issues`
and `review_complete` before interpreting coverage counts: the final example
marks 20 accepted units covered while four substantive inventory entries were
refused. It is not 100% source coverage. No check emits a `ClosureClaim`.

## Review, refinement and changed runtimes

```sh
rulespec-understand serve my-run --audit my-audit
rulespec-understand review my-run --action correction.json
rulespec-understand export my-run --output reviewed-rulebook.json
rulespec-understand evaluate reviewed-rulebook.json --labels expected.json \
  --judgments judgments.json --output evaluation.json

# Explicitly apply the installed parser/compiler to saved responses.
rulespec-understand reprocess my-run --output my-reprocessed-run

# Optional model-proposed recovery and qualification links, with source checks.
rulespec-understand refine my-run --output my-refinement \
  --env-file /path/to/local.env
rulespec-understand refine-replay my-refinement --output my-refinement-replay
```

Review supports add, edit, split, merge, reject and approve, recording the reviewer,
reason and expected revision. SQLite preserves review history. Approval records
an assessment; assertions remain `reviewQueueOnly`. See the
[review action examples](../../examples/document_understanding/manual-slice/review-demo/README.md).

Export the current review state before auditing corrections. Refinement appends
AI-attributed review events only after local checks and a separate model challenge;
it preserves refused proposals. It performs bounded recovery, qualification-link
and final-audit passes, with at most 60 current claims and eight proposals per
focus group. `--audit` can reuse an assessment only when it matches the current
snapshot. This optional path was not part of the final low/medium run.

Strict replay checks saved artifacts and runtime fingerprints and refuses drift.
Reprocessing preserves the original capture and records the changed processing;
it supports the current response format, not retired formats. Recorded compiler
failures can be reprocessed when both run and validation metadata identify the
failure. Missing outputs from a nominally successful run remain an integrity error.
Old experiments retain their own frozen runtime; do not rewrite their manifests
to make an older capture pass under newer code.

## Schema ownership and reuse

The [CUE application profile](src/rulespec_extrapolator/schema_data/document-understanding.cue)
owns interpretation fields, descriptions, titles and field order. Native CUE
produces three views of shared definitions: `provider.schema.json` for normal
extraction, `meaning.schema.json` for complete defaults/refinement and audit field
guidance, and `candidate.schema.json` for local validation. Python does not
maintain a competing copy of those field definitions.

The profile imports existing Core attribution, assignment-role, datatype and
period definitions. The application reuses Core assertions, evidence bindings,
`ApplicabilityScope`, provenance, review records and `Finding`; shared evidence
and release-digest helpers come from Rulespec packages. Fix shared definitions
upstream when needed. The [schema usage assessment](../../thoughts/reviews/2026-09-07-document-understanding-schema-usage.md)
records connected and unused capabilities.

Full meaning records support optional concepts, source claimants, typed values
and effective periods. They create existing Core records only when their source
and value checks pass. Local concepts have document-local identities and do not
claim RefSpec registration. Date-only effectivity does not invent a timezone;
relative deadlines are not periods in force. These richer collections are not
requested by the normal meaning-first pass.

Rulespec requires no DocSpec or SpicyRegs service or release. RefSpec is the only
optional platform integration. `vocabulary` accepts a normalized versioned
snapshot containing `source: RefSpec`, `release_id`, and `concepts` with `id`,
`label` and `aliases`. It matches actor/object labels, records ambiguity and pins
digests; it does not fetch/authenticate a RefSpec release or assert equivalence.
The normal extraction pass leaves actor/object components empty, so vocabulary
matching needs enriched or reviewed components.

```sh
python tools/build_extraction_schemas.py
python tools/build_extraction_schemas.py --check
.tools/document-poc-venv/bin/python -m pytest \
  packages/rulespec-extrapolator/tests tools/test_extraction_schemas.py -q
```

Generation needs Go 1.25 or newer. Installed extraction/replay load packaged JSON
and need neither Go nor CUE. Hashes bind sources, generated files and each run.

## Remaining work and research evidence

The next narrow priorities are reliable audit inventory evidence and faithful
standalone scope. In the final run, bare section markers caused four inventory
refusals, while the checker missed exceptions absent from a statement's summary
and scope but retained in `logic_text`. Do not discard that retained meaning or
claim the short statement is independently complete. Recommendations, descriptive
possibility, non-prohibition and explicit permission still need careful assessment.

Explicit exception targets belong to optional refinement and remain imperfect.
There is no general duplicate detector, complete entity model, automatic
cross-document concept resolution or executable rule engine. Human accuracy,
correction effort and time savings have not been measured. Source reviews are
agent-authored and revisable; saved legal excerpts are not current legal guidance.

| Evidence | What it explains |
|---|---|
| [Final low → medium run](../../examples/document_understanding/low-extract-medium-audit/README.md) | Current end-to-end result, raw review and unresolved issues |
| [Medium audit comparison](../../examples/document_understanding/medium-audit-experiment/README.md) | Thinking-level savings on three isolated cases |
| [Alternative evidence](../../examples/document_understanding/alternative-evidence-experiment/README.md) | Shared passages, omitted options and signature qualifications |
| [Meaning-first adoption](../../examples/document_understanding/meaning-first-adoption/README.md) | Normal extraction and discovery export |
| [Low extraction](../../examples/document_understanding/low-thinking-experiment/README.md) | Four low-thinking runs and quality variation |
| [Context and budget](../../examples/document_understanding/context-budget-experiment/README.md) | Window/list handling and remaining omissions |
| [Schema reuse](../../examples/document_understanding/schema-reuse-finish/README.md) | Core reuse and evidence-backed structured components |
| [Passport example](../../examples/document_understanding/manual-slice/README.md) | Earlier saved manual extraction and review interface |

Historical reports retain the recommendations and limitations measured at their
own snapshots. Use this guide and the final run for the current handoff.
