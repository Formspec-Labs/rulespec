# Real source references: useful additions, one omission

The unchanged five-kind filter recovered 15 of 16 labeled reference occurrences in eight selected passages from two published Federal Register documents. It added no misleading candidates, preserved the current baseline output, and retained exact source spans. The historical Ohio noise control also remained clean.

**The registered gate failed:** it required every labeled occurrence to be recovered. This is bounded improvement with an unresolved syntax gap, not a passed production gate.

## Results by reference family

| Family | Expected | Correct | Missed |
| --- | ---: | ---: | ---: |
| Public law | 4 | 3 | 1 |
| Statutes at Large | 2 | 2 | 0 |
| Executive order | 6 | 6 | 0 |
| Docket | 2 | 2 | 0 |
| Regulatory Information Number (RIN) | 2 | 2 | 0 |
| Total | 16 | 15 | 1 |

All 15 emitted additions matched the predeclared kind, normalized value, and source span. There were zero unexpected additions, zero changed baseline results, and zero invalid spans across all nine cases. Exact replay matched. These are occurrence counts on selected passages, not an estimated general accuracy rate.

## The failure and its likely cause

The published [Congressional Review Act revocation document](https://www.govinfo.gov/content/pkg/FR-2026-01-02/html/2025-24202.htm) contains `Public Law (Pub. L.) 119-20`. The detector emitted no public-law candidate for that occurrence. In a later selected passage, it correctly recognized the same law when a line break separated `Public Law` from `119-20`.

This is an omission, not merely disagreement over how much evidence to quote. The installed SpicySearch `_PUBLIC_LAW` pattern accepts a law label, whitespace, an optional `No.`, and then the numeric identifier. It does not admit the parenthetical abbreviation between the spelled-out label and the number. Starting at the inner `Pub. L.` does not work either because the closing parenthesis intervenes. This code inspection explains the observed difference; no parser modification or diagnostic rerun was performed after the result.

Ordinary line wrapping succeeded for both `Public Law 119-20` and `Public Law 104-113`. More whitespace compensation is therefore not indicated by this failure. Stripping punctuation globally would change source coordinates and could join unrelated material; the smaller follow-up is an upstream grammar change for this explicit citation form, with negative controls for unrelated parentheticals and incomplete numbers.

## Scope and limitations

- Sources were selected before parser execution. The first block mentioning each family and its following block were selected using the written rule; overlapping selections were deduplicated. Expected identifiers and spans were then manually labeled before the run. Those labels remain revisable judgments, not independent gold labels.
- The inputs are real published text from two EPA documents, but only eight selected passage pairs were evaluated. Both documents' full downloaded text and HTML are saved. This does not measure full-document recall or agency diversity.
- The first executive-order mention in the second source is a table-of-contents heading with no numbered order. It was retained as a negative passage rather than replaced by a later positive example. All six positive executive-order occurrences come from the first document's contents listing.
- The Ohio source is an unchanged historical negative control. It is not fresh evidence, and its excluded false Federal Register candidates remain in the raw output.
- This is recognition of citation anchors. `et seq.`, section lists, governing effect, target existence, and legal version resolution are not represented by these added candidates. Source context remains available; no claim of complete citation meaning is made.
- The existing CFR/USC scan is the baseline unchanged from the previous experiment. These observations do not repair its known gaps or assess extraction semantics.

## Decision and next action

Do not broaden the filter or adopt the general query detector. Preserve the failed case and, in a separately authorized implementation step, address the parenthetical public-law form in SpicySearch's existing parser. Validate it against this source and counterexamples, then rerun the frozen broader, additive, and real-source cases. Direct-import verification should precede rebuilding the wheel and repeating the integration check. This follows the existing reuse approach without adding a Rulespec-specific grammar.

No production files were changed, no commits were made, and no model calls were made. Stop this experiment here; do not relabel or tune it into a passing result.

## Evidence and execution notes

- [Preregistered design](design.md), [manual fixture construction](freeze.py), and [frozen cases](cases.json)
- [Raw outputs](raw.json), [readable review](review.txt), [assessment](assessment.json), [summary](summary.json), and [replay](replay.json)
- [Runtime hashes](run.json), [runner reuse record](runner-reuse.json), and [verification](verification.json)
- Official source one: [2025-24202](https://www.govinfo.gov/content/pkg/FR-2026-01-02/html/2025-24202.htm)
- Official source two: [2024-07412](https://www.govinfo.gov/content/pkg/FR-2024-04-16/html/2024-07412.htm)

Both HTML downloads succeeded, but the initial conversion attempt failed because BeautifulSoup was not installed. The saved downloads were converted with the standard-library HTML parser instead, taking character data from the `pre` element without whitespace or punctuation repair. The original failure log is retained in `sources/retrieval.json`; conversion details and file hashes are in `sources/text-conversion.json`. No parser observations existed at that point. Source-relative passage spans permit exact reconstruction from the pinned text.

The prior runner's scan and assessment functions were reused unchanged. Only case-group reporting and the all-five-families gate were adjusted before execution. There were no model settings or provider costs. Execution timestamps are recorded for provenance, not a latency benchmark.
