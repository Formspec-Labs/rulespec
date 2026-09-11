# Native title context helps recognition but does not settle citation identity

**Decision: neither experimental strategy passes the R9 adoption gate. Keep
production unchanged.** Native XML supplies useful evidence, but a reference can
name another authority within the same paragraph. Requiring the words “of this
title/chapter/part” loses most of the useful unqualified references and still
does not handle quoted wording or contradictory native structure.

This comparison reused RefSpec's production coordinate, range, list and
qualification readers through a temporary in-memory dispatcher. It did not
prepend a title to source text, call a model, change a wheel, or add another
production parser. [The plan](PLAN.md) was written before collecting outputs.

## What the comparison showed

Eleven selected publisher paragraphs from pinned eCFR titles 17, 40, 41 and 49
contain 21 manually identified omitted-title references to their own title.
They also contain three references to other authorities. These are diagnostic
labels from raw source review, not an independent benchmark or absolute answers.

| Strategy | Own-title references correctly retained, of 21 | Wrong accepted local titles | Shared syntax failure |
| --- | ---: | ---: | ---: |
| A: current explicit-only reader | 0 | 0 | Not exercised by these omitted-title inputs |
| B: supply native title for marked decimal sections | 20 | 3 | 1 |
| C: B, but require a local-scope phrase for the citation group | 7 | 0 | 1 |

All existing explicit readings remain byte-for-byte equivalent after JSON
serialization, and every returned occurrence quotes the original prepared text
at its exact offsets. List continuations retain their written anchor. Compound
parts, repeated occurrences, pinpoints, explicit range endpoints, note refusals
and open-ended refusals survive where exercised. Those checks establish
representation fidelity, not correct context attribution.

Twenty-two constructed controls add 13 expected readings/refusals. B preserves
all 13 but accepts six unsupported context assignments. C preserves 11, misses
two unqualified references, and accepts three unsupported assignments. The three
remaining C failures are a heading/native-title conflict, an explicitly quoted
other-agency regulation using “of this chapter”, and a reference saying “of this
part” while naming a different part from its native container. Missing native
context, display metadata alone, and nested conflicting native titles produce no
new accepted reference in either prototype. These are prototype checks; the
experiment does not implement production context admission or multi-section
document integration.

The raw summary counts `unexpected` readings, including the syntax refusal. Thus
B's four real unexpected readings are **three wrong accepted titles plus one
incorrect refusal**, and C's one real unexpected reading is that same refusal.
Do not report those aggregate counts as four or one wrong accepted targets.

## Raw examples that change the implementation approach

1. **Useful default, no local-scope phrase.** The refrigerant source requires
   equipment “certified pursuant to § 82.158 unless the situations in paragraphs
   (a)(1) or (2) of this section apply.” B retains 40 CFR 82.158. C declines it.
   The six-reference refrigerant practices paragraph likewise loses all six
   references under C. Requiring a local phrase would leave the original use
   case largely unresolved. See [equipment](inputs-complete/refrigerant-equipment.xml)
   and [practices](inputs-complete/refrigerant-practices.xml).
2. **A later explicit title defeats the native default.** A title-41 paragraph
   says `§ 1954.3(d)(1)(i) of title 29, Code of Federal Regulations`. B assigns
   title 41. The existing explicit reader sees the later title-29 phrase but
   does not connect it to the preceding section. The text itself supplies the
   correction; no document-title inference is needed. See
   [the complete paragraph](inputs-complete/foreign-title-suffix.xml).
3. **A quoted section and a local reference coexist.** Another title-41 paragraph
   says `“§ 20.206” (10 CFR part 20)` and later cites `§ 50-204.34(c)`.
   B gets the first title wrong and the second right. C declines both. Assigning
   one title to the entire paragraph would also be wrong. See
   [the complete paragraph](inputs-complete/quoted-foreign-section.xml).
4. **The source names an authority without a numeric title.** The title-40
   appendix cites `§ 1.169-2(b)(2) of the Treasury Department regulations`.
   B treats it as title 40. The paragraph and surrounding appendix concern tax
   amortization and identify the Internal Revenue Code. The label used here is
   only that a confident title-40 assignment is unsupported; this experiment
   does not implement a Treasury-to-title mapping. See
   [the paragraph](inputs-complete/treasury-regulations.xml).
5. **A shared production grammar issue appeared independently of title choice.**
   `§ 50-202.2 to the same extent` becomes `§ 50-202.2 to the`, with
   `range_end_unread`. The range connector interprets ordinary “to” as a range
   and consumes the next word. A separate declared constructed full citation,
   `41 CFR § 50-202.2 to the same extent ...`, reproduces the defect in the
   installed explicit reader. A real numeric range and an unread explicit range
   remain controls. See [the original paragraph](inputs-complete/compound-part.xml)
   and [installed diagnostics](installed-baseline-and-range-diagnostics.json).

The three installed range diagnostics were a separate follow-up after the
33-case comparison and raw review. They did not rerun an arm or change the
original failed acceptance gate.

## What to build next

Keep one shared reader and one native source index. The next coherent sequence is:

1. Extend RefSpec's explicit CFR occurrence reading for the written reverse
   form `§ … of title N, Code of Federal Regulations`. Reuse the existing
   section marker, item/list/range reader and longhand title matcher. Retain
   whole source evidence and test competing titles, separate sentences, lists,
   qualifiers and malformed scope before replacing the title-only reading.
   This fixes an observed case and gives contextual recognition an explicit
   reading that must take precedence.
2. Compare the “to” range interpretation upstream against ordinary prose and
   real/unread endpoints. Do not fix the example by accepting every unread
   range as its first section. The current occurrence/refusal representation
   already has the necessary output fields.
3. Return to R9 with both the literal citation group and its proposed native
   context. Keep citation-local authority wording ahead of native defaults;
   verify local part/title claims against native structure; retain uncertainty
   for quoted or conflicting context. Do not adopt C as a replacement goal.
   The unqualified refrigerant, definitions and mixed-authority cases remain
   positive acceptance cases, alongside the counterexamples.
4. Pass accepted contextual readings through the existing `record` and optional
   source lookup paths. Context evidence must remain separately inspectable.
   Rejected/uncertain readings must stay visible without authorizing a definite
   target lookup. Reuse current refusal/evidence records rather than introduce
   a confidence framework or model-facing fields.

These are next implementation decisions, not delivered capabilities. R9 remains
open. The reverse explicit reading and range issue have their own upstream
checks; they do not establish general title inference or legal applicability.

## Reproduction and limits

- [Frozen cases](cases.json): all 33 full inputs, native evidence and expected
  readings were saved before running the arms. Original source XML is preferred
  over a regenerated summary. Selected XML excerpts are explicitly materialized
  from original paragraphs; their native context is retained separately.
- [Source versions](source-freeze.json), [raw outputs](results.json),
  [summary](summary.json), [execution log](run.log), and
  [independent source verification](verification.json) retain the comparison.
  All eleven paragraph XPaths and every saved ancestor agree with the four
  full-title files, whose sizes and digests match their capture manifests.
- [Installed baseline verification](installed-baseline-and-range-diagnostics.json)
  matches all 33 source-baseline results. No new production suite was needed
  because application and upstream production files did not change.
- The first input-selection attempt and its two unmatched selectors remain in
  `inputs/`; the corrected complete selection is in `inputs-complete/`. The
  Treasury paragraph is under an appendix, and the 82.155 practices paragraph
  is outside 82.156. These corrections occurred before arm execution.
- Run `compare.py prepare`, then `compare.py run` with RefSpec's source on
  `PYTHONPATH` in a fresh experiment copy. Files use exclusive creation to avoid
  overwriting captures. `capture_inputs.py` verifies the pinned local full titles
  before materializing its inputs. The exact runtime is the current
  `.tools/document-poc-venv/bin/python` with the frozen RefSpec sources.
- The experimental dispatcher uses private helpers and a small repeated overlap
  walk, O(matches × occupied spans). It is a paragraph-level diagnostic, not a
  production full-document implementation or performance measurement. A promoted
  path should share the existing source-order traversal/interval index rather
  than add per-reference rescans.
- No model tokens or API cost were incurred. This comparison measures citation
  recognition and context assignment, not extraction meaning, coverage of whole
  documents, paragraph existence, historical editions or legal applicability.
