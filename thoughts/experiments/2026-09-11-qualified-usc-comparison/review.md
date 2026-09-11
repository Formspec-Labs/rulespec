# Manual review of every native output

Decision: neither API passes the complete integration gate unchanged. Extend the
existing RefSpec matcher for occurrences and qualified targets. Keep SpicySearch's
query defaults and current production extraction unchanged until that extension
passes its own controls. This is a diagnostic result, not a general accuracy rate.

Both APIs were called on the same 29 frozen strings. All native fields, empty
results and refusals are saved in `attempt-02/raw.json`; the replay is identical.
The following judgments compare those raw outputs with the frozen written-target
labels. They are manual and revisable. “Read” means lexical interpretation, not
proof of a provision's existence or applicability. Every RefSpec authority result
lacks occurrence positions, so that shared limitation is not repeated in each row.

| Case | SpicySearch strict output | RefSpec authority output |
| --- | --- | --- |
| case-05 | Complete compound `1395w-4`, with original span | Same compound |
| case-06 | Complete `5 USC 552` inside prose | Same target; `partial` correctly describes surrounding prose |
| case-07 | No chapter reading | Chapter 5 retained |
| case-08 | No appendix reading | Appendix section 3 retained |
| case-09 | Drops `note` | Note flag retained |
| case-23 | Drops listed section 552a | Both sections retained, without their source/context positions |
| case-27 | No invented USC reading | `other/failed`, no invented USC reading |
| case-29 | No shortened accepted token | Reads damaged `1983affirmed` as section 1983 with `partial`; no token-specific refusal |
| publisher-subsection | Both base sections read; loses `(b)` | Both base sections read; loses `(b)` in this API's returned data |
| publisher-chapter | No reading | Chapter 81 retained, but `subchapter I` lost |
| publisher-note | Reads 403j and 402; loses comma-qualified note | Same USC loss; also correctly reads the separately stated public law |
| pinpoints | Drops `(a)(1)` | Drops `(a)(1)` in returned data |
| stated-range | Both stated endpoints and source spelling retained; no separate basis field | Both endpoints and `stated` basis retained |
| abbreviated-range | Keeps `1484-86` opaque | Reads 1484–1486 with explicit `abbreviated-span` basis; written spelling remains only in the supplied input |
| descending-pair | Keeps `553-552` opaque | Same opaque token; does not reverse it |
| unicode | Preserves original Unicode span; drops `(a)` | Correct normalized compound; drops `(a)` |
| repeat | Two distinct occurrences retained | Identical reading deduplicated to one |
| year | Reads section 552 without treating 2024 as a pinpoint | Same interpretation |
| chapter-range | No reading | Chapter endpoints 5 and 7 retained |
| compound-letter-tail | Complete `1395w-114a` retained | Same complete compound |
| appendix-note | No reading | Appendix retained, note lost |
| dotted-damage | No shortened section 1 | `other/failed`, no shortened section 1 |
| reserved-title | Explicit title refusal | Title 53 returned with `ok`; separate title validation is not part of this API |
| zero-title | Explicit title refusal | Title 0 returned with `ok`; same validation boundary |
| high-title | Explicit refusal, though its `fused-digit` reason overstates the cause | Title 55 returned with `ok`; same validation boundary |
| ordinary-numbers | No invented USC reading | `other/failed`, no invented USC reading |
| unrelated-list | Only section 552 | Incorrectly adds application counts 2020, 2021 and 2022 as USC sections |
| historical-cfr | No USC reading | Correctly types a CFR reference; existing CFR occurrence control admits historical title 35 |
| comma-note | Drops note | Drops note |

The three publisher paragraphs each lose a material qualifier in the returned
USC data: subsection, subchapter, or note. Their individual base references can
still be useful, but this experiment's complete-target criterion is not met.

## Why these results follow from the current code

RefSpec's whole-authority reader deliberately scans across intervening text for
USC list members. Its measured authority-field corpus contains real lists resumed
after other citations. That policy explains the false application-count members
in prose; replacing it globally with adjacency would regress its existing field
consumer. An occurrence reader must use adjacent list continuation while sharing
the same token grammar and preserving the field reader's distinct policy.

The existing note suffix matches whitespace plus `note`, but not `, note`, and
only the ordinary section branch uses it. The appendix branch therefore loses
the same meaning even when the suffix is spelled normally. Reuse one note-tail
reader across USC branches. RefSpec's `usc_title_is_possible` already supplies
the title-space check; `parse_status` is not that check and must not become one.

RefSpec's existing `usc_section_pinpoint` reads by normalized section identity
and returns no answer for competing pinpoints. It is useful to its existing
caller, but cannot recover an occurrence after deduplication or restore original
positions. The matcher must retain those positions when it first finds the text.

## Next implementation boundary

1. Reuse the existing authority matcher with a source-occurrence recorder, like
   the current CFR reader. Keep original text positions and repeated mentions;
   avoid whole-value label repairs in the prose occurrence path.
2. Keep `AuthorityCitation` for the existing qualified reading. Carry attached
   pinpoints, subchapter qualifications, exact written spelling and source context
   with the occurrence. Reuse its existing range endpoints and interpretation
   basis; never enumerate implied interior sections.
3. Share note qualification across ordinary and appendix forms; preserve comma
   notes. Record explicit title/token refusals separately from whole-input
   `partial`. Walk prose lists only through adjacent citation syntax, consuming
   pinpoints and notes before looking for the next member.
4. Preserve the current field-reader implementation as a test-only oracle before
   changing it. Pin intentional note-related differences; require parity elsewhere
   on real source and mutation cases. Then connect only the passing occurrence
   behavior to Rulespec's existing evidence and discovery adapter.

The broader gate remains failed until that follow-up is implemented and verified.
No parser or model behavior was changed by this comparison.
