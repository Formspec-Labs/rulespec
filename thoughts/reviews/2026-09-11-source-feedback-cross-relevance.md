# Source, lookup and feedback: cross-relevance after the feedback implementation

**Decision: preserve the shared readers and advance a bounded reference consumer.** The uncommitted feedback operation removes the need for another feedback store or rejected-reference ID scheme. This survey found a source-diagnostic omission; the parent task corrected it locally while final packaging continued. Use that corrected operation with delivered native lookup. General paragraph reconstruction, title inference, graph-parser migration and historical correspondence remain independent decisions.

## Frame, status and lineage

Read-only inspection on 2026-09-11, starting at Rulespec `fd643af` and RefSpec `84bc634d`. Only this report was written. Scope: R3, R8–R14, R18 and R23 in `thoughts/plans/2026-09-10-reference-integration-task-list.md`; category: reference navigation and review, with supporting evidence machinery. Recommendations are not accuracy proof.

Paths: **App** = `packages/rulespec-extrapolator/src/rulespec_extrapolator`; **Tests** = `packages/rulespec-extrapolator/tests`; **Ref** = `/Users/mikewolfd/Work/RefSpec/src/refspec/registry`; **Plan** = the task list above.

| Authority or earlier result | Current consequence |
| --- | --- |
| Plan:113–129 separates recognition, lookup and governing meaning | A located body or saved complaint does not settle applicability. |
| RefSpec `docs/decisions.md:1111–1136,4014–4021` | Keep installed-package/artifact exchange and existing owners; source review is not permission for sibling-source imports. |
| `2026-09-11-reference-dependency-followup.md`, findings 2–3 | Reuse exact native lookup and preserve unresolved states; broad paragraph work is not required first. |
| `thoughts/experiments/2026-09-11-cfr-range-prose/README.md:3–14,92–98` | Refines that follow-up's “fix upstream first”: numeric gating was rejected and the phrase rule deferred. The defect cannot remain a prerequisite for usable feedback. |
| `thoughts/experiments/2026-09-11-reference-feedback/PLAN.md` | Current implementation intentionally captures a challenged reading in existing history; source-only workspaces and automatic resolution are outside that slice. |

| Capability | State at inspection | Exact owner and connection |
| --- | --- | --- |
| Explicit readings, native refusals and occurrence evidence | Delivered | `App/references.py:40–102`; accepted IDs use fragment/kind/value, while rejected rows preserve positions without that ID. |
| Shared XML text, source map, native addresses and target fragments | Delivered | `Ref/xml_text.py:14–64`; `Ref/ecfr.py:17–61`; `App/uslm.py:54–127`. |
| Publisher/text association and supplied-source bodies | Delivered | `App/uslm.py:130–205`; `App/reference_sources.py:19–106`; distinct readings and distinct source pins survive. |
| Feedback helper, CLI and regression cases | Current uncommitted work | `App/reference_feedback.py:8–74`; `App/cli.py:166–175`; `Tests/test_reference_feedback.py:37–226`. Parent task owns final build/install/commit evidence. |
| Existing observation persistence and discovery export | Delivered, now reused | `App/review_store.py:276–277,305–313,410–411`; `App/discovery.py:108`. No new Core shape is required for this connection. |
| Source-only feedback, wholly missed mentions, feedback closure UI | Missing user entry points | Feedback requires a saved run and existing candidate/rejected index; `App/cli.py:166–174`, `App/reference_feedback.py:17–19`, `App/review_store.py:88–119`. |
| Omitted-title/paragraph strategies | Experimental, not adopted | Plan:848–855,889–914 records wrong title assignments, uncertain single paths and changed context selections. |
| Named-act identity and USC edition oracle | Callable, different jobs | `Ref/act_resolution.py:913–982` selects supported name/law candidates; `Ref/usc_section_oracle.py:1278–1298` reports attestation. Neither supplies matching historical body text. |

## Findings that change the next work

**1. CONCERN FOUND AND CORRECTED LOCALLY — retain the source explanation in a missing-target complaint.** The initial helper copied the selected reading completely but omitted `reference_sources[*].issues` when selecting source metadata/records. The source join already retains native-section issues and their XML evidence at `App/reference_sources.py:60–65`. Dropping them narrowed the history precisely when a user disputed why no body was found.

A direct in-memory probe reused the existing literal fixture at `Tests/test_ecfr_sources.py:267–272`, with this surrounding context:

```xml
<DIV5 N="11" TYPE="PART">
  <DIV8 N="11.100" TYPE="SECTION"><HEAD>§ 11.100</HEAD><P>Exact body.</P></DIV8>
  <DIV8 N="11.105-11.106" TYPE="SECTION"><HEAD>§§ 11.105-11.106 [Reserved]</HEAD></DIV8>
</DIV5>
```

The title-49 wrapper is constructed; the combined native shape was observed in the retained title-49 capture. Reading the neighboring exact section rules out an absent whole source: the reader indexes `11.100` and deliberately leaves the combined node unresolved, without inventing endpoint targets. The saved actual `thoughts/experiments/2026-09-11-ecfr-text/source-final/references.json` also contains 84 native-section issues, beginning with `49 CFR 11.105-11.106`.

| Probe: primary text `49 CFR 11.105.` | Result before any parent-task correction |
| --- | --- |
| Scan candidate | `not_in_selected_sources`, no target IDs, `edition_match=not_established` |
| Supplied source | `native_section_scope_not_supported`, value `49 CFR 11.105-11.106`, linked XML fragment |
| Saved observation | Issue and its XML fragment both absent; source identity and title fragment retained |

Correction now inspected: `App/reference_feedback.py:58–62` keeps supplied-source issues plus their referenced XML fragments through the same selection helper. Repeating this survey's existing-fixture probe confirms both are retained, with no target or containing body added. The parent retained the failing regression in `thoughts/experiments/2026-09-11-reference-feedback/source-issue-failure.log` and reports 17 passing focused tests; `Tests/test_reference_feedback.py:190–213` checks missing-target feedback through reload/discovery without adding bodies. Preserve these as source diagnostics, not proof that every issue explains this particular missing target. Final package delivery remains the parent task's separate check.

**2. KEEP — distinguish occurrence, challenged reading and target source without another identity system.** `references.py:66` does not include the full reading in an accepted ID. Feedback therefore correctly keeps the selected row and `digest(scan)`, plus reader/index pins (`reference_feedback.py:35–74`). Tests:37–63 explicitly change a reading without changing the accepted ID; tests:66–81 retain a rejected reading without inventing an accepted ID. XML source digests also distinguish equal prepared text from different source bytes (`Tests/test_ecfr_sources.py:44–53`). This directly serves R3/R12/R14/R18; broad claim-ID migration is not a dependency.

The reusable part is the observation data and existing history, not automatic agreement with the complaint. `ReviewStore._state` skips observations when changing claim review state (`review_store.py:276–277`). Saved issues remain visible alongside a later scan; no current code classifies them as resolved or transfers approval.

**3. RESHAPE — source selection and source interpretation have different prerequisites.** Exact USC pinpoints and publisher links already use native addresses; exact eCFR sections use `section_addresses` on prepared native nodes. Native TITLE establishes an address's title, not an omitted prose citation's intended title (`Ref/ecfr.py:17–60`; Plan:848–855). Address work should reuse `SourceIndex`, not alter `source_passages` merely to hold another index: passage boundaries determine IDs and parents affect `with_context` (`App/documents.py:104–165`).

The existing same-document `--reference-source` route remains sufficient for a consumer. Normalizing that route would justify sharing one verified index across link attachment and lookup; current calls create it separately (`App/uslm.py:133`; `App/reference_sources.py:43`). This is a bounded duplicate-read opportunity, not evidence for a global cache. Native preparation is already shared upstream; R23's unrelated DocSpec/PDF layout work need not block this use.

**4. RESHAPE — the next edition improvement can be evidence display before historical matching.** Target IDs already contain original XML identity; feedback preserves selected bodies, source pins and published USLM fields (`App/uslm.py:119–126`; `reference_sources.py:45–59`; `Tests/test_reference_feedback.py:147–187`). eCFR publication output currently extracts TITLE `N`, not native `DATE` (`reference_sources.py:53–56`), even though the reader retains native attributes. If a dated-source consumer needs it, carry that publisher field with existing XML evidence; do not label it legal-edition correspondence. `section_verdict(edition_year=...)` supplies a different attestation question and cannot settle which body the citation intended.

R13 shares this evidence discipline, not an implementation dependency: explicit law/year discrimination belongs in the existing name-candidate selection after source-supported linkage. Act-relative identity results currently do not enter body lookup because `_identifier` accepts publisher/USC/exact-CFR shapes only (`reference_sources.py:19–31`). Treat any act-to-body connection as a separately requested join that preserves competing identities and unmapped act subsections; do not make all R12 work wait for it.

**5. DEFER — R8 migration and wider parsing do not gate this consumer.** Unified Agenda still invokes its own structured-input graph reader (`packages/rulespec-projection/src/rulespec_projection/projection.py:802–818`); that package deliberately has no dependencies (`packages/rulespec-projection/pyproject.toml:12–15`). Feedback consumes saved application observations and even reloads without optional readers (`Tests/test_reference_feedback.py:216–226`). Replacing the graph reader, adding a grammar package or completing general CFR range syntax delivers no prerequisite for that persistence path.

## Up to three small work packages

| Package and shared owner | Prerequisites and acceptance checks | Counterexamples and deferral |
| --- | --- | --- |
| **1. Finish durable feedback fidelity — R3/R18 with R12 diagnostics.** Rulespec review owner keeps `reference_observation`, `ReviewStore.observe` and existing fragments as the only path. | Package the local correction to finding 1; preserve the complaint, selected reading, source issue and evidence through reload/discovery. Retain existing changed-reading, rejected-reading, repeated-occurrence and stale-revision checks. Update only the R18 subitems actually delivered after final wheel/command verification. | Missing linked issue fragment must fail; a no-target report must retain its source issue; unrelated bodies remain omitted. Defer automatic resolution, claim approval and cross-reprocessing migration. |
| **2. Exercise one native-reference review consumer — R11/R12/R14/R18.** Rulespec consumer owns display; existing `SourceIndex` owns addresses/evidence. | Use an existing saved run and primary XML as `--reference-source`; show literal/native readings, target text, selected source identity and unresolved edition status. Add explicit unsupported-lookup display only where needed; share the verified index only if this becomes the normal invocation. | Distinguish parser refusal, unsupported accepted shape, absent selected target, ambiguous targets and located/edition-unknown. Include duplicate IDs, equal text/different XML pins and publisher/text disagreement; lookup currently investigates the top-level publisher reading only. Defer general hierarchy, target fetching and historical correspondence. |
| **3. Add source-only reporting when the consumer needs it — R3/R18/R23.** Rulespec document/review owner provides one initializer and reuses compilation/evidence/history. | Prove a prepared document can enter the existing review machinery with zero claims and zero model calls; the existing test initializer at `Tests/test_reference_feedback.py:23–28` establishes a narrow starting point. For wholly missed mentions, accept an exact selected source span through existing evidence validation rather than requiring a nonexistent scan row. | Include repeated equal text, inserted separators, a span outside the pinned document and no optional reader during reload. Preserve source/reading distinction; never fabricate scanner acceptance. Defer until a source-only reporting use is selected, and do not create another store or generic migration framework. |

## Invariants, limits and verdict

Preserved: exact source evidence stays separate from interpretation; XML pins stay separate from prepared-text identity; native lookup does not establish governing conditions; observations do not change claim approval; installed optional readers remain outside the dependency-free graph package. Finding 1's concrete fidelity exception is corrected in source, pending final delivery evidence.

Removal test: omitting R9/R10 inference, R8 migration and historical correspondence leaves these three bounded paths possible. Removing saved reading/source context would prevent a later reviewer from reconstructing what was challenged. If the selected consumer gains no useful navigation or actionable report, defer more breadth rather than adding infrastructure.

Verification here used scoped source reads and `.tools/document-poc-venv/bin/python -B` in-memory probes; installed RefSpec `ecfr` and `citation_grammar` bytes matched the sibling source. No models, network, installation, commits or full suites ran. Earlier feedback logs record 661 source/isolated tests; those precede the added source-issue regression and are parent-run receipts, not tests rerun by this survey. Bulk feedback would hash the whole scan per observation (`reference_feedback.py:73`); measure that only if bulk use appears.

**Verdict: RECONSIDER the dependency sequence; keep the delivered ownership and shared helpers.** Intent and current feedback shape mostly match; the actionable value is preserved review context and native navigation. Confidence is high for the traced capability boundaries and reproduced omission, moderate for priority judgments, and absent for general extraction accuracy.
