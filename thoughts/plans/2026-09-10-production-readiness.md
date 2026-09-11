# Production readiness after the recent extraction experiments

Implemented and committed locally following approval. Keep the newer interpretation,
context-selection, and retrieval variants experimental. The
[commit checkpoint](../reviews/2026-09-11-commit-checkpoint.md) separates upstream,
Core and extraction changes from their research. No push or deployment was performed.

For current integration status and the complete reuse/extraction backlog, use the
[comprehensive task list](2026-09-10-reference-integration-task-list.md), updated
2026-09-11. It includes current CFR source integration, upstream qualifier work,
local source lookup, corpus/vocabulary reuse, quality checks and delivery criteria.
The source-credit reader, inserted-separator evidence fix, named-act policy fixes
and multi-law/scope candidate handling are installed and verified. That checkpoint
passed 497 extractor tests from source and the working installation,
448 upstream tests and 42 selected callers. The
[act-name result and receipts](../experiments/2026-09-11-act-name-multiplicity/README.md)
record the source/wheel comparisons and installed commands. The subsequent shared
USLM reader is also installed: its saved checks passed 52 focused upstream tests
and 497 working-installed extractor tests, with unchanged existing CLI results.
The subsequent readable XML preparation and normal publisher-link ingestion/export
checkpoint is installed and verified: 62 upstream tests, 11 preparation controls and 509
application tests pass. The Core selector failure is fixed in the generator using
the existing JSON-LD mapping; 146 compiler tests, 47 Rust tests and the reference
corpus pass, with zero Core divergences across the 299-case parity run. Source,
isolated wheels and the working installation match across 1,031 packaged files
and 24 new command artifacts. An independent XPath engine verifies 110 exported
XML fragments. The [readable-text result](../experiments/2026-09-11-uslm-readable-text/README.md)
preserves that checkpoint's failures and delivery evidence. Its four overlapping
citation rows and false RIN reading of `1998—Pars.` are now addressed by two
separate comparisons. The [RIN result](../experiments/2026-09-11-rin-reference-space/README.md)
reuses RefSpec's identifier-space check and retains rejected source evidence;
the [containment result](../experiments/2026-09-11-reference-containment/README.md)
associates unique contained readings without erasing disagreements or ambiguous
links. Both are installed: 523 application tests pass from source and isolated
wheels, 50 native minter tests pass in both forms, and 24 command artifacts match
the working installation. All 1,318 package files from the seven pinned wheels
match both installations. SpicySearch's query defaults and model schemas remain
unchanged. These are bounded data-quality improvements, not new extraction scores.
Explicit law/year context, qualified USC, general local paragraphs and broader
reuse work remain open. These checks made no new model calls and do not establish
an extraction-quality improvement.

The subsequent [fresh-context comparison](../experiments/2026-09-11-fresh-reference-context/README.md)
is complete: twelve calls across three selected windows. Added context recovered
none of the targeted missing meaning, changed one permission to `must` in both
title-20 observations, and produced one incomplete response. It used 8.9% more
reported tokens. Keep this selector experimental. Saved-output replay also found
two existing extraction losses: exact complete quotations crossing inserted
whitespace, and passage ranges crossing omitted newline-only entries. Those fixes
are now implemented and source-tested under R4/R23: the
[retention comparison](../experiments/2026-09-11-extraction-retention/README.md)
preserves 336 rather than 224 statement occurrences across the same twelve saved
outputs, with seven kind/modality contradictions still rejected. The full source
suite and isolated installed suite each pass 552 tests. Two additional installed
review-history controls pass. Normal reprocess/replay/reference/discovery/review
commands work, and the working environment now uses the verified retention wheel.
Reprocessing changes some claim IDs; the controls verify original reviews remain
intact and the new output stays pending. Broader continuity remains under R18, and
optional-reader runtime capture is also now delivered. The
[capture result](../experiments/2026-09-11-reader-runtime-capture/README.md) records
559 source and installed tests, detected reader/helper mutations, optional-package
absence controls, unchanged candidate/discovery data and working-wheel checks.
The graph differs only in its run-derived lineage ID and links, with the first
overly strict comparison preserved. Qualified USC is the next R5/R6 integration.
The earlier separator repair below fixed source-passage discovery;
it did not fix complete-statement compilation.
The adoption assessment below preserves its earlier checkpoint.

## Implementation and verification

- `3cec55d`: compact exemption links and their saved live evidence committed.
- `6d3f66e`: withheld proposals persist through the existing `observe` action, with checker verdict, target identities and request provenance. Unsupported, unknown and unjudged outcomes remain visible. Accepted meaning and approvals remain intact. Observations about superseded claims stay visible at document level. Replay checks their derivation from captured judgments.
- `2c28fa9`: the browser review is the selected consumer. Overlapping verified source spans appear once, with compact role controls for exact highlights. Distinct occurrences remain separate. Discovery already shares evidence by ID; it needed no new format or materialization layer.

Verification after integration: 439 Python package tests and four Node evidence tests passed. Browser inspection confirmed the consolidated passage and that the Actor control highlights only the correct occurrence after a Unicode character. The follow-ups made no new model calls; these checks establish persistence, replay and presentation behavior, not a new semantic-accuracy result. Other research artifacts remain separate from these implementation commits.

The assessment below records the decision made against HEAD `176baab` before implementation. Its two follow-ups are now complete as described above. “Committed” means present in this repository, not verified deployed.

## Original adoption assessment: compact links

**Compact existing-exemption links.** The model names the current exemption and target aliases; deterministic code retains its meaning, source evidence, and prior links. Existing source challenge, preview, revision checks, and replay remain in use. No new Core schema.

The controlled comparison preserved five links while reducing proposal answer tokens 85.8% and proposal-plus-challenge total tokens 9.0%. This is a narrow efficiency result, not document-wide savings or better semantic accuracy. The local integration subsequently passed 440 package/schema tests and a two-call live railroad check with five supported/applied links. Those saved checks are the verification evidence; they were not rerun during this prioritization review. See [integration result](../experiments/2026-09-10-compact-link-integration/README.md). Commit the implementation with its relevant tests and evidence; preserve unrelated research separately.

## Original follow-up scope (now implemented)

1. **Expose withheld refinement judgments.** `refinement.py` preserves unsupported/unknown judgments in step results, but these do not automatically reach the final rulebook/discovery issues. Reuse `ReviewStore`'s existing `observe` action and source/request provenance to attach them to the relevant current claim or run. Preserve the proposed target and the checker verdict as a model assessment, not a confirmed source defect or accepted relationship. Test reject/unknown/no-edit cases, stale identities, reload/export and replay. No new model behavior is needed to test this data plumbing.
2. **Assemble evidence text once per consumer request.** `export_discovery()` already provides shared evidence IDs and roles. The experimental `records(..., 'packets')` materialization can repeat overlapping quotations; a consumer should use the existing shared representation and deduplicate source positions while retaining roles and distinct occurrences. Select an actual consumer before implementation, and prove that source text/support availability stays unchanged. Do not confuse this deterministic presentation improvement with the failed shared-catalog prompt treatment or a measured ranking improvement.

These recommendations addressed observed data-flow gaps. Their deterministic integration is complete; experimental model changes remain outside production.

## Already committed: do not reimplement

- Existing exemptions retain `exemption` / `not_required` meaning while gaining qualification links, and source-reference challenges avoid copied-quotation whitespace failures: `1426960`.
- Actor/definition enrichment, persistent term identity, claim-ID targets, review observations/provenance, and sparse discovery continuity: `04eda27` / `c4aa4ad` and subsequent checks.
- Source passage fallback, shared discovery evidence references, and usage accounting already exist. Use them instead of proposing another representation or counting layer.

## Hold out of production

- Independent per-target decisions: useful 2/5 → 4/5 result, but the tested bundle failed its broader gate, lost an expected applicability link, and added overbroad explanation. Clarify relation meaning and test without new affected-action prose.
- Full-section context: supplies 22/23 selected spans versus 11/23, but comprehension and false-inheritance behavior with this context remain unmeasured. Keep the current selector until that comparison.
- Source/statement concatenation before ranking and shared evidence prompt compression: measured regressions despite some cost/support gains.
- Target-enumeration instructions, extra contrast explanations, relationship-assisted audit, and actor passage references: no demonstrated gain over their relevant controls.
- At this assessment's checkpoint, RefSpec CFR readings lost subsection paths and no application adapter had been tested. The newer occurrence API now retains pinpoints and is integrated and verified in the installed application (470 tests; outside-checkout CLI checks). The [CFR integration](../experiments/2026-09-11-cfr-integration/README.md) records the remaining subpart-qualifier and local-reference gaps. Use the linked task list for current status.
- Automatic full refinement for every document: the cheap path remains the default; current evidence does not justify making optional audits/recovery/relationship passes universal.

The historical integration README's statement that per-target judgments were “untested” describes its earlier checkpoint. They have since been tested in [the targeted pilot](../experiments/2026-09-10-design-targeted/README.md), which failed its broader gate. Do not treat stale checkpoint wording as current status.
