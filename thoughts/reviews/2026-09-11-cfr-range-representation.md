# CFR compounds and ranges: smallest complete representation

Recommend one small range type holding two existing `CfrCitation` values, plus the existing occurrence evidence. A compound part is one citation; a range is a pair of citations. Do not encode both meanings in `cfr_part` or decide them from a plural label alone.

This is a design assessment from saved source and current code, not an implemented or tested change.

## Evidence that decides the design

I read the surrounding publisher XML retained in `source-cases.json`, the original-variant outputs in `source-results.json`, all control readings in `controls.json`, and relevant complete records in `xml-part-structure.json` under `thoughts/experiments/2026-09-11-cfr-whole-tokens/`.

- The records/forms paragraph explicitly says `41 CFR parts 102-193 and 102-194`. XML separately names `PART 102-193—CREATION, MAINTENANCE, AND USE OF RECORDS` and `PART 102-194—STANDARD AND OPTIONAL FORMS MANAGEMENT PROGRAM`. The plural introduces two compound names, not a range inside each name. The probe captures both but incorrectly flags both implausible: `_part_is_plausible` counts all digits across the hyphen.
- The building-accessibility paragraph applies standards established in `41 CFR 101-19.600 to 101-19.607`. The probe captures only `.600`; the explicitly written end disappears. The authority paragraph under EPA part 6 similarly states `40 CFR parts 1500 through 1508`; the probe emits a mintable part 1500 alone. Whole-token matching fixes only the first half of this problem.
- XML names `50-1 - 50-200` as a `PART` node whose heading is `PARTS 50-1—50-200 [RESERVED]`. The structural node is a range grouping, not one part. Conversely, `PART 102—GENERAL [RESERVED]` is a singular part with no sections. Neither `TYPE=PART` nor a positive section count is a sufficient identity rule. Reserved status, edition presence, lexical identity and applicability answer different questions.

## Compare the simple choices

| Choice | Assessment |
|---|---|
| Full token string plus a label | Smallest patch, incomplete: loses `to`/`through` endings and leaves downstream code guessing whether a hyphen names a part. |
| Add `cfr_part_end` and `cfr_section_end` to `CfrCitation` | Reuses USC's flat endpoint convention and is workable, but existing consumers silently continue reading only the start. Every field-copying path must gain a guard. |
| `CfrCitationRange(start: CfrCitation, end: CfrCitation)` | Recommended. Two fields reuse existing endpoint coordinates and verdicts, support cross-part ranges, and make treating the whole range as a single `cfr_part` fail visibly. No general citation tree is needed. |

Let `CfrCitationOccurrence.citation` accept a single citation or this range. Keep its existing `text`, offsets, context and start `pinpoint`; add `range_end_pinpoint`, following `UscCitationOccurrence`. Reuse the USC occurrence's `refusal` convention for unread/ambiguous tails. Do not overload the existing `qualifier_status`, which describes part/subpart pairing.

A stated range's source slice must cover both endpoints and their labels. Its endpoints are coordinates, not an enumerated membership claim. Reject a same-part-only representation: `40 CFR §§ 60.1 through 61.2` needs both part numbers. Mixed units, incomplete ends and ambiguous hyphen chains remain observable refusals rather than complete start-only candidates.

## Parsing and consumer changes belong together

Use one anchored item reader for the first citation and every list continuation: complete coordinate, attached pinpoint, optional explicit range tail and end pinpoint. Then advance to the next list connector. Preserve the existing plural-label/structured-field policy, other-citation stop guard and paragraph boundaries. A list may contain both single items and ranges.

Use `to`/`through` as explicit range evidence. Recognize title 41's supported one-hyphen compound shape using the documented publisher evidence; do not apply a global rule that every hyphen means a range or every title-41 chain means one part. Unspaced ambiguous forms such as `41 CFR 60-1-60-2` should remain unresolved. Do not invent missing endpoint prefixes or expand interiors. Evaluate plausibility per supported component, preserving the five-digit numeric-part control; do not call total digit count legal existence.

The current code has three field-copying consumers that would otherwise drop range meaning: `parse_authority_citation`, `unified_agenda_parquet`'s CFR-reference rows, and `term_explanation._explain_cfr_part`. They must preserve the range or explicitly report unsupported scope; none should query/mint/explain its first endpoint as the entire reference. Do not enable range production while those paths still assume one part.

Rulespec already stores native readings, source evidence, inherited context and refusals in `references.py`. Reuse those. Store the range's native endpoints and use `match.text` as its displayed value, as the USC path already does. No new Core class or identifier scheme is required. Rulespec's `rkaf:us-cfr` profile already admits a compound part; it describes one coordinate and must not be widened to encode ranges. A range has no single regulatory identifier. Endpoint identifiers, if later exposed, must be explicitly labeled as endpoints, never a complete set of affected provisions.

## Counterexamples that must survive

- Real plural compounds: `41 CFR parts 102-193 and 102-194`; `300-3, 301-10, and 301-70`.
- Explicit ranges: the two saved source ranges; `41 CFR parts 50-1 through 50-200`.
- Synthetic cross-part/mixed controls: `40 CFR §§ 60.1(a) through 61.2(b), and 63.3(c)`; `41 CFR parts 60-1, 60-3 through 60-4, and 102-193`.
- Parentheticals: preserve endpoint `(a)`/`(b)` separately; retain a following qualification in evidence without treating it as an endpoint or pairing it with every list member. Preserve existing ambiguous part/subpart refusals.
- Unknown/damaged: `17 CFR 15c3-3`, `41 CFR 60-1-60-2`, `40 CFR parts 60 through`, or `60 through unknown`. No numeric-prefix rescue and no complete head-only result.
- Adjacent prose: `40 CFR part 37, 12 people attended`; `41 CFR part 102-117, 15 USC 78c`. Neither number becomes an inherited CFR member.
- Controls: part 0, `5 CFR part 10001`, `7 CFR 15a`, historical title 35, impossible title 1345, and the title-3 compilation locator.

Acceptance should compare retained endpoints, full source coverage and absence of a whole-range IRI. A formatting-only mutation must not change meaning. Keep the old reader as a test-only oracle with named divergences, as RefSpec requires. Walk each item once; do not add range enumeration or catalog lookups per match. Existing overlap scans may already be quadratic in citation count, so this change should not add another all-pairs pass.
