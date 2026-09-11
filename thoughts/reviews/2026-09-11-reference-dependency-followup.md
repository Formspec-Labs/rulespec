# Reference dependencies: follow-up decisions

**Keep one reference reader and one source-address index, but split the next decisions by the evidence each needs.** Fix the demonstrated CFR range/prose defect upstream first. Existing exact-source navigation can support a consumer now; general title inference, paragraph reconstruction and historical correspondence remain separate work.

Scope: R3, R7–R13 and R20 in the [canonical task list](../plans/2026-09-10-reference-integration-task-list.md). This supplements the earlier [source](2026-09-11-remaining-source-cross-relevance.md) and [consumer](2026-09-11-remaining-consumer-cross-relevance.md) surveys. It reviews product navigation and supporting verification, not legal interpretation or general extraction accuracy.

## Verified frame and lineage

Read current source and repository instructions on 2026-09-11. Heads at the final check: Rulespec `551a1d6`, RefSpec `84bc634d`, SpicySearch `10824d4`, Spicy Regs `bf10365`. The installed grammar, application reference adapter and `uslm.py` matched their source bytes. Small Python probes used `.tools/document-poc-venv/bin/python -B`; no models, network, installs, builds or full suites ran. Only this report was written.

| Prior decision or result | Consequence here |
| --- | --- |
| Task list:103–120 separates recognition, lookup and governing meaning | A successful lookup supports navigation; it does not settle applicability. |
| RefSpec `docs/decisions.md:1111–1136` (REF-024), narrowed by REF-048 | Reuse installed packages and pinned source artifacts; do not introduce sibling-source imports. |
| Native-context result `thoughts/experiments/2026-09-11-cfr-native-context/README.md:59–88` | Grounded native TITLE data alone does not identify every citation's intended title. |
| Reverse-title delivery `thoughts/experiments/2026-09-11-cfr-reverse-title/README.md:3–8,83–91` | Explicit suffix reading and corrected discovery CLI parity are delivered. Older installation caveats in the two surveys describe their earlier snapshots. |

Paths below use **App** = `packages/rulespec-extrapolator/src/rulespec_extrapolator`, **Graph** = `packages/rulespec-projection/src/rulespec_projection`, and **Ref** = `/Users/mikewolfd/Work/RefSpec/src/refspec/registry`.

## Additional findings and decisions

### 1. Reshape the R9–R12 grouping into shared infrastructure with independent gates

The earlier source survey's shared-index recommendation still holds. Its sequence “native title context, then paragraph addresses” should not become a prerequisite chain. RefSpec `find_cfr_citations` still deliberately accepts explicit citations only (`Ref/citation_grammar.py:2742–2766`). Native section indexing uses the same reader on publisher TITLE/SECTION attributes (`Ref/ecfr.py:17–60`); it does not bind an omitted title in prose or derive paragraph parents.

The smallest next grammar change is independent of both. `_read_cfr_item` commits to a range whenever the connector matches, then refuses when its endpoint cannot be read (`Ref/citation_grammar.py:2828–2851`). The installed reader reproduced:

| Probe input | Current result |
| --- | --- |
| `41 CFR § 50-202.2 to the same extent as other firms.` | Refused as `range_end_unread`; occurrence ends after `to the`. |
| `41 CFR § 50-202.2 through the agency` | Same refusal; a constructed ordinary-prose control. |
| `41 CFR §§ 50-202.2 to 50-202.4` | Both written endpoints retained. |
| `41 CFR §§ 50-202.2 to ???` | Refused; no accepted first-coordinate candidate. |

Raw context matters: the actual section says workers “may be employed at less than the minimum wage prescribed in § 50-202.2 to the same extent such employment is permitted under section 14 of the Fair Labor Standards Act.” The comparison connects permissible employment to another provision; it does not state a numerical endpoint. Source: `thoughts/experiments/2026-09-11-cfr-native-context/inputs-complete/compound-part.xml:1–2`. The explicit-title probe above is constructed, not the source's literal spelling.

**Proposed:** distinguish ordinary following prose from an intended but unread endpoint inside that shared item reader. Preserve uncertain cases as refusals; merely requiring a numeric endpoint would wrongly convert `through unknown` into an accepted single coordinate. Test occurrence, identity-only and authority APIs together: the latter two also consume this reader (`Ref/citation_grammar.py:2923–2931`; `RefSpec/tests/test_cfr_ranges.py:80–98`). Include reverse forms, lists, following explicit citations, notes, paragraph breaks, damaged endpoints and nested ranges. Retain the replaced behavior as a test oracle with declared divergences. No R8 migration or model comparison is needed to decide this fix.

### 2. Keep R3 resolution distinctions visible before expanding R12

The source join intentionally admits only exact supported shapes (`App/reference_sources.py:19–31`). A CFR pinpoint such as `49 CFR 390.5(a)` is retained as a reading but receives no section-body fallback. Notes, ranges, parts and appendices also stay outside this lookup; the guard is tested at `packages/rulespec-extrapolator/tests/test_ecfr_sources.py:73–81`.

There are therefore different unresolved states a consumer must preserve: parser refusal, accepted reading outside lookup scope, attempted lookup with no selected target, multiple selected targets, and located text with `edition_match=not_established` (`App/references.py:47–68`; `App/reference_sources.py:70–106`). Currently an unsupported accepted shape is simply skipped before a resolution record is assigned. A display must not label all missing resolution records “target absent.”

Another distinction is deliberate: a uniquely contained text reading moves under its publisher link, retaining its own value and disposition (`App/uslm.py:172–192`). External lookup visits top-level candidates only. If publisher href and printed citation disagree, only the publisher href is looked up; the text reading is retained without a separate target search (`packages/rulespec-extrapolator/tests/test_reference_sources.py:123–129`). This preserves disagreement but is not symmetric investigation of both possible targets.

**Proposed:** share these distinctions with R18 feedback and one R17 display. Add an explicit unsupported-lookup reason only if that consumer needs it; a new general typed reference schema is not a prerequisite. If a disagreement-review consumer later needs both sources, attach results to each reading separately and preserve the conflict. Never turn the located printed target into proof that the publisher link was correct.

### 3. Reuse exact current-document lookup before rebuilding paragraph hierarchy

The existing API already locates explicit USC references within a primary XML document when that document is also supplied in `reference_sources`; the CLI can pass the same file with `--reference-source` (`App/cli.py:162–171`). The existing test covers this at `packages/rulespec-extrapolator/tests/test_reference_sources.py:156–160`.

A constructed installed probe used a USLM section `/us/usc/t5/s553`, text `See 5 USC 553(b)(B).`, and a native paragraph `/us/usc/t5/s553/b/B`. Ordinary scanning returned the reading without a target; `scan_references(doc, reference_sources=[doc])` located the paragraph. This needs no omitted-title inference, new paragraph parser or model pass.

The same probe counted one `uslm.read_xml` call normally and two when resupplying the primary document: publisher links construct a `SourceIndex` and the optional join constructs another (`App/uslm.py:130–135`; `App/reference_sources.py:34–43`). External duplicates are already deduplicated within the join (`test_reference_sources.py:97–105`). This is a narrow duplicate-read opportunity, not evidence that a global cache is needed.

**Proposed:** use the existing invocation in a consumer pilot. If normal same-document lookup is adopted, reuse that scan's verified index across link attachment and target lookup, with a call-count test and unchanged target/evidence output. Do not change `source_passages` merely to give native addresses a place to live: passage boundaries control identity, and parents drive `with_context` (`App/documents.py:104–143,147–165`). Native address additions should leave those behaviors unchanged unless a separate comparison justifies changing them.

### 4. R7 needs whole-reference scope, not just FR occurrence offsets

The earlier source survey correctly identifies `parse_federal_register_citations` as callable reuse. Its current matcher and returned `FederalRegisterCitation` retain volume and one page (`Ref/citation_grammar.py:1587–1591,4531–4547`). Installed constructed probes returned the same `{volume: 89, page: 91529}` for `89 FR 91529`, `89 FR 91529-91531`, `89 FR 91529 through 91531` and `89 FR 91529 note`; lowercase `fr` and page zero returned nothing.

This does not prove an identity-only API is wrong. It shows why a thin offsets wrapper would be insufficient for an occurrence API claiming complete references. **Proposed:** when a real FR consumer warrants R7, inspect its raw source and retain supported endpoints or explicit unsupported tails along with spans. Reuse the existing matcher, not another application regex. Include repeated mentions, longhand `Fed. Reg.`, lookalikes and range/qualifier controls. Keep other citation families independently deferred.

### 5. R8 migration is a graph-boundary decision, not a prerequisite for navigation

The Unified Agenda graph path emits citation edges from its own parser (`Graph/projection.py:802–835`), whose input also includes dictionaries and compact keys (`Graph/citations.py:595–617`). It cannot be replaced indiscriminately by a prose occurrence reader. The package deliberately has no dependencies (`packages/rulespec-projection/pyproject.toml:12–15`); the application already holds RefSpec behind its optional references extra (`packages/rulespec-extrapolator/pyproject.toml:24–25`).

There is an existing outer seam: `ProfileFacts` contains the graph facts and public `assemble(artifact, facts, ...)` consumes them (`Graph/projection.py:340–356,1276–1291`). **Proposed when a graph consumer needs the change:** compare supplying upstream readings through the producing caller against adding a narrow input to its facts builder. Preserve dictionary/compact-key handling, and explicitly decide how ranges and refusals appear before emitting edges. Do not mint a start coordinate as the identity of a whole range. A new shared grammar package is a fallback requiring evidence of repeated packaging cost, not the first step.

Also correct status prose when updating the task list: SpicySearch `PLAN.md:9–14` still says Rulespec scanning uses its strict CFR reader, while live `App/references.py:71–102` uses RefSpec for CFR/USC and SpicySearch for five other identifier families. Changing query defaults would affect an unrelated consumer.

### 6. R13 discrimination and R12 edition correspondence share evidence discipline, not implementation

`ActRelativeCitation` currently carries name, section and optional division (`Ref/citation_grammar.py:4180–4194`). `resolve_act_relative_citation` already groups possible laws, narrows on explicitly compatible division information and retains conflicting target sources (`Ref/act_resolution.py:913–982`). Explicit law/year discrimination should enter that candidate-selection path only after a source-supported relation is established; proximity alone remains inadequate.

That is separate from checking a target edition. `UscSectionOracle.from_directory` verifies its pinned tables; `section_verdict(..., edition_year=...)` reports printed-section evidence and deliberately does not turn historical nonattestation into universal absence (`Ref/usc_section_oracle.py:986–994,1278–1298`). It neither supplies body text nor proves that a caller-selected body is the citation's intended edition. The current body join states this limit (`App/reference_sources.py:100–106`).

Spicy Regs `CfrSectionsReader` is another separate callable: it acquires metadata, not bodies, and yields no records without a key (`/Users/mikewolfd/Work/spicy-regs/src/spicy_regs/sources/cfr_sections.py:15–29,97–143`). Do not add it to offline lookup as an apparent fallback for missing text.

## Smallest useful next steps and stopping checks

| Decision | Combine | Concrete check and stopping point |
| --- | --- | --- |
| Fix CFR following-prose recognition | R3 + the R9 range follow-up; shared upstream reader | Actual paragraph plus explicit controls; preserve complete/unread ranges across all three APIs and both application commands. Stop after a scoped source/wheel delivery; no native-title adoption implied. |
| Show a usable exact reference result | Existing R11/R12 + selected R3/R17/R18 | Use supplied native addresses; display located, unsupported, absent, ambiguous and edition-unknown separately. Include a publisher/text disagreement and repeated occurrence. Do not wait for a general paragraph index. |
| Extend local paragraph navigation only for a demonstrated missing target | R10 + R11 | Native identifiers first; then a bounded source-label comparison. Require exact target text, source order, duplicate-label ambiguity and unchanged passage/context controls. Numeric label arithmetic is not range membership. |
| Admit one new reference family or discriminator | R7 or R13, independently; R20 for required data | A fresh real source, misleading control, complete evidence and named consumer. Defer if richer recognition changes no useful result. |

R20 should track the inputs these selected changes actually use. The current inventory still labels the USC oracle “not exercised” and eCFR target loading “open” in older rows despite later delivered sections (`task list:386,1263–1279` versus `:928–954,1233–1238`). Refresh those rows in place and leave historical experiment results intact. A capability inventory is useful only if it distinguishes available helpers from delivered behavior.

## Invariants, counterfactuals and verdict

| Invariant | Status and failure to avoid |
| --- | --- |
| Complete literal reading and exact evidence survive | Preserved by `App/references.py:35–68`; a shortened accepted range or overwritten disagreement would break it. |
| Source addresses identify navigation, not governing conditions | Relied upon by `App/reference_sources.py:77–106`; locating more text does not license broader semantic claims. |
| Optional installed readers stay outside dependency-free graph/Core code | Preserved by the package declarations above; a direct RefSpec import in the pure graph package requires an explicit boundary decision. |

Removal probe: dropping new title inference or broad R8 migration leaves the delivered discovery/reference commands usable. Dropping the exact-source/evidence machinery would remove the ability to check a located target. That makes the latter shared infrastructure worth preserving and the former conditional work.

Kill criteria: defer a paragraph strategy if it assigns one path to ambiguous markup or silently changes context selection; reject a range fix if unread ranges escape as accepted starts; defer FR/law-year breadth if no selected consumer benefits. General historical correspondence, recursive source fetching, all-family parser consolidation and universal accuracy claims remain outside this slice.

**Verdict: reshape the dependency sequence; keep the existing ownership and evidence machinery.** The highest-confidence next correction is the shared range/prose boundary. Exact native navigation is already sufficient for a bounded consumer demonstration. The remaining recognition and hierarchy candidates need their own evidence rather than inheriting approval from source availability.
