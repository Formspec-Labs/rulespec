# Document understanding slice: shared implementation decisions

Status: quality iteration implemented locally, 2026-09-07. Experimental application
profile `document-understanding/2`; existing Core schemas remain authoritative.

## Owned files and interfaces

`core.py` compiles meaning and evidence; `documents.py` prepares exact source
and context; `extraction.py` records model requests and processing; `audit.py`
checks source coverage and claims through `evaluation.py`; `review_store.py`
preserves corrections and review. `review.py` and static assets expose those
same operations locally. RefSpec vocabulary is optional in `vocabulary.py`.
`refinement.py` connects source-audit findings to bounded additions/edits and
explicit qualification links through the existing review store.

### Source and candidates

A document is a JSON object with `id`, `sha256`, `text`, `title`,
`source_url`, and `sections`. Each section has `id`, `label`, `start`,
`end` (Unicode codepoints into the exact text). Preparation never rewrites
the pinned text. Model windows may contain several sections.

A candidate has required strings `kind`, `summary`, `actor`, `quote`;
optional `start` and `end` (document-global, null allowed);
strings `action`, `object`, `actor_quote`, `action_quote`, `object_quote`,
`logic_text`; `relation` (none/scope/prerequisite/trigger/exception);
`applies_to` (list of exact main-rule quotations); `references` (list of
section labels as stated); and `section_id` when known. Missing optional
strings become empty and lists become empty. Kinds are requirement, permission,
prohibition, authority, threshold, definition, condition, exception.

Profile v2 adds recommendation, exemption and statement kinds. `modality` is
must/should/may/must_not/not_required/possible/not_stated/uncertain, with
`modality_quote`. `scope_text` and `scope_quotes` retain governing conditions;
`context_quotes` retains explanation. `choice_text`, `choice_quote` and
`alternative_quotes` retain complete alternatives and nested choices. Optional
`jurisdiction` requires `jurisdiction_quote`; it is never inferred from a URL.
All new fields participate in revision identity, correction reconstruction,
export, stale-judgment checks and Core compilation. V1 captures without these
fields retain their old interpretation; reprocessing cannot invent missing meaning.

The provider has one explicit shared `unit`/`unit_attributes` record. Its
native JSON Schema requires every field (empty strings/lists for unstated
information), uses closed enums and objects, and supplies descriptions. Scope
evidence precedes summary generation. Invented examples demonstrate semantics
in plain text without repeating JSON output definitions. Historical requests
retain their original schema field and JSON-example formatting on reprocessing.

`provider_schema()` now emits the exact richer titles/descriptions evaluated in
the schema-order experiment. It derives field types and closed classifications
from `CANDIDATE_SCHEMA`; the model-specific selection, required fields, empty
values, descriptions, and generation order remain explicit. The resulting JSON
Schema is identical to the evaluated `rich` variant, including serialization
order. `refinement.proposal_schema()` reuses those same annotated attributes.

The candidate profile is still Python-authored. Core CUE schemas govern stored
`ValueAssertion`, `RelationshipAssertion`, `SourceFragment`, `EvidenceBinding`,
and related records; they do not define this profile's `modality`, `scope_text`,
or `alternative_quotes` fields. The follow-up is a CUE-owned candidate profile
and generated validator, with a thin model adapter. Exporting the richer field
descriptions also requires extending the current CUE projector, which does not
carry field descriptions. The present adoption makes no new Core schema or
candidate-format change.

Preserve complex logic verbatim in `logic_text`; the first slice marks it
unresolved for review and does not claim executable AND/OR/numeric semantics.
Actor/action/object are reviewable component text, with separate exact evidence
quotes; empty evidence creates an issue, never invented support.

### Core interface (root)

- `canonical(value) -> str`, `digest(str|bytes|JSON) -> hex str`.
- `compile_candidates(document, candidates, run) -> rulebook`.
  Run contains `id`, `model`, `model_version`, `prompt_sha256` and may
  contain `status` and `windows`; fixture defaults are allowed.
- Rulebook has `schema_version`, `document`, `run`, `accepted`, `rejected`,
  `unresolved`, and `graph` (Core JSON-LD).
- Accepted records retain the candidate fields plus `id` (immutable application
  revision ID), `rule_id` (stable review handle), `occurrence_id`,
  `assertion_ids`, `evidence`, `issues`, `target_ids`, and `origin`.
  Evidence records have quote/start/end/field/fragment_id.
- `revise_claim(document, original_claim, replacement_fields, event_id,
  origin="humanAsserted") -> claim` validates exact evidence and preserves
  rule_id. For split/merge, the store supplies fresh rule_id values.
- `build_graph(document, claims, run, attestations=[]) -> graph` emits all
  supplied claim revisions. `validate_graph(graph) -> validation report`
  checks compiled Core JSON Schema and SHACL.

The application revision ID is distinct from Core assertion IDs. Each Core
assertion ID hashes ONLY its subject/predicate/object-or-value/polarity.
Actor/action/object get their own Core assertions; review targets the immutable
component assertions. Evidence and origin never enter proposition identity.
Origin of an old claim is never rewritten. A human correction creates a new
revision and supersession links. A review of unchanged AI text is an Attestation.
Every application revision is also retained as a Core Artifact containing its
canonical content and predecessor references. A restored proposition keeps its
original origin; the revision chain records the restoration without a cycle.

The v2 `meaning` ValueAssertion contains canonical JSON as `xsd:string` with the
complete interpreted meaning. This deliberately keeps application semantics in
the profile. Only this complete assertion receives `hasApplicability`, avoiding
scope changes on a shared summary proposition. `definesScope` and
`providesContext` bind exact fragments to summary/meaning assertions; `qualifies`
retains modifier and target context. Binding function participates in identity.
`ApplicabilityScope` is emitted only with source-supported jurisdiction and
conditions. Missing jurisdiction does not discard scope text or its evidence.

### On-disk run and extraction interface

A new run directory contains `document.json`, `run.json`, `candidates.json`,
`rulebook.json`, `graph.jsonld`, `validation.json` and provider attempt files.
Original extraction files are immutable. Review events live separately.

- `extract_run(document, output: Path, model_id, env_file=None,
  max_chars=6000) -> rulebook`: output must not already exist.
- `replay_run(input_dir: Path, output: Path) -> rulebook`: verify all declared
  artifacts and parser/profile hashes; reparse saved raw responses, compare
  candidates, then compile and compare the base graph. Fail visibly on drift.
- `reprocess_run(input_dir: Path, output: Path) -> rulebook`: verify original
  acquisition records, reparse the saved responses with current code, and freeze
  new processing metadata. Preserve the original run ID and capture bytes; record
  predecessor manifest/runtime hashes. The result must independently strict-replay.

Each planned window records a terminal outcome even if parsing or extraction
fails; one successful window cannot hide another's failure. No candidates is
an explicit outcome, never an inferred successful rulebook.

### Review interface

`ReviewStore(run_dir).snapshot()` returns the effective rulebook plus
`revision` (event sequence), `history`, and `attestations`.
`apply(action_dict)` requires `expected_revision`, `actor`,
`actor_kind` (humanUser/aiAgent), `action`, `targets` (revision IDs),
and `rationale`. Edit/split/merge supply `replacements` candidate dictionaries;
add supplies an empty target list and source-grounded replacements with fresh
rule handles and no invented predecessors;
approve/reject supply only the targets. Every operation appends a durable event.
No operation deletes or rewrites the base extraction or old revisions.
Agent-driven demonstrations must identify aiAgent and never impersonate a human.
`preview(action_dict)` runs the same validation and builds the proposed snapshot
inside a rolled-back transaction. It saves no event or review decision.

### Evaluation interface

Evaluate rulebook `accepted` records with id/rule_id/summary/actor/kind/quote,
evidence and target_ids. Explicit judgments must bind candidate content digests;
changing a summary/actor invalidates an earlier judgment. Unknown/unjudged is
reported separately. Expected units without a reviewed match are not silently
counted as covered. Held-out labels stay outside prompts/repair until extraction
outputs are frozen. Agent labels are disclosed as such.

V2 judgments extend the original dimensions with modality, action, object,
alternatives and thresholds. Fully judged total omission reports both completed
review and failed quality. Schema conformance does not fill missing judgments.

`audit_run(book, output, model_id, env_file=None, max_chars=3000)` first records a
source-only inventory, then a separate comparison with the draft. Both phases
retain exact evidence and raw captures; the existing evaluator accounts for
their judgments. `replay_audit` checks the pinned runtime and recomputes the
observations without provider calls. `load_audit` verifies saved artifacts for
display without requiring the current runtime. Review edits make an attached
audit stale. Inventory and comparison are fallible model observations, not gold,
automatic repairs, human approval or semantic completeness. No `ClosureClaim`
is emitted.

### Refinement interface

`refine_run(run_dir, output, model_id, audit_dir=None, env_file=None,
max_chars=3000)` starts from `ReviewStore.snapshot()`. A supplied audit must match
that snapshot's content digest. The output must be new and separate from the
review workspace. Original captures, before/after snapshots, prompts, raw model
responses, refusals and appended review events are retained.

Each focus group receives full current meanings and exact source context. A
recovery pass proposes missing content or narrow edits; the next pass proposes
only condition/exception records and chooses current target aliases. The shared
native candidate schema supplies all meaning fields. Deterministic code resolves
aliases to current records and quotations, validates candidates through
`ReviewStore.preview`, then asks a separate source challenge about complete
meaning and target correctness. Supported changes use `apply` with the current
revision and `actor_kind=aiAgent`. They do not become approvals.

Source quotes must appear in supplied focus/context/evidence. Repeated main quotes
can be disambiguated only within an explicitly selected target's exact interval.
This establishes the source location; the challenge separately checks what the
qualification governs. An unknown or refused proposal does not discard supported
neighboring changes. A stale review snapshot blocks application.

Limits are one recovery and one relationship pass, 60 supplied claims and eight
proposals per focus group, temperature 0, and 32,768 output tokens per request.
The provider schema retains every meaning field. A controlled provider probe
required removing `maxItems` from the outer proposal array; the parser enforces
the same bound. Model-only input omits opaque provenance hashes and duplicate
copies of proposal fields; saved packets remain complete. A final audit refers to
the final snapshot. Processing status, semantic findings, elapsed time and token
usage remain distinct.

`replay_refinement(directory, output)` verifies frozen runtime/artifacts, reparses
saved proposals and source challenges, reconstructs the exact requests and review
history, and compares the full before/after graph and action accounting without
calling the provider. Recorded action fields must match the parsed proposal and
saved event; a newly generated checksum manifest cannot conceal a mismatch.
