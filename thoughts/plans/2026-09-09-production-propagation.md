# Production propagation plan

Implementation status: the user authorized this plan on 2026-09-09. The operating
guide and maintained case index are committed in `beb3fbf`, together with all four
experiments. Low extraction / medium audit defaults are now implemented locally;
final verification and delivery are recorded in the [implementation check](../../examples/document_understanding/production-defaults-check/README.md).
The proposal below preserves the original decision context.

The current experiment is complete. Propagate the evidence into the operating
guide and maintained evaluation cases. Consider making the recommended thinking
levels explicit defaults. Preserve the current extraction semantics: the recent
tests do not support another instruction, passage-merging rule or fuzzy matcher.

This plan covers the normal extractor code path and its operating guidance. It
distinguishes code already present at `b27a182` from proposed changes; it does not
claim a deployed release. The user requested aggregation, so the items below are
reviewable proposals, not newly applied runtime changes.

## Proposed production work

| Priority | Change | Current code / exact place | Evidence and limits | Acceptance check |
|---|---|---|---|---|
| 1 — ready | Refresh the operating guide with the measured strengths and remaining failures | `packages/rulespec-extrapolator/README.md`, current recommendation and remaining-work sections | Four planted contradictions detected with four original controls accepted; original notice scope failure still missed twice. Use audit for review triage. | Link the saved evidence; distinguish detection from completeness; remove statements that new-source checks or the field-distinction experiment have not happened. |
| 1 — ready | Preserve the selected positive and negative cases as maintained evaluation inputs | Reuse the saved fixtures/labels and existing `evaluation.py`, `audit._judgments` and `audit._assessment` | We now have explicit contradiction controls, correct counterparts and observed false passes. These are selected cases with revisable labels, not general accuracy statistics. | Keep source hashes, field-specific expected behavior and capture provenance. Index/reference existing fixtures instead of duplicating full runtimes. Keep live model evaluation separate from deterministic CI/replay. A current miss stays a known failure, not an expected-success assertion. |
| 2 — configuration decision | Make low extraction and medium audit the explicit default thinking levels, if we want the default invocation to follow the operating recommendation | `cli.py` currently omits both defaults; `extraction.extract_run` and `audit.audit_run` also default to `None`. Both stages already accept, record and replay explicit levels. | The documented recipe and completed full-source runs use these settings; earlier medium/high comparison supports medium as a useful cheaper candidate. Recent trials do not isolate these defaults against the provider's implicit default. This is a configuration promotion, not a new measured semantic fix. | Define each stage's default once; preserve explicit overrides and historical request reconstruction. Test omitted-option behavior, explicit low/medium/high/None behavior at supported interfaces, and saved replay. Run one bounded live workflow after a default change. |

The first two items can be delivered without altering extraction behavior. The
thinking-default item is the only proposed runtime change from this aggregation;
make it a distinct decision and commit so its effect remains attributable.

### Concrete operating-guide edits

- Explain that ordinary extraction represents meaning in prose and can still omit
  qualifications. The current phrase “ordinary extraction preserves complete
  meaning” reads as a guarantee that the saved failures do not support.
- Replace the stale statement that a fresh complete workflow remains unmeasured
  with the two-source passport/waste check, preserving the older experiment's
  historical results and counts as historical evidence.
- Replace the proposed-but-now-completed field-distinction test in remaining work
  with its result: the auditor can select complete governing evidence and still
  accept incomplete standalone wording.
- Add the explicit-contradiction result with its sample limits and the unsupported
  “mutually exclusive” wording in one rationale.
- Keep the user's two consumption paths clear: imperfect source-backed discovery
  with later feedback, and source review before deriving an executable workflow.
  An optional audit fits both; its pass does not certify complete rules.

### Evaluation cases to retain

| Case | Existing source | Desired behavior / known result |
|---|---|---|
| Passport posts versus agencies/centers | `audit-mutation-sensitivity/fixtures/passport.json` plus mutation diff | Identify the wrong actor without transferring agency approval conditions to posts; planted mutation detected. |
| Passport IN response exemption | Same fixture | Preserve not-required versus required; planted reversal detected. |
| Waste label components | `audit-mutation-sensitivity/fixtures/waste.json` plus mutation diff | Both components remain required; planted AND-to-OR change detected. Do not infer exclusive OR. |
| Waste excess deadline | Same fixture | Preserve three consecutive calendar days, trigger and destinations; planted thirty-day change detected. |
| Correct counterparts and neighboring rules | The original views in `audit-mutation-sensitivity` | Avoid falsely rejecting correct targets, IN-change restrictions and closed-container exceptions. |
| Notice original / full logic / full statement | `audit-field-distinction/views/` and original fixture | Distinguish incomplete summary from qualifications retained in logic. Current audit fails the strong criterion; keep that visible. |
| Independent-rule boundaries | `passage-boundary-experiment/fixtures/` and `standalone-qualification-experiment/fixtures/controls.json` | Avoid transferring actors, seasonal conditions or optional methods into unrelated rules. |

All paths in this table are under `examples/document_understanding/`. The existing
experimental comparison views are not full validated Core graphs. Reuse them as
comparison/evaluation inputs; do not feed them directly into the full audit CLI,
which validates a complete graph. No new Core schema or generic experiment framework
is needed to maintain these cases. Live model outcomes must not be presented as
deterministic unit-test guarantees.

## Already present: retain and include in any delivery checklist

| Capability | Verified location | State |
|---|---|---|
| Native CUE source and generated extraction/meaning/inventory schemas | `schema_data/document-understanding.cue`, `tools/build_extraction_schemas.py`, schema loader | Present; extend existing definitions if future evidence supports a semantic change. |
| Example inheritance and complete alternative guidance | CUE `#Summary` and alternative/choice descriptions | Present and shared with audit; do not add a competing Python schema or duplicate instruction layer. |
| Passage IDs in inventory and comparison | `audit.py` inventory/comparison schemas, `_judgments`; `extraction.passage_catalog` / `resolve_passage` | Present, audit version 4; comparison integration committed in `83caace`, new-source checks in `b27a182`. |
| Full `logic_text` and source records in discovery | `discovery.export_discovery` | Present; committed with research in `68de277`. |
| Temperature 0 and explicit thinking/output settings recorded for replay | `cli.py`, `extraction._record_window`, extraction/audit replay | Present. Low/medium are currently a documented recipe, not implicit thinking defaults. |
| Core evidence, applicability, provenance and review history | Existing compiler/review store; shared `Finding` output in audit | Present; no new graph record type is required for these lessons. |
| Separate model assessment and semantic completeness | `audit._assessment`, CLI audit output, discovery accounting | Already emits `semantic_completeness: not_established`; review completeness is separate. Do not build a duplicate approval gate or relabel every passed report as a failure. |

These are verified in the current checkout, not newly implemented by the four
latest experiments and not proof of a deployed release.

## Do not propagate from the recent experiments

| Candidate | Reason |
|---|---|
| Stronger standalone-summary description | No incremental target improvement; treatment also lost two dedicated scope-evidence bindings. |
| Automatic joining of sentence/paragraph boundaries | Diagnostic joining recovered evidence context but fixed no standalone statement. No general safe boundary policy was tested. |
| Whitespace/fuzzy matching fallback or narrowed passage matches | Earlier controls admitted ambiguous/layout-sensitive matches; passage references already address citation reliability. No demonstrated need for another layer. |
| Extra classification wording, judgment reordering or forced grouping | Earlier tests showed regressions, no primary improvement or inconsistent adherence. Existing representations can already express complete meanings. |
| New explicit condition/exception schemas or automatic links | The remaining gap is reliably identifying what governs what; available fields already express the tested meanings. Schema availability is not an inference algorithm. |
| Treating `passed` as automatic approval, or enabling `ClosureClaim` | The current audit missed the known notice defect twice while citing its governing source. |
| New UI or automatic workflow/form generation | Outside this extraction-focused propagation; source review remains necessary for that downstream use. |

Do not bundle output caps or audit window size into a thinking-default change.
Current defaults are 24,000 characters / 16,384 output tokens for extraction and
3,000 characters / 32,768 output tokens for audit; the documented full-source recipe
explicitly uses 24,000 and `--max-output-tokens provider` for both. That difference
must remain visible. Broader default changes need their own cost/long-document
validation; the short saved documents do not establish a universal choice.

## Delivery sequence and verification

1. Update the operating guide and index the selected evaluation cases, referencing
   original captures and keeping the known misses visible. Preserve every original
   experiment and review label. A compact case index is sufficient.
2. Decide explicitly whether to promote the thinking-level recipe to defaults.
   If so, implement only that configuration change with focused request/override/
   replay checks. No schema or semantic-generation change is included.
3. Run the relevant existing tests and native CUE drift check for actual code or
   schema changes. Reuse the saved comparison and extraction replay commands;
   keep historical raw responses and hashes unchanged. Do not rerun live calls
   merely to verify documentation.
4. Review and commit the selected exact paths, keeping runtime configuration
   separate from research/docs. Commit or release is a later execution step;
   neither happened during this aggregation.

The latest four experiments are complete: 26 model calls, 568,045 reported tokens,
all captured runs replayed, original failures preserved. The
[quality decision](../reviews/2026-09-09-extraction-quality-decision.md) explains the
product recommendation; each linked experiment retains its own preregistered gate,
raw data, review and limitations. This plan is the requested aggregation. No further
API experiment is needed to prepare it.
