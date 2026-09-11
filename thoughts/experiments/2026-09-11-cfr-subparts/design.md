# Preserve qualified CFR reference occurrences

Decision: extend RefSpec's occurrence reader and the existing Rulespec adapter
to retain subpart targets and their written list context. Keep the existing
identity-only reader stable. Do not add a Rulespec repair grammar or model pass.

Observed failure: the saved Ohio 3745-52-15 paragraph cites
`49 CFR Part 172 subpart E (labeling) or subpart F (placarding)` as one of several
hazard-marking alternatives. The current occurrence ends at `Part 172`.

Hypotheses:

- The occurrence reader has no subpart representation/matcher. Extending its
  source-anchored callback should preserve both targets, descriptors and the
  written `or` without changing unrelated readings.
- A consumer-only loss would instead show complete native readings and shortened
  application output. Compare both layers before editing.
- Context inference is a separate problem: a subpart in another sentence, paragraph
  or explicitly different CFR citation must not inherit this part merely by proximity.

Arms: capture the current installed/source implementation, then compare a native
RefSpec occurrence extension plus its thin application field mapping. Freeze the
old occurrence function as a test-only oracle before replacement. No provider calls.

Cases: retain the full saved Ohio input. Select the first two distinct paragraphs
in publisher order from each pinned eCFR title 21, 40 and 49 XML containing an
explicit CFR citation followed by a subpart designator (at most six new paragraphs).
Read surrounding source XML and section headings before labeling. Record exact
file digests and the manifest's per-title date. Selection is independent of parser
success; all selected cases, including unsupported forms, remain in results.

Add constructed counterexamples for sentence/paragraph boundaries, intervening
prose, wrong title/part inheritance, similar words, ranges, plural lists, repeated
occurrences, Unicode and parenthetical text. Keep the earlier nine-case reader
fixture and existing parser/consumer checks as regression data.

Held constant: source bytes, selected inputs, default list policy, existing model
outputs and all unrelated families. One deterministic scan per arm; no paid calls,
network fetches, corpus rebuild or new runtime dependency. Bound source inspection
to the three named XML files and at most six new paragraphs.

Decision rule: adopt the connected subpart slice only if the actual Ohio E/F
alternative survives with exact evidence and context, every selected supported
explicit subpart is retained, negative cases do not acquire invented targets,
and unrelated candidates/evidence/IDs remain unchanged. Enumerate intentional
old-reader divergences and preserve unresolved unsupported syntax. Owner and
application tests plus source/wheel/CLI checks must pass before updating the
working environment. More available reference text does not establish correct
applicability, target existence or general extraction accuracy.

Stop this comparison when that decision is answered or its case bound is reached.
The broader reuse task remains open, including local addresses and qualified USC.

## Source inspection and field decisions before implementation

The six selected paragraphs are frozen in `cases.json`; full original XML
sections are saved beside them. Manifest digests match all three source files.
Their context introduces two additional needs: appendix A/B **to** subpart A are
appendix targets, and a list of parts followed by a list of subparts does not by
itself establish every part/subpart pairing. The EPA parenthetical is a complete
qualification about testimony, not merely a short title. Preserve it as source
text without treating it as another subpart or generated explanation.

Use the existing occurrence shape with sparse native `subpart`, `appendix` and
stated `subpart_end` fields. Separate written list members keep their literal
connectors and descriptors in the occurrence text, with the title/part source in
existing context coordinates. No Boolean interpretation or range expansion.
Flag `ambiguous_part_scope` when a subpart list follows multiple parts; retain
the native partial reading and evidence as refused candidates in Rulespec rather
than guessing a pairing. Do not alter the legacy identity-only API.

Expected new supported targets: Ohio E/F; title-21 sample 1 appendix A/B to
subpart A; title-21 sample 2 subpart C; title-40 samples subparts F/E; title-49
sample 1 subparts B/C/D. Title-49 sample 2 must retain A/E but refuse definitive
part assignment. Source bytes and earlier criteria remain unchanged.
