# Can context improve the existing audit without leading questions?

Decision: whether to connect assembled context to the optional audit comparison
stage. The prior fixed-question experiment helped selected answers but failed
promotion; its failure remains unchanged. The evidence export is committed as
`6942225`. No automatic meaning changes are part of this comparison.

Hypothesis: supplying enclosing source context to the existing claim assessment
will uncover missing conditions or mistaken scope without a question naming the
defect. Alternatives: the ordinary extraction already retains the meaning; the
existing audit already sees sufficient evidence; or additional text causes false
inheritance/unsupported additions. Record context availability separately from
whether the auditor uses it correctly.

Fresh inputs: complete 2025 annual CFR sections 40 CFR 262.11 (hazardous-waste
determination) and 14 CFR 91.213 (inoperative equipment). No prior appearances were
found in saved experiment/example text or manifests outside this directory.
These are selected new sections, not an independent benchmark or current-law
advice. Generate one untouched low-thinking extraction per section, then freeze
both drafts. Assess the first existing 3,000-character audit window per source;
this is a bounded comparison-stage check, not an end-to-end whole-document audit.

Controls: the original saved seatbelt labeling claim; the exact prior model
answer that added an adulthood condition, represented as a constructed claim for
this check; and a constructed faithful companion-condition statement. Preserve
the original source and captured wording. The adulthood and faithful cases share
the same source selection and source-only inventory. Score every focus claim,
including correct ones, not only anticipated defects.

Arms: A uses the existing audit's source selection; B uses `export_context` for
that same window. Both use the same fixed claims, source-only inventory, current
comparison prompt and judgment fields/dimensions. No scenario questions or
case-specific hints enter either request. Inventory is generated once from A's
focus source and shared, isolating additional comparison evidence. This does not
test enriching source-first inventory or automatic discovery of entirely absent
rules outside that inventory.

The experimental adapter gives both arms source-qualified references
(`S0/F003:F006`) and supplies identical full draft/inventory data through existing
`_comparison_input`/`_model_input`. It does not use the ordinary request's quote
compaction because the two source catalogs have different local passage IDs.
Thus A is the existing comparison semantics and source selection with a common
experimental encoding, not a byte-identical invocation of the CLI audit. The
response reuses the existing comparison schema, changing only source-reference
guidance. Resolve every reference through the supplying source's existing
resolver and exact original-text support. Keep provider, schema, completeness,
mapping and reciprocal-link failures visible; never repair model output silently.

Source preparation: dated eCFR API calls returned HTTP 406; GovInfo text/HTML
URLs returned error pages and are not inputs. GovInfo annual XML was retrieved
successfully but is outside the current native reader's supported format.
Reuse the already installed DocSpec visible-text reader for acquisition only,
retaining original XML and its block/byte-map outputs. Rulespec consumes the
frozen text through its existing document preparation; no DocSpec dependency or
new XML parser enters production. Compare visible text against every original
section paragraph, allowing only whitespace changes. The 21 CFR 50.23 candidate
was not selected: its 13,527-character rendition exceeds the exporter's short
section limit, so it would not exercise the proposed expansion. This selection
occurred before extraction or audit calls.

Held constant: Gemini `gemini-3.8-flash`, temperature 0, one candidate, output
allowance 32,768; extraction low thinking, inventory/comparison medium thinking,
no thinking budget. One observation per arm, alternating AB/BA order. At most
16 calls: two extractions, four shared inventories, ten comparisons. No retries,
no tuning after the first comparison. Abort dependent comparisons if an inventory
fails; retain the failure and unused budget. Freeze exact inputs and prompts as
each dependency becomes available before downstream calls. Bound provider work
to 30 minutes; no automatic continuation beyond those calls.

Before audit calls: inspect and label both frozen raw drafts against full source.
Labels remain outside requests. Record per-claim missing/incorrect meaning and
uncertainty; do not manufacture a defect if fresh extraction is already correct.
Source judgments are revisable, not gold. After calls, randomize anonymous output
order and hide arm labels for manual assessment, then save judgments before
revealing the arm key.

Measures: supported additional defect findings, correctly retained meanings,
missed defects, false alarms, invented actors/ages/scope/conditions, source and
response validity, and actual recorded usage. Count fresh-source results apart
from constructed/development controls. A finding must identify the specific
source-supported defect; a generic warning, extra quotation, or schema pass is
not a gain. Existing optional fields need not be filled when meaning is already
preserved in the statement.

Decision rule: consider optional audit integration only with at least one useful
additional finding on a fresh source, no new critical unsupported finding or
meaning regression, grounded usable results, and successful detection of the
saved adulthood error without demanding it in the faithful control. Otherwise
defer. If no fresh defect has missing support in A, the experiment is unresolved
for context benefit rather than a failed extraction. Report cost as a tradeoff
for this new comparison; do not reuse or retrospectively change the prior 2×
gate. Any adoption still requires a separate production change and validation.
