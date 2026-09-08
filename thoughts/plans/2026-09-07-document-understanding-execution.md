# Execution: first persistent document-review slice

Started 2026-09-07, following the approved
[final review](../reviews/2026-09-07-document-understanding-path-forward.md).

## Scope and boundaries

Build the first local reviewable manual section, including independent
evaluation, durable corrections, replay and visible failures. Keep historical
POC runs. Do not alter Core schemas or thin-package dependencies. RefSpec
provides optional vocabulary snapshots. No publication or deployment is part
of this work.

## Implemented and verified

- [Application and commands](../../packages/rulespec-extrapolator/README.md):
  prepare, extract, replay, reprocess, serve, review, export, evaluate, vocabulary.
  The application is installed editable in `.tools/document-poc-venv`.
- [Shared implementation decisions](../../packages/rulespec-extrapolator/IMPLEMENTATION.md):
  exact components, immutable propositions, stable rule handles, retained
  revisions, qualification targets, and original AI attribution.
- Five Gemini 3.8 Flash acquisitions: development once; held-out excerpts twice;
  contiguous 8 FAM 403.1-4(a)–(d) twice. Every planned window has a terminal
  outcome. Frozen acquisitions remain unchanged under `manual-slice/runs/`.
- [Final processed outputs](../../examples/document_understanding/manual-slice/README.md)
  reuse the original responses under corrected compiler code. All five strict
  replays pass; every accepted claim and complete source document matches its
  acquisition. Reprocessing records code changes explicitly and preserves run
  identity; it does not weaken replay checks.
- SQLite review supports add/edit/split/merge/reject/approve. First-open manifest
  verification, exact evidence checks, review concurrency, and attestation target
  checks protect the recorded review state. Playwright verified source inspection,
  split, merge, addition, and reopening. Store/API tests cover the remaining actions.
- 167 application tests pass. Existing POC and projection regressions pass
  50 tests and 101 subtests. rdflib emits deprecation warnings; no check fails.
- The built wheel passes reprocessing, replay, Core validation, review storage,
  and HTTP asset checks from isolated Python outside the checkout. Core and
  projection dependencies remain unchanged.
- The [independent implementation review](../reviews/2026-09-07-document-understanding-implementation-review.md)
  closed after fixes for first-open integrity, revision/supersession history,
  hidden refusals, invalid original coordinates, and silent newline conversion.
  Its closure record distinguishes independent checks from author-run regressions.
- An integrator follow-up found that compilation failures retained raw responses
  but could not reprocess because their compiled outputs were absent. Recovery
  now requires matching explicit failure records and all pinned acquisition
  artifacts; strict replay/review retain their complete-output checks. The
  extraction suite has 74 passing tests, including failure recovery and refusal
  of missing outputs from nominally successful runs.

## Source review and remaining extraction work

The evaluation worker prepared 12 source-reviewed excerpts, sealed labels before
the model runs, then inspected 87 accepted claims and 78 scoped expected-unit
assessments. All four evaluated outputs need correction. The two contiguous
section runs fully cover 4 and 5 of 10 expected units respectively; remaining
units are partial, missing, or uncertain. This is agent-authored, uncalibrated
assessment of a small overlapping sample, not a general accuracy estimate.

The [source review](../../packages/rulespec-extrapolator/evaluation/results/FINDINGS.md)
records omissions of document alternatives and weaker guidance, lost shared
conditions, inconsistent ID-waiver extraction, and an exception that became an
unlinked permission. Independent replay and digest checks explicitly transferred
unchanged judgments to the final processed outputs. No prompt tuning used the
held-out labels before the outputs froze.

Next producer work should account for each source paragraph/list item, preserve
the full surrounding condition on every split rule, retain alternatives and
modal force, and stabilize exception targets. Grow development fixtures first,
then evaluate on new blind sources. Broader input parsing and longer windows
follow evidence that these bounded cases improve.

The user's latest steering is to keep the browser useful and focus on core
extraction workflows. A small [post-evaluation correction demonstration](../../examples/document_understanding/manual-slice/review-demo/README.md)
is complete through the API using three explicit agent-attributed actions.
It repairs representative omissions and scope errors while retaining the original
claims; it does not count as blind model improvement or human review.

Human correction time and time savings remain unmeasured. No human usability
study or comparable manual pass occurred; the saved timing observations identify
agent work only. Full PDF/chapter processing, arbitrary executable logic, live
RefSpec fetching, and release publication remain outside this delivery.

## Blind adversarial follow-up

The [three-agent adversarial review](../reviews/2026-09-07-document-understanding-adversarial/FINDINGS.md)
independently checked all 120 accepted claims across five runs and the three
saved correction actions. Source inventories were sealed before output access.
It corroborates omissions, lost inherited conditions and inconsistent exception
representation, and finds the three corrections improve their targets while
leaving the section incomplete. Thirty semantic regression cases are saved.

New offline probes reproduce failure finalization on numeric overflow, incorrect
review-completeness reporting for total omission, and replacement of a valid
child-section ID by its parent. Those fixes remain open. The review passed 91
selected existing tests and made no production changes. The next implementation
should repair these narrow defects and test coverage, inherited scope and force
before expanding the browser or claiming better extraction quality.

The [revised quality iteration](2026-09-07-document-understanding-quality.md)
incorporates the user's two use cases and side-agent feedback. Its
[capability assessment](../reviews/2026-09-07-extraction-capability-assessment.md)
distinguishes implemented paths, unused Core capabilities and missing extraction
behavior. The sequence is to fix the three defects, pin the small profile and
Core conversion, connect governing context, add bounded omission checks, then
demonstrate results on all 30 saved cases and fresh source passages. `qualifies`
already works; scope/context evidence and appropriate `ApplicabilityScope` use
need application wiring. Processing coverage remains separate from semantic
coverage, and `ClosureClaim` stays disabled. Review supports later user feedback
or closer tool-building scrutiny without becoming mandatory for every discovery
run. This revision changes the plan, not the implemented extraction behavior.

## Delivery checkpoint

Implementation, results, and research remain local and uncommitted. Existing
research base is `7f8d99b`; current checkout is `main` at `eac3ab8`. No push,
deployment, or release was performed.
Original POC files remain available as the historical baseline. The API correction
demo, its CLI recreation, and its retained source/assertion checks pass. Recorded
runtime sources and original acquisitions remain unchanged after verification.
The bounded corrected section is served locally at `http://127.0.0.1:8765` from
`examples/document_understanding/manual-slice/review-demo/section-01`.

The [verification record](../../examples/document_understanding/manual-slice/verification.json)
pins the source files and records test, replay, packaging, and review checks.
The [runnable example](../../examples/document_understanding/manual-slice/README.md)
is the starting point for a later session. Its next-work list follows the user's
priority: improve core extraction before expanding the browser.
