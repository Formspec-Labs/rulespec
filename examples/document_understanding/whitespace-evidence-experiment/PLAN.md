# Whitespace evidence matching: pre-run decision

Decision: whether the proposed exact-first, whitespace-tolerant fallback is ready
for automatic comparison evidence acceptance, or should remain experimental.

Hypothesis: preserving every non-whitespace character while allowing whitespace
runs to differ recovers the six saved refused judgments without admitting altered,
ambiguous, out-of-request, inserted, or structurally misleading quotations.

Arms: current audit `_span`; the same exact-first behavior followed by one unique
whitespace-equivalent match inside a supplied focus/context range. Use the existing
EvidenceOffsetResolution type and source-map guard; return the original source
slice and offsets. Preserve the model quotation and matching method in an experiment
receipt. No case folding, Unicode compatibility folding, edit distance, punctuation
changes, word changes or model calls. No production changes authorized by this test.

Cases: all 36 raw judgments from the saved 825.303 comparison, including all three
failed claim/unit pairs; constructed controls for missing negation, changed numbers,
AND/OR, punctuation, omitted intervening text, repeats (including overlapping and
normalization-equivalent repeats), supplied-window boundaries, allowed context,
inserted source-map text, empty quotes, and Unicode whitespace. Two layout-sensitive
negative controls join separate table cells/list items into a sentence. They carry
explicit constructed author intent; these are not representative accuracy labels.
Also report a semantic-risk control where an already-exact fragment omits a leading
negation: an evidence resolver cannot by itself establish complete meaning.

Held constant: source documents, windows, raw model outputs, inventory, claims,
verdicts, assessment code and existing source checks. Deterministic one-pass replay;
no repetitions are needed for a fixed parser. Bound: these predeclared controls and
one full saved audit per arm. Do not tune the implementation after seeing results.

Decision rule: all six saved refusals must recover with original source offsets;
all prior accepted judgments and verdicts must remain unchanged; the source and raw
captures must retain their hashes. All rejection controls must remain refused. Any
new acceptance of a layout-sensitive negative case fails the broad safety gate,
even if the saved document improves. Report literal match reliability separately
from meaning preservation. A normalized match alone never establishes semantic
correctness. No direct comparison against passage IDs is run, so this experiment
cannot select a universally better evidence format.

Expected audit effect: 18 rather than 15 claim judgments accepted; original raw
covered/partial verdicts unchanged, including partial for C0014/U0014. Three unknown
units should become two covered and one partial, producing 15 covered, 3 partial,
0 unknown. Review accounting may become complete, while status must remain failed
because substantive findings remain. Check these outcomes explicitly rather than
calling recovered rows a clean audit.
