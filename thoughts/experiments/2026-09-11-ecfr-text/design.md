# Reuse the publisher XML text path for eCFR

Decision: determine whether the existing RefSpec readable-XML machinery can
preserve eCFR section bodies with a small source-format extension, so the current
Rulespec reference-source consumer can use them. Do not add another independent
XML-to-text engine, catalog, service or model pass.

Observed gap: the currently inspected Spicy Regs section catalog is metadata-only;
RefSpec's eCFR subject-list inspector checks one specific part, not general body
text. The installed USLM reader refuses eCFR DIV XML. Local pinned title files
contain the needed bodies, including tables and effective-date/editorial notes.

Hypotheses: (A) raw Element.itertext is sufficient for navigation; (B) the shared
USLM source-map/boundary engine with an explicit eCFR profile preserves useful
boundaries that raw flattening loses; (C) this source requires a larger layout
solution, in which case keep original XML available and defer the new profile.

Arms: native raw decoded XML text versus a format-specific use of the existing
RefSpec readable-text engine. Existing USLM output must remain exactly unchanged
against a copied test-only baseline on real inputs and mutations.

Cases: three pinned actual sections from the previous body assessment (49 CFR
390.5, 49 CFR382.107,40 CFR82.158), original title context and source receipts;
paragraph/heading/table adjacency controls; empty cells, inline emphasis, mixed
case br, inserted/source whitespace, notes and malformed/wrong-format inputs.
Do not infer paragraph IDs from prose markers, flatten table cells into one
unseparated number, delete suspension notes, or infer a source edition from a
folder date. Preserve native structural selectors and original source text.

Held constant: original XML, source-map meaning, existing USLM contract, Core
schemas, default prompts, dependencies. No network/model calls or corpus rebuild.
Start with small selected sections; measure full-title memory/time before making
that the required application path. Any selected wrapper/context is declared,
with original bytes and title-file selectors retained separately.

Decision rule: continue to the existing optional consumer only if exact source
text and maps replay, paragraph/head/cell boundaries survive, no table values or
notes disappear, wrong-format controls refuse, and USLM behavior is unchanged.
A metadata-only or raw-XML-only result does not pass a readable-body gate. Preserve
failed cases and report layout limitations. Title/section identity and edition
selection need explicit source context; the text reader must not guess them.

Application scope declared before implementation: preserve existing USLM
snapshots and use the same preparation, replay, target/evidence and discovery
functions for eCFR. eCFR lookup initially addresses exact sections with native
TITLE ancestry in the supplied XML; a bare SECTION lacks its title and must
raise an explicit missing-context error rather than infer from a filename.
Preparing a bare section for ordinary extraction can still work. Pinpoints,
ranges, appendices and subparts remain unresolved rather than falling back to a
section. Same-number sections in different titles and conflicting editions are
counterexamples. A native part/section inconsistency must not select a target.
No API compatibility wrapper or duplicate source-map implementation is needed.

## Expanded sibling comparison before adoption

The user's added scope is SpicySearch, DocSpec and SpicyDocs. The candidate
RefSpec code remains uncommitted and uninstalled while these are checked.
DocSpec's visible-text reader and SpicyDocs' acquisition helpers have now been
probed separately; their original outputs and limitations remain in
`sibling-readers/`. This amendment precedes the SpicySearch direct-import probe,
not those earlier observations.

Compare SpicySearch's existing experimental HTML text helper, court markup
helper and Federal Register List of Subjects XML selector on the same three
frozen eCFR sections, plus paragraph adjacency, empty table cells, inline words,
line breaks and malformed markup. Record module identity and raw output. Check
paragraph/cell boundaries, native XML identity, source coordinates and inline
word preservation separately. Successful string production alone does not pass
the native-evidence gate. Do not treat a helper in `experiments` as a supported
production reader. Trace released-document consumers and acquisition APIs to
identify their existing responsibilities; do not build an index or fetch data.

Choose reuse based on these different output requirements. If an existing
public reader meets the required native structure and evidence checks, prefer
it over the pending format extension. If it supplies a different representation,
record that boundary and any useful upstream fixes without adding a duplicate
acquisition, segmentation or retrieval system to Rulespec. No performance claims
or quality rates will be inferred from these diagnostic files.
