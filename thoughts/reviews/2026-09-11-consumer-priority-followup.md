# Consumer follow-up: prioritize a usable result and its correction path

**Decision: keep the two consumer tracks, and make the next discovery experiment smaller.** R17/R18/R3 can first prove that a person finds the right source, sees the retained reading, and reports a correction that survives reload. R19 should first produce one reviewed decision flow. R16/R25/R26 are conditional interventions selected by failures in those uses; none needs to become a universal model pass.

This 2026-09-11 follow-up covers R3, R16–R19 and R24–R26. It supplements the two existing cross-relevance surveys rather than replacing them. The supplied workspace instructions apply; no additional `AGENTS.md` was found in the inspected ancestors or `thoughts` tree. I used the semi-formal architecture-review method: compare stated purpose with current consumers, trace reusable boundaries, and identify the smallest observation that would change the decision. Only this report was written. No models, tests, installs, runtime changes or commits were performed.

Paths abbreviated below: **P** = `packages/rulespec-extrapolator/src/rulespec_extrapolator`; **E** = `packages/rulespec-extrapolator/evaluation`; **X** = `thoughts/experiments`. File/line observations describe the live source read during this survey. Installed claims below belong to retained receipts, not a fresh installation check by this survey.

## Findings that change the next step

### 1. R17 needs a result-combination rule before another retrieval technology

**RESHAPE — user value / implementation boundary.** Reusing the retrieval harness is correct, but simply merging its raw scores would introduce an unmeasured ranking decision. `E/discovery_trial.py:28–42` computes inverse document frequency and average length from each supplied row collection. Source and statement collections therefore have different scoring populations. Their raw numbers are not calibrated for direct comparison.

Use the current source ranking as the baseline. Add a separately ranked statement candidate list, combine by a declared rank/identity rule, then expand only selected results with evidence. Hold retrieval limit and returned-text budget fixed. This is a proposed comparison, not evidence that rank fusion wins. Exact-reference navigation can be another measured query category using existing reference readings; it needs neither embeddings nor semantic audit.

There are two different duplication problems. Repeated search hits consume result slots; repeated evidence consumes display/context space. The saved cargo case produces three hits with essentially the same grouped meaning (`X/2026-09-10-design-retrieval/RAW-REVIEW.md:8`), while the same review measures 57,276 repeated source characters (`:31`). Deduplicating strings inside one hit does not solve either globally. Measure distinct useful provisions and unique source intervals separately. Preserve repeated source occurrences and their roles; equal text is not equal provenance.

`P/discovery.py:60–69,125–137` already distinguishes the primary evidence table from each external source's table. Evidence expansion must retain that source identity: identical offsets in two editions are different evidence. Reuse the existing tables instead of creating another concatenated context representation.

### 2. R18 has a reusable write route, but does not yet have reference-feedback behavior

**RESHAPE — available versus integrated capability.** `ReviewStore.apply` already accepts `observe` with `targets: []`; observation dictionaries require an issue code but do not validate reference identity (`P/review_store.py:477–511`). `P/review.py:128–158` exposes the same action route, and `P/cli.py:146–161` can apply an action and export the resulting discovery snapshot. These are actual callable reuse points.

That reuse currently starts from a saved run: `ReviewStore` requires `document.json`, `run.json` and `rulebook.json` (`P/review_store.py:88–119`). The standalone `references` command can scan a document without that workspace (`P/cli.py:162–171`). Use an existing saved run for the first feedback example; source-only feedback still needs an explicit persistence entry point and must not pretend extraction occurred. This is a bounded consumer decision, not a reason to require a model call.

The current browser reads observation history and general issues (`P/static/review.js:288–295`), but its submit path builds claim actions and no observation payload (`:505–518`). Its snapshot endpoint supplies the review snapshot, not `reference_scan` (`P/review.py:120–123`). A dedicated reference-feedback interaction and source/reading display remain consumer work. Adding another persistence service would duplicate an existing capability; treating the current claim-review UI as a completed reference-feedback UI would overstate it.

One further boundary matters: top-level action `provenance` is explicitly restricted to AI model captures (`P/review_store.py:514–519`). A human reference correction should carry the challenged parser/index/source provenance inside its observation data, with the human author already on the event. Do not put parser provenance into the AI-only field or weaken that validator.

The feedback anchor should identify **the source occurrence and the reading being challenged**. Accepted reference IDs hash fragment, kind and value, while full native `reading`, reader hashes and index pins live elsewhere (`P/references.py:44–68,103–113,130–138`). `export_discovery` rescans with the active readers (`P/discovery.py:111–114`), so an unchanged accepted ID alone cannot establish that a later export contains the same interpretation. Observations annotate that reading; the current route does not use them to change parser results or target selection. A later parser fix and a recorded resolution are separate changes.

Reuse the exact source fragment/document pins plus the retained native reading, refusal, relevant reader module hashes and target-source identity where present. Rejected rows can precede ID assignment; a grounding refusal can also lack verified evidence (`P/references.py:47–63`). Preserve its submitted coordinates and refusal without inventing a verified fragment. A small consumer validator can check this data against the displayed scan. Define a generated application-profile shape under R3 only if a typed interchange consumer actually needs one.

**Smallest deciding check:** one accepted occurrence, one rejected reading, two identical mentions at different positions, and one rescanned changed reading. Record a human observation, reload and discovery-export it, and show the challenged version alongside the current reading. Preserve the earlier event when recording a resolution. This needs zero provider calls and does not depend on migrating claim approvals across reprocessing.

### 3. R25's second boundary is applying the supported subset

**RESHAPE — shared dependency.** Per-target judgment is only half the change. Core deliberately clears all resolved targets when one requested target is missing (`P/core.py:302–316`). Review snapshots also clear changed target sets pending an explicit correction (`P/review_store.py:317–331`). These preserve the integrity of a saved revision; they should not be relaxed to make a trial pass.

For fixed, current targets, assemble the supported subset into one replacement per qualification and run the existing `_action` → `store.preview` → revision check → `store.apply` path (`P/refinement.py:324–339,493–527`). Existing exemption-link preparation already preserves meaning and unions existing links (`:271–295`). Preserve the complete grouped meaning and the evidence/verdict for each supplied target, including outcomes excluded from the replacement. Unknown/unsupported judgments belong in observations. A stale qualification or stale target still stops application; an unrelated unsupported new target should not erase a supported one.

Keep target verdicts separate within one shared request before considering a provider call per target. The existing challenge schema returns one verdict per proposal (`P/refinement.py:124–126,342–364`); a bounded experimental response can identify each supplied target while reusing the source catalog and capture functions. Separate verdicts do not require repeated source text, repeated audits or separate jobs.

Clarify the relationship's meaning before changing labels. The saved listed-substitute/service disagreement reflects applicability already expressed in the baseline versus an exception that changes it (`X/2026-09-10-design-targeted/RAW-REVIEW.md:17–23`). Core can express scope/context evidence separately from qualification assertions (`P/core.py:451–493`), but those representations do not decide the correct interpretation. Test a supported target, a negative target, a genuinely disputed target and a stale-target application control. Do not revive the failed affected-action prose.

### 4. R19 can reuse Core's consumer link without building a workflow bridge first

**KEEP — existing schema ownership; DEFER — implementation breadth.** `constraints/core/generated-work-product.cue:3–18` already defines an overlay for consumer-owned form fields and workflow steps, linked by `rkaf:justifiedByAssertion`. It does not define executable workflow branches. `constraints/core/applicability-scope.cue:10–15` explicitly leaves its free-form condition audited rather than validated. Neither means extracted prose is executable.

Start with a source-backed preparation artifact containing questions, facts, actions, conditions and unresolved choices. Choose the actual consumer's schema only when creating the corresponding form/workflow object; then reuse the existing justification link. No wos-spec/formspec adapter was found in the inspected application source. These available Core shapes are not an installed workflow integration.

The saved passport-name review provides useful development cases: an older-name-change branch is detached from a limited-passport permission, and a within-one-year documentation rule is overgeneralized (`E/results/source-review-decisions.json:30–36`). Its labels are explicitly agent-authored and uncalibrated (`:2–6`). Use those to prepare representative scenarios, then select an untouched comparable activity for a benefit comparison. Do not call the old cases fresh evaluation or infer present legal requirements from their saved source.

Connect R16 only if the chosen scenario needs a specific meaning correction. The current CUE already describes governing conditions, modal force and actor responsibility (`P/schema_data/document-understanding.cue:22–32,46–56`). Repeating those instructions or adding a new explanation field is not yet a distinct intervention. Select one error class and a falsifiable change; keep missing actors or governing relationships explicit where the source does not decide them.

## Shared dependencies and what stays independent

| Work | Combine | Keep independent / defer | Reuse boundary |
| --- | --- | --- | --- |
| R17 discovery | R18/R3 correction path and a narrow R24 query review | Broad R22 vocabulary, R8 graph migration, extra model passes | `records`, `export_discovery`, diagnostic `search`, existing review actions |
| R18 feedback | Occurrence evidence, reading provenance, reload/export check | Cross-reprocessing claim identity and automatic approval transfer | `ReviewStore` observation history; source fragment and parser/index pins |
| R19 preparation | Scenario review plus whichever R16 failure changes that scenario | A general workflow engine, all source families, universal audits | Existing meaning/scope/evidence; actual consumer schemas when needed |
| R25 relationships | Fixed-target semantics, supported-subset application and R24 judgments | New target discovery, external-text lookup, explanation generation | Existing challenge catalog, preview/revision path, observations |
| R26 cost | Measure the optional operation selected by R16/R25 | Public helper API or broad cleanup before measured demand | `_packet`, `_challenge_catalog`, `_challenge_prompt`, `_call`, capture/replay |

R24 is shared proof work, not a prerequisite to finish all document categories before any consumer experiment. `P/evaluation.py:17–23,61–75` already supplies dimensions, unknown outcomes, source pins and exact-span checks. Reuse them and keep a separate case population for each decision. The broad manual/regulation/notice/state/structured sample still matters for a broad release-quality claim; a narrow consumer result cannot close that task.

Installed source navigation is no longer a blanket blocker. The retained eCFR application receipt reports both commands locating supplied exact sections and source/isolated-wheel checks (`X/2026-09-11-ecfr-text/application.md:3–14,41–51,60–65`). Its four located mentions are source-location evidence, not consumer-value evidence. This survey did not independently verify today's installed module bytes; use the root delivery verification for that status. Reader breadth remains conditional on an actual failed query or preparation step.

## Prioritized 80/20 sequence

| Priority | Smallest deliverable and deciding experiment | Cost / stop rule |
| --- | --- | --- |
| 1 | One source/reading display plus the four reference-feedback controls above; use the existing action and export route | Small–medium, no model calls. Stop when the exact challenged reading survives reload/export and a changed reading remains distinguishable. |
| 2 | Freeze a small set of new queries containing exact citation lookup, paraphrase, a missing-statement case, repeated grouped context and an unresolved target. Compare source-only with separate-list combination and selected evidence expansion | Medium; saved outputs support wiring. Predeclare complete required support and a genuinely binding text budget. Adopt only if useful provisions/context improve without critical lost support or duplicate crowding. |
| 3 | Prepare one bounded workflow decision flow from source alone and from the extracted draft; review boundary cases and record preparation/correction effort | Medium before integration. Stop at a reviewed draft or a clear failure. Only its demonstrated source or semantic gap promotes R12/R16/R25. |
| 4, conditional | For a needed relationship, run the fixed-target comparison without affected-action descriptions, then separately replay subset application and stale-target controls | Medium. Adopt only if correct links survive, wrong links remain excluded and disputes remain visible. Reuse one packet; avoid target-per-call expansion. |
| 5, conditional | Compare the useful optional operation with the full audit/refinement route using the same inputs and task labels | Medium. A smaller public callable earns implementation only when useful findings survive at lower total cost. |

The full route currently includes initial audit, recovery/relationships and final audit; `audit_run` itself runs inventory then comparison (`P/audit.py:489–504`; `P/refinement.py:471–478,551`). Existing private helpers are available, not separately supported product operations. R26 should count missed findings and introduced defects alongside tokens. An empty recovery response is insufficient reason to remove it, and smaller JSON files are not evidence of lower provider billing.

## Invariants, counterfactual and verdict

**Preserved commitments:** cheap extraction with optional deeper work; source passages retained independently of extracted statements (`P/discovery.py:52–85`); meaning approval distinct from operational authorization (`P/review_store.py:352–358`); immutable source/reading evidence and distinct unresolved outcomes. The new consumer work relies on these boundaries rather than changing them.

**Removal probe:** without new model investigations, the source-navigation and feedback example still works; without a source-backed result display, the same feedback machinery does not yet help a discovery user. Without a workflow adapter, a reviewed preparation comparison still answers whether extraction saves effort. These are reasons to prioritize consumers over additional infrastructure.

**Kill criteria:** defer result combination if source-only yields equally complete support with fewer duplicate hits; defer preparation automation if source-only preparation is clearer or faster after corrections; defer per-target adoption if semantic ambiguity merely shifts into confident wrong edges; defer smaller public operations if no named caller benefits.

**Verdict: RECONSIDER the breadth of the next batch; keep the overall direction.** Deliver discovery feedback first, measure one result-combination decision, and prepare one separate workflow example. The code supports the proposed reuse with high confidence. Improvements in discovery, human effort or model correctness remain hypotheses until those bounded comparisons run. Failed native-title defaults, forced-context and affected-action variants remain closed as defer.
