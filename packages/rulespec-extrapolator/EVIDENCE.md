# Evidence index

This file preserves the earlier operating guide’s research discussion. Each linked
report describes its own settings and checkpoint; it is not a current installation
recipe. Use the [README](README.md) for the main path and the
[operating reference](OPERATIONS.md) for current commands.

## Confidence, labels and qualification connections — 2026-09-12

Recent [inline confidence](../../thoughts/experiments/2026-09-12-extractor-confidence/RESULTS.md),
[separate confidence](../../thoughts/experiments/2026-09-12-separate-confidence/RESULTS.md),
and [explicit narrative](../../thoughts/experiments/2026-09-12-explicit-verdict/FINDINGS.md)
experiments did not establish a production-ready quality signal. Their original
captures and assessments remain unchanged. The later
[21-item label audit](../../thoughts/reviews/2026-09-12-confidence-label-audit.md)
qualifies the reported errors: two clear standalone-completeness failures, a
debatable explicit-detail loss, and a disputed actor assignment. The positive
statement labels do not certify all structured fields; LEA purpose text appears
in `scope_text`. Keep source fidelity, independent completeness and field roles
separate in future comparisons.

The [read-only qualification trace](../../thoughts/experiments/2026-09-12-existing-qualification-links/FINDINGS.md)
found that the writing requirement and its target clause identifiers already
exist, but the scanner misses the plain-text local references between them.
Manual native-address lookup reaches the correct claims without new identifiers.
The subsequent [local-clause delivery](../../thoughts/experiments/2026-09-12-local-clause-navigation/README.md)
connects the two attendance records with the writing requirement in both
directions. It uses RefSpec occurrence recognition, native sibling lookup and
current claim evidence, with explicit ambiguity and refusal controls. Semantic
qualification assignment remains open. No new model pass or automatic governing
link was adopted; 713 extractor/schema and 180 targeted reader tests passed.

The [subsequent recovery comparison](../../thoughts/experiments/2026-09-12-navigation-repair/README.md)
tested whether supplying that navigation leads to complete statements. Both arms
returned empty proposals on IEP and a constructed control; no omissions were
repaired. Existing fields and review previews can represent the needed changes,
so the result does not justify a new schema. Keep navigation and repair quality
separate; no production model pass changed.

The [fixed-repair diagnostic](../../thoughts/experiments/2026-09-12-fixed-repair-check/README.md)
then supplied ten constructed repairs to the unchanged checker, each twice in
reversed presentation order. Both correct IEP edits were accepted both times;
all seven wrong edits were rejected both times. The constructed request-content
addition was rejected twice as duplication of another claim. One correct
rejection's rationale also wrongly extended writing to agency consent. The full
gate failed despite exact citations and complete verdict output. This supports
recognition of the supplied IEP repairs, not automatic discovery or a general
accuracy claim. No new production pass, prompt or schema was adopted.

## Discovery and optional audit check — 2026-09-12

[Three fresh sources](../../thoughts/experiments/2026-09-12-simple-path/RESULTS.md)
produced 34 statements. Linked evidence recovered complete source support for
8/12 questions versus 7/12 from source alone, with one further substantial partial
gain and no losses. Keep that capability; the small sample leaves broader benefit
uncertain. Optional audit missed the two preselected gaps, found a historical
omission and preserved the faithful control. The full batch used seven requests
and 98,457 recorded tokens. Production extraction settings remain unchanged.

The [retention comparison](../../thoughts/experiments/2026-09-11-extraction-retention/README.md)
fixes passage ranges across blank catalog entries and complete quotation support
across inserted formatting. It preserves more of the model's existing output;
model settings and schemas remain unchanged.

Saved runs also capture the installed reference-reader sources and package versions
through the [existing runtime record](../../thoughts/experiments/2026-09-11-reader-runtime-capture/README.md).
Reader changes produce explicit replay drift. Use `reprocess` to apply new code to
an old capture; its original reviews stay with the original run. Plain-text
extraction and Core validation still work without the optional reference packages.

## Current recommendation and evidence

Start with **low-thinking extraction**. Add a **medium-thinking audit** when its
diagnostic feedback is useful. Keep full source passages available to downstream
search alongside the extracted statements. Relationship refinement and structured
concept/value enrichment are optional. Ordinary extraction represents meaning in
prose, but can still omit qualifications. Keep complete statements and their source
passages available together. When populated, `logic_text` retains verbatim wording
for inspection; it does not replace qualifications missing from a statement.

Normal extraction requires one complete `statement`, `kind`, `modality`, and an
explicit actor assessment (`actor` and `actor_quote`, both nullable). A small
source-backed term index precedes the statements: definitions identify what they
define, aliases retain the source wording, and uses link to the local definition.
Other enrichment may be omitted or null; it should add useful structure.
Audit requests omit empty fields and reuse passage references for exact repeated
quotations. The [sparse-meaning check](../../examples/document_understanding/sparse-meaning-check/README.md)
measured 57–79% fewer audit input tokens while retaining four planted-error
detections. The known qualification miss remains, and two additional modality
flags leave the broader quality comparison unresolved.

Dedicated logic and modality explanations remain experimental. The
[fresh-source comparison](../../examples/document_understanding/fresh-explanation-check/README.md)
found no dependable accuracy gain across three previously unused regulatory
sections. Keep the current optional, nullable enrichment fields; the stricter
omission-only variants were experimental controls and are not the default. Preserve
these evaluation sources without tuning prompts against their observed failures.

The [earlier full-section run](../../examples/document_understanding/low-extract-medium-audit/README.md)
used a saved 6,919-character leave-eligibility regulation before the inventory
evidence change below:

- Low extraction produced 19 accepted statements with no rejected candidates.
- Medium inventory and comparison completed, but four inventory entries failed
  exact-evidence checks. The audit correctly reports `review_complete=false`.
- Direct review found the main conditions, alternatives and examples retained,
  plus remaining weaknesses in standalone wording that the audit missed.
- The three calls used 64,117 reported tokens and about 48 seconds of request
  time. This is one measured run, not a typical-document cost estimate.
- Extraction, audit and discovery export replay identically. At that historical
  snapshot, all 333 package tests, six schema-generator tests and native CUE
  generation checks passed.

The [small medium/high comparison](../../examples/document_understanding/medium-audit-experiment/README.md)
retained detection of two deliberate omissions while reducing token volume by
79%. Its fixture limitation and single samples prevent a general accuracy claim.
The full-section result confirms that a completed model response can still leave
an incomplete review. Neither experiment justifies automatic approval or repair.

The profile now also tells the model to preserve the governing conditions of an
example when extracting it as a separate unit, while respecting explicit scope
changes. The audit reads this guidance from the same generated CUE description.
[Paired inventory experiments](../../examples/document_understanding/example-inheritance-experiment/README.md)
and [new synthetic cases](../../examples/document_understanding/example-inheritance-transfer-experiment/README.md)
support the wording. The passage-ID inventory is now integrated: a
[fresh full-section comparison](../../examples/document_understanding/full-inventory-evidence-comparison/README.md)
produced six evidence refusals among 22 quotation-based observations and none
among 20 passage-ID observations. Both retained the teacher example's governing
condition, while semantic defects remained in both. This is one development
sample per arm, not a general accuracy estimate.

The integrated request exactly matches that successful passage-ID request, and
the parser reproduced all 20 saved inventory records unchanged. At that
integration snapshot, all 347 package and generator tests and native CUE drift
checks passed. Subsequent [passport and waste full workflows](../../examples/document_understanding/passage-id-transfer/README.md)
measured extraction, inventory and comparison on two additional sources; their
processing success does not establish semantic completeness.

The [subsequent small-improvement check](../../examples/document_understanding/minor-audit-improvements/README.md)
adds `logic_text` to discovery exports. Extra classification guidance and unit
judgment ordering remain experimental: the former showed a scope regression,
and the latter improved none of the primary verdict checks. A fresh notice section
produced 18 accepted statements and no inventory refusals, but comparison rejected
three claim/unit pairs for inexact copied quotations. Review remained incomplete.
A [whitespace-only fallback experiment](../../examples/document_understanding/whitespace-evidence-experiment/README.md)
recovers those pairs, but accepts two constructed table/list joins against the
declared expectations. It remains experimental; comparison matching was exact
at that checkpoint. A [known-library comparison](../../examples/document_understanding/library-fuzzy-evidence-experiment/README.md)
then found that installed LangExtract can recover all six judgments through its
token-exact alignment, even with fuzzy matching disabled. That path still selects
ambiguous and layout-sensitive spans in the constructed controls; it remains
experimental. Configurable character-edit matching showed broader content-change
acceptances, and one fuzzysearch setting varied its selected repeated-text location.

The [passage-ID integration](../../examples/document_understanding/passage-id-integration/README.md)
now uses that existing source-reference path in comparison as a narrowly scoped
citation-reliability improvement. It reproduces both saved ID runs, preserving all
36 judgments per run. The broader semantic-quality gate remains unmet.

The [explicit-contradiction check](../../examples/document_understanding/audit-mutation-sensitivity/README.md)
caught four planted changes to actors, exemptions, alternatives and deadlines,
and accepted their four original counterparts. It also preserved the named nearby
correct rules. These selected development cases support audit as review triage;
they do not establish a general detection rate. One rationale incorrectly called
an either/or choice “mutually exclusive,” so explanations also need scrutiny.

Stronger statement instructions and diagnostic passage joining did not repair the
standalone notice statement. The [maintained case index](../../examples/document_understanding/evaluation-cases.md)
keeps desired field behavior separate from observed successes and misses, with
source hashes and original captures. The [quality decision](../../thoughts/reviews/2026-09-09-extraction-quality-decision.md)
explains why these results support retaining the current extraction semantics.
For discovery, users can correct source-backed drafts over time. Before deriving
an executable workflow, review governing conditions and exceptions against the
source; a passed model audit does not certify complete rules.

The [default-configuration check](../../examples/document_understanding/production-defaults-check/README.md)
verified the promoted thinking defaults through three live calls and identical
offline replays. All 371 package/schema-generator tests and native CUE drift checks
passed. The live extraction remained partial because one component quote was
withheld; the audit still missed the known standalone qualification risk.

## Remaining work and research evidence

The example-inheritance wording and passage-ID inventory are integrated through
CUE and the existing resolver. The
[deterministic check](../../examples/document_understanding/refused-evidence-check/README.md)
resolves the original four refusals with reviewed source selections, leaving
meanings unchanged. The fresh comparison above supports this evidence-selection
change; neither check proves those meanings complete. Remaining priorities are:

1. Preserve applicability when separating dependent details such as deadlines.
   The [grouping comparison](../../examples/document_understanding/deadline-grouping-experiment/README.md)
   produced one complete grouped result, but followed the grouping instruction
   in only one of two same-scope runs. Existing fields can express the result;
   the instruction is not adopted. Further work should check segmentation
   adherence separately from semantic completeness.
2. Preserve standalone qualifications and assess each meaning field separately.
   The completed [field-distinction test](../../examples/document_understanding/audit-field-distinction/README.md)
   compared original wording, complete logic only, and a complete statement. The
   auditor missed the original defect twice despite citing its governing source;
   neither logic-only run met the strong field-distinction criterion. Complete
   statements passed both times. This remains a known failure, not a pending test.
3. Check modal classification and duty bearers. Existing fields distinguish
   recommendation, permission, exemption and descriptive possibility, but the
   prototype mislabeled an exemption as permission and a later output used
   ambiguous exemption-actor wording.

Do not discard meaning retained in `logic_text` or claim that an incomplete short
statement is independently complete. These remaining failures do not negate the
narrow improvements measured in the example experiments.

Explicit exception targets belong to optional refinement and remain imperfect.
There is no general duplicate detector, complete entity model, automatic
cross-document concept resolution or executable rule engine. Human accuracy,
correction effort and time savings have not been measured. Source reviews are
agent-authored and revisable; saved legal excerpts are not current legal guidance.

| Evidence | What it explains |
|---|---|
| [Final low → medium run](../../examples/document_understanding/low-extract-medium-audit/README.md) | Earlier end-to-end result, raw review and unresolved issues |
| [Medium audit comparison](../../examples/document_understanding/medium-audit-experiment/README.md) | Thinking-level savings on three isolated cases |
| [Alternative evidence](../../examples/document_understanding/alternative-evidence-experiment/README.md) | Shared passages, omitted options and signature qualifications |
| [Meaning-first adoption](../../examples/document_understanding/meaning-first-adoption/README.md) | Normal extraction and discovery export |
| [Low extraction](../../examples/document_understanding/low-thinking-experiment/README.md) | Four low-thinking runs and quality variation |
| [Context and budget](../../examples/document_understanding/context-budget-experiment/README.md) | Window/list handling and remaining omissions |
| [Schema reuse](../../examples/document_understanding/schema-reuse-finish/README.md) | Core reuse and evidence-backed structured components |
| [Passport example](../../examples/document_understanding/manual-slice/README.md) | Earlier saved manual extraction and review interface |

Historical reports retain the recommendations and limitations measured at their
own snapshots. Use this guide and the
[current handoff](../../thoughts/reviews/2026-09-09-extraction-handoff.md) for the
integrated state.


Qualification edits use immutable claim IDs in `applies_to`. Two rules can share
a quotation; selecting one must not select the other. Editing a target creates a
new revision and requires confirming any affected qualification links. Within a
single add action, `new:0` can refer to the first earlier addition in that action;
the saved record contains the resulting immutable claim ID. Future or unavailable
targets remain unresolved.

Provider output tokens and local storage measure different things. `usage`
counts each retained request/response once, excludes copied base runs, and reports
missing usage as unknown. It also reports local JSON bytes, including local copies;
those copies do not imply additional model output or charges. Recorded provider
usage is not a billing invoice.


The [fresh-source reference comparison](../../examples/document_understanding/consistency-transfer/README.md)
keeps paragraph references as the production default. Sentence references reduced
location ambiguity but introduced standalone-condition regressions and higher
output cost. The consistency update adds persistent term identity, claim-ID
qualification targets, reviewable enrichment findings, actual AI request provenance,
and sparse discovery output. It improves data continuity and review; it does not
establish a new extraction-accuracy rate. The [implementation checklist](../../thoughts/plans/2026-09-10-extraction-consistency.md)
records verification and the remaining limits.

## Historical optional-reader installation checkpoint

The following recipe is retained from the earlier guide; its wheel paths describe
that checkpoint and must not be used to downgrade a newer installation.

SpicySearch and RefSpec are optional application dependencies (`references` extra),
never Core validation dependencies. Install the verified local wheels explicitly;
their versions alone do not distinguish them from older local builds:

```sh
uv pip install --python .tools/document-poc-venv/bin/python \
  --constraint thoughts/experiments/2026-09-11-uslm-source-links/dependency-constraints.txt \
  dist/production-20260910/rulespec_artifacts-1.0.11-py3-none-any.whl \
  dist/reference-integration-20260911-uslm-text/rulespec_conformance-0.2.0rc18-py3-none-any.whl \
  dist/citation-ownership-20260911/rulespec_projection-0.1.0-py3-none-any.whl \
  dist/reference-tools-20260910-parenthetical/spicysearch-0.1.4-py3-none-any.whl \
  dist/reference-integration-20260911-reverse-title/refspec-0.1.0.dev0-py3-none-any.whl \
  dist/reference-feedback-20260911-source-issues/rulespec_extrapolator-0.1.0.dev0-py3-none-any.whl \
  ../DocSpec/dist/docspec-0.2.11-py3-none-any.whl
```

Use the Python environment where you installed the extractor. The scan records
each parser's version and module digest. The recorded
[wheel inputs](../../thoughts/experiments/2026-09-11-reference-feedback/wheel-inputs.json)
pin the matching builds, including reference feedback, optional supplied-source lookup, complete CFR compounds/ranges, the part-zero
minter fix, compilation locators and the RIN, containment
and retention changes; the
[act-name comparison](../../thoughts/experiments/2026-09-11-act-name-multiplicity/README.md)
retains an earlier checkpoint. The full installation includes DocSpec because of
SpicySearch's existing dependency metadata; document segmentation and Core
validation do not call DocSpec.
