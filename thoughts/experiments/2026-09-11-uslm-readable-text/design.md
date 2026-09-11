# USLM readable text with exact publisher locations

Decision: Can a small source-preparation function, using the shared RefSpec USLM
reader and existing Rulespec source maps, replace the diagnostic flattened text
and support publisher-link navigation in the application?

Hypothesis: Missing boundaries between XML block elements cause joined headings,
list items and table cells. Inserting only declared layout separators should make
those boundaries readable without changing source characters, inline wording,
publisher references or target identity. If it corrupts inline text, loses
occurrences, guesses ancestry or cannot map evidence, it fails this hypothesis.

Arms: A is the frozen `uslm-source-links` decoded `itertext()` probe. B adds
boundaries from USLM's block/heading/table structure while preserving decoded
source text and exact XML occurrence locations. This tests source preparation,
not a new model prompt, reference grammar or general semantic segmenter.

Cases: Retain the two original source captures, including the CDC heading/body
join and Inspector General table. Select the first small source section in the
verified title 5 member whose operative reference has a small target in that
member; capture both exact sections. Select before producing B's output. Add
constructed controls for inline punctuation/Unicode/entities, repeated equal
mentions, empty references, duplicate identifiers, adjacent headings, table cells,
footnotes and separators crossing an evidence request. Record uncertain layout
readings instead of forcing them into exact expected prose.

Held constant: Pinned source bytes and existing native reader, one deterministic
run per arm, no model calls, no source corpus rebuild. Use Python's XML parser and
existing source/evidence helpers. Inspect sibling readers and the publisher's
schema/stylesheet before adding formatting rules. Preserve all original captures.

Decision rule: Adopt a bounded preparation/application change only if all source
characters remain recoverable in order, declared block boundaries are readable,
inline reference text is unchanged, every emitted source XPath and available
target still resolves exactly, and existing evidence/discovery checks pass.
Inserted text must never become original-source evidence. Application integration
also requires source/wheel parity and installed command checks. A successful
formatter alone does not complete publisher-link ingestion or demonstrate a gain
in extraction meaning. Report any unsupported layout explicitly.

Stop bound: These three source cases and the declared constructed controls, then
record adopt/defer and the remaining failures. Use newly selected documents for
any later model-quality comparison. The broader reuse objective remains active.

First result and revision: the initial B preserves all 107 reference occurrences
and source characters, but `(b) FunctionsThe Secretary…` still joins an inline
heading to a chapeau. The readability gate therefore failed. The original output
and implementation are retained. B2 adds a generic whitespace boundary after a
heading when no source whitespace separates it from the next text. Block boundaries
still take precedence. This is an explicit text-preparation rule beyond copying
the stylesheet's display values; the original acceptance criteria remain unchanged.
