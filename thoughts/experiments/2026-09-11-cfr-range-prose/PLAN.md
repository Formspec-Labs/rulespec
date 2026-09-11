# CFR range connectors versus following prose

Decision: determine whether a small change to RefSpec's shared CFR item reader
can preserve citations followed by ordinary prose without accepting incomplete
ranges as complete references. Keep recognition, native-title inference and
target lookup separate.

Observed failure: the saved title-41 paragraph says `§ 50-202.2 to the same extent
such employment is permitted ...`; the shared item reader treats `to the` as an
unread range endpoint. The public scanner requires an explicit title, so the
original bare reference must still remain unrecognized. A constructed explicit
title variant isolates the same item-reading error without implying adoption of
native-title inference.

Hypotheses and arms:
- A: the current committed reader; any matched connector starts a range.
- B: require a readable numeric endpoint before recognizing a range. Predicts
  broad prose recovery but risks silently accepting starts of damaged ranges.
- C: exclude clear grammatical prose continuations, while leaving all other
  connectors unchanged. Start with comparative `to [the] [same] extent/manner`
  and instrumental `through [the] use/application of`; no generic determiner or
  alphabetic-word exemption. This predicts narrower recovery and preserved
  unknown endpoints. This is a finite grammar rule, not general prose analysis.

Cases: retain the original XML and full surrounding paragraph; first eight
publisher paragraphs in file order from titles 21, 41 and 49 containing an
explicit CFR citation followed by `to`/`through` and a nonnumeric word; and at
most 32 constructed counterexamples/mutations. Review the actual raw paragraphs
before freezing labels. Include complete, damaged, missing, named and nested
range endings; reverse titles, list members, notes and paragraph breaks. Retain
the earlier publisher-range fixtures as unchanged controls.

Held constant: same source bytes and RefSpec version, no model calls, one run per
deterministic case. Bound the comparison to these sources and controls. Use the
existing native APIs and source evidence; do not add an NLP dependency or another
application parser. Preserve the old shared item implementation as a copied
test-only oracle before any production replacement.

Decision rule: reject an arm if any known incomplete range escapes as an accepted
start or existing exact evidence/endpoints regress. A bounded improvement requires
the actual item-level failure and explicit counterpart to improve, plus at least
one independently selected publisher citation through the public scanner. Report
remaining prose failures separately; do not label limited recovery a general
range/prose solution. If no arm meets this rule, retain the experiment and choose
a different approach. A passing arm still needs API, application, source/wheel
and normal-command checks before local delivery. No native-title default follows
from this result.
