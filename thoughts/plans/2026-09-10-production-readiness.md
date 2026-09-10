# Production readiness after the recent extraction experiments

Implemented locally following approval. Keep the newer interpretation, context-selection, and retrieval variants experimental. No push or deployment was performed.

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
- RefSpec citation reuse: strong existing starting point, but current CFR output loses subsection paths and does not resolve local paragraph references. No adapter or production integration was tested.
- Automatic full refinement for every document: the cheap path remains the default; current evidence does not justify making optional audits/recovery/relationship passes universal.

The historical integration README's statement that per-target judgments were “untested” describes its earlier checkpoint. They have since been tested in [the targeted pilot](../experiments/2026-09-10-design-targeted/README.md), which failed its broader gate. Do not treat stale checkpoint wording as current status.
