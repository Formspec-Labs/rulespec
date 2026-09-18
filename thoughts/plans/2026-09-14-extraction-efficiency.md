# Extraction efficiency: completed tests, retain current production

## Proposed next decision: complete-record usefulness

The user's challenge clarified the conclusion: the granularity instruction is
promising but inconclusive, not demonstrated worse. The recorded statement
differences are real; the small sample does not establish that the instruction
caused them. The existing discovery export preserves scope and evidence alongside
statements. Its full records may therefore gain more from splitting than a
statement-only assessment shows. Preserve the completed study's criteria and
results; the revised assessment below belongs to a new comparison.

Recommended follow-up, proposed only; no new model calls or adoption authorized
by this planning step:

- [ ] Freeze five cases: the drug-record splitting case, monitoring referent case,
  Addressable qualification case, and two previously untested list-heavy sections.
  The fresh sections must include inherited scope and a choice that must not
  become multiple mandatory duties. Freeze source-based expected units before
  generating outputs; do not tune the sentence or choose cases based on its output.
- [ ] Assess a requirement as its statement plus structured scope and explicit
  relationships from the existing export. Count individually selectable, faithful
  requirements, not total records. Separately record standalone statement quality
  and meaning recoverable only by interpreting quoted evidence. Merely copying
  the source into evidence does not earn complete extracted-meaning credit.
- [ ] Compare the unchanged current prompt against the same one added sentence,
  three repetitions per arm per case: thirty extraction calls maximum. Keep
  source presentation, CUE schema and model settings fixed; alternate arm order,
  retain failures, and allow no retries or extra tuning. Reuse the existing harness
  and export; add no production pass, schema or exporter. Cap capture at twenty
  minutes, allowing an in-flight request its existing five-minute timeout.
- [ ] Review anonymized outputs using the frozen source checks. Check who acts,
  what they must/may do, governing scope, alternatives, exceptions and reference
  targets. Record each case's repeat spread and tokens per complete selectable
  requirement, with total usage and standalone weaknesses also visible. Repeat
  counts describe variability; reviewer agreement does not add model samples.
- [ ] Decide at the bound. A candidate for integration must improve complete
  selectable requirements in at least two of three comparisons on each fresh
  case, with no increase in runs containing material meaning errors on the known
  controls. Wrong force, lost governing scope, false mandatory alternatives or
  invented duties are material; wording differences alone are not. Evidence-only
  recovery and statement-only defects stay visible as separate tradeoffs. Shared
  errors need not all be fixed. A pass supports a bounded adoption decision, not
  a general accuracy claim; mixed results mean retain the current default and
  close this instruction experiment rather than add another prompt patch.

## Current decision

The isolated granularity test is complete: twelve calls across five known section
cases, with two drug-record repeats per arm. The added sentence separated all
thirteen list contents in both repeats, versus one control repeat. Some variant
outputs had weaker governing context and report referents in default statements
and replaced an explicit formal qualification with a paraphrase. The original
complete-meaning gate did not pass. Retain current production; the bounded study
is closed and the proposed follow-up above has not run. See the [results](../experiments/2026-09-14-granularity-only/RESULTS.md)
and [frozen plan](../experiments/2026-09-14-granularity-only/PLAN.md).

- [x] Freeze the one-sentence intervention, existing sources and source checks.
- [x] Run contemporaneous controls and treatment, with no retries or prompt tuning.
- [x] Review anonymized outputs, replay and validate captures, then stop with a decision.

All 133 records passed Core compilation and all twelve native replays matched;
that did not prevent the semantic tradeoffs above. B used 8.5% more total tokens;
the decision rests on meaning, not cost alone. Production, schema, section windows
and source presentation remain unchanged. No commit was made.

## Completed grouping study

The user's subsequent "Continue" reopened one narrow investigation: compare
explicit section grouping with current separate extraction on three fresh CFR
pairs plus the known CSBG pair. The [new frozen plan](../experiments/2026-09-14-grouping-fresh/PLAN.md)
allowed twelve model calls, now completed. Production remains unchanged; coordinate removal,
concurrency and the archived twenty-call proposal are outside this round.

- [x] Acquire three fresh source pairs and freeze source-based checks, inputs,
  current runtime and unchanged grouping directive.
- [x] Run the twelve-call paired comparison without retries or prompt tuning.
- [x] Review anonymized results, replay captures and record the decision.

Decision: retain current production and stop this round. Grouping saved 17.3%
total tokens overall (15.6% on fresh cases), with a comparable 24-record safeguards
result saving 12.4%. Drug-list referenceability improved at higher cost; aviation
kept all table meanings but combined them into one record. The cost threshold
passed and the independent-referenceability threshold did not. The earlier CSBG
report regression did not recur. See the [complete findings](../experiments/2026-09-14-grouping-fresh/RESULTS.md).

This study generated the hypothesis of testing the added granularity instruction
alone within existing separate-section extraction. The user's subsequent "test"
authorized that bounded comparison, now completed above. No automatic full-document
follow-up or additional model calls are planned.

## Previous decision

On September 14, 2026, the user chose: "Keep what works."
Keep the current extraction behavior and close this optimization round. The
proposed twenty-call qualification round will not run. Concurrency, smaller input
catalogs and grouped section tasks remain unimplemented research candidates.
There is no active implementation or experiment queue from this investigation.
Retain the findings and captures for a future concrete need; no production changes
or commits were made. The proposals below remain historical context, not scheduled
work.

The [parallel investigation](../experiments/2026-09-14-extraction-efficiency/RESULTS.md)
made twelve fresh calls. Three independent investigators tested optional-field
omission, section grouping, and exact-source assembly. No tested change has
qualified for production adoption. Keep the existing section-focused CSBG path,
CUE schemas, exact source evidence, and optional review/refinement boundary.

## Completed

- [x] Close the optimization round at the user's direction; retain current behavior.
- [x] Measure actual requests, output placeholders, token usage and source coverage.
- [x] Test omission of empty optional output fields on CSBG and the benefits control.
  Reject adoption: the cheaper CSBG answer omits all thirteen plan contents; useful
  term links and an actor disappear in the other case.
- [x] Test adjacent-section grouping, then explicit section tasks in one request.
  The latter saves 22.4% total tokens and preserves 17 records on one pair, but
  improves some references and weakens others. This is promising development
  evidence, not adoption.
- [x] Test source selection/quoted assembly instead of generated statements.
  Reject as the default: it saves 35.9% tokens and preserves one difficult detail,
  but splits an alternative into apparent duties and loses governing context.
- [x] Verify native decoding, source selections, actual settings and retained captures.
- [x] Obtain an independent, anonymized source review of explicit task grouping.
  All duties survive; reference clarity has mixed gains and losses. Both versions
  retain some local dependencies. This adds independent judgment, not new samples.

## Archived follow-up proposal — not proceeding

The prior proposal was one bounded qualification round followed by an integration decision.
Concurrency qualification can run alongside the token experiment because it keeps
the model requests unchanged. This proposal was not executed; no new calls or
production changes were made.

- [ ] **Small speed improvement: qualify two concurrent extraction requests.**
  Preserve exact prompts, schemas and request count; use independent model/client
  instances because the capture helper temporarily replaces its client. Collect
  results in source order and retain partial failures. Test interruption, one failed
  request, receipt ownership and stable aggregation with frozen responses; then
  measure a bounded live run. This saves waiting time, not tokens. Do not introduce
  a scheduler service, planner model or automatic retry policy.

- [ ] **Small input experiment: remove redundant numeric coordinates from the
  model-facing passage presentation.** Keep coordinates in local evidence resolution
  and captures, keep F/C IDs and meaningful section identity, and preserve all source
  text and CUE guidance. The saved-data estimate removes 29,182 catalog characters
  across the chapter; actual token and accuracy effects are unknown. Compare against
  current prompts on new documents with local-reference and scope counterexamples.

- [ ] **One broader call/token experiment: bounded explicit section tasks.**
  Compare separate sections with adjacent small-section tasks in one request,
  preserving the flat current response schema. Keep large/dense sections alone.
  Use new documents; measure independent duties, full antecedents, alternatives,
  source support, tokens, failures and latency. The pilot's 22% saving is a reason
  to test, not a whole-document forecast. A missing report referent fails the wider
  gate even when narrower topic and record counts pass.

- [ ] **At the next consumer integration, use shared source/evidence deliberately.**
  Reuse `discovery.export_discovery` and select the records needed by that consumer.
  Avoid sending whole rulebooks/graphs or repeated expanded quotations into every
  downstream prompt or embedding. Omission of empty values after capture is already
  parser-compatible and reduced compact response characters 19.9% offline; it does
  not refund original output tokens. Do not create a parallel ontology or exporter
  until a concrete caller shows what the existing export lacks.

## Archived experiment design — not run

- [ ] Select one adjacent-section pair from each of three previously untested
  documents, plus the saved CSBG 9913/9914 pair with the report-reference failure.
  Freeze the sources and manually record requirements, governing conditions,
  alternatives, exceptions, supported actors and local reference targets before
  collecting output. Include a misleading neighboring provision that must not be
  inherited and an alternative that must not become two mandatory duties.
  These are selected evaluation cases, not a population benchmark.
- [ ] Run three arms on each pair, keeping model settings and CUE schema fixed:
  A: two current separate-section requests; B: the same two requests with only
  numeric passage coordinates removed from the model-facing catalog; C: one
  explicitly grouped section-task request with current passage presentation.
  This costs twenty generation calls: four pairs times five calls. Do not combine
  the two interventions yet. Alternate arm order across cases and retain every
  response, failure, provider usage count and elapsed duration. No automatic retries.
- [ ] Review anonymized raw outputs against the frozen source criteria. Distinguish
  record count, independent meaning, structured field quality, source support,
  total tokens and latency. Shared baseline errors remain recorded; adoption does
  not require solving every existing error, but new material omissions, wrong
  modality, broken alternatives/scope or unresolved referents block qualification.
- [ ] Decide at the twenty-call limit. Target at least 15% aggregate total-token
  savings for grouping, with case-level results visible and no observed material
  regression. For the simpler catalog change, require consistent measured input-
  token savings, no offsetting total-token increase and no observed material
  regression. These are proposed decision thresholds, not observed results.
  Mixed evidence means hold the change; any repeat experiment needs a separately
  recorded question and bound. Do not patch prompts repeatedly on these cases.
- [ ] If a candidate qualifies, run a contemporaneous full-document comparison
  through the real extraction/export path on another untouched document. Set its
  call/token bound before running. If both candidates qualify, this comparison
  must also check their combination; separate wins do not establish compatibility.
  Integrate only the supported change, validate ordering/evidence/replay and relevant
  regression tests, and make a focused commit when implementation is authorized.

The proposed stopping point was a measured decision for each candidate, plus
qualified production changes if authorized. The user instead chose to retain
current behavior before this round began. Rejected or inconclusive experiments
remain research.

## Deferred until a concrete workload justifies it

- Independent requests through the provider Batch API for non-urgent bulk work:
  documented lower pricing, but requires asynchronous job handling and does not
  reduce model-request count. See [provider notes](../experiments/2026-09-14-extraction-efficiency/PROFILE.md).
- Generate standalone prose on demand for selected workflow items while keeping
  source-first discovery. This is an untested product/process hypothesis; the
  failed source-assembly pilot does not establish a replacement extraction path.
- Extra cache infrastructure, semantic planner models, blanket paragraph splitting,
  mandatory audits and repeated CSBG prompt tuning. No evidence here warrants them.

The priorities are alternatives sized to the bottleneck, not a requirement to build
every item. Check actual caller needs before changing the platform. Experimental
code remains under `thoughts/`; no production changes or commits were made here.
