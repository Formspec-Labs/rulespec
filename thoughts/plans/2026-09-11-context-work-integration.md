# Bring delivered reference work back into the original context workflow

The user's current priority is to use the completed reference/source work in the original extraction and context-understanding effort. The publication-metadata experiment remains saved, but is not the prerequisite or the next diversion for this effort. This plan changes priority; it does not adopt any failed experiment or claim that the integration below is already implemented.

## Intended result

Given an extracted statement or selected source passage, assemble the original section, related extracted meanings, located reference provisions, and relevant recorded feedback. Use that evidence to determine which conditions, definitions, alternatives, and exceptions the statement actually needs. Keep supported findings connected to the original source and review history. The same evidence should remain usable for automatic discovery and later reviewed workflow preparation.

Preserve one readable primary statement and sparse additional meaning. Do not add a mandatory explanation for every field or treat every located citation as a governing rule.

## Reuse map, checked against the current implementation

| Delivered work | Use in the original context effort | Connection still needed |
| --- | --- | --- |
| Statement retention and whitespace/range fixes, R4/R23 | Build the comparison from complete retained statements and exact source slices, not the old lossy decode | Reprocess into a separate run where necessary; preserve original captures/reviews and explicit changed identities |
| USLM/eCFR preparation and native source addresses, R11/R14/R23 | Select actual containing sections and publisher targets instead of reconstructing their hierarchy from prose | Use existing `SourceIndex`/prepared sections in context assembly |
| Qualified CFR/USC, compilation and named-act readings, R2–R7/R13 | Identify what a reference actually says and preserve its scope and competing interpretations | Supply only relevant located targets as context; identity-only or unsupported readings stay unresolved |
| Local and caller-supplied external target bodies, R11/R12 | Deliver the referenced provision with its containing section and source/edition evidence | Bridge existing `reference_scan.targets` and `reference_sources` to a source-aware model input |
| Shared discovery evidence, R17 | Store/describe an occurrence once, retaining all roles and source identities | Reuse that table; a display/request adapter may emit its selected text once without replacing the stored evidence |
| Reference feedback, R18 | Show the exact challenged reading, comment, reader pins and unresolved source diagnostics during context review | Select relevant existing observations; do not treat comments as source authority or scanner overrides |
| Capture, replay, validation, review revision checks, R1/R4/R18 | Reconstruct requests and keep proposed meaning changes reviewable | Include selected external inputs and adapter version in the existing captures; test source/review boundaries |
| CUE meaning fields, terms, `ApplicabilityScope`, `EvidenceBinding` | Express any demonstrated meaning correction in existing structures | Keep `providesContext`, `definesScope` and `qualifies` distinct; availability does not decide the correct role |

Completed publication/source metadata already attached to target bodies belongs in the source context. The unverified 93-row catalog/body association, new shared-vocabulary connections, unadopted title/range heuristics and general paragraph lookup are not completed dependencies. They must not block use of the delivered capabilities or silently enter through this plan.

Relevant code: `documents.load_document`, `documents.source_slicer`, `core.evidence_parts`, `extraction.resolve_passage`, `uslm.SourceIndex`, `references.scan_references`, `reference_sources.attach_reference_sources`, `discovery.export_discovery`, `reference_feedback.reference_observation`, and `ReviewStore`.

## The missing bridge

The delivered reference export already holds target/source tables, containing records, publication observations, exact source evidence and unresolved edition status. It does not automatically feed them to the extractor or audit.

The current extraction `passage_catalog`/`resolve_passage` and audit/refinement grounding functions operate against one prepared document. External text must not be appended while retaining primary-document coordinates or passed through a resolver that assumes those coordinates belong to the primary document.

For the experiment, use an explicit lookup from each supplied source alias to its pinned document and that document's existing passage catalog. Dispatch evidence selection through the existing resolver for that source. Keep the target and source IDs already supplied by the reference export. This is request assembly, not a second citation parser, new identity scheme, new Core schema or migration layer. Assess whether an existing schema can carry the source-qualified selection before extending a model-facing profile.

Use current review observations to expose challenged readings separately from source text. A reported error neither authorizes a correction nor invalidates all other links. A uniquely located provision with `edition_match=not_established` must retain that limitation.

## Sequence

1. **Freeze a current integrated input comparison without model calls.** Use original refrigerant and seatbelt failures, a definition-by-reference case from the completed USLM experiment, an actual external-reference case from the delivered body lookup, and noninheritance/ambiguity controls. Select current retained outputs where available. Pin current source and installed reader identities; do not upgrade sibling wheels. Preserve each input's development or constructed status.
2. **Assemble context from the delivered exports.** Start with the fixed statement, its exact evidence, and a complete short enclosing section. Add relevant related-claim evidence and one-hop, uniquely located reference provisions with their existing containing records. Include relevant feedback and explicit unavailable/ambiguous targets. Keep sources separate, avoid recursive crawling, and deduplicate request text by source position while retaining roles. Do not infer omitted citation titles or collapse a range to one endpoint.
3. **Check the bridge mechanically.** Verify original-source slices; different editions with matching offsets; repeated occurrences; local/external duplicate targets; retained refusals and disputed readings; inserted separators; unavailable target bodies; and unchanged original statements/reviews. A context-limit decision must report what was omitted. An unlimited whole-manual dump is not the intended default.
4. **Run a focused meaning comparison, then decide.** Hold the draft and precise scenario questions fixed. Compare existing context with the integrated context assembled above. Ask whether the draft omits a governing condition, misstates modality, or leaves a referenced definition unresolved. Use the original raw cases plus controls. Reuse existing assessment dimensions/source-evidence capture rather than demanding new explanations across all extraction fields. Freeze exact questions, source-supported labels, settings and request order before calls; initial diagnostic bound is six cases × two arms, at most 12 calls, no tuning or retries. These are selected diagnostic cases, not fresh generalization evidence.
5. **Connect only demonstrated findings.** If the focused comparison earns further work, map proposed corrections to existing meaning fields and apply through preview/revision checks in a separate saved run. Test target decisions and supported-subset application under R25 independently. Keep unsupported/unknown decisions as observations. Use the same evidence after retrieval for discovery; automatic discovery still does not require universal manual review.

Do not count the whole 12-call budget as spent or authorized adoption: this document specifies the next comparison, and no calls were made while writing it. Final source/label choices and acceptance criteria must be frozen before execution.

## Decision boundaries

The original availability experiment established that fuller sections could supply missing passages. The later R15/R16 experiment established that appending sections/reference targets to broad extraction requests did not recover its declared meanings and introduced a modality regression. Both findings remain true.

The next distinct hypothesis is that a **fixed statement and explicit interpretation question** can use the delivered context more effectively than the previous broad extraction task. Its result cannot be credited to better extraction, better reference recognition, or any one component of the integrated context bundle.

The focused comparison must report gains, regressions, abstentions, wrong inheritance, unresolved editions/targets and input/answer/thinking usage separately. A gate needs meaningful improvements on natural cases and no new critical source/actor/modality/scope errors on controls; freeze the exact counts with the cases. Source availability or passing JSON validation alone cannot pass that gate.

If it fails, preserve the integrated source/evidence capability as navigation evidence and record that the selected interpretation task did not improve. Do not return automatically to metadata work or increase prompts indefinitely. Choose the next hypothesis from the actual failed readings in the original context workflow.

## Current status

The [integrated-context comparison](../experiments/2026-09-11-integrated-context-check/RESULTS.md) is complete. Six cases, exact inputs/questions, current runtime bytes and acceptance criteria were frozen before twelve live calls. The bridge grounded all 170 input passages, preserved duplicate occurrences/source identities, rejected unseen ranges, retained ambiguous/missing targets and feedback, and reproduced all twelve decoded captures without model calls.

Integrated context recovered additional grounded meaning in three of four natural cases. The broad gate nevertheless failed: the seatbelt answer added an unsupported adulthood restriction and broadened a paragraph-level exclusion; reported token use was 2.145× baseline against the 2× gate. No automatic context-check pass or meaning correction is adopted. R25 remains independent.

The narrower deterministic evidence integration is implemented as `context.export_context`, `context.resolve_context`, and `rulespec-understand context-export`. It connects current retained statements, enclosing sections, related claims, existing reference/source readers, exact target bodies, shared source metadata, and saved reference feedback. It records allowance decisions and preserves complete relevant observations outside the readable material. It reuses the current evidence/resolver/review machinery; no model-output schema or Core meaning structure was added. All six cases retain the experiment's evidence selection, with an explicit focus role and metadata stored once.

The automatic interpretation/correction work is deliberately deferred under this plan's failure branch. Using the export for navigation or supplying it explicitly to a later check is available; it is not a claim that the extractor now automatically discovers or fixes missing meaning. See the experiment's `delivery/` artifacts for validation and concrete examples. Original captures, statements, approvals and prior failed experiments remain intact. The independent metadata/body-association work stays independent.

This is the current context-work plan under R11/R12/R16/R18/R24, with R25/R26 kept distinct. The [canonical task list](2026-09-10-reference-integration-task-list.md) retains all completed and open work; the [reuse checkpoint](../reviews/2026-09-11-reuse-resume-checkpoint.md) retains the independent metadata experiment's stopping point.

## Follow-up audit comparison

The [comparison-stage experiment](../experiments/2026-09-11-context-audit-comparison/RESULTS.md)
is complete: two fresh annual CFR extractions, four shared source inventories and
ten comparisons across five pairs, with no leading questions or provider retries.
Expanded context found no confirmed additional fresh-source defect. Both arms
missed the equipment statement's overriding special-flight-permit exception and
failed to identify the saved unsupported adulthood restriction. Expanded context
avoided one scope false alarm on a constructed faithful control, but added an
uncertain waste-petition restriction and used 1.93× comparison tokens. This does
not pass the declared integration gate.

All 138 comparison evidence selections grounded and all ten saved comparisons
replay identically. Mechanical success does not change the semantic verdict.
The context export is committed in `6942225`; no automatic audit pass or correction
is adopted. Stop the comparison here. A future process experiment would need to
separately test source-first inventory over assembled context on a broader frozen
set. R25 remains independent.

The user's annual-format question also exposed a concrete R23 reader task:
GovInfo annual `CFRGRANULE` is currently refused. Add native support in RefSpec's
existing reader, preserving addresses, edition metadata and original-source
coordinates. This experiment used an installed reader only to prepare frozen text;
no production dependency or native-format support was added. Details and scope are
saved in its [source-preparation note](../experiments/2026-09-11-context-audit-comparison/SOURCE-PREPARATION.md).
