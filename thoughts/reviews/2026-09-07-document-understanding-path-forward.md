# Final review: document understanding and existing Rulespec capabilities

Date: 2026-09-07. Base commit: `7f8d99b`. The experimental code and recorded
runs under `examples/document_understanding/` are uncommitted.

**Decision: keep the standalone product direction; revise the next delivery
step before expanding implementation.** Rulespec already owns much of the
evidence, provenance, review-record, vocabulary, and validation machinery.
The missing product is the producer and review workflow that use those pieces
to turn an unfamiliar document into a faithful rulebook.

The next milestone is one unfamiliar, bounded manual section that a reviewer
can inspect, correct, split, merge, and approve with its evidence and history
preserved. It must report extraction mistakes, omissions, and unfinished work.
Chapter-scale processing follows that result.

This review updates the delivery recommendations in the
[standalone plan](../plans/2026-09-06-standalone-document-understanding.md)
and [LangExtract plan](../plans/2026-09-07-langextract-schema-integration.md).
It does not change Core semantics, enable disabled features, or declare a release.

## What is already solved, partly solved, and missing

I inventoried the tracked implementation files, inspected the relevant Python
modules and Rust runtime, and traced the associated CUE definitions, generated
schema paths, tests, release validators, and specifications. The generated wiki
was not used as implementation evidence. This is a capability audit, not a
line-by-line review of every generated file or a new audit of sibling repos.

“Reuse” below distinguishes callable code from schemas that describe records.
A schema can prevent an invalid record; it cannot produce a correct
interpretation of a document.

| Remaining need | Existing Rulespec solution and evidence | What still needs work |
| --- | --- | --- |
| Exact source evidence | **Callable Python.** [resolve_exact_evidence_offsets](../../packages/rulespec-projection/src/rulespec_projection/evidence.py):44 checks supplied offsets or a unique exact match. [verify_fragment](../../packages/rulespec-projection/src/rulespec_projection/projection.py):225 re-slices, hashes, and identifies a fragment. [EvidenceBinding](../../constraints/core/evidence-binding.cue):31–46 distinguishes source roles from support, qualification, scope, and context. | Reuse these helpers and records. Add support for each meaningful component of a rule, including inherited actors and remote qualifications. A supporting quote alone does not validate a summary. |
| Faithful rule meaning | **Schemas plus the experimental producer.** [ValueAssertion](../../constraints/core/value-assertion.cue), [RelationshipAssertion](../../constraints/core/relationship-assertion.cue), and [ApplicabilityScope](../../constraints/core/applicability-scope.cue):10–15 provide reusable forms. [semantic_profile.py](../../examples/document_understanding/semantic_profile.py):3–18 distinguishes rule kinds and qualification roles. | A small document-understanding profile must define actors, actions, targets, qualifications, and their evidence. The current strings and links do not represent grouped AND/OR conditions, numeric comparisons, or deadlines precisely. Applicability conditions are explicitly free-form and “audited not validated.” |
| Omissions and unsupported claims | **Executable accounting checks; no completeness oracle.** [Release coverage validation](../../tools/extrapolation_release_v2.py):2086, 2186–2237 reconciles document dispositions and assignment counts. [ClosureClaim](../../constraints/analysis/closure-claim.cue):5–26, 65–73 describes a completeness claim but explicitly disables its use as evidence. | Adapt accounting principles to local sections, windows, attempts, and failures. Independently score missing and unsupported rule content. Do not enable ClosureClaim or turn processing coverage into semantic completeness. |
| Evaluation on unfamiliar documents | **Existing validation fixtures and a narrow experimental checklist.** [evaluate_semantics.py](../../examples/document_understanding/evaluate_semantics.py):9–37 checks selected kinds, distinctions, and target sets. [AI extraction constraints](../../constraints/ai-extraction/consent-vs-warrant.cue):3–7 reject known schema misclassifications. | Build source-reviewed evaluation labels and a real holdout set. These fixtures do not measure general extraction accuracy, actor correctness, faithful summaries, or arbitrary extra claims. |
| Cross-section links and shared scope | **Partial callable code and reusable records.** [citations.py](../../packages/rulespec-projection/src/rulespec_projection/citations.py):626, 756, 823, 935 parses several US citation forms. SourceFragment, RelationshipAssertion, and EvidenceBinding can represent linked evidence. [The prototype](../../examples/document_understanding/poc.py):278–308 links exact target quotations within one candidate collection. | Add a document section index, reference resolution, scope assembly, and explicit unresolved references across windows. Existing citation parsers do not supply a general manual-section resolver or determine which rules inherit a qualification. |
| Rule boundaries, duplicates, and durable identity | **Identity rules and hashing utilities exist.** [Core §2.3](../../spec/rkaf-core.md):163–175 separates proposition identity from other state. [canonical_json and stable_id](../../packages/rulespec-projection/src/rulespec_projection/provenance.py):67–88 provide mechanics. | Apply the existing identity rule correctly; retain separate extraction occurrences and evidence. Detect possible duplicates for review. No general semantic split, merge, or equivalence algorithm was found. |
| Human correction and approval | **Schemas and a callable row builder.** [Attestation](../../constraints/core/attestation.cue):17–35 records who decided, over which targets, when, and with what scope. [attestation_row](../../packages/rulespec-projection/src/rulespec_projection/attestations.py):172–225 builds validated tabular records. [Core](../../spec/rkaf-core.md):366–391 defines supersession and preserves AI origin. | Build editable local review, persistence, and conversion from review actions to Core records. The existing HTML is read-only. Reuse the records and helper where its tabular form fits; it is not a complete review service. |
| Actors, entities, and RefSpec vocabulary | **Schemas, tag verification, and runtime resolution behavior exist.** [verify_candidate_rows](../../packages/rulespec-projection/src/rulespec_projection/projection.py):975–1054 verifies concept assignments. [ConceptResolutionResult](../../constraints/core/concept-resolution-result.cue):3–24 represents resolution outcomes. [concept.rs](../../crates/rkaf-runtime/src/concept.rs):27–57 evaluates supplied concept/mapping graphs. [The RefSpec open-label profile](../../constraints/profiles/refspec/open-label.cue):6–22 preserves eligible open labels with provenance. | Extract document entities and mentions, then map terms through a RefSpec adapter. Keep unmapped mentions visible. The tag verifier refuses candidates without normalized vocabulary identities; routing all rule content through it would lose content. The Rust evaluator is not a vocabulary-fetching client. |
| Repeatability, partial failures, and longer inputs | **Provenance schemas and source-map validators exist.** [ExtractionActivity](../../constraints/core/extraction-activity.cue):10–38 and [AILineage](../../constraints/core/ai-lineage.cue) identify extraction and model inputs. [Source-coordinate validation](../../tools/extrapolation_release_v2.py):1414 onward checks prepared text against pinned source passages. [Release records §4](../../spec/rulespec-releases.md#4-durable-contained-records) defines ProcessingSegment and DerivedTextProjection. | Build local input preparation and the per-window attempt ledger. Extend replay to raw-response parsing and pin parser/profile/schema versions. Existing release validators require compatible release inputs; adapt reusable checks without making platform release bundles a local prerequisite. |

Three names could otherwise suggest more capability than exists:

- **The Rust runtime is a conformance implementation for five named behaviors.**
  Its [dispatcher](../../crates/rkaf-runtime/src/runtime.rs):43–49 handles
  usage eligibility, cascade closure, bridge rules, point-in-time retention,
  and concept resolution. It is useful for deciding how reviewed records may
  be used. It is not an engine for executing arbitrary extracted requirements.
  A [PointInTimeException](../../constraints/core/point-in-time-exception.cue):3–21
  retains assertions at an evaluation time; it does not model every “unless”
  clause in a manual.
- **The analysis module describes comparison records and proof requirements.**
  [RelationComparisonContext](../../constraints/analysis/relation-comparison-context.cue):5–15
  and [MachineAdjudicationProof](../../constraints/analysis/machine-adjudication.cue)
  are reusable for their defined comparison tasks. No corresponding extraction
  evaluator or model adjudication runner was found in the runtime or Python
  implementation. They do not replace the proposed evaluation dataset.
- **Studio is a pointer to another product.**
  [profiles/studio/README.md](../../profiles/studio/README.md):1–13 locates
  authoring schemas in policy-studio. The local
  [schema derivation helper](../../tools/studio_schemas_derive_manifest.py):1–14
  handles curated files; its CUE-constraint and fragment-merge modes are reserved.
  It is not a local review UI or a complete model-schema generator.

## Findings that change the work order

### F1 — High: the current evaluation cannot gate semantic quality

**Category:** evaluation adequacy. **Action: RESHAPE.**

The source-to-check path ends in
[evaluate_semantics.py](../../examples/document_understanding/evaluate_semantics.py):9–37,
which checks selected quotation anchors, types, and links. In an offline probe,
the Constitution baseline scored 20/20; replacing every summary with a false
fee requirement still scored 20/20. Replacing actors or appending an unrelated
invented claim also left the score unchanged.

This probes the evaluator in isolation. The added invented quote bypassed the
compiler; it does not show that exact grounding accepts out-of-source text.
The consequence is narrower and clear: the checklist cannot tell us how good
the extracted meaning is. Its 20/20 result remains a useful regression result.

**Required change:** retain those regressions, then evaluate faithful meaning,
actors, qualification scope, omitted requirements, unsupported assertions, and
boundaries against independently reviewed source labels. Publish separate
measures and error examples. Freeze candidate output before revealing holdout
labels or using them for repair.

### F2 — High: correct claim identity before attaching durable reviews

**Category:** invariant violation in the prototype. **Action: RESHAPE.**

[Core §2.3](../../spec/rkaf-core.md):163–175 requires a content-addressed
assertion to address its proposition alone. The prototype hashes actor labels,
source positions, and target quotations into the assertion ID at
[poc.py](../../examples/document_understanding/poc.py):234–241, but emits a
ValueAssertion containing the document, kind, summary, and polarity at :271–273.

An offline actor-only change produced a different assertion ID with an
identical Core proposition. Once reviews reference these IDs, such changes
would create unnecessary identity churn. Actor content also remains outside
the exported proposition, so reviewing the displayed actor is not equivalent
to reviewing the current ValueAssertion.

**Required change:** distinguish extraction occurrence identity from assertion
identity. Give reviewer-facing rules a reference that can retain revision
history; bind each substantive component to the appropriate immutable
assertion. Reuse Core supersession and Attestation. Changing evidence or a
review decision must not silently redefine a proposition.

### F3 — Medium: replay and accounting are incomplete at the model boundary

**Category:** reproducibility and failure visibility. **Action: RESHAPE.**

The [replay path](../../examples/document_understanding/poc.py):374–377 reads
saved candidates and invokes the current compiler. The run records the script
hash and saves a candidate schema, but compilation loads the current profile
and schema (:179–188, :221–222). This proves repeatable compilation in the
tested environment, not replay of raw-response parsing.

The final status at :386–398 distinguishes empty from nonempty grounded
output. It does not prove that every requested window parsed successfully.
That distinction matters when one successful window can hide another's failure.

**Required change:** pin the relevant implementation and schema artifacts;
retain an attempt and terminal outcome for every planned window. Replay raw
responses into candidates separately from candidate-to-graph replay. Report
partial processing visibly. Keep semantic coverage a separate assessment.

### F4 — Medium: parallel work needs one owner for shared data and a sealed evaluation step

**Category:** delivery dependencies. **Action: RESHAPE.**

The proposed evaluation, extraction, review, and preparation streams all touch
the same source references and candidate representation. The current
[experimental profile](../../examples/document_understanding/semantic_profile.py):3–18
and [compiler](../../examples/document_understanding/poc.py):217–308 do not yet
define the richer shared representation. Starting four independently designed
implementations would leave integration decisions until late.

**Required change:** one integrator owns the minimal versioned data format and
candidate-to-Core mapping. Agree on worked fixtures first, then run three worker
streams alongside the integrator. Four workers plus an integrator would exceed
the four available agent slots. Evaluation independence means controlling when
labels influence development; a different agent alone does not establish it.

## Revised next milestone

**What goes in?** An immutable real manual section, its neighboring context,
and a small development set. Start with exact text and section labels. Include
at least one definition, shared qualification, cross-section reference,
exception, and unfamiliar wording. Select 10–15 real excerpts across the
development and held-out sets; record who reviewed their labels.

**What happens?** Rulespec prepares identifiable source units, asks LangExtract
for candidates, checks their evidence, assembles meanings and links, and shows
uncertainties to a reviewer. RefSpec adds vocabulary matches where available.
Unmatched terms and unresolved references remain visible.

**What comes out?** A local rulebook, exact source links, processing outcomes,
saved model attempts, and append-only corrections and review decisions.
Assertions retain their origin and history. Unsupported logical forms remain
explicitly unresolved rather than receiving invented precise semantics.

**How do we check it?**

1. All accepted evidence resolves to the pinned source. Missing or ambiguous
   evidence and unresolved links have explicit outcomes.
2. Evaluation distinguishes correct meaning, missing content, unsupported
   content, actor errors, qualification errors, and boundary errors. The
   deliberately corrupted summary/actor probes must be detected.
3. A reviewer can correct, split, merge, reject, and attest; reopening the run
   preserves those actions and their targets. Original AI assertions remain
   available.
4. Raw-response parsing and candidate compilation each replay without a
   provider call. A deliberately failed window remains visible even when
   another window succeeds.
5. Repeat fresh extraction on the held-out section and compare the material
   differences and review effort. Byte-identical replay is not a substitute
   for this repeatability check.

Report counts and examples for this small set; do not turn them into a broad
accuracy claim. Compare reviewer correction time with a manual pass on a
comparable section. This establishes whether the tool saves work as well as
whether its records validate.

### Parallel implementation after the shared fixtures exist

| Owner | Bounded responsibility | Deliverable |
| --- | --- | --- |
| Integrator | Own the candidate format, assertion identity, Core mapping, and acceptance fixtures; prepare the small source index and integrate results. | Versioned formats, one hand-authored complete example, and the runnable end-to-end slice. |
| Evaluation worker | Label development examples; keep held-out labels out of prompt/repair work until output is frozen. Define error categories and review-effort recording. | Dataset, rubric, error report, and corrupted-output checks. |
| Extraction worker | Implement meaningful components, evidence, qualification targets, ambiguity, model-attempt accounting, and replay against the shared fixtures. | Candidate producer and compiler behavior with targeted regressions. |
| Review worker | Work from fixed input fixtures. Implement correction, split/merge, rejection, and attestation persistence using the existing Core records. | Local review flow that survives reopening and preserves history. |

The preparation work expands into its own worker assignment after one of these
streams finishes. Then test a whole chapter, cross-window assembly, repeated
passages, tables, and page coordinates. Add broader document parsing based on
observed source needs. Do not make PDF ingestion, distributed scheduling, a
universal rule language, or automatic adjudication prerequisites for the first
reviewable slice.

## Architecture review record

### Decision frame and lineage

| Element | Evidence and assessment |
| --- | --- |
| Product decision | [Owner clarification](../../docs/decisions.md#2026-09-06-validate-document-understanding-within-rulespec): Rulespec owns standalone document understanding; RefSpec supplies vocabulary. **KEEP.** |
| Existing design | The standalone plan separates source structure, processing windows, and semantic units; the LangExtract plan keeps model output provisional. These remain the right boundaries. **KEEP.** |
| Current implementation | The proof of concept extracts from one small real section and synthetic scope cases, validates evidence and Core records, and renders read-only review. It has not delivered the manual-review workflow. |
| Specification authority | [constraints/README.md](../../constraints/README.md):9–28 makes CUE the schema source and keeps profiles dependent on Core. Add only the missing document semantics; do not duplicate generic evidence or review schemas. |
| Superseded ownership text | [The release specification's opening clarification](../../spec/rulespec-releases.md):8–16 permits local Rulespec preparation. Older prepared-input release restrictions and fixture comments do not reverse that decision. Actual release exchanges retain their requirements. |

### Dependencies and consumers

The local application depends on ordinary input/model libraries and Rulespec
data/validation components; a RefSpec adapter supplies vocabulary. The
standard-library-only projection package and thin artifact package should
retain their existing dependency boundaries. Put model and application
dependencies in the new application package.

The first consumer is a human reviewer using exact source links and saved
decisions. Later consumers may use the rulebook's immutable assertions and
evidence. Platform release validators are optional exchange boundaries, not
mandatory stages of a local run. Full Federal Register graph assembly and
tag-only candidate verification do not fit every manual rule unchanged.

### Invariants and user value

| Invariant or value | Status at review | Practical consequence |
| --- | --- | --- |
| Local operation without other platform products | Preserved by the prototype and accepted direction. | The next build can proceed inside Rulespec. |
| Evidence matches the pinned text | Verified for the recorded small cases and tested refusal paths. | Reuse the grounding implementation; add evidence for structured meaning. |
| Valid structure implies correct meaning | Explicitly false; demonstrated by F1. | Display and measure the assessments separately. |
| Proposition identity survives non-proposition changes | Violated by the prototype; F2. | Repair before persisting review targets. |
| All work is accounted for and reproducible | Partial; F3. | Add raw parsing replay and per-window outcomes before scale. |
| A user can finish review and resume later | Not implemented. | Make this the first complete product milestone. |
| Review saves user effort on unfamiliar source material | Not measured. | Record correction time and unresolved work, alongside extraction errors. |

### Counterfactuals considered

- **Connect existing modules without new semantic work:** simpler, but the
  current tag verifier, schemas, and release checks do not discover or verify
  complete rules. Keep their useful pieces and supply the missing producer.
- **Scale document preparation first:** tests throughput and layout while
  leaving meaning and review value unresolved. Defer expansion beyond the
  bounded source needs of the first milestone.
- **Send all Core schemas directly to the model:** adds identity and metadata
  work without resolving rule semantics. Retain a small model-facing view
  with an explicit mapping to Rulespec-owned definitions.
- **Build a general executable rule language now:** exceeds the immediate
  source-understanding goal. Preserve unsupported logic honestly and use
  worked examples to grow the profile when justified.

**Verdict: RECONSIDER the delivery plan as previously framed; KEEP the product
direction.** The revised milestone and work split above address the review's
architectural concerns. The implementation findings remain open.

## Verification and saved evidence

- Proof-of-concept suite: **20 passed**, with two rdflib deprecation warnings.
- Existing projection package suite: **30 passed; 101 subtests passed**.
  Command: `PYTHONPATH=packages/rulespec-projection/src:src .tools/document-poc-venv/bin/python -m pytest packages/rulespec-projection/tests -q`.
- Offline evaluator and identity probes:
  [review-checks.json](2026-09-07-document-understanding-review-checks.json)
  records the mutations, outcomes, and input hashes. Recorded model artifacts
  were not changed.
- No new model calls, full repository test run, Rust test run, release, or
  publication occurred during this review.

The earlier recorded v2 runs' 20/20, 12/12, and 7/7 results are targeted
regressions on one development document and two synthetic cases. They are
not independent accuracy measurements. This review adds evidence about the
limits of those checks, not a new model-quality score.
