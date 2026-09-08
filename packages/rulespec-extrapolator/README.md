# Rulespec document understanding

This experimental application turns exact document text into individually
referenceable rules, requirements, permissions, definitions, conditions, and
exceptions. It preserves the source, model responses, uncertainties, corrections,
and review decisions. The local workflow produces useful drafts for discovery
and a source-linked starting point for reviewed workflows or forms. Automatic
extraction and automatic checks remain fallible; review can happen upfront or
through later user feedback.

Start with the [recorded passport-manual example](../../examples/document_understanding/manual-slice/README.md).
It includes five Gemini 3.8 Flash runs, offline replay, independent agent review,
and a small persistent review interface. No model credentials are needed to
inspect the saved results.

The [quality iteration](../../examples/document_understanding/quality-iteration/README.md)
adds explicit modal force, inherited scope, alternatives and source-first gap
checks, with saved before/after cases and their remaining failures.

The [refinement experiment](../../examples/document_understanding/refinement-iteration/README.md)
adds bounded recovery and relationship passes. It records proposed corrections,
separate source checks, applied review events and a final audit.

Extraction and refinement now share the richer schema guidance tested in the
[schema experiment](../../examples/document_understanding/schema-order-experiment/README.md).
It explains inherited conditions, complete alternatives, modal force, and the
evidence needed to assign an actor or object. That experiment preserved its output
order; the current profile also adds concepts, attribution, typed values and
effectivity. Historical [adoption checks](../../examples/document_understanding/schema-guidance-adoption/README.md)
record the exact schema comparison and saved-output compatibility.

## Use the local example

From the repository root, the environment used for the recorded experiment is:

```sh
.tools/document-poc-venv/bin/rulespec-understand serve \
  examples/document_understanding/manual-slice/reprocessed/section-01
```

Open the printed localhost address. The browser shows exact source passages,
candidate meanings, component evidence, qualification links, and unresolved work.
It supports Add rule, Edit, Split, Merge, Reject, and Approve. Every action records
an explicit reviewer and reason. SQLite preserves the event history on reopening.
Review approval records an assessment; assertions remain `reviewQueueOnly`.

For a fresh environment, compile only the required Core JSON Schemas, then
install the application and its shared Rulespec packages:

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

Use `.tools/document-understanding/bin/rulespec-understand` with that environment.
Model, parser, dependency, and schema versions are recorded for each run. Strict
replay refuses a run when those versions differ. Explicit reprocessing applies
the installed code to saved responses in the current format; it does not migrate
retired formats.

Reprocessing also recovers source and model responses saved before a compiler
failure. The saved run and validation record must both identify that failure;
missing outputs from a nominally successful run remain an integrity error.

## Core workflow

**Input:** UTF-8 text, or a prepared JSON document with exact text, its SHA-256
digest, and named section coordinates. Text loading preserves original newlines.
Offsets count Unicode codepoints in half-open intervals: `text[start:end]`.
Optional source maps distinguish copied source passages from inserted separators.
PDF, OCR, and layout extraction are outside this first slice.

**Processing:** Rulespec partitions the text into recorded windows and supplies
bounded context from paragraph/list parents and neighboring passages. The
explicit Gemini JSON Schema retains meaning, scope, alternatives and evidence;
LangExtract supplies its native schema adapter and provider. Invented semantic
examples guide interpretation. Rulespec parses each response, checks exact evidence, resolves
available section and qualification references, and converts candidates into
existing Core records. It supplies identities and provenance itself.

The [CUE application profile](src/rulespec_extrapolator/schema_data/document-understanding.cue)
owns shared field types, classifications, rich descriptions, titles, and model
field order. Native CUE generates the candidate and model schemas that ship with
the Python package. Local candidates add stricter evidence checks; model output
allows empty placeholders for unstated information. Extraction and refinement
use that same generated model schema. The profile imports Core attribution,
assignment-role, datatype and period definitions directly. The build stages the
Core sources as a native CUE import and fingerprints them. Existing Core record
generation stays on its current build path.

To change the application schema, edit that CUE source, then run
`python tools/build_extraction_schemas.py` from the repository root.
`python tools/build_extraction_schemas.py --check` detects generated-file drift.
Generation needs Go 1.25 or newer; installed extraction and replay use packaged
JSON and need neither Go nor CUE. The loader checks source/output hashes, and
each run freezes the schema inputs and build manifest. See the
[native generation checks](../../examples/document_understanding/native-extraction-schema/README.md).

The parser accepts the CUE-defined `unit` / `unit_attributes` format and requires
all model fields, including explicit empty values for unstated meaning. Field
lists come from the generated schema. Retired per-kind responses, context-free
windows, JSON prompt examples, and reduced review checks are unsupported.
Local candidate input may omit unstated components; compilation records them
as empty or uncertain and always creates the complete meaning assertion.

Use existing Core schemas for assertions, evidence, applicability and provenance.
Keep document-specific extraction guidance in this application profile. When a
shared Core definition needs improvement, fix it there and regenerate its outputs
instead of maintaining a competing application definition. The
[active schema reuse checklist](../../thoughts/reviews/2026-09-07-document-understanding-schema-usage.md)
tracks connected capabilities and the next integrations. Supported conditions
use `ApplicabilityScope` even when no territory is asserted; audit quality issues
use `Finding`. Model lineage records the actual request temperature.

The [temperature-zero polish results](../../examples/document_understanding/extraction-polish/README.md)
preserve twelve live trials, including rejected changes. They show remaining
exception-link and discovery gaps; lower temperature does not guarantee completeness.

The [provider-free discovery trial](../../examples/document_understanding/discovery-trial/README.md)
compares summary search with source passages and linked evidence. It also verifies
narrow attribution and duration checks: unsupported structured suggestions remain
visible with issues but do not emit specialized Core records. Direct named speakers
and simple year/month/day durations are supported; issuer metadata, implied speakers,
and more complex duration wording still need review or a later integration.

The [composition experiment](../../examples/document_understanding/composed-extraction-experiment/README.md)
compares all-fields extraction with complete statements first and optional
relationship enrichment. The smaller pass performed best in that four-excerpt
trial; it remains an experimental candidate, with production defaults unchanged.

The optional structured collections add useful detail without requiring invented
values. `concepts` comes first in each unit and supplies a label, distinguishing
definition, topical role and exact quotation. Rulespec creates `LocalConcept`,
`ConceptScheme` and `ConceptAssignment` records with content-derived releases,
actual membership and verified release digests. Repeated label/definition pairs
within a document share an identity; cross-document identity still needs RefSpec
resolution. These local concepts do not claim RefSpec registration.

`claimants` records source attribution separately from the actor. `typed_values`
becomes typed Core `ValueAssertion` records; their predicates reference retained
JSON descriptions of the value's name, source comparator, unit and reference
event. `effective_periods` links the complete meaning through `ApplicabilityScope`
to `EffectivePeriod`. Date-only effectivity stays a typed date: the profile does
not invent midnight or a timezone. Relative deadlines remain values, not periods
in force. Invalid or unsupported components remain visible as issues and produce
no structured Core record. Review corrections retain the original records.

The extractor reads Core schemas, context and shapes from `rulespec-conformance`
and reuses its release-digest implementation. It no longer packages another copy
of those validation files. See the [integration checks and live captures](../../examples/document_understanding/schema-reuse-finish/README.md).

**Output:** a local rulebook and Core JSON-LD graph, with the exact source,
requests, responses, accepted and refused candidates, processing outcomes,
unresolved issues, and validation results. Here, `accepted` means a candidate
passed the compiler's checks; it does not mean its interpretation is correct.

**Checks:** exact source re-slicing; compiled Core JSON Schema; SHACL, the graph
constraint language; raw-response replay; and separate source-based judgments of
meaning, omissions, actors, scope, links, and rule boundaries. A run can finish
processing and still omit rules. Semantic evaluation is a distinct result.

```sh
# Prepare exact text. Preparation does not discover a manual's section hierarchy.
rulespec-understand prepare manual.txt --title "Manual section" \
  --source-url https://example.org/manual --output prepared.json

# A new run makes provider calls. Supply GEMINI_API_KEY in the environment,
# or use an explicitly selected env file. Existing output directories are refused.
rulespec-understand extract prepared.json --model gemini-3.8-flash \
  --env-file /path/to/local.env --output my-run

# Temperature defaults to 0; specify it explicitly for a recorded comparison.
# Fresh model calls can still differ at 0. Replay reproduces saved responses.
rulespec-understand extract prepared.json --temperature 0 \
  --env-file /path/to/local.env --output my-run-t0

# Verify frozen requests, parse saved responses, and reproduce candidates/graph.
# This makes no provider call and refuses runtime or artifact drift.
rulespec-understand replay my-run --output my-replay

# Intentionally apply changed processing code to the original captures.
# This makes no provider call, preserves the original, and records the change.
rulespec-understand reprocess my-run --output my-reprocessed-run
rulespec-understand replay my-reprocessed-run --output my-reprocessed-replay

# The same durable review actions are available without a browser.
rulespec-understand review my-reprocessed-run --action correction.json
rulespec-understand export my-reprocessed-run --output reviewed-rulebook.json

# Unjudged or stale judgments remain unknown; schema checks cannot fill them in.
rulespec-understand evaluate reviewed-rulebook.json --labels expected.json \
  --judgments judgments.json --output evaluation.json

# Inventory source meanings before seeing the draft, then challenge the claims.
# Model observations expose gaps; they are not human approval or evaluation gold.
rulespec-understand audit my-run/rulebook.json --env-file /path/to/local.env \
  --output my-audit
rulespec-understand audit-replay my-audit --output my-audit-replay
rulespec-understand serve my-run --audit my-audit

# my-audit/findings.jsonld contains Core Findings with stable references.
# The detailed report and source judgments retain their evidence and rationale.

# Refine the current review snapshot, including earlier corrections.
# This appends AI-attributed review events in my-run; original captures stay intact.
rulespec-understand refine my-run --env-file /path/to/local.env \
  --output my-refinement
rulespec-understand refine-replay my-refinement --output my-refinement-replay
```

The commands above assume the environment's `bin` directory is on `PATH`.
See the [review demonstration](../../examples/document_understanding/manual-slice/review-demo/README.md)
for source-backed action files. Changes use an expected review revision to prevent
one editor from silently overwriting another editor's work.

`refine` performs one recovery pass, one qualification-link pass and a final
audit. Each proposed addition or edit must pass the existing source/Core checks
and a separate model challenge before it becomes a review event. It saves the
proposal, its rationale and any refusal. `--audit my-audit` reuses an
audit only when it matches the complete current snapshot. Export first when
auditing a workspace with review history. Replaying makes no provider calls and
checks proposals, requests, actions, history and the resulting graph.

Each refinement request contains at most 60 current claims; other claims are
counted as omitted context. Each focus group allows at most eight proposals per
pass. The model input keeps complete meaning, citations, exact evidence and
positions, using short aliases for opaque identifiers. Full identifiers remain
in saved packets and Core records. Refused or unresolved findings remain visible;
the process does not loop until the checker agrees with itself. Tokens and elapsed
time are recorded in `refinement.json`, including the initial and final audits.

## What is reused and what the application adds

| Need | Implementation |
| --- | --- |
| Exact evidence, fragment hashes, canonical IDs | Existing `rulespec-projection` helpers |
| Source, assertions, qualifications, model lineage, attestations | Existing Core schemas and SHACL shapes |
| Stable rule handles and immutable revisions | `document-understanding/3` application format; each revision is also a Core `Artifact` |
| Actor, action, object, modality, scope, alternatives and preserved logic | Source-backed component assertions and a complete meaning assertion using experimental application predicates |
| Governing conditions and explanatory context | Existing `EvidenceBinding` functions `definesScope` and `providesContext`; `ApplicabilityScope` for supported conditions or explicit effectivity, with no inferred territory |
| Missing or ambiguous target links | Explicit unresolved records; a partial target set emits no misleading complete link |
| Source-to-rule extraction and failure accounting | New application package, recorded windows and attempts |
| Reproducibility | Frozen acquisition artifacts, strict replay, and explicitly recorded reprocessing |
| Corrections and review | Append-only SQLite events, retained revisions, Core supersession and `Attestation` records |
| Omission discovery | Source-first model inventory, separate claim comparison, existing evaluator and exact passage accounting |
| Automatic corrections | Bounded recovery and relationship proposals, real review validation, separate source challenge and appended AI review events |
| Concepts and vocabulary | Source-supported local concepts and release-pinned assignments; optional RefSpec label suggestions remain separate from semantic identity |
| Attribution, typed values and effectivity | Existing `SourceClaimant`, typed `ValueAssertion`, `EffectivePeriod` and `ApplicabilityScope` |

Core assertion identity covers its proposition. Evidence changes do not invent
a different proposition. A rule handle survives ordinary edits; each revision
records its predecessor, component assertions, and exact evidence. Restoring an
earlier value preserves the intervening revisions without changing the original
assertion's origin or creating a supersession cycle. Split, merge, and addition
create new rule handles. These are stable references within the recorded review
history, not claims of identity across independent model runs.

The complete meaning assertion includes scope in its value. A scope-only edit
creates a new proposition while preserving the old one. `ApplicabilityScope`
does not discover governing conditions; selecting them remains an interpretation.
When jurisdiction is unstated, scope remains explicitly recorded in the meaning
and evidence without inventing a territorial code.

The audit saves raw requests/responses, an inventory, judgments, a report and
passage accounting. Its default focus is 3,000 characters with at most 2,400
additional context characters; its output budget is 32,768 tokens. Extraction
keeps its separate 6,000-character focus and 16,384-token budget. Each phase is
bounded, and incomplete or refused responses remain visible. The browser shows
missing/partial units and marks a saved assessment stale after corrections.
Neither processing completeness nor a clean assessment emits a `ClosureClaim`.

Rulespec requires no DocSpec or SpicyRegs service or release. RefSpec is the only
optional platform integration. Ordinary Python/model libraries live in this
application package; Core and the projection package gain no new dependencies.

## Optional RefSpec vocabulary

`vocabulary` accepts a normalized, version-identified snapshot:

```json
{
  "source": "RefSpec",
  "release_id": "urn:refspec:example:release:1",
  "concepts": [
    {"id": "urn:refspec:example:applicant", "label": "Applicant", "aliases": ["Passport applicant"]}
  ]
}
```

```sh
rulespec-understand vocabulary my-run/rulebook.json \
  --snapshot vocabulary.json --output vocabulary-suggestions.json
```

Matches use exact case-insensitive labels or aliases on actor/object text. The
sidecar binds the source rulebook and vocabulary digests and distinguishes a
suggestion, ambiguity, and an unmapped mention. It does not fetch RefSpec,
authenticate a release, or automatically assert semantic equivalence. This
adapter's input format is experimental, not a new RefSpec release format.

## Present limits and next extraction work

The saved source review found missing document alternatives, lost shared
conditions, omitted weaker guidance, and inconsistent exception links. The
application exposes and records correction work; the producer does not yet
consistently avoid it. See the [detailed findings](evaluation/results/FINDINGS.md).

Prioritize explicit source-unit accounting, inherited scope, exception targets,
and representative development examples before expanding input size. Retain
complex logic verbatim and unresolved until a tested representation exists.
Context selection uses exact paragraph/list structure and a bounded character
budget. Omitted context passages are recorded; structural proximity does not
establish governing scope. Remote references resolve only when the named section
is present. There is no general semantic
duplicate detector, complete entity model, or executable rule engine.

All quality judgments in this delivery are agent-authored and uncalibrated.
Human accuracy, correction time, and time savings have not been measured. The
recorded manual passages are pinned examples, not current legal guidance.

## Check the implementation

```sh
.tools/document-poc-venv/bin/python -m pytest packages/rulespec-extrapolator/tests -q
```

Tests cover source drift, malformed and partial responses, failed windows,
replay/reprocessing drift, evidence and identity, revisions, review concurrency,
first-open integrity, HTTP protections, and evaluation that detects corrupted
meaning or actors. The [execution record](../../thoughts/plans/2026-09-07-document-understanding-execution.md)
links the saved verification and independent implementation review.
