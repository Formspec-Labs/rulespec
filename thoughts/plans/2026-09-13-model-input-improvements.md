# Model input improvements: prioritized task list

**Iteration closed — September 13.** The
[final repair-format comparison](../experiments/2026-09-13-repair-finish/README.md)
generated **0/10 complete fresh repairs in each arm**, while preserving the four
complete-control outcomes per arm. Sparse output did not meet either adoption
route and is deferred. The standalone checker remains deferred. Retain the
already committed provider-setting and identifier fixes; verify the local
installation matches them as part of this closeout. The historical tasks below
are an evidence-backed backlog, not instructions to continue automatic experiments.

The finishing point is the existing extraction → source-linked records → review
and export path, with an explicit limit on independently complete rules. Use
concrete documents and feedback to decide whether to reopen repair work. Do not
add another default pass, schema or prompt patch to complete this list on paper.

Improve independently usable rule meanings while preserving the simple extraction
path. This list follows the [independent input review](../reviews/2026-09-13-model-input-construction-review.md)
and [construction experiment](../experiments/2026-09-13-explicit-rule-construction/README.md).
Previous checkpoint: the [two-factor diagnostic](../experiments/2026-09-13-checker-input-factors/README.md)
finds **8/8** correct unchanged-reading judgments with competing edits versus
**6/8** checking the reading alone. Extra `link_issues` do not change correctness
counts; neither factor meets the preregistered repeated-failure criterion, so the
cause remains unresolved. The standalone prototype stays deferred and production
unchanged. Next test actual repair generation on fresh sources with manual source
review as primary evidence and the comparison checker advisory. Do not add prose
warnings, optional fields or fabricated edits to satisfy the checker.

The preceding [fresh positive-task comparison](../experiments/2026-09-13-fresh-field-completeness/README.md)
passes its preregistered checker gate: **24/36 to 36/36** shared edit judgments,
**1/6 to 6/6** needed repairs, and **16/16** explicit no-change decisions correct.
All redundant-field and wrong-edit controls pass; useful actor/link corrections
survive. Fresh checker tokens increase 17.8%, with 44.4% more assessed decisions.
The concrete integration tasks are at the end of this list. Production remains
unchanged by this experiment; M5 repair generation still needs separate evidence.

M2 is implemented and verified. M3's identifier presentation is integrated, though
its original semantic diagnostic failed. Earlier M4 comparisons and field-only
paragraphs remain recorded below, with their failed gates intact. The successful
policy is the unchanged positive shared task, not either field-only revision.

Reuse CUE definitions, passage catalogs, evidence resolution and the current review
path. Keep useful schema descriptions and semantic examples. Preserve original
captures and review history. Model-behavior changes require comparisons; code and
schema validity alone do not establish extraction quality.

## First: define success and fix known input problems

- [ ] **M1 — Define the complete reading we want.** Small specification change.
  State that a selected reading must identify its actor, force, action and all
  source-supported governing conditions, exceptions, alternatives and timing,
  where applicable. Definitions and impersonal statements need not invent actors.
  Explain incoming qualifications as well as references within the selected rule.
  For a permission with separate content requirements, preserve both meanings
  without inventing loss of permission for noncompliance. An exemption must name
  what it waives; when needed for independent use, explain surviving duties as
  separate obligations, never as invented prerequisites for the exemption.
  **Done when:** generation, checking and manual labels use the same criterion.
  Labels distinguish faithful wording, complete retained document meaning and
  independently usable readings. Existing disputed labels remain visible.

- [x] **M2 — Bring Gemini 3.8 request settings into line with its current API.**
  Small compatibility fix. Trace extraction, audit and refinement through
  `_create_model` and `_record_window`; remove deprecated sampling parameters and
  `candidate_count` from new 3.8 requests, including defaults inserted by the
  provider library. Retain supported thinking levels and output limits. Update
  affected CLI/configuration descriptions so they do not promise an effective
  temperature control that has not been established. Follow the exact-model
  [migration guidance](https://ai.google.dev/gemini-api/docs/generate-content/latest-model),
  updated September 3, rather than older generic temperature advice.
  **Done when:** request-capture tests and a bounded live smoke verify the actual
  new request shape; saved runs still replay through the existing capture design.
  Record compatibility separately from quality. Hold the new settings constant
  in subsequent comparisons; do not rewrite historical parameter receipts.

- [ ] **M3 — Keep checker identifiers and reference status consistent.** Small
  presentation fix in `_model_packet` / `_challenge_prompt`. Use the same short
  aliases for proposed targets and their relationships; avoid sending a redundant
  application revision identifier as apparent source-derived meaning. Retain
  identifier resolution and provenance internally. Distinguish a located target,
  an unresolved canonical reference, and an unassessed semantic relationship;
  these statuses are not interchangeable. Navigation is not exhaustive.
  **Done when:** the saved cell 6 target resolves identically before and after the
  presentation change, with no opaque identifier needed for semantic checking.
  Wrong-target and ambiguous-target controls remain invalid. A fresh checker
  diagnostic must still detect cell 6's separate action/object error; removing
  the misleading identifier does not make that proposal correct.

## Next: test the repair interface and its evaluation

- [ ] **M4 — Give generation and checking the same task, including no-change decisions.**
  Moderate change; test before adoption. Reuse one concise task description and
  selected-target set in the existing optional repair/check path. Ask the checker
  to assess the resulting selected reading, including targets left unchanged.
  Report an unassessed target as unassessed. Explain that empty optional fields
  may be intentional: adding action/object structure alone does not demonstrate
  repair of a missing condition. Avoid another default pass or a new task framework.
  **Done when:** a controlled checker test separates genuine completeness repairs,
  harmless enrichment, incomplete no-ops and correct no-ops. Include the saved
  notice omission, unchanged inspection permission and wrong-meaning controls.
  Keep checker verdicts separate from manual completeness labels and application
  approval. Depends on M1 and M3; use the M2 settings for both arms.

- [ ] **M5 — Test edits that return only the meaning and evidence that need changing.**
  Moderate experiment. Compare the current full replacement with a bounded
  changed-fields response, deriving field definitions from CUE and retaining
  untouched fields deterministically. Reuse the existing statement-to-`summary`
  mapping. Permit a genuinely necessary component correction; do not preserve
  a newly inconsistent scope or actor merely to keep the response small.
  Define omitted fields as unchanged, and explicit clearing separately. Avoid
  building a general patch language or a second hand-maintained meaning schema.
  **Done when:** the comparison measures complete readings, unnecessary edits,
  component regressions, quote refusals, checker acceptance and tokens separately.
  Keep task, checker policy, source, model and effort fixed. Test with M8's fresh
  cases after M4 establishes a usable evaluator. Fewer refusals alone is not
  evidence of more complete meaning.

- [ ] **M6 — Reuse passage selection for repair evidence; isolate optional failures where justified.**
  Moderate follow-up, only if evidence copying remains a material problem. Test
  using the existing passage catalog and resolver for repair evidence instead
  of retyping full quotations. Keep exact-word evidence where it serves a distinct
  purpose. Separately assess reuse of existing component-withholding behavior:
  a failed optional component may be withheld only when the remaining evidence
  independently supports the complete proposed meaning. Unsupported substantive
  changes must still fail; a valid main quote alone is insufficient.
  **Done when:** the saved pension list-marker failure is retained as a regression
  case, and tests preserve repeated-text locations, whitespace handling, missing
  passages and substantive-difference refusals. Report any retained repair and
  withheld component explicitly. Compare evidence selection and withholding
  separately from M5; do not bundle three changes into one claimed result.

- [ ] **M7 — Test simpler input layout without deleting useful meaning.** Lower
  priority. Separate stable instructions, source, existing readings, reference
  navigation and the final selected task consistently. Consider placing the
  specific task after the data, using supported instruction roles, and omitting
  unused empty draft metadata. Preserve full relevant source and useful CUE
  descriptions. Evaluate statement placement/naming separately from layout;
  required output fields do not have to contain invented values.
  **Done when:** one layout, ordering or instruction-redundancy change at a time
  improves accuracy or cost on a fixed comparison without losing conditions or
  evidence. Keep meaningful examples unless their removal passes evaluation.
  Current user-message instructions are not inherently invalid, and large character
  counts alone do not prove a context problem. Defer if M4–M6 solve the target issue.

## Evaluate and integrate only the useful changes

- [ ] **M8 — Freeze a fresh evaluation set before the next generation comparison.**
  Moderate evaluation work; prepare alongside M2–M4. Start with eight new source
  excerpts and two repetitions per arm. Include outgoing eligibility references,
  incoming exceptions, an exemption with a surviving duty, a permission plus
  content requirements, repeated clause labels, nested alternatives, unavailable
  references and a complete no-change control. Keep old failures as development
  regressions, separate from fresh-case results.
  **Done when:** source versions, scope, labels, uncertainty, calls/token/time
  ceilings and stop/adoption criteria are saved before calls. Review raw answers
  anonymously; measure omissions, overreach, field damage, no-op correctness,
  evidence validity, tokens and latency. Repetitions measure variability, not
  additional source coverage. Preserve all failures and requests.

- [ ] **M9 — Integrate the smallest supported result.** Small-to-moderate final
  step. Make coherent local commits for independent fixes and adopted behavior.
  Regenerate CUE-derived artifacts when definitions change. Run relevant existing
  extraction/schema/refinement tests, captured-request checks, provider-blocked
  replay and a fresh end-to-end smoke through review/export. Exercise combined
  sequential application as well as independent previews, including stale targets.
  **Done when:** evidence records exactly what improved, what remains experimental
  and what failed. No automatic approval or completeness claim follows from a
  schema-valid result. Keep refinement optional; stop adding prompt patches when
  a comparison no longer changes the decision.

- [ ] **M10 — Optionally compare OpenAI after the task is stable.** Deferred
  experiment, not a prerequisite for these fixes. Reuse the same source, field
  meanings and labels, with provider-compatible structured output and reasoning
  settings. For OpenAI strict output, required nullable fields represent absence;
  do not transplant the Gemini optional-property schema unchanged. Compare model
  choice separately from response shape and prompt changes.
  **Done when:** fresh paired results establish a useful accuracy/cost tradeoff
  under the same product criteria. Reading provider guidance is not an adoption test.

## Implementation locations and order

Use [extraction.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py)
for provider requests and initial prompting,
[refinement.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/refinement.py)
for repair/check input and decoding, and the existing
[CUE application definitions](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/schema_data/document-understanding.cue)
for model-facing meanings. Reuse tests in `test_extraction.py`, `test_schemas.py`,
`test_refinement.py` and `test_refinement_source_refs.py`.

M1, M2, M3 and fresh-case preparation can proceed independently. Finish M1–M3
before evaluating M4; then test M5. Pursue M6 or M7 only when remaining evidence
justifies them. Integrate proven fixes through M9 without waiting for every
optional experiment. M10 remains a separate decision.

## September 13 checkpoint

- M1: shared definition and frozen manual criteria saved in the experiment's
  `TASK.txt`; used by the experimental checker. Wiring it into production
  generation and checking remains unadopted with M4.
- M2: implemented across extraction, audit, refinement and structural enrichment,
  including actual SDK defaults, Core provenance, CLI, review and replay. A live
  smoke succeeds; original acquisition settings and capture bytes are preserved.
- M3: short aliases and reference-status explanation integrated as an input
  correctness fix. The bad action/object diagnostic was accepted, so the full
  semantic success criterion is **not met**. Wrong-target controls remain rejected;
  ambiguous/unknown target and exact-evidence regression tests pass.
- M4: completed controlled test, **not adopted**. Shared task scores 22/24 versus
  current checker's 10/18 plus six unassessed no-ops. It misses the incoming notice
  exception twice. On the eighteen shared edit candidates the score is 18/18.
  Labels, denominators, repeated-source limitations and raw failures are retained.
- M5–M8: not started; M5's evaluator prerequisite failed. Next experiment should
  test source-to-baseline applicability accounting on unseen excerpts, with
  unrelated-duty controls, before testing response-size changes.
- M9: local API/input fixes verified, with 709 extractor tests, Core fixture and
  parity checks, native compilation, saved-capture reprocessing and a live
  extraction/review/export smoke. Sequential review observations and stale
  revisions tested; combined proposed meaning-edit application remains conditional
  on a future treatment being adopted. No push or release.
- M10: remains deferred.

## Fresh-source validation checkpoint — September 13

The [fresh comparison](../experiments/2026-09-13-fresh-complete-reading/README.md)
used eight new source excerpts, ordinary extraction drafts and two repetitions
of each checker arm. Shared edited-candidate accuracy improved from **19/32 to
26/32**, with five contexts improving and one regressing. Most of the gain was
rejecting unnecessary action-field filling (**0/6 to 6/6**). Needed complete
repairs improved only **3/10 to 4/10**. Both versions rejected all sixteen known
wrong-edit judgments. Shared-task no-change accuracy was **10/16**.

This confirms useful value beyond the original documents, but misses the
preregistered 85% edit and 75% no-change thresholds. Medical-exception detail is a
real regression. Privacy responses invert one negated instruction; the original
notice exception remains missed. Keep the full checker replacement experimental.
No production behavior changed in this validation. Eight native captures and all
94 judgments replay/re-decode without provider access; 44 calls were made without
retries. Initial partial extraction/component issues remain retained.

Next bounded work, in order:

- [ ] **M4a — Isolate rejection of unnecessary component edits.** Compare the
  current checker with only a clear instruction that empty optional action/object
  fields do not by themselves require repair. Preserve legitimate corrections
  to wrong populated fields and useful actor/term links. Include the three
  complete-reading controls, the lost medical detail and a real component-error
  correction. Retain useful CUE field semantics; avoid a blanket equality rule
  that rejects every edit with an unchanged default statement.
- [ ] **M4b — Test positive wording for inherited conditions.** Change only the
  ambiguous negated sentence in the shared task, then compare on the actual
  privacy inversion, medical omission, old notice failure and unrelated-duty
  controls. Explicitly assess the selected default statement rather than crediting
  complete meaning retained elsewhere. Follow a successful diagnostic with new
  source excerpts; the eight sources above are now development data.
- [ ] **M8 continuation — Preserve an untouched generation holdout.** The eight
  fresh checker excerpts are delivered; they did not test generation of repairs.
  M5 still needs its own frozen fresh comparison once a usable checker policy is
  established. Do not count repetitions or constructed edits as new documents.

M2 and the mechanical M3 fixes remain integrated. M9's next production integration
should be the smallest demonstrated behavior from M4a/M4b; M6, M7 and M10 remain
conditional. This checkpoint supersedes the earlier suggestion to redesign
source-to-baseline accounting first: isolate the observed optional-field benefit
and the concrete instruction ambiguity before expanding the pipeline.

## Instruction-isolation checkpoint — September 13

- [x] **M4a diagnostic completed; not adopted.** A single optional-field paragraph
  changes unnecessary-edit rejection from 0/6 to 6/6, while retaining all four
  component/link fixes and rejecting all twelve wrong edits. Medical-repair
  acceptance falls from 1/2 to 0/2. Total 17/24 to 22/24 is a bounded benefit with
  a regression; the preregistered gate fails. Do not add this paragraph alone.
- [x] **M4b diagnostic passed; fresh-source validation now passed below.** Replacing only
  the negative sentence in the shared task improves 25/32 to 32/32, across all
  three target contexts. Needed repairs improve 5/8 to 8/8; incomplete no-change
  rejections improve 4/8 to 8/8. Wrong-target/meaning and complete no-change controls
  remain correct. Raw rationale imperfections are recorded separately.
- [x] **Validate the unchanged positive shared task on eight new excerpts.**
  Compare with the production checker under frozen source-based criteria and
  current provider settings. Preserve all shared-edit and no-change denominators,
  original captures, rationale problems and unavailable-context controls. These
  now-repeated cases are development regressions, not that fresh cohort. Avoid
  combining M4a's paragraph with the successful wording.
- M5 repair generation and M8's untouched generation holdout remain pending. M9
  may integrate the smallest supported checker policy only after the new-source
  decision. No production behavior changed in this diagnostic.

Evidence: [plan, raw review and results](../experiments/2026-09-13-checker-instruction-isolation/README.md).
Forty fresh calls, 112 judgments, 286,274 tokens and 350.7 summed provider seconds;
all request bodies and saved-response decodes verified without provider access.

## Requested field-necessity iteration — September 13

- [x] **M4a revision tested; not adopted.** Replacing the optional-field paragraph
  with a semantic-change criterion improves 28/30 to 29/30. Both versions reject
  all six plain redundant fills and six new cosmetic variants, accept all four
  needed component/link edits, and reject all twelve wrong edits. The revised
  version accepts the needed medical repair 1/2 times versus 0/2, so the gate fails.
  Reported token use increases 29.6%. Twenty-four calls, 60 judgments; no retries
  or mechanical failures. [Evidence](../experiments/2026-09-13-field-necessity-revision/README.md).
- [x] **Extend the fresh-source criteria with these field controls.** Include
  redundant action/object fills, synonymous rewording that adds no meaning, valid
  component corrections and missing qualification links. Compare the unchanged
  positive shared task with production as already planned. Do not append another
  field paragraph, add a default pass, or reject every edit with unchanged prose.

The field-noise distinction is supported on these controls. The unresolved issue
is reliably assessing needed meaning in the selected statement rather than
crediting detail retained elsewhere. The current results do not isolate the
effect of instruction ordering. Fresh-source and generation evaluations remain
separate, and production remains unchanged.

## Fresh positive-task result and concrete integration steps — September 13

The [eight-source comparison](../experiments/2026-09-13-fresh-field-completeness/README.md)
passes all fourteen preregistered checks. It improves six source contexts with no
observed regression. The needed-repair gain is now present on new sources, as well
as the field-noise benefit. Excluding the three uncertain labels still improves
shared edits from 16/26 to 26/26. This supports the following bounded proposal;
it does not automatically adopt the experiment or test generation of repairs.

### Existing implementation and actual gaps

| Capability | Existing code | Integration work |
|---|---|---|
| Complete meanings and component semantics | CUE-derived `meaning`, `CANDIDATE_SCHEMA`, `MEANING_FIELDS` | Reuse; no new meaning schema |
| Source and current claim selection | `refinement._packet`, `_model_packet`, `_challenge_catalog` | Make the selected statement aliases explicit for the checking task |
| Source-grounded model judgments | `CHECK_SCHEMA`, `_decode_checks`, passage resolver | Reuse judgment format and exact source resolution |
| Validated meaning edits and history | `_decode_proposals`, `_action`, `ReviewStore.preview/apply` | Keep mutations behind these checks |
| Unchanged selected readings | No mutation operation; generator observations have only quote/rationale/disposition | Build temporary checking candidates from selected current records; do not infer target approval from observations |
| Recorded assessments | `_withheld_observations`, `_observation_action`, review `observe` action | Extend assessment mapping for unchanged targets without creating replacement claims |
| Replay and provenance | `refine_run`, `replay_refinement`, captured request/runtime files | Record selected aliases/candidates and reproduce them during replay |

Production currently calls the checker only when `prepared` contains edits/additions.
An empty proposal list is therefore unassessed, not an independently verified
complete reading. Replacing `CHECK` alone would not deliver the tested no-change
behavior. Existing `already_represented` observations also lack a selected claim
alias and cannot safely fill this gap through fuzzy quote matching.

### Ordered tasks

- [ ] **M9a — Add the tested policy at the focused checking seam.** Reuse the exact
  winning task text from `instructions.json` B and its explicit selected aliases.
  Keep the policy in one application constant. Extend `_challenge_prompt` to accept
  an explicit set of selected current aliases for a bounded optional check; retain
  the existing catalog, draft meaning and navigation. Do not silently select all
  60 context records or transfer the policy to initial extraction. A whole-run
  selection policy and add-only recovery were not measured here.
- [ ] **M9b — Account for unchanged selected statements without extra model output.**
  Construct a temporary `no_change` candidate from each selected current reading,
  alongside valid proposed edits. Copy the current fields deterministically and
  assign distinct candidate IDs. Reuse `CHECK_SCHEMA` and `_decode_checks` for the
  judgments. These are assessment inputs, never mutation proposals: keep them out
  of `_decode_proposals`, `_action` and the edit-application loop. An unchanged
  judgment is about that saved revision; invalidate its relevance after an edit.
  Keep missing/invalid judgments and unresolved targets explicitly unassessed.
- [ ] **M9c — Preserve assessment and evidence status separately.** Reuse the review
  `observe` action for unchanged-target judgments, source selections, model identity
  and capture provenance. Reuse exact revision/claim mapping; do not interpret
  unsupported as an automatic deletion or supported as human approval. A semantic
  correction must not clear `component_evidence_unresolved` unless the evidence
  resolver actually succeeds. Retain cell 20 as a status counterexample.
- [ ] **M9d — Verify integration before treating it as the production checker.**
  Exercise empty proposals with selected targets, missing/duplicate candidate IDs,
  wrong aliases, context-only edit refusal, unknown source, useful actor/link fixes,
  redundant edits and stale revisions. Validate main-quote bounds as well as
  evidence bounds: the fresh synthetic diagnostic inherited a parent's top-level
  offsets, despite its correct evidence location. Keep `refine-replay` equivalent, including
  observations and combined sequential edits. Use existing refinement/source-ref
  tests and saved captures. A bounded live bridge must check the actual integrated
  candidate construction and request, because the experiment supplied candidates
  externally. Any edit-only or newly bundled request differs from the tested policy;
  save that comparison rather than assuming equivalent behavior. Initial extraction
  gains no default pass; expose the check through the existing optional review path.
- [ ] **M5/M8 — Test repair generation on untouched sources using this evaluator.**
  Once the checking seam is verified, compare existing full replacements with the
  proposed changed-fields response under the same shared task and checker. Freeze
  new source criteria and raw-label review before calls. Measure generated complete
  readings, preserved fields, evidence refusals, unnecessary edits, applied outcomes
  and usage separately. The eight checker sources above are now regression cases,
  not the fresh generation holdout. Keep unavailable-context and unrelated-duty
  controls from earlier studies. Do not add the failed optional-field paragraphs.

M1's completeness criterion has checker evidence, but its generation/checking
alignment remains unfinished. M4's checker evaluation is complete; its production
integration is pending M9a–d. M6 evidence changes, M7 layout changes and M10 broader
pipeline changes remain conditional. No further wording tuning on this cohort is
needed before the integration and generation work.

## Standalone integration bridge checkpoint — September 13

- [x] **Build and mechanically verify the focused checker prototype.** The
  candidate command selects exact current statements, copies unchanged candidates,
  records source-grounded assessments without meaning edits, preserves evidence
  warnings/approval, and replays through existing review machinery. All 729 tests
  pass. Code and tests are retained in the experiment's implementation patch.
- [x] **Test actual integrated requests before adoption.** Four known sources,
  two repetitions, 16 fresh calls. Source and meaning remain identical; production
  review adds current `link_issues`, and standalone input removes the constructed
  edit alternatives. Old comparison input gets 8/8 shared no-change judgments;
  standalone gets 7/8. Both catch every real billing/offset omission. One leave
  no-change response conflates complete meaning with unresolved record metadata.
  The all-correct/no-regression gate fails. Original labels and failures remain.
- [x] **Isolate the two actual input differences before another policy change.**
  Use the saved leave failure and unaffected hazard control: competing candidates
  present/absent crossed with saved/current link-status detail, same source and
  policy, two repetitions. Preserve genuine warnings in captures; do not repair
  the benchmark by clearing them or rewriting correct prose. If status visibility
  drives the result, test a clear distinction between meaning and traceability.
  If competing candidates drive it, keep the checker attached to comparisons
  rather than treating standalone checks as equivalent. Neither explanation is
  established by the present bundle. Freeze a bounded comparison before calls.
  **Completed below:** the two-factor comparison is directional but does not
  meet its repeated-failure criterion; no causal explanation is established.

M9a–c exist as a tested prototype, not adopted production behavior; M9d's
mechanical checks pass and its live gate fails. The code is restored to its prior
production version. M5/M8 repair generation remains separate; the earlier rich
candidate checker evidence survives, but standalone unchanged-reading approval
cannot yet be treated as an interchangeable evaluator. This checkpoint supersedes
the previous instruction to proceed directly with integration.

## Two-factor result and next useful work — September 13

- [x] **Separate candidate context from extra link status.** Sixteen fresh calls,
  two known sources and two repetitions per condition. Leave unchanged judgments
  are 2/2 with competing edits and 1/2 alone under both status settings. Hazard
  is 2/2 in every condition; all 24 edited controls are correctly rejected. Both
  false alarms cite real traceability limits without identifying an omitted
  supplied condition. The prompt's broad construction task leaves a plausible
  meaning-versus-record ambiguity. The preregistered mechanistic-lead gate is
  unmet; do not turn this directional pattern into a causal claim.
- [x] **Preserve the exact boundary and verification.** All sixteen actual inputs
  reconstruct and all forty judgments re-decode without provider access. Arm D
  exactly matches the previous standalone requests. Raw review precedes aggregate
  scoring. Total 133,159 tokens and 118.3 summed call seconds. Production remains
  unchanged; the prior integration patch and its failed gate remain intact.
- [ ] **M5/M8 — Move to actual repair generation with independent source review.**
  Freeze untouched source excerpts, complete/no-change controls, required
  component/link fixes, unavailable-reference cases and manual criteria before
  calls. Compare full replacement with the smallest CUE-derived changed-fields
  response, holding task, model, source and checker policy fixed. Feed actual
  before/after candidates and current statuses to the earlier supported comparison
  policy; record no-proposal cases explicitly without fabricated alternatives.
  Manually assess source completeness, field fidelity and unnecessary changes;
  checker agreement is a separate measurement, not the primary quality gate.
  Confirm accepted edits survive existing evidence validation and review/export.
- [ ] **M9 — Integrate only a demonstrated end-to-end improvement.** Standalone
  unchanged-reading approval remains deferred. Do not silently apply the saved
  prototype or require prose disclaimers to clear true record warnings. Reuse
  existing CUE definitions, review actions and capture/replay; keep initial
  extraction unchanged and optional checking explicit.

This checkpoint revises the earlier M5 prerequisite rather than declaring the
standalone evaluator fixed: use manual source judgments to avoid waiting for a
perfect automatic checker. Stop tuning this diagnostic cohort. Generation and
its actual checking requests still need fresh evidence before production adoption.
See [plan, raw review, scores and receipts](../experiments/2026-09-13-checker-input-factors/README.md).

## Final repair-format decision — September 13

- [x] **M5/M8 — Complete the bounded generation comparison.** Four new source
  excerpts, two repetitions per format, plus the exact old pension failure and
  one constructed actor error. Twenty-four generation calls follow four ordinary
  extractions. Both formats repair 0/10 fresh meaning gaps; complete controls stay
  unchanged 4/4. The fourth excerpt lacks its introductory force and its two
  readings remain explicitly uncertain, outside decisive counts. No fresh case
  was replaced or planted after extraction.
- [x] **Make the non-adoption decision.** Sparse output repairs the actor error
  2/2 versus 1/2 valid full replacements, but known/constructed gains do not meet
  the fresh-source gate. Five of its six proposals still emit all fields; two
  denial edits leave missing meaning unchanged. Total generation tokens increase
  8.9%. No new repair behavior enters production. Stop the optional checker phase
  because neither required fresh-repair outcome can be established by its verdicts.
- [x] **M9 — Close with preservation checks and usable guidance.** Reproduce the
  native extractions and generated proposals offline, exercise valid proposals
  through review/export in disposable workspaces, retain all warnings and source
  history, and verify the local installed tool matches the already committed
  checkout fixes. Keep the experiment and local delivery receipts with the result.

M1/M4 shared task adoption, M6 repair evidence changes, M7 layout changes, M10 model
comparison and the standalone prototype are deferred. They are not prerequisites
to using the current discovery/review pipeline. Reopen only for a concrete product
need with new evidence; this closeout does not schedule another experiment.
