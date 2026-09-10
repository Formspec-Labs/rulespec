# Extraction consistency implementation

User authorized the complete task list, relevant tests, experiments, integration,
and coherent commits. Preserve original captures. No legacy compatibility layer.
This checklist remains open until each outcome has direct evidence.

## Deterministic corrections

- [x] Align extraction prompt and native CUE schema (actors and term registry).
- [x] Align conceptScope schema, JSON-LD context and both concept emitters.
- [x] Target qualifications by claim identity, never quotation uniqueness.
- [x] Separate term identity from editable definition wording; explicit sense replacement.
- [x] Keep current aliases/definitions consistent with historical graph records.
- [x] Complete partially populated enrichment lists without overwriting conflicts.
- [x] Surface withheld enrichment and conflicts in review issues and captured proposals.
- [x] Distinguish unresolved evidence from deliberately declared hypotheses.

## Complete the workflow

- [x] Define uses-term semantics and omit redundant definition self-use.
- [x] Provide audits with term lookup including out-of-window definitions.
- [x] Audit names, aliases, senses, and uses separately from target existence.
- [x] Export logical rule and term identities alongside immutable revisions.
- [x] Bind AI revisions to actual model/request/input provenance.
- [x] Support term names, aliases, references and explicit sense replacement in review. Implemented, backend-tested and manually inspected in saved data; user requested data inspection instead of the remaining browser pass.
- [x] Render component diffs and distinguish AI changes from human decisions.
- [x] Explain unavailable definitions with retained names and reasons.

## Controlled extraction experiments

- [x] Precise supporting spans with paragraph context and repeated modal words.
- [x] Standalone qualified requirements without relying on neighboring claims.
- [x] Compound exemption splitting with counterexamples to mechanical splitting.
- [x] Explicit actors, literal you, passive and multiple-role counterexamples.
- [x] Sparse choice/logic fields with coherent evidence requirements.
- [x] Self-contained antecedents and subjects after splitting.
- [x] Assess existing source hierarchy and retain useful paragraph/note structure.

Before fresh calls, record arms/cases/criteria/settings and stop bound in a
separate experiment note. Use existing capture/replay facilities. Judge raw
outputs manually; no model judgment is absolute gold. Adopt only supported
changes; a demonstrated no-change decision closes an experiment, not its
underlying quality limitation.

## Noise reduction and integration

- [x] Concise consumer representation retaining evidence and history access.
- [x] Reuse sparse-field/passage compaction; avoid competing representations.
- [x] Render shared evidence once without losing component support roles.
- [x] Separate provider usage from local serialized size.
- [x] Verify extract/enrich/audit/correct/export/reload/replay lifecycle.
- [x] Document reproduced/fixed/improved/deferred findings and commit exact paths. Production commit c4aa4ad; experiment artifacts committed separately.

## Verification and progress

Baseline: clean main worktree, latest integration captures under
`examples/document_understanding/actor-term-integration`. Manual review findings
are hypotheses until reproduced where execution matters. Source spec declares
conceptScope xsd:string; the live context incorrectly coerces it to @id.

Tests will exercise outcomes (same-passage targets, link continuity, alias edits,
partial lists, unresolved proposals, actual RDF literals, and consumer behavior),
then run package/generator checks and a captured live workflow. UI changes require
rendered interaction. Original captures are immutable historical evidence.

### Implementation checkpoint (2026-09-10)

Implemented but not yet fully integrated/committed: prompt correction, upstream
context fix, persisted term IDs with explicit sense replacement, latest concept
descriptors with immutable revision history, claim-ID qualification targets,
partial-list additions, recorded enrichment observations/Core Findings, captured
AI revision provenance, term-aware audit lookup, sparse shared-evidence discovery
export, term editor/diffs and claim selector. Package suite passed 395 tests at an
intermediate checkpoint; 57 focused tests subsequently passed including new
same-passage targeting, named out-of-window term lookup, withheld enrichment
replay/provenance and sparse discovery checks. Run full suite again after final edits.

Correction to the manual review: document `sections` were flat, but existing
`source_passages` already derives list parent relationships and supplies context.
Reuse it. Discovery now exposes that existing hierarchy; NOTE markers gain only
a structural kind, without guessing which rule they govern.

Still required: fresh controlled experiments (no calls made yet), live workflow
and replay, rendered UI interaction, final documentation/checklist audit and
coherent commits. Existing live UI may still be an old in-memory backend; use a
fresh current-code run when verifying. Tests use `.tools/document-poc-venv/bin/python`;
root `.venv` lacks pytest. Recent logs: `/tmp/rulespec-consistency-tests.txt` and
`/tmp/rulespec-consistency-focused.txt`. Preserve old captures; do not retrofit
their immutable identities or manifests to the new runtime.


### Final data/process verification (2026-09-10)

- 408 package/schema-generator tests passed; native CUE vet, extraction-schema
  drift check, Core contract-export check, JS syntax and git whitespace checks pass.
- Tests cover RDF scope type, same-quotation target selection, stable term identity,
  alias correction/current graph, rejected/replaced definitions, partial lists,
  actual AI request fingerprints, retained observations, out-of-window audit lookup,
  sparse consumer output, usage accounting and invalid-existing-definition recovery.
- [Fresh controlled comparison](../../examples/document_understanding/consistency-transfer/README.md):
  ten actual calls across three new official snapshots, passport development data
  and constructed counterexamples. All responses parsed; all ten frozen-runtime
  replays passed. Sentence references reduce location ambiguity but fail the
  no-regression gate for complete meaning. Keep paragraph references. Completing
  these experiment tasks means testing and recording the decision, not claiming
  their underlying semantic problems solved.
- Four additional live integration calls exercise enrichment and two-stage audit.
  An intentionally partial term-use list was completed. Repeated Staff evidence
  was withheld and recorded as an observation/Core Finding; a source-backed agent
  correction subsequently resolved it. Actual request provenance, stable rule IDs,
  pending corrected revisions, review reload, graph validation, discovery export
  and replay passed. An order-sensitive smoke measurement was corrected using
  stable rule IDs, with its original result retained.
- The live first-aid audit completed processing and flagged missing background
  content. Its failed semantic verdict and not_established completeness remain
  visible. Replay is processing evidence, not an accuracy claim.
- Existing source hierarchy and shared-evidence rendering were reused. The new
  discovery format stores source/terms/evidence once and retains support roles.
  No new sentence splitter, explanation fields, inferred section targets, or
  automatic scope propagation entered production.

### Browser verification and remaining task

In the isolated preview at port 63695, real browser interaction verified the term
editor, alias correction, retained name after definition rejection, readable alias
history diff, and navigation to the affected use. Original captures were untouched.
Backend tests cover explicit sense replacement, references and claim-ID targets.

The final browser pass is still pending: exercise term-use relinking, explicit
sense replacement and the qualification selector, reload, and inspect the final
compact support-change/audit-count rendering. On two attempts the browser tool
reported a locked Mac and could not unlock it. User input has been requested;
this is the only external blocker. Do not mark the overall goal complete or call
this UI pass verified until those interactions run. The changes are implemented;
no further provider calls or source tuning are required to finish this goal.

### Quality limits carried forward

Default statements can still omit governing conditions or leave pronouns unresolved.
Repeated actor/modal words can make component locations ambiguous. Term uses can be
missed even when definitions exist; some domain modality choices remain uncertain.
A linked or processed passage does not prove all its meanings were extracted.
These limits are documented with raw examples, not hidden behind successful schema
validation. Discovery supports gradual correction; executable workflows still need
source review. Future quality work should be a separate bounded decision.

Current-code preview is running at http://127.0.0.1:63696/ against the isolated
`.tools/consistency-ui-preview` workspace. Original user tab/server at 63694 was
not changed. Resume the remaining interactions after unlock; do not spend more
on provider trials for this completed experiment.


### Closeout after user-directed manual inspection

The user subsequently requested “Just look at the data manually yourself,” replacing
the blocked final browser pass with direct data review. The browser-pending notes
above describe the earlier stopping point, not a current request to unlock the Mac.

[Manual closeout](../reviews/2026-09-10-manual-data-closeout.md) records inspection of
actual source/output, enrichment edits, old/new actor evidence, consumer exports,
Core Findings, read-only passport review events and retained regression-test events
for alias edits, explicit sense replacement and qualification retargeting. The
implementation/data checks are complete under that direction. Remaining browser
interactions were not performed or represented as verified. No new model calls or
runtime changes were needed. Known semantic limits and residual repetition remain
explicitly documented; completion does not mean perfect extraction.
