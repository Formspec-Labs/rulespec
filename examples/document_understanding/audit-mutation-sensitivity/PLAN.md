# Audit sensitivity beyond the notice case

Decision: Does the existing audit detect explicit semantic corruption more
reliably than the notice context-inheritance defect? This measures sensitivity
on selected saved sources, not an extraction improvement or general error rate.

Hypothesis: with full original source evidence retained, the audit will identify
four planted changes in normalized meaning and avoid finding those same defects
in the original corresponding records. If exact original quotes mask corrupted
meaning, or correct controls are rejected for the planted defect, the hypothesis
is weakened. Different defect types/documents are prioritized over repeatability.

Cases: complete saved 8 FAM 801.2-1 introduction (16 draft records, 15 substantive
inventory units) and complete saved Ohio 3745-52-15 (14 records, 21 units).
The original drafts/inventories are fallible model outputs. Passport still has
the previously known C0005 standalone qualification issue; do not call the entire
control document flawless. Use only the corresponding target records as correct
controls and inspect other audit findings separately.

Arms: original comparison draft A versus constructed corrupted draft B. Two
distinct records change per document, so this is a multi-error sensitivity bundle,
not a causal isolation of one mutation. All other model-facing fields stay fixed.
- Passport C0004 actor: replace the subject passport agencies/centers with posts
  in summary and the corresponding scope phrase. Preserve approval wording and
  exact source evidence, which applies this restriction to agencies/centers.
- Passport C0013 negation: replace the IN no-response exemption with a duty to
  respond, changing summary/kind/modality consistently. Preserve source quotation
  and modality evidence, which still state no response is required.
- Waste C0008 alternatives: replace both label components (words AND hazard
  indication) with either component in summary and choice_text. Preserve the
  complete original source logic and examples.
- Waste C0009 deadline: change both three-consecutive-calendar-day alternatives
  to thirty consecutive calendar days in summary and choice_text. Keep the trigger,
  all destinations and original source logic unchanged.

Store unmodified fixtures and explicit mutation diffs. Diagnostic draft views are
not rewritten Core graphs or provider extractions. Give changed targets separate
experimental identities without exposing arm names to the model. No new Core
Findings, approval records, production schema or prompt changes.

Held constant: current audit comparison prompt/schema/input generation/capture/
parser/accounting, gemini-3.8-flash, temperature 0, medium thinking, no numeric
thinking budget or application output cap. Full source and inventory per call;
one repeat per case/arm, four calls maximum. Randomize order before calls. Existing
five-minute request timeout, no retry, extraction, inventory, repair or tuning.
Saved sources are development data; mutations are constructed, not real failures
or independent gold labels. Earlier notice failures remain the historical contrast.

Primary criteria: for each planted defect, a relevant error verdict with a rationale
identifying the actual changed actor, reversed exemption, AND/OR mismatch or wrong
deadline. Track summary verdict separately; do not force an error on an empty
structured actor/threshold field if summary or other relevant dimensions already
identify the problem. Mere generic error without the planted reason is insufficient.
Corresponding original targets must not be falsely accused of the planted error.
Review additional errors and unchanged passport IN-change restrictions and waste
closed-container exceptions for false propagation from neighboring corrupted rows.

Decision: bounded sensitivity support only if all four planted defects are correctly
identified, all four original target controls pass the corresponding checks, and
no source-incorrect propagated findings are observed in the named unchanged controls.
Count detection, specificity, other findings, mechanical validity and cost separately.
Partial success is not reliable automatic approval. This cannot resolve the known
notice defect or prove causal mechanisms. No production adoption under this test.

Freeze actual requests and all raw/derived results. Mask/randomize output labels
for initial self-review, then unmask against exact mutations; note that rationales
may reveal mutations and the reviewer designed the cases. Verify complete manifests,
exact judgment spans and replay through the existing parser/accounting without
provider calls. Stop after four calls, preserve every failure, and consolidate the
decision with the preceding experiments rather than patching prompts again.
