# Local evidence review

All 37 cases ran without model calls. Three historical provider quotations recover
at the same original offsets under whole-window and passage-restricted token
alignment: 1413–2317, 3377–3597 and 3377–3715. Hand-selected passage evidence totals
2,087, 1,045 and 1,045 characters respectively; narrowed citations total 904, 220
and 338. This demonstrates citation size, not faster review or model ID selection.

Two repeated-text controls demonstrate the intended benefit of selection. The
whole-window library picks the first occurrence (offset 0); a hand-selected F001
restricts it to the second occurrence (offsets 18 and 19). The selection supplies
intent that the matcher cannot infer. Within one passage, repeated and overlapping
wording still produces one selected result, not an ambiguity refusal. Both table
and list joins still align. No matcher or layout guard was added to force passing.

Missing negation, altered threshold, changed AND/OR, stitched omitted words and the
three long meaning changes remain refused. Typos, OCR substitutions and apostrophe
changes also remain refused: there is no fuzzy stage in this experiment. Case-only
changes still align. This is token equality, not character equality.

Invalid and unavailable IDs, an unseen context gap and inserted source-map text
are refused by the existing passage/source guards. A valid unrelated ID resolves
mechanically; the selected passage does not support the proposed rule. Its quoted
wording fails scoped matching in this constructed case, but a passage-only workflow
would require semantic review to identify irrelevance.

The remote qualification case selects both supporting passages correctly. Narrowing
returns only the duty sentence (45–81), losing the selected condition (0–43).
Therefore smaller citations do not pass the component-preservation gate. Keep
narrowing experimental; do not replace selected source evidence with its output.

## Source correction before meaning assessment

The preregistered plan describes C0014's logic_text as retaining the complete source
paragraph. Direct inspection shows it starts at F004, mid-sentence, after an XML
blank-line split. It retains unusual-circumstances and emergency qualifications,
but omits F003's explicit unforeseeable-leave lead-in. The review must distinguish
these: credit recognition of the qualifications actually present; do not demand an
incorrect claim that every condition survives in logic_text. The original plan
remains unchanged. The main gate (detect overbroad summary/scope without pretending
all meaning disappeared) remains the same, with this source-backed correction.

The fresh Q prompt is byte-for-byte identical to the historical full comparison
prompt. Both fresh arms keep all repeated draft/inventory input: Q has 221,202
characters and P 221,427. No input deduplication or reduced-context intervention is
being tested.

One scoped control needed a fixture correction: the long inserted-negation case
contains the full document, so the default first passage was its heading. That
refusal did not test altered meaning within relevant evidence. The separately saved
`stage1-supplement.json` selects F002, which contains the original notice alternatives;
both whole-window and scoped matching still refuse the inserted negation. The
original 37-case result is preserved. This was a post-result fixture correction,
not a new passed preregistered case.
