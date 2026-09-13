# Raw review before opening the arm key

All three source texts, original selected records, eight generation payloads,
decoder results, previews and five checker responses were read before consulting
`arm-key.json`. Response wording sometimes reveals the requested task; these are
anonymous, revisable agent assessments, not independent blinded human labels.
The original criteria remain in PLAN.md and BASELINE-REVIEW.md.

“Complete” below means the selected default statement incorporates the specified
governing meaning. It does not certify every optional component or every possible
legal inference. Each pension repetition counts separately as an opportunity,
not as another independent source. A missing proposal leaves the original gap.

| Cell | Selected positive outcomes | Raw proposals | Decoded / preview-valid | Checker supported | Complete default readings generated | Complete readings with valid preview and support |
|---|---|---:|---:|---:|---:|---:|
| 1 | Pension C0001 complete | 1 | 1 | 1 | 1 | 1 |
| 2 | Notice C0000 missed; C0001 missed; C0002 complete | 1 | 1 | 1 | 1 | 1 |
| 3 | Pension C0001 complete wording; optional quotation refused | 1 | 0 | 0 | 1 | 0 |
| 4 | Request C0000 missed; selected inspection control unnecessarily enriched | 2 | 2 | 2 | 0 | 0 |
| 5 | Pension C0001 missed; optional components enriched | 1 | 1 | 1 | 0 | 0 |
| 6 | Notice C0000 missed; C0001 incomplete with useful relationship; C0002 partial | 3 | 3 | 2 | 0 | 0 |
| 7 | Pension C0001 missed; empty answer | 0 | 0 | 0 | 0 | 0 |
| 8 | Request C0000 missed; inspection correctly left unchanged | 0 | 0 | 0 | 0 | 0 |

## Pension

Cells 1 and 3 incorporate both 2007 conditions, the year-end account measurement
and referenced account rule, single-employer scope, sponsor permission and the
until-zero duration. Cell 1 retains the old clause pointer but explains it in
full, which meets the declared criterion. Cell 3 removes the pointer and also
preserves the required meaning. Neither changes the separate prefunding rule or
the record containing the eligibility criteria.

Cell 3 fails decoding because its optional `logic_text` combines the two list
items without the intervening `(II)` marker. Its primary statement is a faithful
paraphrase, but `logic_text` is defined as evidence. Checking all populated
`core.evidence_expectations` against the source identifies only `logic_text` as
absent. This is not merely a whitespace mismatch. The unchanged decoder rejects
the whole proposal; no checker receives it. Do not quietly remove that field and
count the result as an accepted repair.

Cell 5 adds source-supported action/object and repeats the until-zero limit in
scope, but leaves the default statement's unexplained clause (ii) intact. The
checker supports that enrichment. Cell 7 produces nothing. These do not close
the named eligibility gap.

## New notice source

Cell 2 repairs C0002 by explicitly naming the State attorney general's
determination that advance notice is infeasible, together with notice and a
complaint copy to the Commission at filing. It retains a subparagraph (A)
reference but expands the governing clause (i) condition specified in the label.
The default statement meets that bounded criterion. Its optional `scope_text`
still says “that subparagraph” without naming A, and its reference array does not
add the A citation newly appearing in the statement. Thus this is not a claim of
complete structured-field quality.

Cell 2 declines both other repairs. Its explanation treats C0000 as complete
because paragraph (1) is unavailable, overlooking the supplied exception and
surviving notice duty. C0001 is called independently complete while still naming
only subparagraph (A) and omitting the remaining notification duty. Both no-ops
fail the declared independent-use criterion. The original isolated quotations
remain source-faithful; the problem is their usability without surrounding rules.

Cell 6 enriches C0000 without its exception. C0001 gains an explicit exception
link to C0000 and paraphrases the infeasibility test, but still does not expand
the waived duty and surviving notification. Its action is “provide the notice
described in that subparagraph before the filing of the action”; its object is
“Subparagraph (A)”. That action/object pair is misleading.

The checker rejects C0001 partly for that real component problem and partly for
an “extraneous internal URN” in `applies_to`. The latter explanation is wrong:
the raw proposal selected `qualifies: ["C0000"]`; `_decode_proposals` inserted the
correct revision identifier deterministically; `_challenge_prompt` sent it in
the fields alongside the short aliases. An internal relationship identifier need
not appear in statutory text. This finding does not make the whole rejection
wrong, because the action/object criticism still stands.

Cell 6's C0002 says advance notice “was determined not feasible under clause (i)”
and preserves the correct at-filing duty, but no longer identifies who makes the
determination. Score partial against the explicit actor-preservation criterion.
A reader might infer the attorney general as determiner; that is a label
uncertainty. A more permissive label would give this cell one complete reading,
without changing either arm's failed overall gate. The checker supports it while
overlooking that missing explicit actor.

No notice proposal invents permission for later notice, transfers the duty to a
different actor or makes compliance with the surviving duty a new prerequisite
for the exemption. The old incomplete statement still does not represent those
relationships independently. Those two findings should not be conflated.

## Constructed request and inspection

Cell 4 adds optional fields without changing either default statement. Neither
adds the applicant name/reference-number requirement to the request reading.
Its request object, “a request electronically,” also places an adverb in the
object. The checker approves both enrichments, demonstrating that checker support
is not evidence that the intended completeness gap was repaired.

Cell 8 says the request permission is already independently complete and has no
dependence on another provision. The request-content provision applies to an
electronic request under that very clause. This no-op fails the declared product
criterion. There remains a record-boundary choice: an isolated permission can be
faithful while leaving requirements in another record. We are measuring the
explicitly requested independently usable reading, not declaring the original
source quotation false.

Cell 8 correctly leaves inspection unchanged. Cell 4 redundantly enriches it but
preserves its meaning and opening-hours condition. Neither transfers agency
reporting duties to applicants, turns reporting into permission to act, or
imports request-content requirements into inspection. No raw proposal adds a
record or edits an unselected statement. Previews are independent, not a combined
sequential application, and originals are not mutated.

## General distinction

Nine raw proposals become eight mechanically valid proposals, all with valid
individual previews; seven are checker-supported. Only three raw default
readings meet the predeclared meaning criteria, and only two of those also pass
decoding, preview and checking. One more reading makes partial progress. Optional
field population repeatedly produces supported edits without closing the target
gap. Empty optional fields are not automatically extraction defects, despite
some checker rationales calling them missing defects.
