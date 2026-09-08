# Refinement execution checkpoint

Started 2026-09-07 under the user's instruction to execute the
[quality refinement plan](2026-09-07-extraction-quality-refinement.md).

## Current state

- Existing work is local and largely untracked; preserve it. No commit/push or UI
  work is part of this iteration.
- `.tools/refinement-iteration-baseline/package` holds the starting package.
  `protected-sha256.json` pins 4,371 existing manual, quality and adversarial files.
- Implement one omission-recovery pass, one relationship pass and final audit.
  Reuse Core v2, exact evidence, recorded provider calls and `ReviewStore`.
- Start from `ReviewStore.snapshot()` including prior corrections. Add a preview
  operation that uses the real correction validation without saving an event;
  challenge proposed changes against source before committing them.
- Target NREG-10 first, then three baseline source runs. Acceptance: close at least
  six failures including NREG-10/NREG-04, preserve 17 passing cases, preserve prior
  captures/history, assess three fresh passages frozen before extraction.
- At most two measured implementation revisions. Keep temperature 0. Save raw
  attempts, current-state pins, exact actions, semantic checks, final audit and
  provider usage. Unknown/refused work remains visible.

## Delivery status

Implementation and both bounded measurements are complete. Results, raw captures,
case adjudications, fresh-source expectations and verification are saved in
`examples/document_understanding/refinement-iteration/`. The checkpoints below
record the work; the final section is the current state.

## Implementation checkpoint after first live run

- Added `refinement.py`, CLI `refine`/`refine-replay`, `ReviewStore.preview`, and
  runtime pins for refinement/review code. Refiner captures initial audit, recovery
  proposals, separate source challenges, attributed actions, relationship pass,
  final audit, usage, snapshots and source-preserving replay.
- Full suite passed 230 tests/101 subtests before the repeated-quote anchor fix.
  Eight refinement tests pass after that fix. A further prior-history test passes.
  A new action-consistency replay test FAILS and must be fixed before delivery:
  `test_replay_checks_recorded_action_against_proposal_and_saved_event` shows that
  outcome.action was not checked against proposal fields and saved event fields.
- Live slice-01 failed proposal transport. Four controlled native probes isolate
  maxItems:8 on the nested proposal array as the rejection trigger. Removing only
  that keyword succeeds; the local parser still enforces 8. Every meaning field,
  required property, enum and description remains. Probes and failures preserved.
- Slice-02 restores both spacing/suffix rewrite statements from a deliberately
  empty draft. Repeated unless quotations refused relationship actions. Added
  exact disambiguation within the explicitly selected target's source interval;
  never choose the first occurrence, and semantic target checking remains separate.
- `prepare_fresh.py` froze three new local CFR passages and 20 expected units in
  `fresh-source/` BEFORE extraction. Slopes (30 CFR716.2 intro/a-d), valid/defective
  authorizations (45 CFR164.508 b1-b2), marketing (45 CFR164.508 a3). XML originals,
  deterministic whitespace conversion, labels and source hashes are saved. No
  fresh extraction calls have been made yet. Labels must stay outside prompts.
- `run_sample.py` runs an isolated saved/fresh sample. Three first measurements
  under `runs-01/`: names, photos, names-excerpts. Workspaces are in
  `.tools/refinement-live/benchmark-01/`. Historical captures remain read only.
- Names completed: 2 actions, 12 final records, 7 requests, 232,979 total tokens.
  Recovers generally-needs-documentation and improves married-name reference
  context on the document-list rule. Qualification proposals are refused for
  converting a baseline permission/duty or incompatible modal/kind combinations.
- Photos completed: 3 actions, 36 records, 15 requests, 909,897 total tokens
  (359,196 cached input tokens included separately). Adds certificate date caution
  and explicit four-child medical-glasses scope links plus missing-photo context
  links. Some exception candidates still fail modal/kind compatibility.
- Names-excerpts is/was finishing final audit in session 74882. It recovered the
  applicant definition, material-discrepancy definition/documentation rule, general
  ID guidance, both rewrite caveats and Sr./Señor explanation/referral. Preserve
  and inspect its applied edits to pending-name finality/clearance as well.
- Source packet overhead is measurable: names recovery packet claims 53,320 chars,
  inventory 11,160, unit judgments 9,136, claim judgments 13,259, source only 2,717.
  Opaque fragment IDs and repeated proposal field copies inflate model inputs.
  A second measured revision should clarify qualifier modality/companion-record
  selection and compact model-only metadata without dropping meaning or quotes.
- Do not edit runtime modules while any model process is active: nested final
  audits read current on-disk fingerprints, which must match loaded code. Finish
  outstanding model calls before the second revision.

Next: inspect complete first-run changes; finish replay action consistency; clarify
qualifier generation; preserve full captures while reducing model-only opaque IDs
and duplicate fields. Then run the final saved-source measurement and all three
fresh passages, adjudicate 30 saved cases plus 20 fresh units, verify negative
controls/history/old compatibility/replay/package/preservation, and report effort
versus improvement. No more than two measured implementation revisions.

## Final implementation and measurement

- The first full measurement completed with 17 applied actions and 25/29 saved
  cases passing, versus 17/29 initially. It recovered certificate guidance,
  medical child links, family preference, rewrite caveats, definitions and Sr.
  It still missed infant/disability/confidential exceptions and damage grouping.
- The second revision clarified modifier modality and companion-record selection.
  Model inputs omit opaque provenance hashes and use aliases; full meaning,
  source quotes/positions, citations and saved packets remain intact. Duplicate
  copies of proposed fields are omitted from challenge requests.
- The second measurement applied 20 actions and also passed 25/29, preserving all
  seventeen original passes. It recovered the required NREG-04/NREG-10 cases,
  disability, medical-glasses and family links, and definitions/weaker meanings.
  It declined certificate guidance recovered in revision 1. Final failures:
  R01 infant link, R03/R15 certificate guidance, R05 damage-category ambiguity.
- All 37 applied actions across both baseline measurements were source-adjudicated.
  No new unsupported normative duty/permission/exception was observed in those
  changes. Some components remain unresolved/inferred; one names summary leaks
  a request-local C alias. Meaning-case success is not component perfection.
- Fresh labels preceded provider calls. Slopes: 11 initial/final claims, no edits,
  8/8 named meanings. Authorizations: 7 to 8 claims, one prerequisite link, 8/8.
  Marketing: initial MAX_TOKENS response produced zero candidates; refinement
  added four meanings and connected both exceptions through two edits, 4/4.
  Total fresh score 16/20 to 20/20. Marketing still has an awkward object and
  unresolved actor; two logic_text quotations remain noncontiguous/uninterpreted.
- Negative controls both detected. Omitted alternative: valid repair content was
  bundled with an unsupported actor and the source challenge refused the whole
  edit; the option remains omitted. Wrong target: corrected first, then baseline
  edits caused ReviewStore to demand target-revision reconfirmation; the duplicate
  guard wrongly blocked that reconfirmation. Final audit exposes the missing link.
- Fixed that guard after measurement: equal wording is a duplicate only when the
  currently resolved target IDs also match. A source-backed regression test edits
  a baseline, observes the intentionally unresolved edge, reconfirms unchanged
  modifier wording to the new revision and checks duplicate refusal thereafter.
  No additional provider experiment was performed or claimed successful.
- Fixed the earlier replay action-consistency gap. Tests now require actions to
  match parsed proposals and saved events even after a manifest is regenerated.
- Same three source runs use 2,055,895 versus 1,026,905 total refinement tokens,
  and 1,695,507 versus 669,067 input tokens. Both have 37 requests including the
  initial and final audits. Final elapsed time is 222/305/394 seconds per source,
  concurrently. One final excerpt relationship response reached MAX_TOKENS and
  remains visibly partial. Fresh marketing's initial failure is separately saved.
- Offline delivery verification succeeds: five v1 runs, six v2/fresh captures,
  thirteen refinement replays, twenty-six audit replays, three historical review
  actions, packaged-wheel compilation/validation, and all 4,371 original hashes.
  Captures use their verified frozen application; the delivered guard fix is
  separately tested. Final test receipts are saved beside the experiment.
- Final combined package/projection suite: **236 tests and 101 subtests pass**.
  CLI help, Python syntax and whitespace checks pass. No provider process remains
  active. The experiment README, full 30-case ledger, fresh 20-unit ledger, all
  applied-change decisions, negative controls and processing costs are saved.

## Stopping decision

The bounded iteration is complete. The mechanism produces useful recovered data
and relationships, but one pass can still skip weaker guidance, mistake local
qualifications for remote ones, or reject a good repair over an optional component.
The control failures remain explicit. Keep the process available and use the
records in a small discovery test before committing to a larger extraction effort.
The full repeated-audit path is expensive for this amount of text; improve the
identified recovery/relationship decisions before scaling it. No model sweep,
UI expansion, commit or push occurred in this iteration.
