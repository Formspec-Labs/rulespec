# Upstream act occurrence change

The first observation loaded both real indexes and found three usable mappings
among eight selected publication fields. It also showed a duplicated mention
collapsed, `(d)` omitted, and an unrelated next-sentence `division B` attached.
Two published crop-insurance fields lack the recognizer's required `of`/comma
connector. These are input/representation gaps, not an index-availability problem.

Decision: expose exact, repeated act occurrences in RefSpec, reuse the same
matcher for the identity-only API, retain attached labels, and restrict division
context to the actual citation. Admit the two observed directly adjacent known
act-name forms; unknown names remain unknown.

Arms: frozen pre-change matcher versus the shared occurrence-based matcher.
Use the saved eight publication fields and diagnostics, plus whitespace, Unicode,
wrong-name and adjacent-sentence mutations. Preserve old identity results except
the explicitly declared adjacent-name additions and removal of borrowed division
context. Keep the old implementation as a test-only oracle. Do not change index
resolution policy or infer USC subsection correspondence from an act pinpoint.

Gate: each repeated mention has a separate exact source span; labels survive;
unrelated division text is not adopted; named-act mappings and explicit unresolved
reasons remain available. Owner tests and the frozen real/mutated comparisons must
pass before rebuilding the owner wheel and connecting an application consumer.
Any unlisted legacy divergence requires investigation before adoption. This is
still a bounded improvement; ranges and all act-name spellings are not solved.

Validation extension, before packaging: checking document boundaries exposed
three more instances of the same neighbor-context problem: `Clean Air Act.
Section 111`, a blank paragraph between the name and section, and the reversed
blank-paragraph form. The failing checks are retained in `sentence-boundary-red.log`.
The direct occurrence matcher now refuses those ungrounded associations while
preserving single-line wrapping. These deliberate legacy divergences are covered
by explicit negative controls. Short source qualifiers such as `(2025)` and
`(as amended)` still allow the indexed act to be read, but are not labeled as
subsection pinpoints. Original criteria and initial results remain above.
