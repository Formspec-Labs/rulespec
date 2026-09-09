# Proposed experiment: reliable source inventory at medium thinking

Status: executed with user authorization. Six calls completed; the semantic gate failed, so the conditional full audit was not run. The prototype was preserved and production restored. See [results](../reviews/2026-09-09-audit-grounding-experiment.md).

Decision to test: can the audit retain useful source meanings more reliably by
selecting existing source passage IDs instead of reproducing quotation text and
section markers? The final full-section audit refused four substantive inventory
entries because their scope references were absent or ambiguous. Fix this before
adding more reasoning or automatic repair.

## Scope and reuse

Keep saved extraction drafts unchanged. Change only inventory evidence selection;
keep comparison instructions, meaning requirements, model, medium thinking and
temperature zero fixed. Continue to omit a numeric thinking budget and application
output cap. No retries.

First map the change to callable code and generated schemas. Reuse the CUE
#SourceRef definition, extraction.passage_catalog, extraction.resolve_passage,
and existing audit inventory records and evidence validation. Select exact source
passages and deterministically populate the existing quote/source-span records.
Use a small CUE-generated inventory view if needed; do not create competing Python
field definitions or change Core. A valid passage location does not establish
that its text governs the rule.

## Cases and calls

Prepare three source excerpts with complete governing context:
1. Employer proof burden and teacher wording: the absent combined (c)(3) marker.
2. Eligibility timing and non-FMLA transition: the repeated/ambiguous (d) marker.
3. Break-in-service list: both USERRA and written-rehire alternatives, their
   thresholds and inherited conditions, as a positive preservation control.

List expected source meanings and governing passages before calls. These are
revisable source-reviewed expectations, not unquestionable gold labels.

Run current quotation-based and proposed passage-ID inventory on each excerpt:
six medium-thinking calls, one per cell. Keep full requests, responses, invalid
selections, normalized inventory and runtime fingerprints. Compare raw meanings
and their source support, not just accepted record counts.

Only if the narrow checks pass, run the proposed inventory and unchanged
comparison on the final saved full leave draft: two more medium calls. Do not
re-extract or apply repairs. Total budget: at most eight calls. Saved prior audit
is a historical reference, not a contemporaneous whole-document control.

## Pass criteria

- All targeted substantive meanings survive valid evidence resolution.
- Governing passages contain real conditions, not merely unique section labels.
- Both service/rehire options, seven-year thresholds and their qualifications
  remain faithful; passage granularity causes no new false omissions.
- Invalid IDs, out-of-focus main references and ranges across unsupplied text are
  refused and preserved. Existing evidence tests should be reused and extended
  only where the new audit connection creates a new failure mode.
- Full-section source review finds no lost principal meanings compared with the
  saved draft/source checklist. Processing and review completeness remain distinct
  from semantic completeness.
- Record token volume, request time, raw refusals and false findings; do not equate
  a better coverage fraction with improved extraction accuracy.

The full-section run must also report whether the known accounting-scope weakness
is still missed. Fixing that is a separate experiment, not part of this change.

## Task list

1. Freeze fixtures, source-reviewed expectations, control settings and runtime.
2. Map/reuse the existing schema and passage functions; build the smallest audit
   evidence-selection change and deterministic conversion.
3. Verify generation, evidence refusal behavior and unchanged downstream records.
4. Run the six paired inventory calls and review their raw outputs.
5. If they pass, run the two-call full audit and compare against the saved checklist.
6. Replay, record results and make an explicit adopt/revise/reject decision. Preserve
   original captures and do not change defaults from one small experiment.

Next experiment, separately: distinguish a condition retained in summary/scope,
retained only in logic_text, and missing from every meaning field. Correct the
adjacent-duty fixture first. Reuse the comparison schema and test both false
alarms and missed defects without combining this with the inventory change.
