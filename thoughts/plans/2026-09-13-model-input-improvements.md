# Model input improvements: prioritized task list

Improve independently usable rule meanings while preserving the simple extraction
path. This list follows the [independent input review](../reviews/2026-09-13-model-input-construction-review.md)
and [construction experiment](../experiments/2026-09-13-explicit-rule-construction/README.md).
Implementation update: see the [recorded checker comparison](../experiments/2026-09-13-complete-reading-check/README.md).
M2 is implemented and verified. M3's identifier presentation is integrated, but
its semantic diagnostic failed. M4 improved some judgments but failed its adoption
gate; M5 remains on hold.

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
