# Rulespec reuse and extraction: comprehensive task list

Updated 2026-09-11 against the local code and saved evidence. This is the current
backlog for the reference work, useful sibling-repository capabilities, and their
extraction/discovery consumers. R1–R26 are stable identifiers for follow-up work.
This update includes retention, optional-reader capture, qualified USC delivery,
removal of unused citation copies, compilation occurrence delivery and the
independent part-zero minter correction and complete CFR range delivery. The latest
application suite passes 616 tests from source and its installed wheel; the graph
package's preceding checkpoint passes 30 tests from source and its isolated wheel.
Earlier counts belong to their linked checkpoints. Original captures and reviews
remain intact; no model call, publication or deployment was needed for this cleanup.

**Recommended next slice:** finish the bounded R12 source-format assessment, then
measure this context in one discovery or workflow consumer. Optional USLM target
text is now connected to both commands; the
[body comparison](../experiments/2026-09-11-reference-bodies/README.md) preserves
exact provisions and parent context without changing model prompts. Migrate remaining R8 graph readers when that
consumer needs them, preserving structured-input behavior. The [caller trace and direct comparison](../experiments/2026-09-11-citation-ownership/README.md)
are complete; unused act-name and compilation-locator copies are removed.
The [whole-token experiment](../experiments/2026-09-11-cfr-whole-tokens/README.md)
recovered 189 compound tokens but failed the complete-range gate: explicit endings
still disappeared. Its [coordinated successor](../experiments/2026-09-11-cfr-ranges/README.md)
is now installed: complete compound keys, explicit endpoints, consumer guards and
source evidence survive. Independent
[representation](../reviews/2026-09-11-cfr-range-representation.md) and
[consumer](../reviews/2026-09-11-cfr-range-consumers.md) reviews identify the
coordinated grammar, authority/Arrow rows, comparisons, explanations and application
changes delivered together. The [part-zero utility correction](../experiments/2026-09-11-cfr-zero-parts/README.md)
is separately installed: nine verified keys now mint, all 8,415 nonzero keys keep
their prior results, and 112 upstream tests pass. The current CFR scanner does
not use this minter; this does not claim better extraction or migration of R8.
Compilation volume/page occurrences are now connected through RefSpec, including
page-first court citations and the existing publisher XML path. The
[comparison and delivery](../experiments/2026-09-11-compilation-occurrences/README.md)
removes nine false CFR parts from the saved opinions. One citation interrupted by
a PDF footnote remains a source-reading-order failure under R23. Prefer publisher
XML containing the needed text in a supported format; the caller currently
chooses the source, and `.xml` support means USLM, not arbitrary XML.
The selected
USC reader is [connected and installed](../experiments/2026-09-11-usc-delivery/README.md),
including an upstream fix for the newly observed `et seq.` qualification loss.
Retention, review-boundary checks and reader capture are delivered. The upstream,
Core and application changes are now [committed locally](../reviews/2026-09-11-commit-checkpoint.md),
with research preserved separately. The 26 workstreams
cover the full candidate backlog; they are not prerequisites for a useful release.

### Read this first

| Order | Outcome | Tasks | Completion evidence |
| --- | --- | --- | --- |
| 1 — Delivered | Preserve generated statements in the working installation | R1, R4, R23 | Installed tests; reprocess/replay/export/reload; exact source and wheel identities |
| 2 — Delivered and committed locally | Preserve reviews and record supported installed readers | R1, R18 | Passing history/drift controls, build receipt and scoped commits |
| 3 — Reuse the next needed reader | Preserve qualified USC references and resolve useful local or external targets | R5–R13, R20 | Actual failures and counterexamples pass through the existing adapter; target text has a pinned source |
| 4 — Connect existing data | Use publication fields and shared term/agency identities where a consumer benefits | R20–R22 | A named consumer gains useful links without false merges or duplicated parsing |
| 5 — Demonstrate user value | Improve discovery or preparation of one reviewed workflow | R17–R19, R24 | Fresh queries/scenarios, source-backed review, measured omissions and effort |
| Separate experiments | Improve one semantic failure or optional-stage cost | R16, R25, R26 | A bounded comparison supports adopt/defer; failed context and explanation variants stay experimental |

Each detailed task below names its owner, dependencies, reuse point and completion
check. An available helper is not automatically an integrated feature. The order
above is a prioritization judgment, not a measured ranking of all possible value.

## Decision and scope

Preserve the delivered publisher structure, readable text and local reference
targets, alongside the installed Code of Federal Regulations (CFR) and named-act
reader. The observed RIN and duplicate-row fixes are delivered. The fresh test
supplied missing context but did not recover its meaning. Prioritize preserving
correct generated output before another model intervention. Reuse RefSpec,
SpicySearch, Spicy Regs and existing corpus artifacts where they solve a
demonstrated problem. Recognition,
target lookup, and deciding whether a provision governs another provision remain
separate tasks.

For this work, a feature is useful when it has a named consumer, an observable
benefit, and less maintenance cost than rebuilding it. Its smallest comparison
must preserve source evidence and pass relevant counterexamples. A feature can
also improve cost or remove duplication without changing semantic accuracy.
Unproven candidates get a bounded experiment; failed or irrelevant candidates get
a recorded reason to defer. Importing every module is not the completion criterion.

Two uses share the same source/evidence foundation:

- **Discovery:** better search, tagging, embeddings, and conceptual links. Useful
  candidates can be exposed automatically and improved through later feedback.
- **Operational preparation:** assemble the relevant provisions for a named
  workflow or form, with review of the resulting decisions and unresolved cases.

The CFR/named-act reader, CFR subparts, source-credit evidence and tested act-name
ambiguity fixes are installed and verified. The inserted-separator discovery
failure is fixed without changing passage text or IDs. R4/R23's separate complete
statement and blank-entry range losses are now fixed, with local delivery verified. The fixes reuse existing evidence records and source-map slicing.
RefSpec's U.S. Legislative Markup (USLM) link reader is also shared and installed.
The newer readable-text
reader, normal XML ingestion, publisher occurrences and shared local target table
are **packaged, installed and verified**.

The Core `XPathSelector` shape and plain-string SHACL generation agree with JSON
Schema at the delivered USLM checkpoint. Its parity gate has zero Core divergences,
and independent XPath checks verify 110 XML fragments. That installed reader slice passes
523 application tests from source and isolated wheels. All 24 CLI artifacts agree
with the working installation. The false `1998—Pars.` RIN reading now retains its
evidence under an explicit refusal; four overlapping citation rows now associate
with their unique publisher occurrence. Ambiguous associations and conflicting
readings remain visible. These changes improve representation, not proven
extraction accuracy or identifier existence. See the
[RIN result](../experiments/2026-09-11-rin-reference-space/README.md) and
[containment result](../experiments/2026-09-11-reference-containment/README.md).

Not all useful sibling features have been integrated. Selected U.S. Code (USC)
readings are now installed; broader qualification coverage, general local paragraph
lookup, eCFR target bodies, historical correspondence and shared vocabulary links
remain open. Optional external USLM section/pinpoint bodies are now installed.
The completed **R15/R16** experiment found zero of three targeted meaning
gains, a repeated modality regression and one incomplete response; B used 8.9%
more reported tokens. The [result](../experiments/2026-09-11-fresh-reference-context/README.md)
also identified the two deterministic retention defects for **R4/R23**. Their
[separate comparison](../experiments/2026-09-11-extraction-retention/README.md)
now retains 336 rather than 224 statement occurrences from the same twelve saved
outputs, with seven kind/modality rejections remaining. The full source suite
and isolated installed suite each pass 552 tests. Two additional installed review
controls pass. This preserves generated output; it does not establish that its
meaning is correct. Normal commands and working delivery are now verified.
Continue **R9–R10** for unmarked
CFR references separately; the paragraph-ancestry heuristic failed its acceptance
check. More citation families alone will not recover missing conditions in the
saved passport, seatbelt and refrigerant cases. This ordering is a product judgment
to test, not a measured general ranking of value.

### What is actually reused today

| Source | Connected or verified | Still available to assess or connect |
| --- | --- | --- |
| Rulespec | CUE schemas; statements, terms, scope, evidence, passage IDs, review history, discovery and optional audit/refinement; USLM ingestion/export and XPath validation delivered | Reuse existing records for context and corrections; measure remaining duplication |
| SpicySearch | Public laws, Statutes at Large, executive orders, dockets and Regulation Identifier Numbers (RINs) in the reference adapter; upstream strict CFR/USC behavior tested | Selected other families, Atlas/agency readers and association suggestions; RefSpec supplies the selected USC consumer |
| RefSpec | CFR and qualified USC occurrences, named-act/source-credit lookup and ambiguity fixes in both commands; USLM link and readable-text readers installed | Assess section/subsection oracle, broader qualifier forms, vocabulary and publication metadata |
| Spicy Regs | Source preparation and catalog implementations inspected; no new extractor runtime connection | Verify catalog/body lookup fit and useful source preparation; use RefSpec's newer grammar instead of copying the older one |
| Local corpora | Selected act indexes and eCFR/USLM source captures verified and used | Check remaining loaders, editions and fresh inputs before use; a directory's presence is not an integration |

Effort labels are relative: **S** is a focused adapter, test, or documentation
change; **M** spans an upstream API and consumer; **L** needs source indexes or an
end-to-end quality experiment. They are planning estimates, not delivery promises.

## Task index

**Current count: 19 tasks contain open items, six are fully delivered
(R1, R2, R4, R5, R6, R14), and one experiment is closed with adoption deferred
(R15).** R16's completed experiment is closed, but its new semantic follow-up
remains open. This count includes conditional work and optional research inside
broad workstreams; many already contain delivered capabilities.

This index separates existing code from completed integration. **Installed** means
verified in the intended local environment, not published or deployed. **Source
tested** means the working implementation passed its recorded checks but still
needs delivery. **Experimental** means its adoption criteria remain unmet.
Details, dependencies and completion criteria follow each task.

Read the work in this order: preserve correct output; verify and deliver the
small fixes; complete selected reference readers; then measure discovery or
workflow value. Keep failed context changes out of production.
The 26 tasks are the complete candidate backlog, not 26 prerequisites for a useful
release. Preserve the completed foundation and make one bounded change at a time.

| Task | Deliverable | Current status | Effort |
| --- | --- | --- | --- |
| R1 | Reproducible installation and scoped delivery | Reader, retention and capture wheels delivered; scoped local commits complete | S |
| R2 | RefSpec CFR reader in both application commands | Implemented and verified locally | S–M |
| R3 | One evidence-backed representation of richer readings | Unique containment installed; all four observed overlaps resolved; ambiguity and refusals preserved | S–M |
| R4 | Combined reader and extraction retention checks | Delivered; 595 source/installed tests, six fresh XML cases, review controls and normal CLI checks pass | S–M |
| R5 | Complete qualified CFR/USC readings | Selected qualifiers, complete compounds and explicit ranges installed; unsupported scope retains refusals | M |
| R6 | Upstream occurrence fixes and qualified USC integration | Selected USC readings installed; 579 application tests and both commands verified | M |
| R7 | Additional reference families with individual acceptance checks | RIN helper reuse and upstream explanation corrections delivered; further families remain experimental | M per further family |
| R8 | Remove divergent production citation copies | Caller comparison and upstream range delivery complete; unused copies removed; live graph migration open | M |
| R9 | Source-supported context for omitted citation titles | General support missing | M |
| R10 | Exact local paragraph address index | Marker extension tested; ambiguity/inline-child gate failed; production unchanged | M |
| R11 | Local paragraph and range lookup | Publisher targets delivered; general prose addresses and ranges remain open | M–L |
| R12 | External provision text in a pinned edition | Optional USLM body lookup installed; eCFR bodies and historical correspondence remain open | L |
| R13 | Named-act lookup through existing indexes | Competing law/scope candidates delivered; explicit law/year context and ranges open | M–L |
| R14 | Publisher-provided citation links | USLM ingestion, evidence, reference/discovery export and local targets delivered | M |
| R15 | Bounded context from sections and located references | Experiment selector and controls complete; adoption deferred after failed gate | M |
| R16 | Measured comprehension gain from that context | Twelve-call comparison complete; no targeted gain, new modality defect, one incomplete response | L |
| R17 | Better search and discovery using source and meaning | Retrieval pilot regressed; narrower alternatives open | M–L |
| R18 | Persistent corrections and review identity | Changed-ID delivery controls pass; reference feedback and optional continuity work remain open | S–M |
| R19 | One reviewed workflow/forms preparation example | Planned | L |
| R20 | Verified inventory of useful sibling code and corpus inputs | Partial inventory; three fresh USLM chapters captured; remaining compatibility checks open | S–M |
| R21 | Reuse structured publication metadata and useful associations | Existing producers/consumers; new connection unverified | M |
| R22 | Shared vocabulary links for terms and actors | Existing readers and local terms; new connection unverified | M |
| R23 | Preserve meaningful source layout and complete statement evidence | USLM preparation and complete source-fragment support delivered; broader layout cases open | M |
| R24 | Fresh end-to-end quality and cost report | Three-window review/replay complete; broader document mix and product-value report open | M–L |
| R25 | Independent relationship verdicts without extra prose | Earlier bundle failed its gate; isolated experiment open | M |
| R26 | Cheaper optional checks and removal of proven duplication | Existing operations available; comparison open | M |

## Next executable batch

**Retention and reader capture are delivered.** The
[retention result](../experiments/2026-09-11-extraction-retention/README.md) records
224 → 336 accepted occurrences from the same twelve saved responses, with seven
kind/modality contradictions remaining. Original reviews stay intact and new
reprocessing output starts pending, including when claim IDs change. The
[capture result](../experiments/2026-09-11-reader-runtime-capture/README.md) adds
reader/helper sources and versions without changing those statements or discovery
output. Its current source and installed suites each pass 559 tests.

1. **Complete CFR readings before migrating graph callers — R8; RefSpec,
   Rulespec projection and SpicySearch; effort M.** Caller tracing is complete.
   The direct comparison found 189 compound-part truncations in RefSpec's
   reading of constructed index citations and confirmed that the strict
   SpicySearch reader retains but refuses them. Original publisher XML now
   distinguishes the observed compounds from explicit ranges. The token-only
   gate failed; the coordinated successor now delivers one complete item reader
   plus endpoint representation, preserves/refuses scope through authority and
   typed rows, guards single-part lookups/explanations, and uses original
   occurrence text in Rulespec. Before a graph migration, test
   the existing graph's dictionary/compact inputs before replacing its live parser.
2. **Select the next useful reader or consumer — R7/R20/R22; effort M.** Use the
   existing inventory to choose a concrete application need. Compare the callable
   native reader on actual source and misleading controls before connecting it.
   R5/R6's selected USC integration is delivered; do not restart that comparison
   or add more syntax without a demonstrated missing use case.
3. **Scoped commits complete — R1.** Upstream reader fixes, Core selector
   generation, application integration and retention/capture changes are committed
   locally. Research is preserved separately. The
   [checkpoint](../reviews/2026-09-11-commit-checkpoint.md) identifies the commits
   and source/wheel checks. Publication and deployment remain separate.
4. **Select one consumer or semantic experiment — R16/R17/R22/R24/R25.** Do not
   assume more citation syntax improves rule meaning. Choose a named discovery task
   or one observed semantic failure, with fresh cases and a distinct intervention.
   Define baseline, counterexamples, fixed settings, case/cost bounds and an
   adopt/defer rule. Keep the failed context and explanation bundles experimental.

**Natural stopping point reached:** the two small deliveries are in the working
installation with captured evidence and explicit review/replay behavior. The broad
reuse goal remains open. Each further useful candidate needs its own bounded
adopt/defer result and verified connection, not merely a successful import.

### Closed fresh-context comparison

- [x] Pin three USLM chapter selections and their natural production windows.
- [x] Read all focus windows and selected targets; freeze positive and negative labels.
- [x] Build the experiment-only selector; pass budget, overlap, ambiguity, editorial,
  boundary and no-op mutation controls.
- [x] Freeze generated schemas, prompts, runtime sources and balanced AB/BA requests.
- [x] Run twelve calls with unchanged model settings, no retry and no tuning.
- [x] Review raw outputs manually; replay candidates, refusals, Core and discovery.
- [x] Record **defer**: zero of three targeted gains, the same new modality error
  in both title-20 B runs, one incomplete B response, and 8.9% more reported tokens.
- [x] Preserve the failed freeze attempt, original captures, completed verification
  and the [result](../experiments/2026-09-11-fresh-reference-context/README.md).

R15's experimental implementation and this R16 comparison are complete. Their
production adoption is deferred. R24's broader quality and product-value report
remains open. More source availability did not establish comprehension.

## Priority and dependencies

Owners below name responsible repositories or components, not assigned people.
An unchecked item remains open even when a related helper already exists. Effort
estimates describe relative scope; they are not delivery promises.

| Priority | Tasks | Dependency or stopping condition |
| --- | --- | --- |
| Preserve the delivered foundation | R2, R14; completed portions of R1/R3/R4/R11/R13/R23 | Use current readers, schemas and evidence; do not rebuild them |
| Do now | R5 → R6 qualified USC | Compare complete native readings and actual failures, then expose source occurrences upstream |
| Preserve delivery records and commits | R1 scoped changes | Reader capture and scoped local commits are complete; retain their original receipts |
| Next reader work | R5 → R6; R9/R10 → R11 | Qualified USC and general local addresses need separate gates |
| Consolidate when a replacement is ready | R8 | Trace callers and prove parity before removing superseded code; avoid dependency cycles |
| Choose for a demonstrated consumer | R12, remaining R13, R17, R21, R22, remaining R23 | Verify required data under R20 and connect one useful capability |
| Follow real use | R18, R19 | Persistent feedback and a reviewed workflow example share the source/evidence foundation |
| Separate model experiments | R16/R25 → relevant R26 work | Fix deterministic loss first; test one semantic change or cost reduction at a time |
| Validate claims of benefit | R24 | Fresh source meanings and product outcomes, distinct from package tests or schema validity |

R1/R4 recur for each adopted slice; they are not new runtime stages. An affected
UI flow needs a smoke check if delivered data changes its behavior. The user's
priority remains the data and extraction process, not a browser redesign.

## Verified starting point

Checked against the local worktrees on 2026-09-11. “Complete” below means locally
implemented and verified at the recorded checkpoint. The reference changes in
Rulespec, RefSpec, and SpicySearch are now committed locally; installed wheels are
not published releases. See the [commit checkpoint](../reviews/2026-09-11-commit-checkpoint.md).

### Current delivered USLM checkpoint

The subsequent RIN/containment follow-up is also installed. Its
[receipt](../experiments/2026-09-11-rin-reference-space/verification.json) records
523 source/wheel application tests, 50 source/wheel minter tests, equality of 24
CLI artifacts and 1,318 wheel files across both installations. The tests below
remain the earlier USLM/Core checkpoint; their narrower suites were not all rerun
for this adapter-only follow-up. Neither new fix changes Core or model schemas.

| Check | Recorded result | What remains |
| --- | --- | --- |
| RefSpec link + readable-text tests | 62 pass from source and new wheel | Fresh consumer-quality evidence |
| Readable-text controls and independent XPath checks | 11 preparation controls pass; 107 links retained; 110 application XML fragments verified | Generalization to other layouts |
| Full extractor package tests | 509 pass in both isolated and working installations | These are not semantic-accuracy scores |
| Core schema/compiler checks | 146 compiler and 47 Rust tests pass; 299 parity cases yield zero Core divergences and two separately reported adversarial findings | Preserve the original failure and checks |
| Generated schema outputs | Canonical compilation passes; only the extraction manifest changes, model-facing schemas remain identical | Recheck affected outputs for later source changes |
| Reference corpus | Native and Python validation report PASS; one fixture, zero Python SHACL violations | Preserve updated digest pins and receipt |
| Intended local environment | 1,031 package files match source/wheels; 24 new CLI artifacts agree across all three runs; three earlier command outputs unchanged | Scoped commits when requested |

Evidence: [preparation result](../experiments/2026-09-11-uslm-readable-text/README.md),
[upstream tests](../experiments/2026-09-11-uslm-readable-text/upstream-source.log),
[preparation controls](../experiments/2026-09-11-uslm-readable-text/counterexamples.log),
[application tests](../experiments/2026-09-11-uslm-readable-text/application-source.log),
[selector failure](../experiments/2026-09-11-uslm-readable-text/selector-schema-tests.log),
and [corpus check](../experiments/2026-09-11-uslm-readable-text/reference-corpus-check.log).
The [final delivery receipt](../experiments/2026-09-11-uslm-readable-text/verification.json)
links the newer installed tests and comparisons. The original failures remain saved.

### Newer retention checkpoint — locally delivered

The [retention result](../experiments/2026-09-11-extraction-retention/README.md)
records 552 passing source tests and completed checks of all twelve saved outputs.
Accepted statements increase from 224 to 336; the remaining seven Core rejections
are kind/modality contradictions. The incomplete provider result stays incomplete.
These are output-retention results, not a semantic accuracy score.

The rebuilt extractor wheel matches its source package files and both installations.
The installed suite passes 552 tests, and two subsequent review controls pass.
Normal reprocess/replay/reference/discovery/review commands succeed; working outputs
match the isolated outputs. The [delivery receipt](../experiments/2026-09-11-extraction-retention/delivery-checks.json)
verifies the files, commands and unchanged captures. Reprocessing changes some IDs;
R18's controls confirm original reviews remain intact and new output stays pending.
The subsequent optional-reader capture is also delivered: 559 source/installed tests
pass and working outputs match. It adds eleven source files and two package versions
to the existing runtime record. Candidates/discovery stay identical; the graph
changes only its run-derived lineage ID. See the [capture result](../experiments/2026-09-11-reader-runtime-capture/README.md).
Broader reuse remains open.

### Capability inventory

| Capability | Current state | Next task |
| --- | --- | --- |
| SpicySearch public laws, Statutes at Large, executive orders, dockets, RINs | Connected through `references` and `discovery-export --references` | R1, R3, R4 |
| Parenthetical public law, e.g. `Public Law (Pub. L.) 119-20` | Fixed upstream; source and installed wheel verified | Preserve regression; R1 |
| RefSpec `find_cfr_citations` / `CfrCitationOccurrence` | Installed; pinpoints, subparts, appendix targets, list context and uncertain pairing refusals retained | R5–R6 remaining qualifier forms; R24 quality |
| SpicySearch `extract_citations(..., strict=True, keep_rejected=True)` | Implemented and tested; remains experiment comparison data | R2, R5; avoid a second default CFR reader |
| SpicySearch `extract_usc_citations(..., strict=True, keep_rejected=True)` | Implemented and tested; not connected; strict syntax still loses some qualified meanings | R5–R6 |
| RefSpec `parse_authority_citation` | Richer qualified readings tested; most lack occurrence offsets; some damaged tokens become shortened readings | R5–R7 |
| RefSpec `find_usc_citations` | Connected and installed; native fields, source/context evidence and refusals retained in both commands | R6 delivered; broader coverage under R24 |
| RefSpec FR pages and EO compilation locators | Compilation occurrences connected and installed with exact evidence; FR pages remain unconnected | R7 |
| RefSpec named-act recognition and resolution | Occurrence API fixed upstream and installed; optional act/source-credit indexes connected through both commands | R13 follow-up cases; R24 fresh quality |
| RefSpec USC section/subsection oracle | Source-inspected; not yet connected or exercised in this application | R12, R20 |
| RefSpec publisher USLM link extraction | Shared `iter_edges`, `read_text`, XML ingestion/export and unique text-reading association installed and verified | R15/R16 consumer context; broader R3 ambiguity if a new case requires it |
| Spicy Regs CFR section metadata | Existing catalog reader inspected; no target lookup integration | R12 |
| Document-local paragraph addresses and inherited CFR titles | General resolver still missing; exact supplied section-label matching exists | R9–R11 |
| Rulespec projection citation copies | Existing callers remain; known divergence from newer readers | R8 |
| Reference-driven audit/context/retrieval | Candidate export exists; these downstream uses are not connected or proven | R15–R18 |
| RefSpec vocabularies / SpicySearch Atlas and agency readers | Existing implementations; current Rulespec concept-assignment and local-term foundations also exist; new extractor-to-vocabulary connection unverified | R22 |
| Corpus publication metadata and publisher links | Local Unified Agenda tables and eCFR/USC source directories located; presence is not loader compatibility or target-text verification | R12–R14, R20–R21 |
| Fresh end-to-end benefit | Selected experiments and regression cases exist; general extraction quality, reviewer effort and cross-document discovery gains remain unmeasured | R24 |

Older records saying RefSpec cannot retain CFR subsection paths describe the
pre-occurrence API. They remain historical evidence, not current implementation
status. The original broader-parser adoption gate still failed; the narrower
five-family integration does not reverse that result.

### Previous installed checkpoint

The previous USLM checkpoint records **52 focused upstream tests** and **497
working-installed extractor tests** passing. Source, isolated-wheel and working
USLM probe outputs match exactly. Three existing application command outputs also
match the preceding named-act checkpoint. Its receipt preserves the source hashes
at that time. The USLM and reference-adapter sources subsequently changed and the
new delivery above reestablishes equality with the installed modules. Keep the
earlier receipt attached to its own wheel hashes.

The USLM probe preserves **70 publisher links**: 7 operative, 5 source-credit and
58 note occurrences. Two targets are present within the selected sources, both
from editorial-note links; 68 are explicitly outside those selections. An independent
XPath engine verified 95 source/target fragments across the source and control
cases. These results establish coordinates and bounded lookup behavior, not legal
applicability, readable document preparation or extraction-quality gains.

At that checkpoint `.tools/document-poc-venv` used the `20260911-uslm` RefSpec
wheel and the unchanged `20260911-names` extractor wheel. The
[wheel inputs](../experiments/2026-09-11-uslm-source-links/wheel-inputs.json),
[USLM probe](../experiments/2026-09-11-uslm-source-links/current-probe.json),
[XPath check](../experiments/2026-09-11-uslm-source-links/xpath-verification.json),
[upstream log](../experiments/2026-09-11-uslm-source-links/owner-wheel.log),
[extractor log](../experiments/2026-09-11-uslm-source-links/application-current.log)
and [command records](../experiments/2026-09-11-uslm-source-links/cli-current/commands.json)
preserve this checkpoint. The [final verification receipt](../experiments/2026-09-11-uslm-source-links/verification.json)
now checks all seven wheel inputs and eight installed/source/wheel module identities.
The [result and fresh-install recipe](../experiments/2026-09-11-uslm-source-links/README.md)
close that experiment; application ingestion was still open then. The newer
readable-text delivery above closes that application connection.

Earlier results remain in their experiment reports:

- [Act-name multiplicity](../experiments/2026-09-11-act-name-multiplicity/README.md):
  497 extractor, 448 RefSpec and 42 selected downstream tests; source/wheel parity
  on 1,056 name diagnostics and 8,174 policy queries. Candidate preservation removes
  row-order selection without losing earlier selected USC targets. The 448-test
  suite was not rerun as part of the narrower USLM check.
- [Act-resolution policy](../experiments/2026-09-11-act-resolution-policy/README.md):
  conservative page exclusions, competing source-credit targets and preserved
  uncertainty; the original source selections and policy comparisons remain available.
- [Source-credit integration](../experiments/2026-09-11-source-credit-consumption/README.md),
  [CFR subparts](../experiments/2026-09-11-cfr-subparts/README.md),
  [act-index integration](../experiments/2026-09-11-act-index-reuse/README.md) and
  [CFR integration](../experiments/2026-09-11-cfr-integration/README.md): original
  builds, failures and bounded acceptance results.

These are compatibility and representation checks. They are not a general
semantic-accuracy estimate, and installed local wheels are not published releases.

## Completed foundation — preserve, do not rebuild

- [x] Use the CUE application profile and generated schemas for model-facing data;
  compile to existing Rulespec evidence, assertions, scope and review records.
- [x] Keep low-thinking extraction as the cheap path and deeper audit/refinement
  optional; retain source passages even when extraction misses a statement.
- [x] Retain explicit actor assessment, defined terms, aliases, term identity,
  claim-ID targets, withheld review observations and sparse discovery output.
- [x] Share discovery evidence by ID and show overlapping evidence once in the
  review browser. Reuse these paths for new data instead of rebuilding them.
- [x] Reuse upstream parsing instead of introducing a Rulespec citation grammar.
- [x] Add RefSpec's occurrence API without changing its identity-only API.
- [x] Add opt-in strict SpicySearch CFR/USC behavior while preserving permissive
  query parsing and its existing callers.
- [x] Diagnose the broad-parser bundle with saved counterexamples and raw outputs.
- [x] Test the restricted five-family reader on constructed cases and published
  passages; retain the original missed public-law occurrence.
- [x] Fix that occurrence upstream, add counterexamples, and compare direct imports
  with the rebuilt wheel.
- [x] Connect the five-family reader to optional document scanning and discovery.
- [x] Reuse exact evidence, fragment identity, source maps, and passage IDs; keep
  repeated occurrences separate and refuse evidence built from inserted text.
- [x] Verify the packaged commands outside the checkout and retain the result.

Evidence: [integration](../experiments/2026-09-10-reference-integration/README.md),
[parenthetical fix](../experiments/2026-09-10-public-law-parenthetical/README.md),
[RefSpec occurrence work](../experiments/2026-09-10-reference-tool-reuse/README.md),
[broader comparison](../experiments/2026-09-10-broader-parser-comparison/README.md).
The integration's 459 passing extractor tests establish the recorded mechanical
checks, not a document-accuracy rate. Selected real-source labels are now
regression data, not a fresh benchmark.
The earlier extraction and review changes are recorded in
[production readiness](2026-09-10-production-readiness.md); this task-list update
did not rerun those historical checks.

## First delivery: a coherent explicit-reference reader

### R1 — Make the current implementation reproducibly installable

- [x] **Owner: Rulespec + RefSpec + SpicySearch; effort S.** Capture the exact
  source changes and wheel digests required by the current reader and the CFR
  occurrence API. Several local wheels share a version while containing different
  code. Use an unambiguous build identifier or a pinned, installable wheel receipt.
- [x] Confirm optional application dependencies install together in a fresh
  environment. RefSpec must not become a required dependency of Core validation;
  its own Rulespec dependencies make that direction especially important.
- [x] Check the actual installed module paths and dependency changes. The local
  RefSpec install changed `pyarrow` from 23.0.1 to 23.0.0; run dependency and relevant
  consumer checks before describing that environment as verified. Measure import
  or install cost only if it affects the chosen consumer; split a small upstream
  package only when the measured burden justifies it.
- [x] Finish the source-credit build and R4's export repair: wheel digests,
  dependency checks, earlier fixture replay and outside-checkout working-environment
  verification are saved. The README now selects the delivered wheel paths.
- [x] Deliver the subsequent named-act policy wheels through the same installation
  path. Save the current installed module hashes and seven CLI artifact comparisons;
  preserve the earlier builds and their results as historical checkpoints.
- [x] Deliver the name-multiplicity wheels: seven runtime modules match source,
  the new comparison and earlier policy CLI controls pass, and the intended
  working environment passes 497 tests and dependency checks.
- [x] Build/install the shared USLM reader and compare direct, isolated-wheel and
  working outputs. Preserve the 52-test upstream and 497-test application logs and
  unchanged results from the three existing application commands. This verifies
  the runtime package, not an application XML-ingestion feature.
- [x] Consolidate the USLM checkpoint into a final verification receipt and
  experiment result. Pin the completed files and current installed module hashes;
  retain the original failed XPath test and dependency-install attempt. The frozen
  source/case files still match; only `freeze.log` was hashed before its buffered
  output finished. Explain that mismatch and pin the completed log without
  rewriting the original freeze receipt.
- [x] Document the exact fresh-install recipe, including the locally supplied
  DocSpec wheel required by SpicySearch's existing package dependencies. The retry
  used pinned wheel inputs and dependency constraints. This packaging dependency
  does not provide document segmentation or become a Core validation dependency.
- [x] Deliver the newer readable USLM application slice after R4's selector check
  is resolved. Rebuild **Rulespec conformance, RefSpec and the extractor** because
  the source change includes a Core shape as well as two runtime packages. Pin
  exact wheel hashes, install the complete dependency set in a fresh environment,
  and compare CLI results outside the checkout with direct imports. Update the
  working environment only to the verified build; confirm module identities and
  dependency health. Same version strings do not establish equivalent code.
- [x] Refresh the experiment result, CLI input help, support inventory and install
  recipe. Describe `.xml` support as USLM, not generic XML. Preserve original
  failures and freeze the final manifest after output logs finish. Record local
  installation separately from commit, publication and deployment status.
- [x] Deliver the RIN and unique-containment follow-up as rebuilt RefSpec/extractor
  wheels. Verify all seven pinned wheels against both installations and all Python
  source files in the two rebuilt packages. Source, isolated-wheel and current CLI
  outputs agree. Preserve the earlier USLM receipt and the first failed harness run.
- [x] Build the retention extractor wheel and install it with the six pinned
  dependency wheels in an isolated environment. Preserve the first build before
  the README update. Current source package files and isolated package bytes match
  the final wheel. Installed execution and working delivery are now complete below.
- [x] Complete the retention installed-suite and normal reprocess/replay/export/
  review checks under R4/R18, update the working environment and close its result.
  The source/installed suites each pass 552 tests; two new review controls pass
  separately. Original captures and comparison snapshots remain unchanged. Keep this receipt separate from the earlier
  reader delivery and any later runtime-capture change.
- [x] Commit the upstream fixes, Core changes, consumer adapter/tests, and relevant
  research in scoped local commits. Exact staged paths and source/wheel checks are
  recorded in the [checkpoint](../reviews/2026-09-11-commit-checkpoint.md).
  Publishing remains a separate action.
- [x] Bring the existing runtime source capture up to date with the optional
  USLM/reference modules and traced helpers. The six-module failure case is covered;
  eleven source files and RefSpec/SpicySearch versions are added. The baseline control
  fails as expected, five source controls and 559 source/installed tests pass, and
  the working wheel matches the verified outputs. Absent optional packages still
  permit plain extraction/Core validation. This records supported installed readers,
  not an exact execution trace; a changed captured reader can cause strict replay
  drift even when unused by a particular plain-text run.

**Done when:** another local installation can select the same code without an
editable checkout or guessing which `0.1.4` wheel is correct. Package checks and
an outside-checkout CLI smoke test pass with recorded source identity.

### R2 — Finish the source integration of RefSpec's explicit CFR reader

- [x] **Owner: Rulespec adapter; effort S–M; depends on R1's dependency choice.**
  Call `find_cfr_citations` from the existing `references.py` path. Retain the
  current five-family additions; use RefSpec as the preferred CFR producer.
- [x] Preserve native `citation` fields and verdicts, `pinpoint`, exact text,
  occurrence offsets, and `context_start/context_end` for list continuations.
  Ground the written title-bearing context separately from the abbreviated member.
- [x] Route these occurrences through both existing commands and the same
  evidence/passage machinery in application source.
- [x] Verify candidate identity across ordinary reruns and compare source with
  the installed build in R4. Distinguish changes to a reading from changes to its
  source location; preserve native context for abbreviated list members.

**Done when:** the adapter returns both members of
`40 CFR §§ 82.155(a), 82.156(b)` with their individual labels and source evidence;
handles `7 CFR 15a`, spaced labels, repeats, and Unicode; preserves impossible-title
verdicts; and does not invent titles for unsupported local references.

### R3 — Preserve richer readings without multiplying representations

- [x] **Owner: Rulespec + upstream reader owners; effort S–M; alongside R2.**
  Extend the existing application result only for fields that affect interpretation:
  qualification, native validity/refusal, parsing context, and producer provenance.
  Keep raw spelling and normalized value distinct.
  CFR source currently adds `reading`, grounded `reference_context` evidence and
  a `parsers` provenance list under `document-references/2`; verify that completed
  candidates and rejected readings remain equally inspectable in discovery output.
- [x] Write a compact field map: native meaning → application field → existing
  Rulespec evidence/schema → validation → unresolved question. Reuse `SourceFragment`
  and selectors. Inspect the US rulemaking profile for identifier fields before
  adding any; do not assert an `Artifact` exists merely because its name parses.
  The CFR integration README contains the map and the remaining qualifier gap.
- [ ] If a typed exported shape becomes necessary, define it in the application
  CUE profile and generate its schema. Do not hand-maintain a second JSON schema or
  add fields to the model response for deterministic parser output.
- [ ] Preserve disagreements and rejected readings without selecting a winner
  from a normalized prefix. Do not collapse separate occurrences or reinterpret
  `partial` as either automatically acceptable or automatically invalid.
  Named-act conflict identifiers and multiple source-credit targets now survive
  native output, application tests and the installed discovery path. Remaining
  ambiguity policies and other families still need their own checks.
- [x] Compare source containment with the previous `by_start` association in
  `uslm.attach_publisher_links`. In four saved cases a text reading such as
  `Pub. L. 113–235` starts inside the longer publisher label
  `section 1301(b) of Pub. L. 113–235`; the current policy leaves both rows.
  Preserve one publisher occurrence with its distinct text reading when the
  association is unique. Keep ambiguous associations separate, and retain each
  reading's evidence and disposition. Reuse the existing node index; avoid a
  document-wide rescan for every reference. The adopted enclosing-anchor index
  passes the three actual sources, eleven controls and the exact-owner oracle.

**Done when:** the consumer can distinguish an exact source mention, an incomplete
reading, an unresolved target, and a located target without losing the evidence.
One canonical reading per chosen producer is sufficient; comparison copies belong
in diagnostics unless a real consumer needs the disagreement.

### R4 — Verify and deliver the combined reader

- [x] Reproduce and fix `discovery-export` when passage evidence crosses inserted
  separators. Source-map-bounded evidence retains every source character and
  excludes inserted characters without changing passage text, IDs or hierarchy.
  Ten controls cover original/inserted whitespace, mixed sources, empty statement
  lists, repeated Unicode, supplied fragment IDs and quotation relocation. The
  original failure and earlier reference cases now pass from installed wheels.
  This closes R23's source-passage discovery failure, not complete-statement
  compilation across inserted separators; it is not a model-quality result.
- [x] Fix in source the separate complete-quotation rejection under R23 and the
  blank-entry passage-range failure. Preserve the
  [103 main-evidence and nine range refusal events](../experiments/2026-09-11-fresh-reference-context/processing-checks.json)
  as fixed-output regression evidence. Four processing arms isolate the fixes;
  together they retain 112 additional occurrences. All twelve output checks and
  552 source tests pass. Seven contradictory kind/modality candidates stay rejected.
- [x] Finish installed execution, normal reprocess/replay and discovery/review
  export for the retention wheel. R18's changed/unchanged-ID controls pass, original
  captures remain unchanged, and component support/refusals are inspected. Working
  outputs match isolated exports. Keep parser, Core and semantic failures separate;
  retaining a candidate does not establish complete rule meaning.
- [x] **Owner: Rulespec; effort S; depends on R2–R3.** Reuse the frozen parser and
  consumer cases. Assert that adding CFR leaves the five-family results and existing
  extracted statements intact. Check both commands, source-map boundaries, repeated
  occurrences, parser absence, and installed-wheel behavior.
- [x] Add independently selected real CFR passages before making a broader accuracy
  claim. Label complete occurrences and supporting title context before execution.
  The [six-paragraph fresh XML review](../experiments/2026-09-11-cfr-ranges/fresh-review/README.md)
  froze judgments before parsing. Final installed replay preserves all six results.
  This is a bounded diagnostic result; no general accuracy claim is made.
- [x] Update CLI help, support inventory and install instructions to name the actual
  connected families. Refresh stale *current-status* summaries with links to the new
  evidence; preserve original experiment results.
- [x] Run the new USLM application source tests, including CLI preparation/scanning,
  transformation mutation refusals, XML-only empty mentions, shared targets and
  excluding raw XML attributes from the model prompt. The full package log now
  records 508 passing tests. The subsequent nested-refusal control and installed
  checks now pass 509; preserve the earlier source log as its own checkpoint.
- [x] Resolve the new Core selector test failure. `XPathSelector` has a CUE
  shape with required string `rdf:value`; baseline generated SHACL lacked the string
  datatype check. A runtime comparison confirmed that omission. The generator now
  uses the existing JSON-LD mapping for plain-string checks. Preserve the positive, missing-value and
  nonstring fixtures. Use the existing generator, not a handwritten parallel schema.
- [x] Verify affected JSON Schema/SHACL parity, generated Rust behavior and the
  extraction-schema manifest. CUE compilation/vetting and the reference corpus
  already passed at this source checkpoint; repeat affected checks if the fix
  changes their inputs. Do not weaken a negative case merely to obtain green tests.
- [x] Inspect application scans and discovery from all three saved USLM cases.
  Verify original-character evidence, shared target and fragment IDs, nested
  rejected readings, native/text conflicts, empty and repeated mentions, and note
  versus operative context. Measure residual duplicate rows before adding more
  merge logic. Then complete source/wheel/installed comparisons under R1.
  The [raw review](../experiments/2026-09-11-uslm-readable-text/raw-review.md)
  preserves four overlapping rows and the false RIN `1998—Pars.` for R3/R7.

**Done when:** combined scanning works from the installed package, exact evidence
survives discovery export, and its documented scope matches its enabled readers.
The parser-text mismatch and shared rejected-evidence checks now pass. Raw parity
scans cover three CFR occurrences in the selected source set; they do not label every complete
CFR reference or establish that qualifiers are all retained.

## Next explicit references: qualifiers before breadth

### R5 — Settle qualified CFR/USC readings before adding more families

- [x] **Owner: Rulespec + RefSpec + SpicySearch; effort M.** Compare the existing
  strict USC reader with RefSpec's authority readings on the frozen failures.
  Decide which producer supplies each field before connecting USC to the adapter.
  The [qualified USC comparison](../experiments/2026-09-11-qualified-usc-comparison/README.md)
  now covers 29 cases, including three publisher paragraphs read in their original
  context. Every raw output was reviewed; replay is identical. Neither existing API
  passes the complete integration gate. Extend RefSpec's shared matcher under R6:
  retain qualifications and original positions together, and separate prose list
  continuation from whole-authority-field interpretation. The first load-gated
  non-run and the documented execution-scope correction remain saved.
- [x] Add the actual Ohio source example:
  `49 CFR Part 172 subpart E (labeling) or subpart F (placarding)`.
  The original occurrence ended at `Part 172`. The upstream fix now preserves E/F,
  literal connectors/descriptors and grounded title/part context. Six newly selected
  publisher paragraphs also exposed appendix targets and ambiguous multi-part scope;
  those now retain their native readings and explicit refusal where needed. See the
  [subpart comparison](../experiments/2026-09-11-cfr-subparts/README.md).
- [x] Include `42 U.S.C. 1983 note`, `5 U.S.C. App. 3`, chapter references,
  subsection labels, compound section names, and stated versus abbreviated ranges.
  Include the valid embedded `5 U.S.C. 552` and damaged `1983affirmed` controls.
- [x] Preserve a range's written endpoints and expansion basis. Do not invent every
  intermediate member, merge an appendix with the title body, or discard `note`.
- [x] Retain native validity flags without treating them as edition-existence
  checks. Include historical CFR title 35 as a positive control: current RefSpec
  explicitly admits titles 1–50, including that title. An unavailable present-day
  target must not turn a historical citation into an impossible one.
  R6's USC delivery and the [CFR range delivery](../experiments/2026-09-11-cfr-ranges/README.md)
  cover these selected cases. Ambiguous or unsupported scope remains explicit;
  the minter and remaining independent graph parsers are still separate R8 work.

**Done when:** the chosen path preserves the intended kind of target and its exact
source. Plain strict token matching alone does not satisfy this task. A remaining
ambiguity can stay explicit instead of becoming a confident section identity.

### R6 — Extend the owning occurrence APIs, then connect qualified readings

- [x] **Owner: RefSpec first, Rulespec second; effort M; depends on R5.** Reuse
  RefSpec's internal authority matchers to expose occurrence offsets and qualified
  readings. Separate completeness of a token from unrelated surrounding prose.
  Preserve the existing API for its current callers where required.
- [x] Fix demonstrated truncation in the owning matcher; do not recover positions
  by searching for normalized output or add a Rulespec repair regex.
  The [native checkpoint](../experiments/2026-09-11-qualified-usc-comparison/native-review.md)
  records 468 passing tests, 14 slow tests deselected, and unchanged whole-field
  results on 31 inputs with seven variants each. The source occurrence reader
  retains the full damaged token with an explicit refusal. It does not repair
  damage or establish legal existence. The copied prior reader stays test-only.
- [x] Verify direct imports, owner tests and null controls before rebuilding the
  wheel. Connect the selected USC behavior to the same adapter and replay the
  frozen combined cases.
  The [delivery](../experiments/2026-09-11-usc-delivery/README.md) preserves all 31
  native inputs, unchanged other-family/default output and six additional USC
  observations associated with publisher links. The final source and installed
  suites pass 579 application tests, with 116 focused upstream tests installed.
  The native owner suite passes 503 tests, with 14 slow tests deselected.
  The additional actual `38 U.S.C. 4301, et seq.` example exposed a missing open
  tail; the upstream correction retains it with an explicit unresolved-range
  refusal. Both installed commands preserve that wording. Earlier captures and
  failed attempts remain intact. No model call or legacy conversion was added.
- [x] Extend the existing RefSpec CFR occurrence output for demonstrated subpart
  or other qualifier gaps from R5. Reuse its grammar and native data types; do not
  append a Rulespec regex that guesses the tail of an upstream match.

**Done when:** the selected CFR qualifiers and qualified USC targets survive intact
with original spans; ordinary citations inside prose remain readable; malformed
continuations remain visible as unresolved/refused rather than shortened identities.
The CFR fix and USC integration are separate deliverable slices.

### R7 — Evaluate the remaining reference families individually

- [x] Inspect the real amendment paragraph and the existing APIs. SpicySearch
  deliberately recognizes a permissive query shape. RefSpec `normalize_rin`
  accepts that same broad shape; replacing the scanner with it would not remove
  `1998-PARS`. RefSpec `mint_rin_iri` checks Rulespec's narrower identifier space.
  Rulespec already has a narrower `rulespec_projection.citations.normalize_rin`
  as well. Neither helper checks issuance or source meaning. The
  [independent review and verified follow-up](../reviews/2026-09-11-rin-boundary-review.md)
  records this boundary; no new strict detector mode has been justified.
- [x] **RIN owner: Rulespec adapter; effort S.** Preregister current recognition
  versus the existing RefSpec minter applied to normalized candidate values.
  Inspect the Rulespec normalizer as the existing alternative, not a new parser.
  Require unchanged exact evidence and supported valid candidates, preserved
  rejected readings, unchanged query defaults and no new model fields. Include
  labeled/bare, lowercase, Unicode-dash and repeated occurrences; the complete
  `1998—Pars.` paragraph; an Office of Management and Budget control number;
  the five historically documented publisher exceptions; and a constructed
  `9999-ZZ99` product code. Both narrow helpers retain the verified artifact's
  46,562 distinct values; the product-code control still demonstrates that a
  representable shape is only a candidate. The [result](../experiments/2026-09-11-rin-reference-space/README.md)
  records the selected RefSpec helper and the population's limits.
- [x] Reuse `record(..., refusal=...)` for
  `rin_outside_supported_identifier_space` and fingerprint the added native helper
  with the existing parser provenance. Do not call the result “not a RIN,” erase
  the original mention, or turn successful minting into target resolution.
- [x] **Explanation owner: RefSpec; effort S.** Correct the unsupported universal
  format claim and the test's attribution of refusal to a roster lookup that
  never runs. Preserve REF-054's decision history with a dated clarification.
  Keep the earlier 46,547-value population historical; the verified local artifact
  supplies the separately measured count above. The upstream runtime AST is
  unchanged by these explanatory edits.
- [x] **Compilation owner: RefSpec grammar plus Rulespec consumer; effort S.**
  Reuse SpicySearch's page-first recognition in the existing RefSpec grammar.
  Export exact occurrences, both year/page endpoints and unclosed-parenthetical
  refusals through the existing reference/discovery path. Nine contiguous court
  citations and two real USLM mentions retain their locators; twelve publisher
  links survive. The [bounded result](../experiments/2026-09-11-compilation-occurrences/README.md)
  leaves the cross-page PDF failure and the older partial `AuthorityCitation`
  row's missing range endpoints explicit. No executive-order identity is inferred.
- [ ] **Owner: RefSpec/SpicySearch plus Rulespec consumer; effort M in bounded
  slices; depends on R3 and any needed occurrence API.** Prioritize Federal Register
  volume/page citations, then corpus-demanded families:
  proclamations, reorganization plans, constitutional provisions, treaty citations,
  and court cases. Use existing readers, not a new generic grammar.
- [ ] Distinguish FR volume/page, FR document number, docket, Regulations.gov
  document ID, and RIN. Apply document-number variants only with the source metadata
  or context they require; keep bare ranges and Ohio rule numbers as controls.
- [ ] For each addition, require a real positive source, a misleading lookalike,
  exact occurrence evidence, and a useful consumer field. Leave families disabled
  when that small test fails or there is no current demand.

**Done when:** each enabled family has its own justified scope. Passing one family
does not promote the entire previously failed broader bundle.

### R8 — Consolidate divergent citation copies without changing package boundaries blindly

- [x] **Owner: Rulespec projection + RefSpec + SpicySearch; effort M.** Trace
  actual consumers of `rulespec_projection.citations`, including `projection.py`'s
  calls. Inventory behavior that is shared, richer, outdated, or deliberately different.
  [Verified caller map and comparison](../experiments/2026-09-11-citation-ownership/README.md):
  the graph readers remain live; source extraction already uses RefSpec. Seven
  unused act-name/compilation definitions and their private constants were removed
  from Rulespec, with unchanged surviving code and graph fixtures. The comparison
  also records SpicySearch's ten five-digit-part misses and its useful parenthetical
  compilation refusal for follow-up upstream. This cleanup does not complete migration.
- [ ] Address known `7 CFR 15a` / compound-part truncation in the owning production
  path. Determine whether callers can consume upstream observations directly or
  whether a shared small grammar package is warranted. Do not introduce a Core ↔
  RefSpec dependency cycle merely to remove a file.
- [ ] Migrate one callable path with parity tests, then remove the superseded
  implementation and its dead callers. Keep experiment captures intact.

**Done when:** each production parsing job has an explicit owner, useful differences
are preserved, and the old copy is removed only after its consumers have moved.

## Local references and actual source targets

### R9 — Support explicitly grounded document citation context

- [ ] **Owner: RefSpec grammar + Rulespec caller; effort M.** Allow omitted-title
  references such as `§ 82.155` only when the caller supplies a source-supported
  title/section context. Keep evidence for that context separate from the literal
  occurrence; never rewrite the input to insert the missing title.
- [ ] Test conflicting headings, citations to another title, multi-section files,
  missing context, and context supplied only by unverified metadata.

**Done when:** the refrigerant-style reference can be recognized when its title is
established, and the identical text remains unresolved when that context is absent
or conflicting. This recognizes a target name; it does not locate its text yet.

### R10 — Index exact local paragraph addresses

The [local-address comparison](../experiments/2026-09-11-local-paragraph-addresses/README.md)
reused RefSpec's lexer with the existing Rulespec passage algorithm. Matching
reconstructed paths improved from 82/135 to 134/135, but two of four uncertain
controls would receive an unjustified single path, one fresh inline child remained
missing, and 57 sampled context selections changed. These are address diagnostics,
not extraction accuracy. The broader gate failed; no production behavior changed.
The next comparison must preserve uncertainty and source features, and distinguish
a paragraph's label from its complete text before using addresses for R11 lookup.

- [ ] Check whether publisher markup or an existing source reader already supplies
  the needed addresses. Reuse that structure when it maps to the prepared text;
  compare a maintained parser before introducing substantial new hierarchy code.
  A citation-token reader alone does not establish paragraph ancestry.
- [ ] **Owner: Rulespec source structure; effort M.** Extend/reuse `source_passages`
  for the needed uppercase, spaced, Roman, and combined labels. Preserve original
  markers, hierarchy, source maps, and spans. Keep existing passage IDs stable where
  boundaries do not change; document identity changes when boundaries must change.
- [ ] Define how section-local indexes handle duplicate labels, ambiguous Roman
  numerals, headings, and malformed structure. Include a declared section boundary
  without a blank line, overlapping supplied sections, and a combined marker that
  resets an earlier list. An address must not silently select a similarly named
  paragraph from another section.
- [ ] Trace effects on `with_context`, extraction windows and discovery export.
  These already consume passage structure; changing their selected context is a
  behavior change even when every character remains grounded. Record boundary/ID
  changes separately from parent/address changes, and test each affected consumer.

**Done when:** saved seatbelt and label paragraphs are individually addressable
without converting structural parentage into a claim about governing conditions.

### R11 — Resolve document-local addresses and ranges

- [x] **Owner: Rulespec; effort M–L; depends on R14/R23 for publisher addresses,
  R9–R10 for unmarked prose addresses.** Connect exact publisher identifier lookup
  to the source consumer. It now uses a shared target table and exact XML/text
  evidence; duplicate identifiers remain ambiguous and absent targets retain an
  out-of-selection status. The fresh 5 U.S.C. 302 reference reaches 5721's definition
  in the supplied capture, including its exclusion. Source application tests pass.
- [x] Finish R4 validation/export checks and R1's installed delivery for that
  bounded publisher lookup. It does not implement the general prose cases below.
- [ ] Resolve unmarked forms
  such as `paragraphs (b)(1) through (4), (c), and (d)(1) of this section`, and
  relative “this paragraph” forms, against the pinned source index.
- [ ] Preserve the literal `paragraph (a)(3)(iii)(B)( 4 ) of this action`; do not
  silently change “action” to “section.” Return ambiguous/unsupported readings
  when the referent cannot be established.
- [ ] Use the actual available paragraph order for ranges. Retain missing members,
  multiple candidate targets, and context used to interpret shared prefixes.

**Done when:** selected local references land on exact source slices or retain a
specific unresolved reason. A successful address lookup creates navigation, not
an exemption or applicability relationship.

### R12 — Locate external provisions in pinned editions

- [x] **Owner: Rulespec integration + Spicy Regs/RefSpec data owners; effort L.**
  Exercise Spicy Regs' CFR section catalog and RefSpec's USC section/subsection
  oracle with their required pinned artifacts. Reuse existing loaders and integrity
  checks before adding storage or lookup services.
  Use R20 to check the local artifacts first. `CfrSectionsReader` acquires annual
  GovInfo metadata; it is not a ready-made offline body resolver. Its keyless
  behavior yields no records, which must remain distinguishable from “target absent.”
- [x] Connect exact accepted USC sections/pinpoints and publisher targets from
  explicitly supplied USLM documents to `references` and `discovery-export`.
  Reuse RefSpec `read_text` and `normalize_section`, and the existing Rulespec
  XML/source-map/evidence path. The [comparison and delivery](../experiments/2026-09-11-reference-bodies/README.md)
  resolves three actual 553(b)(B) occurrences to one 243-character body with one
  shared 4,352-character containing section. Source/installed suites pass 616 tests;
  different editions remain ambiguous and edition correspondence unestablished.
  Do not count this as a general CFR/USC resolver or improved extraction meaning.
- [ ] Keep edition/date, catalog release, original citation, selected target and
  source digest together. Distinguish missing data from an invalid citation or a
  provision absent from the selected edition. Handle repeal/renumbering as recorded
  facts, not an automatic substitution of today's provision.
- [ ] Retrieve and pin target text through an existing source-fetch path where
  available. Keep lookup/fetch optional and bounded; local validation must work
  from captured evidence without network access.

**Done when:** a cited provision can be located in a declared source version or
remain unresolved with a reason. Metadata-only catalog recognition is not counted
as having fetched the provision's body.

### R13 — Connect named-act references when indexes are available

- [x] **Owner: RefSpec + Rulespec; effort M–L; depends on verified indexes from R20.**
  Use `find_act_relative_occurrences` with the verified index's name set, then
  `resolve_act_relative_citation` with the required name/classification/source-credit
  indexes. Start with a concrete corpus need such as a named act and section.
  Identity lookup does not depend on fetching source bodies in R12.
- [x] Preserve uncertainty, conflicting source-credit verdicts and unresolved
  results emitted by the native resolver. This covers the resolver's current
  output, not every possible ambiguity in the underlying name table.
- [x] Exercise real source-credit-only positives through the application reader:
  PIPES section 103 maps to USC 49:60303 and SECURE section 303 to USC 29:1153.
  Reuse the existing year-first spelling operation upstream; retain the written
  name and require an indexed match. Preserve four candidate USC targets for
  SECURE section 127 without choosing one.
- [x] Exercise constructed agreement, conflict, multiple-target and wrong-division
  controls through application tests. Retain both source-labeled conflicting
  identifiers. The initial 608-pair population had no real source conflict; the
  wider policy experiment found 58 baseline conflicts among 8,174 diagnostic
  lookups. Neither population is an independent document-accuracy benchmark.
- [x] Complete installed discovery and environment checks under R4/R1. Source and
  wheel CLI artifacts agree exactly; previous named-act cases remain unchanged.
  The working environment received those verified policy builds; subsequent
  USLM builds retain their behavior in the earlier command comparisons.
- [x] Apply the named-division page exclusion to a **single** Table III row as
  well as multiple rows. RefSpec now excludes only when all relevant page values
  are known, complete and outside the conservative division bounds. Reuse sealed
  `quarantine.parquet` to retain shortened-page uncertainty. Unknown, compound or
  shortened page evidence cannot justify exclusion; in-range survivors do not
  select a winner among multiple rows. Mixed classification/quarantine artifacts
  fail loading. SECURE section 127 and positive/negative controls passed.
- [x] Preserve multiple source-credit targets when Table III supplies one answer.
  Return `act_section_ambiguous`, keep the existing credit candidates and retain
  the table candidate in optional `table3_candidate_iri`. The wider comparison
  found 29 such name/section lookups representing 7 distinct source keys, with
  selected Table III XML and original USLM credit evidence inspected. The two
  policy changes were compared separately and together before wheel verification.
- [x] Fix loss of **multiple laws sharing a popular name** upstream. The existing
  popular-name builder reproduces all 20,865 normalized source rows and already
  identifies multiple laws. Reuse its `PopularNameRecord` in the runtime loader;
  preserve 41 names' competing law/division identities, including 34 multi-law
  names, without a first-row winner. Retain each compatible `ActResolution` as a
  candidate, including possible USC targets and refusals. Source-row order no
  longer changes results, and every formerly selected target remains available.
- [x] Test explicit division context, aliases/year spelling, duplicate records,
  missing division data and contradictory scopes. A stated division can narrow
  candidates; missing division information cannot exclude a source record.
  Same-law records with only different page metadata do not invent another identity.
  Native candidates and source records survive installed application/discovery
  output, with the written citation retained once.
- [x] Fix the dependent calendar lookup using the same source alternatives.
  Supply an enactment year only when all possible laws state the same known year.
  Three multi-law names retain their common year; eight conflicting names no
  longer take the first law's year. Keep the original publication artifact's
  receipt intact and test the new refusal through fresh caller controls.
- [ ] Evaluate source-supported **explicit law numbers and enactment years** as
  discriminators when they occur beside a named-act mention. Preserve the written
  qualifier and its evidence rather than attaching it by proximity alone. A year
  inside the popular name is not necessarily an enactment year: the Detainee
  Treatment Act of 2005 entry also names a law approved in January 2006. Keep that
  counterexample. The current year-spelling helper does not bind a dated mention
  to one candidate law.
  Use fresh positive, conflicting and unrelated-neighbor cases before connecting
  that context. More precise title/subtitle boundaries remain a source-data gap.
- [ ] Evaluate remaining spellings, act-relative ranges and explicit division
  placements when demanded by fresh sources. Do not interpret an act subsection
  label as a mapped USC subsection without separate evidence.

**Done when:** both the recognized occurrence and the evidence/index version behind
its proposed USC target are inspectable. Recognition tests alone do not complete it.
The bounded integration is delivered: seven of eight selected publication fields
are recognized, three resolve through the supplied tables, repeats/pinpoints retain
their source, and unknown sections remain explicit. That is the earlier act-index
checkpoint. The [source-credit experiment](../experiments/2026-09-11-source-credit-consumption/README.md)
delivers selected positives and retained ambiguity; the
[policy experiment](../experiments/2026-09-11-act-resolution-policy/README.md)
settles the two tested source-composition/page questions. The
[name-multiplicity experiment](../experiments/2026-09-11-act-name-multiplicity/README.md)
delivers source identities, per-candidate lookups and the calendar correction.
Explicit law/year context and remaining source-demanded spellings/ranges stay open. Complete page
parsing, target-edition verification and semantic completeness are not claimed.

### R14 — Reuse publisher-provided links where they are better evidence

- [x] **Owner: RefSpec runtime + Rulespec ingestion; effort M; application work
  depends on R23's readable preparation.** Move the existing pure USLM reader from
  the build tool into `refspec.registry.uslm`. The tool now imports it; acquisition
  and build policy remain in their existing owner. Default rows, order, skips and
  refusals agree with the copied old implementation on real sources and mutations.
- [x] Add opt-in `include_source_path=True` to return each occurrence's exact
  `sourceXPath`. Repeated equal text stays tied to distinct elements. Preserve
  publisher anchors, target paths, source-credit/note/operative context and refusals.
- [x] Exercise pinned title 5 section 423 and title 42 section 242c selections.
  The experimental consumer uses existing `SourceFragment`, XPath selectors and
  exact text evidence. Ten constructed controls cover duplicate/absent targets,
  repeated mentions, Unicode, nested/empty text, source contexts and native skips
  or refusals. Independent XPath checks verify the selected source/target fragments.
- [x] Compare direct imports, rebuilt wheels and the working installation. The
  saved [design and captures](../experiments/2026-09-11-uslm-source-links/design.md)
  establish this narrow runtime/evidence result. R1's final receipt is now complete.
- [x] Connect XML addresses to **readable prepared text** through the existing
  source map. RefSpec's new `read_text` preserves every decoded source character;
  Rulespec saves the XML once and verifies the transformation before using its
  coordinates. Original XML identity, inserted formatting and decoded text remain
  distinct. XML paths are not text or byte offsets. Source tests pass.
- [x] Expose mapped publisher occurrences through the existing `references` and
  discovery paths in source. Preserve links without visible text or available
  targets and retain context types. Share targets and evidence by ID; add no
  mandatory model fields. The initial source suite passes 508 tests; the final
  installed suite includes the added refusal control and passes 509.
- [x] Complete R4's separate Core selector validation and application-output
  review, then R1's three-wheel delivery. Passing the application suite alone does
  not establish generated-schema parity or installed runtime behavior.
- [x] Compare publisher links and text recognition on the same source. Decide
  how one occurrence retains both producer readings when they agree or disagree;
  do not merge repeated mentions merely because their labels match. Unmarked
  references remain eligible for the existing text reader. The source implementation
  initially associated same-start readings and preserved disagreements. R3's
  subsequent unique-containment comparison is now installed: the three actual
  sources retain 77 associated text readings and no residual overlapping rows;
  nested ambiguities, disagreements and refused readings have regression controls.
  Association does not prove the two readers agree.
- [x] Add a previously untuned operative reference with a supplied target: the
  selected 5 U.S.C. 302/5721 pair adds 37 links to the earlier 70-link preparation
  comparison. The three prepared cases have three present targets, one operative.
  This closes the missing preparation case, not a comprehension claim. Select
  fresh consumer cases under R24; these captures are now development controls.

**Done when:** a publisher link is traceable to its original markup and target,
its readable text evidence resolves through the saved transformation, and the
installed application exports that result. The USLM slice meets this criterion;
other publisher formats and context-assisted interpretation remain separate work.

## Make the references improve extraction and discovery

### R15 — Feed located references into a bounded context selector

- [x] Preregister the [fresh-context comparison](../experiments/2026-09-11-fresh-reference-context/design.md).
  Current production `with_context` still uses neighboring/ancestor passages;
  publisher targets are available but do not yet drive extraction context.
- [x] **Experiment owner: Rulespec; effort M; uses R11/R14 publisher targets.**
  Reuse passage IDs, section structure and existing context fields in
  [the experimental selector](../experiments/2026-09-11-fresh-reference-context/context.py).
  Compare current context against complete short enclosing sections plus located
  references. Preserve unavailable targets and budget omissions explicitly.
- [x] Deliver overlapping experimental context once, preserving distinct source
  occurrences. Verify one-hop traversal, duplicate targets, cycles, missing and
  ambiguous targets, editorials and budget boundaries before model execution.
- [x] Allow a complete target section up to 6,000 characters, otherwise its exact
  target node; consider enclosing focus sections up to 12,000 characters afterward.
  Add at most 12,000 distinct characters beyond baseline, skipping whole additions
  over budget. Operative links inside the focus are the only expansion triggers.
- [x] **Record production adoption as deferred.** The completed selector failed
  R16's meaning and regression gate. A different intervention must earn its own
  bounded test under R16; this is not an unfinished obligation to adopt this selector.

**Experiment complete:** required text availability, raw meaning, false inheritance
and usage were assessed separately. Production context still uses the existing
neighbor/ancestor path. The [result](../experiments/2026-09-11-fresh-reference-context/README.md)
does not rule out a later retrieval or targeted-review use of the same source data.

### R16 — Test consumer comprehension before changing model defaults

- [x] Freeze three previously untuned chapter captures, complete manual labels,
  actual requests and the existing CUE schema. Keep model/settings unchanged.
- [x] Complete twelve calls, read every complete raw output and the incomplete
  prefix/tail, and verify saved candidate/refusal, Core and discovery replay.
- [x] Record the failed gate: no targeted gain in any case, repeated title-20
  authorization/modality regression and one incomplete B response. The 1.089 total
  token ratio passes only the cost bound. These windows do not measure complete
  chapter extraction or general document accuracy.
- [ ] **Owner: Rulespec extraction/audit; effort M–L; after R4/R23 retention fixes.**
  Select one semantic hypothesis grounded in the fresh review: explicit permission
  versus obligation, beneficiary versus responsible actor, definitions by reference,
  or preserving governing conditions in split statements. Define a distinct
  intervention and new evaluation cases rather than tune the completed comparison.
- [ ] Map the proposed meaning change to current CUE fields and existing
  `ApplicabilityScope`, terms, and `EvidenceBinding` roles `definesScope`,
  `providesContext` and `qualifies`. Those structures record supported judgments;
  they do not decide which provision governs another provision.
- [ ] Persist unresolved judgments through existing review observations. Test
  per-target relationship decisions separately under R25; the earlier bundled
  target pilot failed its broader gate.

**Done when:** a declared comparison supports an adopt/defer decision, with costs
and errors visible. This comparison is closed as defer; a new semantic consumer
change remains unproven. Reference recognition does not justify a mandatory audit.

### R17 — Prove discovery value without repeating context into every embedding

- [ ] **Owner: Rulespec discovery plus a selected search consumer; effort M–L.**
  Test exact-reference lookup and source-first retrieval followed by evidence
  expansion. Compare source/statement result combination separately from context
  supplied after retrieval.
- [ ] Retain source retrieval when extraction is absent or wrong. Measure relevant
  provisions, duplicate results, complete supporting context, unresolved targets,
  payload size and cost on fresh labeled queries. Reuse the existing retrieval
  harness before building another index or search product.

**Done when:** reference features improve a named discovery task. Do not revive
source-plus-summary concatenation by default; its saved comparison regressed.

### R18 — Preserve review identity and carry reference feedback into existing history

- [x] Compare existing review data against baseline and new source. The latest
  normal saved extraction reloads with the same snapshot in both. The older
  actor/term example fails identically in both; retain that pre-existing finding.
  Saved [checks](../experiments/2026-09-11-extraction-retention/checks.json) separately
  record 52 changed claim revision IDs on reprocessing, including 48 changed rule
  IDs. Recovering skipped candidates shifts ordinal-based identities; this is
  distinct from changing the meaning of an existing statement.
- [x] **Delivery owner: Rulespec review/reprocess; effort S.** Verify normal
  installed reprocessing and two constructed controls with review events, covering
  changed and unchanged IDs. Original snapshots, corrections and approvals remain
  intact; the new output stays pending and does not copy reviews by text or ID.
  No immutable-assertion check was weakened for the older incompatible example.
  The controls now live in `tests/test_review_reprocessing.py`.
- [ ] **Follow-up only if a consumer needs cross-reprocessing continuity; effort M.**
  Assess the existing source-occurrence identity versus candidate-order identity
  with inserted/reordered rows, repeated identical provisions and changed meaning.
  Reuse existing identities and supersession records where they fit. Record a
  bounded keep/change decision before altering identity rules; do not add a general
  migration layer or silently transfer review state.

- [ ] **Owner: Rulespec consumer; effort M; after a real consumer uses R4/R11/R12.**
  Let users report a wrong citation reading, wrong edition/target, or missing
  reference against stable occurrence and source identities. Distinguish that
  correction from a claim about the legal relationship between provisions.
- [ ] Reuse review events and provenance. Preserve observations when claims or
  parser readings are superseded, and show what was resolved versus still disputed.
  Avoid requiring a person to approve every discovery candidate.

**Done when:** a correction survives reload/export and is connected to the version
of the reading it corrects. Operational approval remains a distinct decision.

### R19 — Demonstrate one reviewed workflow preparation use

- [ ] **Owner: Rulespec plus the selected workflow/forms consumer; effort L;
  depends on enough source location and context support for that example.** Choose
  one bounded passport-adjudication activity or comparable document-driven task.
  Assemble source-backed facts, questions, actions, conditions, deadlines,
  alternatives, exceptions and remaining unknowns.
- [ ] Compare the draft with preparation from the source alone. Review omitted
  branches, unsupported actions/form fields and time saved before mapping to
  wos-spec/formspec. Reuse their actual schemas when the example reaches that stage.

**Done when:** the selected decision flow and representative scenarios are reviewed
against their sources. This is product-value evidence for that use, not general
legal automation approval.

## Existing data and capabilities beyond citation syntax

### R20 — Verify a small, reusable corpus inventory

- [x] Exercise RefSpec's USC body reader and edition/existence oracle, Spicy Regs'
  metadata-only section catalog, strict SpicySearch identity fields, and three
  pinned eCFR bodies. The [bounded inventory](../experiments/2026-09-11-reference-bodies/README.md)
  separates the installed USLM consumer from available eCFR data and missing
  body-reader integration. It retains suspension notes, tables, missing targets,
  wrong pins and edition mismatch; no source or corpus rebuild was needed.

- [x] Verify the USLM release 119-102 archive/member pins and capture title 29
  chapter 4B, title 38 chapter 7 and title 20 chapter 6A for the fresh-context
  comparison. Prepared text, references, windows and exact source identity are
  saved in the [selection record](../experiments/2026-09-11-fresh-reference-context/source-selection.json).
- [ ] **Owner: Rulespec research + source repository owners; effort S–M; can start
  now.** Record each relevant capability as already used, available but disconnected,
  missing upstream, or deferred with a reason. Name the callable reader, required
  data, current consumer and smallest next check. Extend this list rather than
  creating a second integration backlog.
- [ ] Start with the artifacts below. Check their receipts, schemas, declared
  editions and required loader pins before use. A directory date is not a legal
  edition or proof that the current reader accepts its files. Save small exact
  source selections and their identity; use existing readers to avoid loading or
  copying an entire corpus for one experiment.
- [ ] Separate source documents from derived annotations, parser outputs and
  inferred relationships. Use the source for labels; preserve the derivation of
  useful annotations. Include absent, conflicting and wrong-edition controls.

| Located input | Existing reader or first check | Intended use |
| --- | --- | --- |
| `RefSpec/output/usc-act-index-2026-08-22` | `ActIndex.from_artifact`: verified and exercised | R13 named-act sections and popular names; now connected |
| `RefSpec/output/usc-source-credit-index-2026-08-02` | `SourceCreditIndex.from_artifact`: verified; real positive and multi-target rows exercised | R13 mappings and tested source-composition policies delivered; reused independently for each act candidate |
| `RefSpec/research/evidence/usc-regeneration-2026-08-31/popularnames.htm.gz` | Existing popular-name builder reproduces all 20,865 normalized frozen rows; ambiguous entries inspected with raw HTML context | Shared builder/runtime record type and multi-law/scope lookup delivered under R13 |
| `RefSpec/output/usc-annual-2026-08-24/xml_uscAll_119-102.zip` | Archive verified against source-credit pins; title 10/18 credit sections inspected; title 5/42 reader controls delivered; title 29/38/20 chapters and natural windows captured | R14 supplied-XML lookup delivered; R15/R16 comparison complete with adoption deferred; R12 external edition/body lookup open |
| `RefSpec/output/ecfr-title-xml-2026-08-24` | Manifest and title 21/40/49 file digests verified; exact sections and paragraph text exercised in the subpart comparison; production source/target loader still open | R9–R12 headings, paragraphs and target text |
| `corpora/refspec-registry-unified-agenda-parquet` | Existing verifier accepts all four output hashes and declared schema; RIN comparison exercises 241,726 actions / 46,562 distinct values from 60 editions. `PublishedTables` is an interface, not an on-disk loader; metadata consumption remains unconnected | R7 compatibility check delivered; R21 stated CFR/authority metadata and RIN links open |
| `corpora/supply-2026-09-02/releases` and `corpora/fr-mirrulations-1k-v1` | Existing release manifests and source readers; verify a selected small source | R7/R23 real positive inputs; R24 fresh documents |
| RefSpec vocabulary/Atlas releases | Existing release verification; SpicySearch `AtlasSearchView` where compatible | R22 stable concepts, labels and agency suggestions |

Paths above are relative to `/Users/mikewolfd/Work`. The populated corpus root is
`/Users/mikewolfd/Work/corpora`; `~/corpora` was absent at inspection. The source
repository is `spicy-regs`, not `spicyregs`. Artifact presence is verified. The two
act indexes are verified and connected. Selected eCFR XML is now verified and
usable for experiments. The USLM archive and selected title 10/18 sections are
captured in the [policy source evidence](../experiments/2026-09-11-act-resolution-policy/raw-credit-context.json).
The [USLM cases](../experiments/2026-09-11-uslm-source-links/cases.json) also pin
title 5/42 members and the exact source selections used for publisher-link checks.
Its release point is 119-102; a directory named `usc-annual` does not establish an
annual legal edition. A production target-text connection and the remaining
artifact/loader compatibility checks stay open.

The [paragraph comparison](../experiments/2026-09-11-local-paragraph-addresses/README.md)
also pins whole sections 21 CFR 1.276 and 49 CFR 1.25a from the verified source.
Their inline and combined markers are now development controls. They do not
establish a production paragraph loader or provide untouched evaluation inputs
for further tuning of that candidate.

**Done when:** every candidate selected for this iteration has an owner, a usable
input or specific missing prerequisite, and an adopt/test/defer decision. General
search engines, feed statistics and unrelated registries stay with their current
products unless a concrete Rulespec consumer needs them.

### R21 — Consume stated publication metadata before reparsing prose

- [ ] **Owner: Rulespec projection/application + RefSpec/Spicy Regs; effort M;
  depends on R20.** Trace existing `federal_register_facts`, `unified_agenda_facts`,
  `PublishedTables`, and the source transforms. Test whether their existing CFR,
  authority, RIN and docket fields provide useful reference candidates with less
  code than scanning those same structured fields again.
- [ ] Compare stated metadata with text occurrences from the same pinned record.
  Retain both when they serve different purposes or disagree. Metadata has its own
  source field evidence; never invent a quotation span for it in a document body.
- [ ] Inspect SpicySearch's existing `citation_bridge` only for a discovery use
  that needs USC-to-CFR suggestions. Its Unified Agenda co-occurrence evidence is
  a suggested association, not proof that one provision legally implements another.
  Compare exact-key suggestions with the current consumer and include unrelated
  whole-act/range controls. Do not reuse its historical scores as Rulespec accuracy.

**Done when:** at least one named consumer uses verified upstream fields without
a duplicate parsing path, or the bounded comparison records why no connection
adds value. Declared source references remain distinct from inferred associations.

### R22 — Connect terms and actors to existing vocabulary identities where useful

- [ ] **Owner: RefSpec + Rulespec terms/projection; SpicySearch where its reader
  fits; effort M; depends on R20.** Start from `terms.py`, existing
  `VocabularyConcept`/`concept_assignment`, RefSpec releases, and SpicySearch's
  `AtlasSearchView` and `AgencyProjection`. Map what is already connected before
  adding an extractor-to-vocabulary adapter.
- [ ] Test a bounded set of defined terms, aliases and actor mentions across fresh
  documents. Keep document-local definitions and source-supported roles intact;
  a shared label or acronym must not merge distinct meanings. Include `INs`,
  `IRLs`, `Posts`, agency/center roles, and colliding agency abbreviations as
  development controls, with fresh cases for generalization.
- [ ] Carry concept release, original mention, candidate identities, match method
  and ambiguity through existing records. Resolve exact unambiguous names only
  within the reader's supported scope; preserve broader matches as suggestions.
  An agency-name match does not establish that the agency is the actor of a rule.

**Done when:** a named tagging or cross-document lookup task gains useful links
without false identity merges or larger mandatory model output. Broader/narrower
concept relationships retain their type and provenance; label similarity does
not become an asserted legal relationship.

### R23 — Reuse source preparation where layout carries meaning

The R10 comparison now supplies specific source cases: italic deep-level markers
in the saved seatbelt XML, `(i)` embedded in a definition's physical paragraph,
and a refrigerant sentence split across two source passages. Preserve those raw
captures. Markup can disambiguate some labels but does not supply a complete tree
or make a physical passage equal to a complete referenced paragraph.
The USLM probe supplies another concrete gap: exact decoded XML text can join a
heading such as “In general” directly to the following sentence. Its offsets
verify, but that alone does not make the prepared document readable or suitable
for extracting meaning. The subsequent readable-text comparison fixes this join
and is now installed, while retaining the failed first attempt as evidence.

- [ ] Prefer publisher XML when its supported structure contains the required
  document text. For PDF-only captures, preserve and test reading order before
  joining a split citation. The [compilation comparison](../experiments/2026-09-11-compilation-occurrences/page-boundary-case.json)
  retains a citation crossing printed pages 342–343: a footnote and page header
  intervene between `3 CFR` and `60–61 (1971–1975 Comp.)`, producing a false part 9
  in the flat text. Contiguous citation recognition does not solve this failure.

- [x] Close R4's source-passage discovery failure at inserted separators.
  Prepared passage text remains available; only original-source slices become
  evidence, verified by the existing shared helper. Broader layout work below
  remains independent of that fix.
- [x] **Owner: Rulespec Core application/evidence; effort M.** Implement complete
  statement support across inserted whitespace with `evidence_parts` and the shared
  `source_slicer`. Preserve the whole quotation and use existing source fragments
  and bindings for its original-source pieces. Graphs, definitions, term identities,
  structured components, qualifications and review validation retain every piece.
  Concept assignments target the whole prepared region; their supporting evidence
  excludes inserted formatting. Atomic `_evidence` remains strict. No new CUE/Core
  shape or model field was needed. Saved-output and source tests pass; R1/R4 own
  installed delivery, now complete, and R18 the passing changed-ID checks.
- [ ] **Owner: Source producer first, Rulespec document preparation second;
  effort M; depends on an actual corpus need from R20.** Revisit the saved
  Spicy Regs segmentation comparison and existing source readers before extending
  preparation. Compare prepared text with the original selected HTML/XML/PDF,
  especially tables, footnotes, headings, list lead-ins and attachment text.
- [x] Compare USLM preparation with the publisher's captured stylesheet/schema
  and the relevant sibling helpers. RefSpec now owns the small readable-text reader.
  Spicy Regs' attachment transform does not supply XML coordinates; SpicySearch's
  text-unit helper is a possible search consumer, not a replacement formatter.
- [x] Connect R14's USLM consumer in source: preserve heading/list boundaries and
  inline content while mapping prepared text to the captured XML. Existing source
  maps distinguish original text from inserted separators. Three saved cases retain
  all decoded characters and 107 reference texts; 11 preparation controls pass.
  Target text, Unicode/entities, nested elements, repeats, empty references and
  table-cell boundaries have checks. Build the node index once per replay and share
  targets; do not copy or reparse the source separately for every reference.
- [x] Finish R4/R1 validation and installed delivery. Preserve the first failed
  heading-join attempt and the successful B2 outputs in the
  [readable-text experiment](../experiments/2026-09-11-uslm-readable-text/README.md).
  Original XML whitespace remains; the formatter preserves table order and cell
  separation, not full visual table layout. Broader layout support needs its own
  source case rather than an unmeasured general-purpose renderer.
- [ ] Use available publisher text or already extracted source text where it is
  adequate. Spicy Regs' `EnrichCommentText` reuses Mirrulations attachment text;
  it does not establish original-page offsets or legal structure. Keep the
  captured text's own identity and extraction status rather than inventing a map.
- [ ] Fix a demonstrated loss in the source-owning reader. Use Rulespec's existing
  sections/source map for the result. Inspect rendered layout when the decision
  depends on it, and retain ambiguous reading order instead of flattening it into
  a confident rule. Do not replace semantic extraction with overlapping chunks.

**Done when:** the actual failing structure survives preparation and exact evidence
still verifies. No new crawler, generic parser framework or Docspec dependency is
needed for inputs the current prepared-document interface already handles.

## Quality and optional deeper processing

### R24 — Establish fresh end-to-end evidence and a cost baseline

- [x] Complete the narrow fresh-context evaluation: three pinned USC windows,
  two arms, two observations, twelve captured calls, full manual review and
  deterministic replay/export verification. Preserve its
  [defer result](../experiments/2026-09-11-fresh-reference-context/README.md), reported
  usage and newly observed processing defects. Its prepared sources, labels and
  responses now serve as development/regression data, not untouched future tests.
- [x] Separate deterministic retention from model accuracy in the subsequent
  four-arm saved-output comparison. Record the 112 recovered occurrences, remaining
  contradictions, incomplete response and reprocessing identity changes. Do not
  present 552 passing package tests or a higher acceptance count as an accuracy rate.
- [ ] **Owner: Rulespec evaluation; effort M–L; select cases early, run against
  the relevant delivery.** Freeze a small, previously untuned set spanning a manual,
  regulation, notice, state rule and structured source where available. Separately
  retain adversarial development controls. Define expected complete meanings and
  disputed readings before running the compared variants.
  Three statutory chapters alone do not cover this document mix. Keep the narrow
  context comparison separate from the broader report and its source population.
- [ ] Review every layer for those selected inputs: original source → prepared
  text/passages → actual provider request → raw response → accepted/rejected
  candidates → Core records/review history → discovery output and located targets.
  Count omitted conditions, wrong actors/modality, lost alternatives/thresholds,
  incorrect exception targets, unsupported additions and unnecessary repetition.
- [ ] Keep one readable primary statement and optional enrichment that adds
  information. Test whether standalone statements preserve scope even when a
  separate logic quote is complete. Do not adopt explanation fields or extra
  mandatory prose simply because their reasoning sounds plausible.
- [ ] Report processing validity, source grounding, semantic findings and user
  benefit separately. Reuse saved usage accounting for input, answer and thinking
  tokens, retries/refusals, latency and request settings. Price a run only against
  a stated price snapshot; stored JSON size is not billed output tokens.
- [ ] Use source-supported, revisable labels. Keep disagreements visible. Repeat
  live comparisons only where model variability affects the decision; use fixed
  raw outputs for deterministic adapter comparisons. Stop at the declared case
  and cost bound, then adopt, defer or choose a different hypothesis.

Use the following failure categories when labeling and reporting that comparison.
They are checks within R24, not additional pipeline stages or new schemas.

| Check | What the review must distinguish | Related work |
| --- | --- | --- |
| Missing content | Source passages processed versus complete rules, branches and alternatives actually retained | R15–R16, R26 |
| Inherited conditions | A standalone statement retains its governing condition; a nearby but unrelated condition is not attached | R10–R11, R15–R16 |
| Actors and definitions | Who must act versus who is mentioned; what a definition defines; local aliases versus unrelated shared names | R22 |
| Modality | Must, should, may, must not, not required and descriptive possibility keep their distinct meanings | R16, R25 |
| Alternatives and limits | All/any choices, negation, numbers, units, deadlines and threshold boundaries survive together | R16 |
| Exceptions and relationships | The qualification retains its meaning and correct targets; disputed or missing targets remain visible | R11, R16, R25 |
| References and versions | The complete written target, its supporting context and its declared edition survive recognition and lookup | R5–R6, R9, R12–R14 |
| Evidence and identity | Exact source occurrences, source-map boundaries, stable identities and review history survive every export | R3–R4, R18, R23 |
| Noise and cost | One primary statement; optional fields add information; repeated evidence or literal null strings do not masquerade as useful meaning | R26 |

Report counts against each declared case population, with the original source and
raw outputs available for review. Keep semantic disagreements separate from
mechanical failures and from unexamined content.

**Done when:** the current release has an honest, reproducible quality/cost report
on the declared population and a ranked list of remaining failures. No passing
schema, agent verdict or small selected sample is called a general accuracy rate.

### R25 — Test separate relationship verdicts without extra generated prose

- [ ] **Owner: Rulespec refinement/review; effort M.** Clarify whether an existing
  qualification link records scope context, an exception to an otherwise applicable
  duty, or another relationship already expressible in Core. Do this before
  relabeling the disputed refrigerant or carrier examples.
- [ ] Preregister one change: judge each supplied target independently using the
  existing source/evidence path, without the previous affected-action descriptions.
  Compare with the bundled verdict on the original failures, negative targets and
  fresh cases. Hold context, model/settings and candidate targets fixed.
- [ ] Separately test applying only supported links through existing preview and
  revision checks. Preserve unsupported/unknown targets as review observations;
  stale claims or mixed outcomes must not erase a supported link or change an
  exemption's `not_required` meaning. Keep original captures and corrections.

**Done when:** the declared gate passes for both retained correct links and avoided
wrong links, or the intervention remains experimental. The earlier 2/5 → 4/5 gain
did not pass that broader gate. Independent verdicts also do not discover targets
that were never proposed.

### R26 — Make optional investigations cheaper and remove proven duplication

- [ ] **Owner: Rulespec application/refinement; effort M; after the relevant
  decisions in R16/R25.** Compare the existing optional full route with reusing
  its callable omission, relationship or scenario check for a named task. Measure
  useful findings, missed issues, introduced defects, unresolved outcomes, tokens
  and elapsed time; an empty recovery response alone does not prove the stage useless.
- [ ] Deduplicate supplied source positions using the existing evidence table and
  passage IDs, preserving roles and distinct occurrences. Keep nullable enrichment
  sparse. Change source assembly separately from prompt compression so the result
  identifies which change helped or hurt.
- [ ] Reuse current request capture, replay, review history and CLI operations.
  Remove obsolete helpers or duplicated model-facing representations only after
  tracing their consumers and proving parity. Keep historical experiment files;
  avoid a new plugin registry, job system or abstraction for each optional step.

**Done when:** a named optional task retains its useful results at measured lower
cost or with simpler maintained code. The cheap extraction default stays usable
by itself; adopting a new universal model pass requires its own evidence.

## Shared completion checks for each enabled slice

- [ ] **Q1 — Evidence:** retain raw inputs, exact source coordinates, qualification,
  native uncertainty/refusals, parser provenance and edition context where used.
  Repeated occurrences stay distinct; normalized strings do not replace evidence.
- [ ] **Q2 — Regression:** include the actual failure plus counterexamples. Keep
  frozen observations; source/wheel parity is a packaging check, not accuracy proof.
- [ ] **Q3 — Fresh evidence:** evaluate newly selected sources before claiming
  generality. Report measured populations and unresolved/disputed labels separately.
- [ ] **Q4 — Delivery:** test direct imports first, then rebuilt wheels outside the
  checkout; update the intended local environment and support inventory together.
- [ ] **Q5 — Scope:** record which stage changed: recognition, source location,
  interpretation, discovery, or workflow preparation. Processing completeness stays
  separate from semantic completeness; do not use `ClosureClaim` to certify no omissions.

These checks apply to the work being enabled; they are not a new multi-stage
process that every ingested document must run.

## Work that can proceed independently

- **Delivered foundation:** retention, review-history boundaries and reader
  capture are complete. Preserve their receipts while assessing independent readers
  and consumers; recheck affected capture coverage when enabling another module. Preserve the completed R15/R16 experiment and its runtime inputs; its
  failed selector does not enter production through these fixes.
- **Qualified USC:** R5/R6 can assess the frozen qualifier failures independently
  of the context experiment; it does not need new model calls to prove spans and
  native meanings survive.
- **Source structure:** R9–R11 can inspect publisher-supported local addresses
  independently. R14's USLM navigation is delivered; further R23 preparation
  work requires a specific source-layout failure. Coordinate upstream grammar and
  shared adapter edits with R5/R6 before integration.
- **Other reuse candidates:** R20/R21/R22 can check loaders, metadata and vocabulary
  readers independently of model behavior. Select a concrete consumer before
  adding the application connection; a successful import alone is not adoption.
- **Fixed relationship targets:** R25 can compare decisions on already supplied
  targets without waiting for new lookup capabilities. It does not solve missing
  target discovery. R26 follows the particular optional task that earns adoption.

Use the ordering in “Next executable batch” for prioritization. Independent work
still needs a combined consumer check before delivery. Located text, supported
interpretation and measured consumer benefit remain distinct results.

## Natural stopping points

- **Reader delivery:** R1–R4 complete, with explicit qualifier limitations. This
  is a small useful release and does not require solving every later task.
- **Extraction retention:** the demonstrated complete-evidence and passage-range
  defects pass installed checks, changed-ID/review behavior is explicit and the
  delivery receipt is complete. This stopping point is now met. Commit when requested without requiring
  a new model pass or reopening the failed selector.
- **USLM navigation delivery:** the new selector check passes, application exports
  are inspected, and the three new wheels reproduce source results in the intended
  installation. Stop and record this useful result even if the subsequent
  comprehension experiment shows no benefit. Do not label navigation as extraction
  accuracy or require a new model pass to use a publisher-provided link.
- **Reference-assisted extraction:** one route through local or external source
  lookup improves the declared context task, passes fresh checks and replays from
  captured data. More parser families remain independently selectable.
- **Reuse objective complete:** the relevant candidate inventory has been assessed;
  every demonstrated useful connection is delivered and verified, and remaining
  candidates have an evidence-backed defer decision or a clearly stated external
  prerequisite. An untested candidate is not silently counted as unnecessary.
- **Commit/release boundary:** prepare scoped commits and the exact installed-build
  receipt for the delivered slice. Commit when requested. Publication/deployment
  status stays separate from local implementation. Do not call the overall reuse
  objective complete merely because a partial release is ready.

## Main implementation and evidence pointers

- Current adapter: [references.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/references.py)
- Delivered retention implementation: [result](../experiments/2026-09-11-extraction-retention/README.md),
  [saved-output checks](../experiments/2026-09-11-extraction-retention/checks.json),
  [source suite](../experiments/2026-09-11-extraction-retention/application-source-command.log),
  [review comparison](../experiments/2026-09-11-extraction-retention/old-review-check.json),
  [wheel inputs](../experiments/2026-09-11-extraction-retention/wheel-inputs.json)
- Consumer and source evidence: [discovery.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/discovery.py),
  [documents.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/documents.py),
  [core.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/core.py)
- RefSpec native CFR occurrence API: [citation_grammar.py](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/citation_grammar.py)
- RefSpec shared publisher-link reader: [uslm.py](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/uslm.py),
  [USLM experiment design and captures](../experiments/2026-09-11-uslm-source-links/design.md)
- Installed USLM application: [uslm.py](../../packages/rulespec-extrapolator/src/rulespec_extrapolator/uslm.py),
  [application tests](../../packages/rulespec-extrapolator/tests/test_uslm.py),
  [readable-text result](../experiments/2026-09-11-uslm-readable-text/README.md)
- Delivered selector validation: [source-fragment.cue](../../constraints/core/source-fragment.cue),
  [compiler tests](../../tools/test_constraints_compile.py),
  [cross-format fixtures](../../tools/constraints_parity.py)
- SpicySearch strict readers: [cfr_citations.py](/Users/mikewolfd/Work/spicysearch/src/spicysearch/cfr_citations.py:139)
- Delivered RIN boundary and comparison: [review](../reviews/2026-09-11-rin-boundary-review.md),
  [result and delivery receipt](../experiments/2026-09-11-rin-reference-space/README.md),
  [RefSpec minter](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/iri_minting.py:536)
- Capability/source inventory: [reference-parser-reuse.md](../reviews/2026-09-10-reference-parser-reuse.md)
- Context availability evidence: [context-selection](../experiments/2026-09-10-context-selection/README.md)
- Completed fresh-context comparison: [result](../experiments/2026-09-11-fresh-reference-context/README.md),
  [design](../experiments/2026-09-11-fresh-reference-context/design.md),
  [captured cases](../experiments/2026-09-11-fresh-reference-context/source-selection.json),
  [source review](../experiments/2026-09-11-fresh-reference-context/source-review.md),
  [raw review](../experiments/2026-09-11-fresh-reference-context/raw-review.md),
  [replay and processing losses](../experiments/2026-09-11-fresh-reference-context/processing-checks.json)
- Context/target/retrieval pilot decisions: [design-pilots](../experiments/2026-09-10-design-pilots/README.md)
- Current CFR integration decision and captures: [design](../experiments/2026-09-11-cfr-integration/design.md),
  [raw scans](../experiments/2026-09-11-cfr-integration/source-raw.json)
- Existing RefSpec act resolution: [act_resolution.py](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/act_resolution.py)
- Existing SpicySearch vocabulary/agency readers: [atlas_search_view.py](/Users/mikewolfd/Work/spicysearch/src/spicysearch/atlas_search_view.py),
  [agency_projection.py](/Users/mikewolfd/Work/spicysearch/src/spicysearch/agency_projection.py)
- Existing Rulespec vocabulary assignment and publication metadata: [projection.py](../../packages/rulespec-projection/src/rulespec_projection/projection.py)
- Source-preparation comparison: [Spicy Regs segmentation](2026-09-06-spicyregs-segmenter-comparison.md)
- Broader process recommendations: [pipeline recommendations](../reviews/2026-09-10-pipeline-recommendations.md)
- Earlier completed extraction changes: [production-readiness](2026-09-10-production-readiness.md)

Future execution should update this list's statuses and link the resulting
evidence. Original experiment verdicts and captures remain unchanged.
