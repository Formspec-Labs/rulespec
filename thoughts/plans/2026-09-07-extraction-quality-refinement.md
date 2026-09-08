# Quality iteration: recover missing meaning and connect qualifications

Status: executed locally, 2026-09-07. This document follows the
[effort/value assessment](../reviews/2026-09-07-extraction-effort-assessment.md).
The two measured revisions are complete. The
[recorded result](../../examples/document_understanding/refinement-iteration/README.md)
passes 25/29 saved cases versus 17/29 initially and retains all original passes;
the three fresh passages pass 20/20 named meanings after refinement. Both
negative controls remain detected but incompletely repaired. A final local
duplicate-guard fix is tested separately from the measured provider results.
No further model iteration is running. The sequence below is retained as the
approved plan against which the result was assessed.

## Outcome

Produce a more complete set of referenceable meanings and more useful
relationships from the same document. Recover content the initial extraction
missed, make exceptions point to the correct rules, and preserve the conditions
and modal distinctions already working.

The proposed process is:

```text
extract draft -> inventory and check source -> recover missing meaning
              -> connect qualifications -> check final result
```

The source inventory, compiler, evidence checks, review history and evaluator
already exist. The main new capability turns findings into small, source-backed
corrections. One recovery pass and one relationship pass are followed by a final
check; remaining findings stay visible without triggering an endless loop.

## Reuse, extend and build

| Capability | Current code and decision |
| --- | --- |
| Initial extraction with bounded governing context | Already implemented in `extraction.extract_run`, `plan_windows` and `documents.with_context`; retain the current profile and temperature 0 |
| Source inventory, claim comparison and recorded assessment | Already implemented in `audit.audit_run`, `load_audit` and `replay_audit`; reuse the complete comparison input, including citations and component evidence |
| Exact component evidence and modal compatibility | Already implemented in `core._claim`, the existing evidence resolver and `CANDIDATE_SCHEMA`; use them when checking proposed changes |
| Correction history and current state | Already implemented in `ReviewStore.snapshot` and `ReviewStore.apply`; append attributed `aiAgent` actions with `expected_revision` |
| Qualification representation and target resolution | Already implemented in `core.resolve_links`, `RelationshipAssertion` and `EvidenceBinding.qualifies`; available for the new relationship pass |
| Scope/context evidence | Existing `definesScope`, `providesContext` and supported `ApplicabilityScope` handling; preserve these when adding or editing meaning |
| Deciding which finding merits an addition or edit | Genuinely missing as a callable workflow; build a small refinement module around the existing paths |
| Choosing the rule a qualification governs after extraction | Genuinely missing as a dedicated pass; build bounded semantic target selection, then use existing resolution and validation |
| Comparison against reference answers | Existing evaluator and the 30-case reference set; extend the experiment runner to compare initial and refined output, including introduced errors |

The application profile remains `document-understanding/2`. No Core schema change
is planned. A small local proposal record can identify an operation, current claim
alias, candidate fields, source evidence and rationale. It is process data, not
a new representation of policy meaning. Reuse the strict native Gemini schema
approach rather than duplicating the candidate shape for every operation.

## Implementation sequence

### 1. Make one omission become a preserved correction

Start with the omitted spacing/suffix rewrite guidance in NREG-10. The source
says those issues are generally insufficient grounds for rewriting, with an
exception when the Department disregarded a clear preference. The output must
retain that qualified meaning and reference without inventing a mandatory
rewrite instruction.

Build a proposed `refine` command/module that consumes the current review
snapshot and a content-matched audit. Its first working slice should:

1. Supply the finding, exact passage, governing context and existing meanings.
2. Decide whether the meaning is missing, already represented, incorrectly
   represented, or unresolved from the available source.
3. Propose `add`, `edit` or no change using existing candidate fields.
4. Validate the candidate and apply the supported correction through the existing
   review path. Save the request, response, decision, action and resulting revision.
5. Recheck the output against the source and show the before/after case result.

This makes a concrete vertical slice before generalizing recovery. It also proves
that a detected gap can become useful data without requiring a human checkpoint.

The runtime starts from `ReviewStore.snapshot()`, including prior corrections.
It must not silently reprocess original responses and discard that review state.
Benchmark runs use isolated workspaces so the saved original captures and review
examples remain untouched.

### 2. Broaden recovery to the observed omission families

Apply the same mechanism to certificate guidance (R03/R15), generally needing
name-change documentation (NREG-11), the applicant definition including DS-2060
(NREG-13), and the Sr./Señor explanation and conditional referral (NREG-14).

Source-first inventory can also miss material. For these cases, inspect its
inventory and background dispositions before blaming correction generation. If
it omitted or dismissed the source meaning, improve that inventory behavior and
record the failure at that stage. Do not feed the gold answers into extraction
or repair requests.

An existing quote containing a clause does not make the clause referenceable
meaning. Conversely, a faithful grouped claim can already represent several
options. Recovery must assess full meaning and scope so it adds missing content
without producing paraphrase duplicates or splitting every sentence mechanically.

### 3. Connect qualifications after the meanings exist

Run a separate pass over local rule groups. Give it full current meanings,
source locations, governing context, citations and candidate target aliases.
Ask which rule each condition or exception qualifies and what changes when the
condition holds. The pass should also identify caveats embedded in prose that
lack an explicit relationship, even when the omission audit called them covered.

Prioritize:

- **Confidential names, NREG-04:** qualify the court-document both-names rule;
  preserve the application's disclosure duty and additional-evidence permission.
- **Photo qualifications, R01/R09/R10:** link infant, medical-glasses and
  disability conditions to their supported baselines; preserve the child rules.
- **Family spacing, NREG-09:** connect the preference exception to general family
  consistency, while leaving unstated precedence over special-issuance guidance
  unresolved.

Current Core conversion permits only `condition` and `exception` candidates to
qualify other rules. Add or edit those records; preserve the underlying
permission, recommendation or duty. Model aliases are mapped deterministically
to current records and their exact target quotations. `resolve_links` then
enforces the existing target-resolution rules. It does not establish that the
selected target is semantically correct; that remains a source check.

If local evidence does not identify a target, retain the unresolved qualification.
An unresolved remote citation is not permission to invent the remote rule. A
`not_required` exemption also need not be forced into an exception relationship.

### 4. Fix evidence selection only where it affects these results

The current resolver already checks the main evidence interval before looking
for a unique document match. Reuse it. Prefer a longer distinguishing source
quotation when a short component quote repeats; retain unresolved support when
the available evidence is still ambiguous.

Address R05's immaterial-damage categories through clearer source-backed choice
wording: either category can qualify independently. Preserve the distinction
between a list of categories and conditions that must hold together. This does
not require a general Boolean-expression language or looser quotation matching.

## Checking and bounded execution

Use `add` and narrow `edit` actions in this iteration. Ordinary recovery does not
need automatic approval, rejection, merge or split operations. Keep model identity,
parameters, raw responses, refused changes and review attribution with each run.

Each correction addresses a specific source-backed finding. Verify that it
preserves governing scope, modality, alternatives and neighboring duties, and
that any target is a current record with the intended meaning. Exact grounding
and Core validation are necessary checks, not semantic verdicts. Proposed changes
that cannot be supported remain findings instead of silently changing the draft.

Apply recovery before relationship selection so new meanings are available as
targets. Use current review revisions for each action; an old plan cannot simply
be applied again against changed records. Capture failures and skip unsupported
changes without discarding successful neighboring work.

For this small benchmark, rerun the existing audit over the final sample instead
of building a new system for selectively auditing changes. Compare it with the
gold reference set. Record before/after output and introduced defects, not just
whether the repair agrees with the audit that suggested it. Final judgments refer
to the final snapshot; do not relabel stale judgments as current.

The budget is one recovery pass and one relationship pass per relevant passage
group, followed by one final audit. Allow at most two measured implementation
revisions before the next effort/value review. Record calls, input/output tokens,
truncations and elapsed time so the quality gain has an observable cost.

## Evidence of success

Freeze the current temperature-0 outputs and reference decisions. They pass 17
and fail 12 of the 29 automatic-extraction cases; NREG-15 independently checks
correction history. This is a challenging, overlapping case set rather than a
general accuracy percentage.

Proposed success threshold:

- Close at least six of the twelve failing cases, including NREG-10's omitted
  qualified guidance and NREG-04's confidential-name relationship.
- Preserve all seventeen currently passing cases, especially inherited emergency
  scope, negative force, should guidance and complete document alternatives.
- Demonstrate correct photo qualification targets and continued detection of
  the deliberately wrong-target control. A missing or wrong link must remain
  visible if it cannot be repaired.
- Introduce no source-unsupported obligation, permission or exception in the
  reviewed benchmark. Preserve correction history and original captures.
- Keep the omitted-option control effective. Distinguish detecting its omission
  from actually restoring the missing option in the refined output.

Then test three previously unextracted passages: one with qualified guidance,
one with nested alternatives, and one with related rules and exceptions. Include
a source outside this passport sample where locally available. Freeze source
expectations before the first run. Evaluate initial and refined outputs against
those same expectations, outside the prompts. Adjudicate all changes, reporting
true additions, correct links, duplicates, introduced errors and unresolved items.

The fresh sample should show useful recovery where defects exist and restraint
where the initial output is already correct. Do not force additions to satisfy a
count, tune on the fresh answers, or describe the combined process's success as
better first-pass extraction. Codex can supply the reference adjudication with
source evidence; a mandatory human review stage is not part of this proposal.

## Effort and stopping point

The recovery-to-correction connection is the largest new piece. Relationship
selection is the second. Both are moderate work because evidence, schema
conversion, review storage and assessment already exist. Anchoring and grouping
are supporting fixes tied to observed cases. A general retry engine, task queue,
review UI, new model sweep, executable policy language and new Core schemas are
outside this iteration.

Deliver one runnable refinement command, saved before/after results, the full
case ledger, fresh-source results and measured processing cost. Preserve raw
extraction and refined output as distinct artifacts. If the bounded revisions
do not materially improve omissions and links, stop and reassess the specific
failing stage rather than widening the architecture.

On success, use the resulting records in one small discovery application or
review one workflow branch for a downstream forms/workflow consumer. That is the
next test of product value after this data-quality iteration.
