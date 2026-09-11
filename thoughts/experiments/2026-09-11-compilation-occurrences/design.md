# Compilation citations in source extraction

Decision: Reuse SpicySearch's recognition of page-first Title 3 compilation
citations in RefSpec, and expose grounded compilation locators to Rulespec's
existing optional reference/discovery exports.

Hypothesis: RefSpec's year-first grammar explains the phantom CFR parts in
`3 CFR 127 (1981 Comp.)`. Supporting the second ordering in its existing grammar
should remove those false parts and retain the volume/page instead. Losing
ordinary Title 3 parts, source coordinates, ranges or neighboring references
would weaken the proposal.

Arms: Current RefSpec `53c0f387` and Rulespec `76e4fc1`; an extension of RefSpec's
existing compilation grammar and occurrence API; SpicySearch `10824d4` strict
source reader as an unchanged comparator, not a new dependency of RefSpec.

Cases: Read the original text and rendered citation context in the saved
68-opinion Supreme Court capture that produced SpicySearch's regression tests.
Retain all compilation occurrences found there, the existing RefSpec compilation
fixtures, and constructed controls for actual Title 3 parts, wrong titles,
unclosed parentheses, repetition, Unicode/line breaks, page/year ranges and
adjacent CFR/USC references. Cases chosen after reading are development data,
not an independent accuracy benchmark.

Held constant: No model calls; the same frozen text and deterministic settings.
Use copied old parsing checks as test oracles, with explicit divergences for
the newly recognized locators. Stop after the source comparison, upstream and
application correctness checks, then a rebuilt/installed-wheel check.

Decision rule: Adopt when complete source locators survive in the native output
and both application exports, phantom CFR parts disappear on the actual source
cases, controls retain their original meaning and neighbors, and the relevant
existing tests pass. Preserve written page/year endpoints rather than guessing
an executive-order identity. Any unsolved truncation or uncertainty must remain
explicit. This does not settle the separate compound-CFR-part/range migration.

XML source extension (user steering, before collecting XML outputs): prefer
publisher XML whenever it contains the needed source. Use the existing USLM
reader, not a parallel XML parser. The pinned title 18 archive contains two
year-first compilation mentions in section 798A, including an editorial note
that questions the printed proclamation number. Preserve both mentions, that
uncertainty, publisher links and exact source evidence. Add constructed XML
controls for page-first citations inside publisher links and citation-like
attribute values, which must not become visible-text references. These are
source-format checks, not evidence that an XML edition of the court opinions
exists. The visually observed PDF page/footnote interruption is a separate,
retained reading-order failure; the contiguous-text grammar cannot resolve it.
