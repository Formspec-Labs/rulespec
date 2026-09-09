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
concept/value enrichment are optional. Ordinary extraction represents meaning in
prose, but can still omit qualifications. Keep complete statements and their source
passages available together. When populated, `logic_text` retains verbatim wording
for inspection; it does not replace qualifications missing from a statement.

Normal extraction now requires one complete `statement`, `kind` and `modality`.
Optional enrichment may be omitted or null; it should add useful structure.
Audit requests omit empty fields and reuse passage references for exact repeated
quotations. The [sparse-meaning check](../../examples/document_understanding/sparse-meaning-check/README.md)
measured 57–79% fewer audit input tokens while retaining four planted-error
detections. The known qualification miss remains, and two additional modality
flags leave the broader quality comparison unresolved.

Dedicated logic and modality explanations remain experimental. The
[fresh-source comparison](../../examples/document_understanding/fresh-explanation-check/README.md)
found no dependable accuracy gain across three previously unused regulatory
sections. Keep the current optional, nullable enrichment fields; the stricter
omission-only variants were experimental controls and are not the default. Preserve
these evaluation sources without tuning prompts against their observed failures.

The [earlier full-section run](../../examples/document_understanding/low-extract-medium-audit/README.md)
used a saved 6,919-character leave-eligibility regulation before the inventory
evidence change below:

- Low extraction produced 19 accepted statements with no rejected candidates.
- Medium inventory and comparison completed, but four inventory entries failed
  exact-evidence checks. The audit correctly reports `review_complete=false`.
- Direct review found the main conditions, alternatives and examples retained,
  plus remaining weaknesses in standalone wording that the audit missed.
- The three calls used 64,117 reported tokens and about 48 seconds of request
  time. This is one measured run, not a typical-document cost estimate.
- Extraction, audit and discovery export replay identically. At that historical
  snapshot, all 333 package tests, six schema-generator tests and native CUE
  generation checks passed.

The [small medium/high comparison](../../examples/document_understanding/medium-audit-experiment/README.md)
retained detection of two deliberate omissions while reducing token volume by
79%. Its fixture limitation and single samples prevent a general accuracy claim.
The full-section result confirms that a completed model response can still leave
an incomplete review. Neither experiment justifies automatic approval or repair.

The profile now also tells the model to preserve the governing conditions of an
example when extracting it as a separate unit, while respecting explicit scope
changes. The audit reads this guidance from the same generated CUE description.
[Paired inventory experiments](../../examples/document_understanding/example-inheritance-experiment/README.md)
and [new synthetic cases](../../examples/document_understanding/example-inheritance-transfer-experiment/README.md)
support the wording. The passage-ID inventory is now integrated: a
[fresh full-section comparison](../../examples/document_understanding/full-inventory-evidence-comparison/README.md)
produced six evidence refusals among 22 quotation-based observations and none
among 20 passage-ID observations. Both retained the teacher example's governing
condition, while semantic defects remained in both. This is one development
sample per arm, not a general accuracy estimate.

The integrated request exactly matches that successful passage-ID request, and
the parser reproduced all 20 saved inventory records unchanged. At that
integration snapshot, all 347 package and generator tests and native CUE drift
checks passed. Subsequent [passport and waste full workflows](../../examples/document_understanding/passage-id-transfer/README.md)
measured extraction, inventory and comparison on two additional sources; their
processing success does not establish semantic completeness.

The [subsequent small-improvement check](../../examples/document_understanding/minor-audit-improvements/README.md)
adds `logic_text` to discovery exports. Extra classification guidance and unit
judgment ordering remain experimental: the former showed a scope regression,
and the latter improved none of the primary verdict checks. A fresh notice section
produced 18 accepted statements and no inventory refusals, but comparison rejected
three claim/unit pairs for inexact copied quotations. Review remained incomplete.
A [whitespace-only fallback experiment](../../examples/document_understanding/whitespace-evidence-experiment/README.md)
recovers those pairs, but accepts two constructed table/list joins against the
declared expectations. It remains experimental; comparison matching was exact
at that checkpoint. A [known-library comparison](../../examples/document_understanding/library-fuzzy-evidence-experiment/README.md)
then found that installed LangExtract can recover all six judgments through its
token-exact alignment, even with fuzzy matching disabled. That path still selects
ambiguous and layout-sensitive spans in the constructed controls; it remains
experimental. Configurable character-edit matching showed broader content-change
acceptances, and one fuzzysearch setting varied its selected repeated-text location.

The [passage-ID integration](../../examples/document_understanding/passage-id-integration/README.md)
now uses that existing source-reference path in comparison as a narrowly scoped
citation-reliability improvement. It reproduces both saved ID runs, preserving all
36 judgments per run. The broader semantic-quality gate remains unmet.

The [explicit-contradiction check](../../examples/document_understanding/audit-mutation-sensitivity/README.md)
caught four planted changes to actors, exemptions, alternatives and deadlines,
and accepted their four original counterparts. It also preserved the named nearby
correct rules. These selected development cases support audit as review triage;
they do not establish a general detection rate. One rationale incorrectly called
an either/or choice “mutually exclusive,” so explanations also need scrutiny.

Stronger statement instructions and diagnostic passage joining did not repair the
standalone notice statement. The [maintained case index](../../examples/document_understanding/evaluation-cases.md)
keeps desired field behavior separate from observed successes and misses, with
source hashes and original captures. The [quality decision](../../thoughts/reviews/2026-09-09-extraction-quality-decision.md)
explains why these results support retaining the current extraction semantics.
For discovery, users can correct source-backed drafts over time. Before deriving
an executable workflow, review governing conditions and exceptions against the
source; a passed model audit does not certify complete rules.

The [default-configuration check](../../examples/document_understanding/production-defaults-check/README.md)
verified the promoted thinking defaults through three live calls and identical
offline replays. All 371 package/schema-generator tests and native CUE drift checks
passed. The live extraction remained partial because one component quote was
withheld; the audit still missed the known standalone qualification risk.

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
file. Each new run needs a new output directory. CLI and library calls default to
low extraction and medium audit. This promotes the operating recommendation; the
recent experiments did not compare these levels against the provider's implicit
default. The recipe above also explicitly increases the audit window and removes
application output caps, which remain separate from the thinking defaults:

| Setting | Extraction default | Audit default | Recipe above |
|---|---|---|---|
| Focus characters | 24,000 | 3,000 | 24,000 for both |
| Generation allowance | 16,384 tokens | 32,768 tokens | provider limit |
| Thinking level | low | medium | low / medium |
| Temperature | 0 | 0 | 0 |

`--max-output-tokens provider` omits the application's cap; provider limits still
apply. `--thinking-level` accepts low, medium or high and sends no numeric
`thinking_budget`. Python callers can explicitly pass `thinking_level=None` to
use the provider default. Saved requests retain their recorded setting during
replay and reprocessing. Requests allow up to five minutes, with no automatic retries.
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
conditions. The model emits complete statements, kind, modal force and source
references using the CUE-generated schema. Scope, choice and other enrichment are
optional. LangExtract supplies its Gemini
adapter; Rulespec supplies evidence resolution, validation, identities and Core
records.

`unit` selects a focus passage such as `F003` or a contiguous range such as
`F003:F009`. Supporting fields can also select context passages (`C000`). The
application resolves those selections to exact original text. `logic_quote`
becomes verbatim `logic_text`; model `statement` becomes candidate `summary`.
One passage can support several meanings or alternatives. Every option and
qualification must still survive in the explicit meaning; a quotation alone is
not proof of semantic completeness.

Omitted or null model enrichment becomes an empty string/list in the existing Core
record shape; the raw capture preserves what the model actually emitted. Separate
scope, choice or logic fields are not required to repeat a complete statement.
Audit input omits empty fields and replaces exact catalog quotations with passage
references while preserving every populated meaning field and its role. Saved
evidence, review history and source text remain complete.

Invalid main references refuse a row. Invalid supporting references withhold the
component and preserve the statement, raw suggestion and field-specific refusal.
Schema and kind/modality contradictions can reject candidates. The application
does not silently guess replacements. Optional component uncertainty can remain
on accepted records.

**Output:** `rulebook.json`, a Core JSON-LD graph, exact source, requests,
responses, candidates, refusals, validation results and frozen runtime inputs.
The discovery export retains every source paragraph/list item, linked statements,
exact evidence and review/processing status. Statement records also retain existing
`logic_text`, so detailed wording survives alongside the shorter statement. It
makes no model calls and creates
no embeddings or inferred legal relationships.

**Audit:** a separate source-first inventory selects focus passage IDs for each
observation and focus/context IDs for its scope. The existing resolver turns these
into exact source text and offsets; invalid selections refuse the observation.
A subsequent draft comparison selects `source_refs` using the same CUE-generated
passage references and resolver. Full selected source passages and governing
context are retained with exact offsets. Invalid or unavailable selections are
refused; a valid ID alone does not prove relevance. Comparison produces raw judgments, a detailed report and existing Core `Finding` records in
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
Audit version 4 uses passage IDs in inventory and comparison. Earlier captures
require their frozen historical runtime. Old experiments retain that runtime; do not rewrite their manifests
to make an older capture pass under newer code.

## Schema ownership and reuse

The [CUE application profile](src/rulespec_extrapolator/schema_data/document-understanding.cue)
owns interpretation fields, descriptions, titles and field order. Native CUE
produces four views of shared definitions: `provider.schema.json` for normal
extraction, `meaning.schema.json` for complete defaults/refinement and audit field
guidance, `candidate.schema.json` for local validation, and `inventory.schema.json`
for audit evidence selection and observations. Python does not
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

The example-inheritance wording and passage-ID inventory are integrated through
CUE and the existing resolver. The
[deterministic check](../../examples/document_understanding/refused-evidence-check/README.md)
resolves the original four refusals with reviewed source selections, leaving
meanings unchanged. The fresh comparison above supports this evidence-selection
change; neither check proves those meanings complete. Remaining priorities are:

1. Preserve applicability when separating dependent details such as deadlines.
   The [grouping comparison](../../examples/document_understanding/deadline-grouping-experiment/README.md)
   produced one complete grouped result, but followed the grouping instruction
   in only one of two same-scope runs. Existing fields can express the result;
   the instruction is not adopted. Further work should check segmentation
   adherence separately from semantic completeness.
2. Preserve standalone qualifications and assess each meaning field separately.
   The completed [field-distinction test](../../examples/document_understanding/audit-field-distinction/README.md)
   compared original wording, complete logic only, and a complete statement. The
   auditor missed the original defect twice despite citing its governing source;
   neither logic-only run met the strong field-distinction criterion. Complete
   statements passed both times. This remains a known failure, not a pending test.
3. Check modal classification and duty bearers. Existing fields distinguish
   recommendation, permission, exemption and descriptive possibility, but the
   prototype mislabeled an exemption as permission and a later output used
   ambiguous exemption-actor wording.

Do not discard meaning retained in `logic_text` or claim that an incomplete short
statement is independently complete. These remaining failures do not negate the
narrow improvements measured in the example experiments.

Explicit exception targets belong to optional refinement and remain imperfect.
There is no general duplicate detector, complete entity model, automatic
cross-document concept resolution or executable rule engine. Human accuracy,
correction effort and time savings have not been measured. Source reviews are
agent-authored and revisable; saved legal excerpts are not current legal guidance.

| Evidence | What it explains |
|---|---|
| [Final low → medium run](../../examples/document_understanding/low-extract-medium-audit/README.md) | Earlier end-to-end result, raw review and unresolved issues |
| [Medium audit comparison](../../examples/document_understanding/medium-audit-experiment/README.md) | Thinking-level savings on three isolated cases |
| [Alternative evidence](../../examples/document_understanding/alternative-evidence-experiment/README.md) | Shared passages, omitted options and signature qualifications |
| [Meaning-first adoption](../../examples/document_understanding/meaning-first-adoption/README.md) | Normal extraction and discovery export |
| [Low extraction](../../examples/document_understanding/low-thinking-experiment/README.md) | Four low-thinking runs and quality variation |
| [Context and budget](../../examples/document_understanding/context-budget-experiment/README.md) | Window/list handling and remaining omissions |
| [Schema reuse](../../examples/document_understanding/schema-reuse-finish/README.md) | Core reuse and evidence-backed structured components |
| [Passport example](../../examples/document_understanding/manual-slice/README.md) | Earlier saved manual extraction and review interface |

Historical reports retain the recommendations and limitations measured at their
own snapshots. Use this guide and the
[current handoff](../../thoughts/reviews/2026-09-09-extraction-handoff.md) for the
integrated state.
