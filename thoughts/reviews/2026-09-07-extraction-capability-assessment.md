# Extraction capabilities: reuse, connect, extend and build

**Keep the current foundation and extend the document-understanding profile.**
Rulespec already supplies the evidence, identity, provenance, correction history
and validation machinery this iteration needs. The missing work is selecting
complete meanings from source text, preserving the conditions that govern them,
and discovering content that the first extraction missed. Existing Core records
can represent the resulting information; their schemas cannot discover it.

This is a static assessment of the current working tree, dated 2026-09-07. It
incorporates the user's supplied side-agent feedback into the
[revised implementation plan](../plans/2026-09-07-document-understanding-quality.md).
No production implementation, model experiment or new runtime test occurred in
this assessment.

## What is already implemented, available, or missing

The status refers to the local document-understanding application, not merely
to whether a similarly named schema exists somewhere in the repository.

| Capability | Current status and evidence | Decision for this iteration |
| --- | --- | --- |
| Pinned text, sections and source coordinates | **Already implemented:** `prepare_document`, `validate_document`, `load_document` in [documents.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py#L8). Sections are supplied or default to one whole-text section. | Reuse. Extend the source index with paragraph/list relationships and explicit parent context; preserve the existing text and coordinates. |
| Exact quotations and individual component evidence | **Already implemented:** [`core._evidence`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L63) calls the projection package's `resolve_exact_evidence_offsets` and `verify_fragment`; `_claim` grounds summary, actor, action, object and available logic evidence. | Reuse the same resolver for scope, context, modality and alternative quotations. Ambiguous or absent support stays visible. |
| Assertion identity, provenance and immutable revisions | **Already implemented:** [`assertion_id`, `_component_nodes`, `build_graph`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L145), `AILineage`, `ExtractionActivity`, `Artifact`, `ValueAssertion` and `RelationshipAssertion`. | Preserve proposition identity and original attribution. Extend explicit field lists when adding meaning; do not create a parallel identity/history system. |
| Local condition/exception links and qualifying evidence | **Already implemented:** [`resolve_links`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L168) resolves exact target quotations. [`build_graph`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L319) emits modifier-to-target `RelationshipAssertion` records and `EvidenceBinding` with `rkaf:qualifies`. | Reuse and extend evidence to include the support for the relationship's target and inherited scope. `qualifies` is already connected; it is not a missing feature. |
| Scope and surrounding-context evidence roles | **Available but not connected:** [EvidenceBinding](../../constraints/core/evidence-binding.cue#L31) defines `rkaf:definesScope` and `rkaf:providesContext`. The application currently emits `supports` for components and `qualifies` for modifier relationships. | Connect these roles to the relevant existing assertions. Context evidence explains a reading; scope evidence supports a proposed applicability limit. Neither role proves the reading correct. |
| A Core record describing applicability | **Available but not connected:** [ApplicabilityScope](../../constraints/core/applicability-scope.cue#L10), its [compiled schema](../../compiled/json-schema/core/applicability-scope.schema.json), and `rkaf:hasApplicability` on [ValueAssertion](../../constraints/core/value-assertion.cue#L56) and [RelationshipAssertion](../../constraints/core/relationship-assertion.cue#L45). | Reuse when a coherent applicability statement fits the record. Extend the application validator's type list before emitting it. Keep generic context in evidence bindings. |
| Modal distinctions and standalone exemptions | **Genuinely missing in the profile:** [`KINDS` and `CANDIDATE_SCHEMA`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L18) lack a recommendation, standalone no-obligation statement and descriptive-possibility distinction. The [prompt](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py#L35) defines requirements as “must do.” | Extend the small profile and examples. The Core forms already exist; the application meanings, consistency checks and extraction behavior need work. |
| Alternatives, thresholds and compound conditions | **Partly implemented:** `logic_text` retains text, `kind: threshold` exists, and `_claim` marks logic as unresolved. **Available but not connected:** [ValueAssertion](../../constraints/core/value-assertion.cue#L3) supports typed values. **Missing:** reliable extraction of full alternatives and interpreted grouping/comparators. | Add explicit alternatives with their source choice wording. Retain threshold/grouping text. Formal arithmetic and arbitrary executable logic are not required for this iteration. |
| Requests, raw responses, attempts, replay and reprocessing | **Already implemented:** [`extract_run`, `replay_run`, `reprocess_run`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py#L589), with frozen schemas, prompts, examples and runtime inputs. | Reuse. Fix the recorded overflow/finalization defect and version every profile/parser change. New output goes to a new run or processing result. |
| Persistent corrections and revision-bound review | **Already implemented:** [`ReviewStore.apply`, `_state`, `_snapshot`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/review_store.py#L267) and `core.revise_claim`. | Reuse for explicit reviewer corrections or later user feedback. Include new fields in integrity and reconstruction checks. Review remains a capability; it is not a mandatory ingest step for discovery. |
| Processing coverage | **Already implemented for windows:** [`plan_windows`, `_overall_status`, `_pipeline_status`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py#L142). **Available accounting principles:** release validators reconcile source/disposition sets and actual counts. | Extend local accounting to source passages. Adapt the principles, not the entire prepared-document release dependency chain. |
| Semantic coverage assessment | **Already implemented as explicit judgment accounting:** [`evaluation.evaluate`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/evaluation.py#L130) checks source-bound expected units and current claim judgments. **Genuinely missing:** an automated source-first omission finder integrated with extraction. | Reuse the evaluator. Add a bounded checker that proposes findings; it does not certify completeness. Preserve separate processing, semantic-quality and review-completeness results. |
| Optional vocabulary suggestions | **Already implemented, narrow:** [`vocabulary.annotate`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/vocabulary.py#L30) matches actor/object labels and aliases from a supplied RefSpec snapshot. | Preserve. This is not broad automatic tagging, embedding generation or cross-document entity resolution; this iteration improves their source material without claiming to implement those consumers. |

The current [`validate_graph`](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py#L373)
accepts eight Core record types and rejects others, including `ApplicabilityScope`.
The scope schema is present in the repository and the extraction runtime's
[frozen-data collection](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py#L357)
already includes all Core schemas. The required change is application wiring
and validation coverage, not a new Core schema.

## Meaning → application fields → Core → checks → uncertainty

Names marked **proposed** below are application-profile fields, not new Core
properties. Keep the model response as a small set of strings and lists of exact
quotations. The compiler creates IDs, source fragments, bindings, assertions,
scope records and provenance. No model-produced Core graph or identity is needed.

| Extracted meaning | Application fields | Core representation | Validation check | Remaining uncertainty |
| --- | --- | --- | --- | --- |
| Must, should, may, must not, not required, descriptive possibility | **Proposed:** `modality`, `modality_quote`; existing `kind`, `summary`. Add only the missing compatible kinds for recommendation, standalone exemption and descriptive statement. | An application-predicate `ValueAssertion` for modality, alongside the existing statement assertion; exact support in `SourceFragment`/`EvidenceBinding`. | Closed profile values; compatible kind/modality; exact supporting quote; revised fields included in identity/history/export. | A word such as “may” does not identify permission by itself. Context still decides its meaning. |
| Who acts, action and object | Existing `actor`, `action`, `object` and their quote fields | Existing component `ValueAssertion` records and `supports` bindings | Reuse exact evidence checks; add source-reviewed component judgments where current dimensions are too coarse. | A source-supported token can still be assigned the wrong role. Empty or not-applicable components are preferable to an invented actor. |
| Inherited conditions and case limits | **Proposed:** `scope_text`, `scope_quotes`; existing condition candidates and target links remain usable. | A profile scope-content `ValueAssertion`; `definesScope` evidence on the affected statement. Add `ApplicabilityScope.applicabilityCondition` and `hasApplicability` where the declared scope fits. | Resolve all quotes; check scope-node references and source fields; verify that split children retain the governing scope; test revision integrity. | Selecting the governing condition and interpreting AND/OR or timing remain profile/source-review work. `applicabilityCondition` is explicitly free-form and audited, not semantically validated. |
| Surrounding explanatory context | **Proposed:** `context_quotes` | Existing `EvidenceBinding` with `providesContext`, attached to the relevant assertion | Exact quotations and resolvable binding targets; include them in retained revision evidence | Nearby text is not automatically a prerequisite, exception or supporting authority. |
| An exception and the rule it changes | Existing `kind: exception`, `relation: exception`, `applies_to`, compiled `target_ids`; standalone no-obligation statements use the new exemption representation when no baseline target is asserted. | Existing modifier-to-target `RelationshipAssertion` and `qualifies` binding; add scope/context evidence where needed | Existing exact target resolution plus semantic target tests, direction checks and correction/relink tests | Correct endpoints do not establish that all exceptions were found. An unresolved target is preferable to attaching an exemption to a different timing class. |
| Acceptable alternatives and their grouping | **Proposed:** `alternative_quotes`, `choice_text`; retain complete `logic_text` | Profile `ValueAssertion` records for alternatives and source-stated choice wording, each with supporting fragments; retain the complete grouping in the revision Artifact | Every declared option has support; preserve parent grouping and one-or-more wording; compare against source-list accounting | Do not flatten nested options or infer executable any/all-of logic from a list alone. Complex grouping remains textual until explicitly interpreted. |
| Thresholds, quantities, deadlines and negation | Existing `kind`, `logic_text`, exact evidence; extend evidence coverage as needed | Existing text `ValueAssertion`; Core typed values are available for a later or narrowly justified normalization | Preserve comparator, unit, anchor and conjunction in source-backed text; reject unsupported conversions in regressions | “Within one year” does not supply date arithmetic, and six months must not silently become a fixed day count. Core datatype validity cannot establish the intended comparison. |
| A possible omission or incomplete extraction | Local source-passage accounting and existing expected-unit/claim judgments | Local diagnostic/evaluation artifacts; use ordinary `Artifact` only if an export needs a content-addressed record | Reconcile processing dispositions separately from assessed semantic coverage; keep unknown/missing/partial and stale judgments distinct | The checker may miss an omission or misclassify background. Its inventory is not independent evaluation gold. |

The modality vocabulary is categorical, not an ordering of legal force. A
prohibition is not implemented by blindly setting `rkaf:assertionPolarity` to
`denied`: Core polarity affirms or denies the proposition being stored. The
profile must state what that proposition means. This follows
[Core §2.1](../../spec/rkaf-core.md#21-proposition-bearing-relationship-assertions) and its explicit placement
of duty/permission semantics in domain profiles.

## ApplicabilityScope and evidence: the concrete reuse decision

Connect the evidence roles first. They directly address the observed loss of
parent conditions and antecedents using records already emitted by the app.
They also preserve useful contextual passages for discovery without requiring
every passage to become an operational rule.

Use `ApplicabilityScope` for an actual applicability description, not as a
container for arbitrary neighboring text. Its required jurisdiction field and
optional subject/effective-period fields must have an honest interpretation.
Do not invent a jurisdiction, universal scope or effective date merely to fill
the schema. When the data does not fit, retain the profile's condition and its
`definesScope` evidence with explicit uncertainty. This does not require a
competing general-purpose scope schema.

Before connecting `hasApplicability`, add a small compiler fixture covering a
supported scope and a changed-scope revision. Core assertion IDs currently hash
only subject/predicate/object-or-value/polarity; `build_graph` retains the first
node for an ID. A scope-only correction must therefore create an explicit
changed scope proposition/revision and preserve the old scope. It must not
silently mutate metadata on a shared historical assertion. The prototype must
pin which scoped statement gets the link before that link is used in exports.

Also include the evidentiary function in new binding identity calculations:
`supports`, `definesScope` and `providesContext` over the same fragment and
assertion are distinct bindings. Preserve existing v1 artifacts and identities;
record changed processing explicitly.

## Coverage reuse and the missing discovery step

[`_validate_dispositions_and_coverage`](../../tools/extrapolation_release_v2.py#L2086)
already checks that every pinned document has a disposition, declared counts
match actual assignments/evidence, and failures have records. Its arguments
are release-specific, including `DocumentReleaseView`; importing this whole
validator would couple local extraction to a different workflow. Adapt those
same accounting checks to the existing local document/run data.

[`stamp_coverage`](../../tools/rulespec_release.py#L188) hashes a coverage record.
It does not discover missing content. Likewise, `evaluation.evaluate` counts
explicit judgments; it does not infer them. Extend these existing patterns with
source-passage dispositions and a bounded source-first assessment that can
propose missing statements, options or qualifiers. Keep its findings and any
repair attempts recorded. Do not require a manual review for every discovery
run or silently treat an automatic audit as a human decision.

[ClosureClaim](../../constraints/analysis/closure-claim.cue#L5) remains disabled.
Do not emit it as proof of completeness or create a `RelationFinding` omission
claim through that route. Application diagnostics and explicit evaluation
judgments already provide a place for the bounded observations needed here.

## Assessment of the milestone

**Verdict: keep the milestone, reshape its acceptance wording and wiring order.**
The [README's product objective](../../README.md#from-documents-to-referenceable-knowledge)
and the user's two-use-case clarification support coherent, traceable units
with different levels of review. The
[adversarial findings](2026-09-07-document-understanding-adversarial/FINDINGS.md)
support improving scope, modality, alternatives and omission discovery. They do
not establish a universal requirement for perfect extraction or a manual review
before search/discovery use.

The existing evaluator and review store already cover judgment accounting and
corrections. Replacing them would add duplicate state without addressing the
model's observed mistakes. The smaller useful change is to extend their
existing fields and connect currently unused evidence/scope capabilities.

The design fails its user-value test if it produces more richly labeled graphs
while conditions still disappear, alternatives remain absent, or tagging and
retrieval lose useful context. Evaluate those outcomes on saved cases and fresh
inputs; report remaining errors. Formal workflow/Formspec generation and broad
retrieval benchmarking are downstream work, not additional prerequisites for
this extraction milestone.

The assessment's implementation claims are grounded in the linked callable
paths and schemas. The new field mapping and compiler wiring are proposals,
not implemented or tested behavior. Confidence is high in the reuse inventory
and current gaps; exact v2 serialization needs the proposed compiler fixtures.
