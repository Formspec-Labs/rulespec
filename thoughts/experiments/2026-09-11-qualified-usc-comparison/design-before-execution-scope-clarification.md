# Qualified U.S. Code references: next integration decision

Decision: Choose which existing reader should own qualified USC meaning and what
must change before Rulespec exposes its readings through the reference adapter.

Hypotheses: SpicySearch's current strict prose reader preserves ordinary section
tokens and original positions but loses qualifications that its output cannot
represent. RefSpec's authority reader preserves more qualified meaning but uses
whole-field interpretation, which can accept damaged tokens or surrounding number
lists. Both may be true. This comparison separates recognition, qualification,
and source positions; it does not test legal existence or applicability.

Arms: Current direct imports of SpicySearch `extract_usc_citations(strict=True,
keep_rejected=True)` and RefSpec `parse_authority_citation`. Keep every native
field, partial/refusal result, and exception. Run each once and replay once.
Use existing `find_cfr_citations` only for the historical-title null control.

Cases: At most 32. Reuse the saved compound, ordinary-prose, chapter, appendix,
note and fused-word cases verbatim. Add constructed attached subsections,
stated/abbreviated/reversed ranges, repeated references, Unicode whitespace/dashes,
unrelated prose numbers and impossible-title controls. Add three first-matching
publisher paragraphs from pinned eCFR title 5, selected by note/chapter/subsection
spelling before either parser runs. Read the original surrounding section and
freeze exact paragraph text plus source identity before labeling. If a category
has no match, record absence rather than quietly changing its selection rule.
Labels describe written targets, not their existence in a current edition.

Held constant: Exact inputs and labels, checkout source hashes, interpreter and
dependencies. No provider calls, model changes, prompt changes or parser edits.
Stop after the frozen cases and one replay, or 25 minutes of active work. Record
host load; make no performance comparison. Serialize reader execution under the
SpicySearch measurement lock when the one-minute load is below 4.

Decision rule: Connect an existing path only if it preserves the complete written
target, exact original occurrence positions, repeated occurrences, range endpoints
and interpretation basis, and refuses damaged continuations without regressing
ordinary prose references. A whole-input `partial` alone is neither a refusal nor
evidence of a malformed token. If neither path passes, name the smallest owning
API extension and retain current production behavior. Improvements in individual
dimensions do not turn the combined gate into a pass. Keep this a diagnostic
comparison; do not claim a general accuracy rate from selected development cases.
