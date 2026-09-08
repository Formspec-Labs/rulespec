# Execution: preserve meaning and expose extraction gaps

Started 2026-09-07 following the user's instruction to execute the
[revised quality plan](2026-09-07-document-understanding-quality.md).

## Completed checkpoint

The implementation and assessment are saved in
`examples/document_understanding/quality-iteration/README.md`. The user requested
that work stop after this iteration and that remaining effort be weighed against
current usefulness. No further iteration, provider run or UI work is underway.

- Reproduced and fixed W1/W2/I1 with failing-then-passing tests: overflow refusal
  recovery, completed total-omission assessment, and explicit section identity.
- Profile v2 preserves modal distinctions, scope/context, alternatives and exact
  component evidence. Complete meaning has its own Core assertion identity;
  existing scope and evidence roles are connected without changing Core schemas.
- Paragraph/list indexing and bounded governing context are connected. Primary
  source coverage and exact source coordinates remain separate from meaning.
- Source-first inventory and a separate claim comparison feed the existing
  evaluator. Raw attempts, frozen runtimes, passage accounting and replay remain.
- Official Gemini/LangExtract guidance and four controlled schema probes are in
  `thoughts/reviews/2026-09-07-gemini-schema-guidance.md`. A shared strict native
  schema retains every semantic field; duplicated per-kind shapes failed through
  both schema transports. Schema acceptance does not measure extraction quality.
- Three source pairs differ only in recorded temperature 0 versus 0.2. Names
  recover some content at 0.2; photos omit more. Default stays 0. Both settings'
  outputs, failures and refusals remain saved.
- Codex source adjudication supplies the project's versioned gold reference set
  for all 30 known cases, with exact source evidence and claim IDs. The user asked
  that agent decisions establish the reference answers. Attribution remains
  aiAgent, and evidence-backed revisions remain possible.
- Of 29 automatic cases, temperature 0 passes 17/fails 12; 0.2 passes 16/fails 13.
  R05 baseline fails for ambiguous category AND wording, not proven executable
  conjunction. One separate correction-process case passes. These overlapping,
  strict cases are not an overall document-accuracy percentage.
- Automatic-assessor disagreements remain explicit. Temperature names assessment
  batches exhausted their output budget and remain unknown. Source adjudication
  supplies their reference decisions without relabeling those model attempts.
- Audit names-03 catches the saved names-04 lost parent condition and omitted
  generally-needs-documentation meaning. Earlier missed and incomplete audits
  remain preserved. Audit focus is 3,000 characters; output budget is 32,768.
- Real negative controls catch omitted customary-usage documentation and an exact
  exception quote linked to the wrong existing rule. The first control exposed
  omitted references/component anchors in the checker handoff. A regression
  reproduced that defect; the fix and follow-up preserve citations and still
  detect both deliberate defects. The omission audit retains other unknowns.
- Fresh responsibilities expectations were frozen before the first extraction.
  Its model audit missed factual statements typed as possibility. An informed
  follow-up corrects modality and retains all seven expected meanings; exact
  component anchoring leaves three units unknown in the evaluator. It is not a
  second blind holdout.
- All five original v1 runs reprocess and strict-replay without inventing v2
  fields. All three historical corrections preserve prior nodes, attribution,
  current target resolution and reopen behavior. Their remaining coverage gaps
  remain disclosed.
- A separate confidential-name correction adds the correct exception target and
  retains all 25 existing records, including the neighboring disclosure duty and
  evidence permission. It demonstrates corrected output, not improved automatic
  extraction.
- Final verification: 223 tests and 101 subtests pass. Seven new extraction runs
  reprocess/strict-replay; all eight saved audits strict-replay with their verified
  original application snapshots. The built wheel imports its packaged Core
  data, compiles and validates. These checks make zero provider calls.
- All 1,406 protected originals match their baseline hashes. Changes are local
  and uncommitted. No UI correction was saved; the local server was stopped.

## Remaining value versus effort

See `thoughts/reviews/2026-09-07-extraction-effort-assessment.md` for the stopping
point and prioritized next work. The main remaining data defects are omitted
qualified statements, absent explicit exception edges, ambiguous grouping and
some unresolved component anchors. Reuse the present workflow to address them;
no wider architecture expansion is needed to demonstrate further improvement.

## Implementation decisions

Reuse existing evidence, identity, capture, review and evaluation paths. Connect
`definesScope` and `providesContext`; retain existing `qualifies`. Scope records
must fit supported source information and preserve historical assertions.
Keep original v1 interpretation and new processing explicitly distinguishable.
`ClosureClaim` stays disabled. Discovery does not require upfront human review.

The v2 `meaning` ValueAssertion holds the full interpreted meaning as a typed
string. Scope is part of its proposition value; only that assertion gets
`hasApplicability`. A scope change therefore makes a new meaning assertion and
scope record while retaining any shared summary proposition. Jurisdiction is
emitted only with explicit source support. All original v1 fields retain their
existing representation when new meaning fields are absent.

## Verification and delivery

At the last preservation check, all 1,406 original capture and adversarial files
matched their baseline hashes. New experiments live under
`examples/document_understanding/quality-iteration/`. Work is local; no commit, push,
publication or deployment is part of this execution.
