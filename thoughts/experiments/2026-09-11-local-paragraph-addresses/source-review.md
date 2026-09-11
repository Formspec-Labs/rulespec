# Source review before candidate execution

The new selections are **21 CFR 1.276** and **49 CFR 1.25a**, from the verified
RefSpec eCFR corpus. They were not in the earlier subpart or selected design-context
cases checked here; no claim is made that no other researcher has ever read them.
Whole captured sections and source offsets are retained. Their paragraphs were
manually read before writing `labels.json`.

- 21 CFR 1.276 embeds `(i) For an article ...` inside the same `P` as the `(4)`
  definition. Its following `(ii)` is a separate `P`. Splitting only at line starts
  cannot make the first child independently addressable. Capital `(A)/(B)` paragraphs
  belong to `(b)(5)(i)`. This source gives a fresh boundary case as well as labels.
- 49 CFR 1.25a starts two groups with `(1)(i)`. The existing `(letter)(number)`
  special case does not handle this combination. `(A)` through `(E)` belong to
  `(b)(6)(ii)`. No paragraph IDs are present on those XML elements.
- The saved seatbelt source uses italic number/Roman markers, represented as
  `E T="03"` in its original GovInfo XML at
  `examples/document_understanding/consistency-transfer/sources/seatbelts.xml`.
  The flattened capture retains spaced spelling but not an explicit typography
  field. A space is not proof of italic type. The saved XML itself jumps from
  `(B)(3)` to `(ii)`; this inspection does not claim a paragraph `(i)` was dropped
  by Rulespec or that the saved source is semantically complete.
- The refrigerant text has a blank-line break inside the `(a)(1)` sentence. Address
  discovery and retrieving a paragraph's complete content are different checks.
  An index returning only the first physical passage would truncate its meaning.

Labels represent revisable source readings. The `spaced-path` control deliberately
ends with `(4)` after `(a)(3)(iii)(B)`: the supplied plain text alone permits an
outer `(a)(4)` or a deeper `(a)(3)(iii)(B)(4)` reading. Its expected result is
unresolved. The complete seatbelt document supplies more context and its source
markup distinguishes levels; the control must not inherit that knowledge.

The analogous `(g)(1)(i)` fragment could mean a Roman child or a later top-level
letter with a skipped `(h)`. Expected unresolved labels test false confidence,
not merely marker recognition. Duplicate addresses must retain both occurrences.
An explicit full `(a)(3)(iii)(B)(4)` marker does not have these ancestry ambiguities.
