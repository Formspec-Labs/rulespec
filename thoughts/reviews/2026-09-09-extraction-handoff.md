# Extraction handoff — September 9, 2026

The [operating guide](../../packages/rulespec-extrapolator/README.md) describes the
current workflow. Use low-thinking extraction with an optional medium-thinking
audit. Retain full source passages for discovery and human review before deriving
executable workflows. CLI and library thinking defaults are now low extraction
and medium audit; window sizes and output caps retain their earlier values.
See the latest implementation entry below; older entries describe their snapshots.

The latest [quality decision](2026-09-09-extraction-quality-decision.md) consolidates
four completed experiments: retain the current workflow; audit helps with the
tested explicit contradictions but does not guarantee inherited qualifications.

## Integrated

- Audit inventory selects passage IDs through a CUE-generated schema and resolves
  them through the existing source resolver. Missing, out-of-focus and inserted
  evidence remains refused. Exact source text, offsets, raw responses, rejected
  observations and provenance remain available. Comparison now also selects
  passage references, resolves exact source text, and produces existing Core
  `Finding` records.
- The successful example-inheritance wording lives in CUE `#Summary`. Extraction,
  refinement and audit share it. Native CUE now generates four schema views,
  including `inventory.schema.json`; Python has no competing inventory definition.
- Audit version 4 records the current response shape. Historical version 2
  experiments retain their original captures and frozen runtimes. Their manifests
  were not rewritten. No legacy response conversion was added.

## Evidence and verification

The [fresh full-section inventory comparison](../../examples/document_understanding/full-inventory-evidence-comparison/README.md)
used the same 6,919-character source and current example guidance in both arms.
Quotation-based inventory refused 6 of 22 observations; passage-ID inventory
accepted all 20. Both retained the teacher example's governing condition. Both
still omitted details and produced imperfect classifications. This is one call
per arm on development data, with agent-authored, revisable meaning judgments.
The changed schema and instructions form a bundle; the comparison does not
isolate identifier syntax as the cause or establish general semantic accuracy.

Historical inventory-integration verification (later checks are recorded below):

- All 347 package and schema-generator tests pass; native CUE drift check passes.
- The integrated provider request exactly equals the saved successful passage-ID
  request. The current parser reproduces all 20 saved inventory records unchanged.
- All eight newly saved experiment/check directories replay with their frozen
  inputs and runtimes; all 547 artifacts pinned by their outer manifests retain
  their recorded hashes.
- No fresh provider calls were made during integration. A new complete
  extraction-plus-comparison run under this runtime remains unmeasured.

The [earlier end-to-end run](../../examples/document_understanding/low-extract-medium-audit/README.md)
produced 19 accepted extraction statements, but four inventory refusals made its
review incomplete. Its three calls used 64,117 tokens and 48.24 seconds. Those
counts predate the integrated evidence and guidance changes. The
[deterministic evidence check](../../examples/document_understanding/refused-evidence-check/README.md)
reproduces all four refusals and resolves them using reviewed substantive quotes
or passage IDs without changing meaning. An unrelated valid ID still passes the
mechanical check: source existence does not prove interpretation.

## Remaining focused work

1. Test whether audit distinguishes complete standalone wording, qualifications
   retained only in `logic_text`, and qualifications absent everywhere. Existing
   instructions ask for this distinction, but the earlier audit missed it.
2. Check exemption/permission classification and duty-bearer wording against saved
   failures. Existing schemas express these distinctions; no new Core type is
   needed.
3. If revisiting dependent deadlines, measure segmentation-instruction adherence
   separately from meaning preservation. The
   [grouping experiment](../../examples/document_understanding/deadline-grouping-experiment/README.md)
   followed the grouping instruction in only one of two same-scope runs. No
   grouping instruction is adopted; existing fields support the successful form.
4. Before claiming broader improvement, repeat a complete workflow and evaluate
   new source material with independent, revisable judgments. Neither schema
   validity, accepted evidence nor replay establishes complete source coverage.

The [example-inheritance experiment](../../examples/document_understanding/example-inheritance-experiment/README.md)
and [transfer cases](../../examples/document_understanding/example-inheritance-transfer-experiment/README.md)
support the adopted wording narrowly. Detailed historical reports preserve their
original adoption decisions and settings; this handoff states what is integrated.

Implementation and research are committed separately. No push, deployment, release
or global memory change is part of this work.

## Subsequent small improvements

Discovery now exports existing `logic_text` alongside short statements. Fourteen
focused tests pass; the field preserves qualifications in both the saved accounting
case and a fresh notice-procedure case. Full source passage records remain intact.

The [two controlled comparisons](../../examples/document_understanding/minor-audit-improvements/README.md)
used 16 calls. Added CUE classification guidance improved labels but lost teacher
scope in one result; no adoption. Unit judgment order passed the primary verdict
checks 6/6 in both arms; no measured improvement and no adoption.

A reserved 29 CFR 825.303 section then produced 18 accepted extraction statements
and 19 accepted inventory observations. Comparison refused three claim/unit pairs
because copied quotations changed whitespace, leaving review incomplete. The raw
audit caught one overbroad permission but could not admit its evidence. Detailed
source reviews, refusals and identical replay are saved in the linked experiment.
The next candidate is comparison-stage passage references, not more prompt tuning.
These subsequent changes are local and uncommitted.

## Whitespace fallback tested, not adopted

The [follow-up experiment](../../examples/document_understanding/whitespace-evidence-experiment/README.md)
reprocessed the saved comparison with a whitespace-only fallback. All six refused
judgments recovered with original source offsets and unchanged raw verdicts;
accounting became complete, while the audit correctly remained failed. Of 17
expected-refusal controls, 15 remained refused, but two constructed table/list
joins were accepted. This fails the broad acceptance gate. No production matcher
change or provider calls; preserved artifacts include all 23 controls. General
whitespace matching and its superiority to passage IDs are not established.

## Known-library fuzzy comparison

The [library comparison](../../examples/document_understanding/library-fuzzy-evidence-experiment/README.md)
tests fuzzysearch 0.8.1 and installed LangExtract 1.6.0 across nine configurations
and 29 controls. Strict LangExtract (token coverage/density 1.0/1.0) recovers all six
judgments while rejecting seven content-change counterexamples; three ambiguity
and two layout cases remain accepted. Disabling fuzzy alignment produces identical
controls and audit, proving token-exact alignment suffices for these recoveries.
Reuse of that existing aligner is a concrete next candidate, with explicit
uniqueness/layout policy; no production alignment change was adopted.

The full-grid replay has stable printed outcome counts but fails exact equality.
A short-control diagnostic finds the asymmetric fuzzysearch configuration choose
a different occurrence of repeated text. The token-exact follow-up replays exactly.
All observations and counterexamples are saved; no model calls were made.

## Comparison passage-ID experiment executed

The [four-call comparison](../../examples/document_understanding/comparison-passage-ids/README.md)
kept the saved full source, draft and inventory fixed. Current exact matching accepted
32/36 then 36/36 judgments; token alignment accepted 36/36 in both; passage IDs
accepted 36/36 in both. Both ID runs cite the governing phone-call lead-in that the
second quote run leaves out of its selected evidence. All four detect the known
scope defect, but none explicitly identifies qualifications retained in logic_text.
The strict adoption gate is unmet; no production matcher or comparison change.

IDs used 22.6% fewer mean output tokens, but only 3.0% fewer total tokens because
input repetition remained fixed. All four calls used 254,201 reported tokens.
Local controls show cross-passage disambiguation but unresolved within-passage
ambiguity, layout joins and loss of separately selected conditions when narrowing.
Passage-only comparison is the simpler candidate for a separately narrowed
reliability decision; no evidence supports adding a fuzzy layer. Stop this bounded
experiment here. Captures, masked/unmasked review and identical replay are saved.

Source correction: C0014.logic_text starts mid-sentence at F004. It retains unusual-
circumstances/emergency qualifications but lacks F003's unforeseeable-leave lead-in;
it is not the complete original paragraph. Preserve that distinction in later
field-specific quality work. These results remain local and uncommitted.

## Passage references integrated after explicit next-step authorization

The user authorized the proposed narrower citation-reliability integration and a
checkpoint commit, followed by two untouched source checks. Comparison now selects
CUE-generated source references; the existing resolver retains complete passages
and refuses invalid evidence. All 356 package/schema tests and CUE drift checks
pass. Both saved P runs reproduce exactly through production, without new calls.
Audit format is version 4. Previous research/runtime is committed at `68de277`;
old captures retain their original schemas and observations. This adoption does
not retroactively pass the broader semantic gate. Two-document transfer evaluation
is the next bounded task, with no semantic prompt tuning in that evaluation.

## New-source transfer check completed

Integration is committed as `83caace`. The
[two-source check](../../examples/document_understanding/passage-id-transfer/README.md)
ran complete 8 FAM 801.2-1 and Ohio rule 3745-52-15 through low extraction, medium
inventory and medium comparison. Six calls used 104,909 reported tokens. Passport:
16 accepted claims, 15 substantive inventory units, 31 accepted judgments. Waste:
14 accepted claims, 21 substantive units, 35 accepted judgments. Both audits say
passed and review complete; all citations resolve, and both full workflows and
discovery exports replay identically.

Direct review preserves this distinction: passport C0005/C0006 split cleared-language
use from qualified local adaptation; both meanings survive collectively, but the
standalone duty lacks that qualification. Treat severity as consumption-dependent,
not a proven universal prohibition. The waste nested exceptions, AND/OR groups and
three-day disposal destinations survive well. One noncontiguous passport modality
component was withheld; five component warnings across both documents remain.
Three local waste citation records lack graph targets. No outputs were repaired.

The [next focused task](../plans/2026-09-09-preserve-standalone-qualifications.md)
prioritizes self-contained qualifications using existing fields and the clearer
notice failure, with the successful waste groups as regression controls. No further
prompt/schema/matcher experiment was run. The bounded integration and transfer work
is complete; further condition-profile changes remain a separate iteration.

## Standalone-description experiment completed without adoption

The [eight-call follow-up](../../examples/document_understanding/standalone-qualification-experiment/README.md)
changed only one native CUE statement description. Both arms retained the passport
qualification and both still lost the notice permission's governing conditions
from its statement and scope. Waste semantic groups and the three independent-rule
controls passed, but treatment added two missing scope-evidence bindings. No
incremental target benefit was demonstrated; keep the production schema unchanged.

All 106 raw statements survive conversion unchanged; all 420 retained evidence
spans match source offsets. Eight runs completed without parser refusals and replay
identically. Eight calls used 44,851 reported tokens. Masked self-review, raw outputs,
warnings, metrics and the unmet decision gate are saved. One sample per case/arm
does not establish repeatability. This latest research is local and uncommitted.

The notice row is identical in both raw outputs and selects only F004, after a
blank-line split within its governing sentence. The next proposed diagnostic tests
that passage boundary while keeping source bytes and runtime settings fixed, with
repeat notice pairs and independent-rule controls. This is a different hypothesis,
not evidence for a generic merge policy. It is saved in the experiment README and
has not been executed. Stop further description tuning at this checkpoint.

## Passage-boundary diagnostic completed without adoption

After the user asked to continue with the test-hypotheses skill, the
[boundary diagnostic](../../examples/document_understanding/passage-boundary-experiment/README.md)
ran the proposed eight-call comparison. Joining only the known sentence break
preserved the notice lead-in in selected logic in 2/2 treatment runs versus 0/2
baselines. It fixed the standalone statement in 0/2 treatment runs and 0/2
baselines; one treatment partially improved scope. Both constructed independent-rule
controls passed in both arms. Modality labels still varied. The semantic gate is
unmet, and the catalog intervention remains experimental.

All eight captures completed: 80 accepted records, no rejected rows or parser
refusals, 314 exact retained evidence spans. Raw-to-record checks and full replays
pass. Eight calls used 32,961 reported tokens. Both experiments in this continuation
used 16 calls and 77,812 reported tokens total; no further calls are pending.

Stop this iteration here. Source-context retention improved under the diagnostic,
but complete short statements did not. The next useful decision is whether the
existing audit can distinguish qualifications absent from the statement from
qualifications absent from both statement and evidence, using the now-saved
contrasting cases. No audit comparison or repair was run in this iteration.
Production remains unchanged; latest research and this handoff remain uncommitted.

## Existing audit field distinction tested

The [six-call audit diagnostic](../../examples/document_understanding/audit-field-distinction/README.md)
held the full notice source, 18 claims and 18 inventory units fixed and varied only
the target draft. Original failure: audit passed it 2/2. Same short statement with
full governing logic: scope error 2/2, summary error 1/2. Constructed complete
statement: correct 2/2. No rationale explicitly made the complete logic-versus-
statement distinction. All six selected the full governing F003:F004 evidence.
The preregistered reliability gate is unmet; valid evidence does not make this an
automatic standalone-quality gate.

All 216 judgments have valid exact evidence and complete reciprocal accounting.
Six calls used 326,531 reported tokens. The initial replay hit a harness manifest
mismatch; an isolated comparison-manifest wrapper preserves the frozen runner and
reproduces all six judgments/reports exactly. Raw captures, constructed-input
provenance, masked review, metrics and the replay failure are saved. Production and
original Core graphs/history are unchanged. Latest research remains uncommitted.

Do not keep tuning this notice sentence. A broader audit sensitivity evaluation
on different losses of negation, alternatives, actors and deadlines is the next
candidate. The overall goal remains active pending clarification of whether the
user wants a tested recommendation or a verified improvement integrated. No further
provider calls are pending for this completed six-call experiment.

## Broader audit sensitivity checked

The [four-call mutation test](../../examples/document_understanding/audit-mutation-sensitivity/README.md)
caught four planted actor, negation, AND/OR and deadline changes and accepted the
four original target records. Nearby named correct rules remained correct. One
rationale overstates OR as exclusive; the underlying AND-to-OR finding is valid.
The previously known passport qualification issue still went unflagged. This is
bounded sensitivity evidence, not a general accuracy rate or completeness gate.

All 132 judgments have complete accounting and 225 exact evidence spans. Four
calls used 163,702 reported tokens and replay identically. The consolidated
[quality decision](2026-09-09-extraction-quality-decision.md) recommends preserving
the current workflow and using audit for review triage. No additional prompt,
schema, matcher or approval feature is adopted. Latest research is uncommitted;
the overall goal remains active pending the requested endpoint clarification.

## Production propagation aggregated at the user's request

The current experiment and its verification are complete. The
[production propagation plan](../plans/2026-09-09-production-propagation.md)
maps all candidates to current code: update operating guidance and maintain the
selected evaluation cases; separately decide whether low extraction / medium audit
should become explicit thinking defaults. Existing code supports those settings,
but currently defaults to the provider's unspecified thinking level. Output caps
and window sizes are separate decisions, not bundled promotions.

Passage IDs, source-preserving discovery, CUE guidance and completeness limitations
are already integrated. The plan excludes unsupported wording, merge, fuzzy and
automatic-approval changes. This is an aggregation, not newly implemented runtime
behavior or a commit/release. No further experiment is required to deliver it.

## Production propagation implemented

The user explicitly requested implementation of the plan. Research, revised
operating guidance and the maintained evaluation case index are committed in
`beb3fbf`; all 26 historical calls replayed before runtime changes. Historical
uncommitted/pending statements above describe their earlier checkpoints.

The only runtime change makes low extraction and medium audit the CLI/library
thinking defaults and updates reprocessing's current-settings comparison. Explicit
levels and Python `None` remain supported. Output caps/windows, CUE definitions,
meaning generation, evidence matching and review behavior retain their prior design.
All 371 package/schema-generator tests and native CUE drift checks pass.

The [bounded live check](../../examples/document_understanding/production-defaults-check/README.md)
used three calls and 33,025 reported tokens. Actual requests match the new defaults;
extraction, audit and discovery replay identically. It produced 16 accepted records,
one withheld non-verbatim modality quote and three unresolved reference records.
Extraction is partial; the audit passed but still overlooked the standalone local-
adaptation qualification. These are retained limitations, not a failed configuration
promotion or a demonstrated semantic improvement. No further calls are pending.
The implemented scope is complete. This entry accompanies the separate runtime
configuration commit; no push, release or deployment is included.

## Statement-first extraction and compact audit input

Implemented the requested reduction in repeated fields. Canonical CUE now requires
a complete nonempty statement, kind and modality; other lean extraction fields
accept omission/null. Parser version 6 keeps current Core empty-value conventions
and original raw captures. Audit version 5 omits empty request fields and replaces
exact catalog quotations with passage references. Populated meaning and evidence
roles remain separate, and saved source/records/history remain full.

The [eight-call check](../../examples/document_understanding/sparse-meaning-check/README.md)
measured 57–79% fewer audit input tokens, with all four planted errors still caught
and the passport/waste neighboring controls intact. The notice qualification miss
persists; two new modality flags leave the broad quality gate unresolved. This is
a bounded noise/token reduction, not general accuracy validation. Fresh passport
and waste extractions omitted all redundant scope/choice/logic enrichment while
retaining the reviewed governing conditions, alternatives and deadlines. Some
cross-record overlap and mixed-modality segmentation remain.

All eight captures replay identically without provider calls. Native CUE drift
and the full 377-test suite passed; all 35 audit tests passed after adding two
quote-reference counterexamples. This work and the preceding compact evidence UI remain local;
no new commit, push or deployment was requested in this iteration.

## Interpretation-order experiment — no adoption

The [nine-call interpretation check](../../examples/document_understanding/interpretation-order-check/README.md)
compared current extraction with an instruction to populate existing scope/choice
interpretations, placed before versus after the statement. All arms passed 17/18
selected statement checks and missed the same notice qualification. Early output
omitted interpretation on both real documents. Late output added explanations but
used 22% more output tokens overall and produced some incomplete structured scopes.
The actual requests and observed key order were verified; absence of optional
fields means order compliance alone did not demonstrate the intended mechanism.

No prompt/order change was adopted. A separate concise interpretation-note field
remains untested. If revisiting this idea, first measure whether the known failure
receives an actual condition-binding explanation, then whether its statement
improves without harming counterexamples. Preserve the raw secondary differences
and nonfatal issues recorded in the report; this is not a general accuracy score.

## Dedicated explanation fields tested separately

The [fifteen-call field comparison](../../examples/document_understanding/field-explanation-check/README.md)
tested actor, modality, logic and applicability explanations independently against
fresh baselines on the same three real sources. Each isolated CUE-generated variant
required one nullable field before statement; production remained unchanged.
Logic gave selective, supported decompositions; modality exposed classification
choices and a possible uncertainty-handling improvement; actor was nearly all null;
applicability mostly produced generic descriptions and missed the known notice
qualification. No field met its predefined matching statement-repair criterion.

Required-note variants also emitted many unrelated optional nulls: output rose
52–62%, partly because of those placeholders rather than explanation content.
All fifteen captures replay identically. Keep the per-field outcomes separate;
do not infer that all explanation fields are equally useful or that notes improve
statements merely by preceding them. No additional calls or adoption are pending.

## Logic/modality omission experiment — no adoption

The [eight-call omission check](../../examples/document_understanding/omit-empty-explanation-check/README.md)
tested logic and modality independently with fresh required-nullable controls.
Optional non-null CUE fields plus omission instructions removed all 438 optional
null placeholders and reduced output tokens by 35–55% per pair. However, the same
change omitted every explanation, including useful control notes. Logic retained
the named statement checks; modality's waste output also lost the satellite-
exemption setting on five independent statements. The known notice qualification
miss persists. One repeat per cell does not establish a causal quality regression.

Neither field meets the full retention gate; production remains unchanged by this
experiment. A useful next isolation is to keep the required-nullable explanation
while omitting empty values only from other enrichment fields, which accounted
for 400 of the control nulls. Field-specific explanation inclusion criteria can
then be tested separately. Native generation rejected minimum-length source-ref
lists before calls; the documented trial instead enforced non-null/nonempty
strings and requested empty-list omission in the prompt. All eight saved runs
are complete; no further model calls are pending.

## Omit other empty enrichment, retain the explanation slot

The [eight-call scoped enrichment check](../../examples/document_understanding/scoped-enrichment-check/README.md)
kept each required-nullable explanation definition identical and changed only the
other enrichment to omission. It removed 390 other-field nulls, retained every
useful control explanation observed, and reduced output tokens by 24–43% per pair.
All named statement checks were unchanged; the notice qualification miss persists.
A control also changed “may not be required” to “is not required,” while its paired
intervention retained uncertainty. One call per cell does not establish causation
or a repeatable accuracy gain.

Logic remained selective but supplied no notice explanations in either arm.
Modality supplied an explanation for every intervention record, including many
straightforward restatements. Twenty-three required note nulls remain deliberately;
this isolation removes the larger overhead without claiming all-null elimination.
The result supports separating omission from explanation generation. It does not
justify adding explanation fields to production, which currently has none.

Stop repeating these development sources for now. If pursuing explanations, judge
their marginal value on untouched documents against current statement-first
extraction, separately for logic and modality. A schema-only omission change
without explanation fields is a separate production decision. All eight runs are
saved; no additional calls, adoption or commits are pending from this experiment.

## Fresh-source accuracy comparison — leave explanations out

The [twelve-call fresh-source check](../../examples/document_understanding/fresh-explanation-check/README.md)
compared current extraction, omission-only cleanup, logic explanation and modality
explanation on previously unused oxygen, employee-alarm and procurement sections
retrieved from the official eCFR API (September 4 version). Schemas and 30 source
checks were frozen before calls; no guidance was tuned to these sources.

Logic supplied no field-relevant repair over both controls. Modality alone retained
the all-employees-can-hear limit on a separate alarm backup exemption, but lost an
oxygen exemption boundary and omitted a procurement possibility that both controls
retained. Logic misclassified that procurement possibility as permission. An
additional alarm-testing scope judgment is interpretation-sensitive; excluding it
does not change either failed accuracy gate. Most other selected checks passed.

The result is a tradeoff, not a case for production explanation fields. Logic
used 10.4% more output tokens than omission-only; modality used 15.7% fewer, partly
alongside omitted content. The 289 emitted records all passed mechanical validation,
which did not catch these semantic issues. Preserve the raw captures and revisable
review judgments. Stop this explanation-field hypothesis branch and keep the new
sections frozen rather than tuning against them. Production remains unchanged;
no further calls, adoption or commits are pending from this experiment.

## Integration and verification

Runtime commit `376183f` integrates complete statements with optional nullable
enrichment, compact audit input and grouped review evidence. The dedicated
explanation fields and stricter omission-only variants remain experimental.
The package guide and evaluation index now point to the fresh-source decision.

Verification passed: 379 tests, native CUE generation, and offline replay of all
60 captures across the six new experiments. Browser inspection confirmed compact
evidence display, component highlighting and keyboard access to field details.
Original captures, source files, manifests and review judgments remain intact.
No additional provider calls were made for integration. Commits are local; no
push or deployment was requested.
