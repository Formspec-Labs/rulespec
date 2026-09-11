# Paragraph labels improve; automatic address lookup is not ready

**Do not promote the tested nearest-parent extension.** Reusing RefSpec's
parenthetical lexer inside Rulespec's existing passage algorithm recovers most
selected source addresses. It also produces unjustified single paths for ambiguous
fragments, misses an inline child and changes existing context selection. This
answers the [registered comparison](design.md); it does not close R10 or R11.

No production code, model settings, Core schemas or installed packages changed.
The new code is confined to this experiment. No model calls or new source downloads
were needed. Public format/library documentation was consulted during the reuse
assessment; all regulatory test inputs came from saved local captures.

## Results

The [labels](labels.json) contain 135 expected addresses and four controls whose
absolute address is not established by the supplied text. They are manually
reviewed source readings, not immutable truth. The original source and labels are
separate from both arms' output.

| Population | Current parent metadata: matching reconstructed paths | Extended marker/parent guesses: matching paths |
| --- | ---: | ---: |
| Saved refrigerant and seatbelt documents | 27 / 42 | 42 / 42 |
| Newly selected 21 CFR 1.276 and 49 CFR 1.25a | 23 / 58 | 57 / 58 |
| Constructed controls with stated expected paths | 32 / 35 | 35 / 35 |
| All positive address labels | 82 / 135 | 134 / 135 |
| Uncertain controls that would incorrectly receive a single path | 1 / 4 | 2 / 4 |

The current production API does not export these paths. The baseline column is
an explicit diagnostic reconstruction from its saved passage labels and parents;
the candidate column is experimental output. These counts are neither production
reference-resolution coverage nor extraction accuracy.

The candidate retains both occurrences of duplicate addresses. All prepared text
remains covered, and all 179 unchanged spans keep their passage IDs. Eleven old
spans are replaced by 23 new spans; 33 shared spans change parent. The comparison
JSON names the span replacement counts `removed_boundaries` and `added_boundaries`;
they count passages, not distinct boundary coordinates. Fifty-seven of the 139
fixed 120-character focus windows receive different context from the existing
`with_context` function. That consumer effect has not been assessed for meaning.

## Raw examples and what they establish

- **Seatbelts:** the candidate reconstructs `(a)(3)(iii)(B)(4)` and the uppercase,
  spaced and deeper Roman label paths. The old metadata exposes only eight of 23
  expected paths in this source. This supports the missing-marker hypothesis.
- **Fresh redelegation source:** `(1)(i)` is a combined label, followed by `(ii)`.
  The previous letter-plus-number special case does not cover it. Reusing the
  upstream lexer restores all 34 reviewed paths in 49 CFR 1.25a.
- **Fresh definition source:** `(4) FDA Country of Production means: (i) ...`
  contains two addressable levels in one physical paragraph. The candidate still
  cannot locate `(b)(4)(i)` independently. XML retains the words but provides no
  separate child element there; a general line-start rule is insufficient.
- **Ambiguous fragments:** `(g)(1)(i)` could end with a Roman child or a later
  top-level letter. After `(a)(3)(iii)(B)`, a final `(4)` could return to `(a)(4)`
  or descend further. The candidate chooses one path in each case. `false_unique`
  in the result means a consumer would overstate these structural guesses if it
  treated them as resolved addresses; no production consumer did so.
- **Complete content remains another problem:** the current refrigerant passage
  for `(a)(1)` contains only `No person maintaining, servicing, repairing, or`.
  The rest of that sentence is in the next physical passage. Correctly labeling
  its start does not retrieve the complete paragraph or its descendants.

The [source review](source-review.md) records complete-source inspection and the
uncertain controls before candidate execution. The saved seatbelt XML uses
`E T="03"` for italic markers; flattened spacing cannot serve as proof of that
formatting. [GPO's eCFR XML guidance](https://github.com/usgpo/bulk-data/blob/master/ECFR-XML-User-Guide.md#24-paragraphs)
also explains that numbered paragraphs are flat elements with embedded labels.
Publisher markup can supply useful distinctions, but is not itself a complete
paragraph tree for these sources.

## Decision and next experiment

H1 is supported for the observed marker forms. H2 remains a blocking issue for
unique lookup, and H3 is supported by the fresh inline child and the broken-up
refrigerant sentence. The broader adoption gate fails. The test used a deliberately
small nearest-parent heuristic; it does not rule out a better text-only parser.

The next comparison should reuse the same source/evidence foundation and separate
three responsibilities:

1. **Locate labels and their source features.** Preserve marker typography and
   publisher addresses where present. Exercise RefSpec's existing USLM link/anchor
   reader on a pinned source as a separate reusable producer. Keep its XML anchors
   distinct from prepared-text coordinates.
2. **Represent possible addresses.** Keep ambiguous paths or an unresolved reason;
   do not expose one heuristic guess as a verified local target. Test the current
   fragment controls plus fresh ambiguous cases. An explicit full label can still
   be used without solving every surrounding hierarchy.
3. **Retrieve complete source text.** Use existing spans and passage IDs to include
   unmarked continuations and the requested subtree, and locate inline children.
   Compare paragraph address enrichment separately from changes to default context
   selection. A subsequent model comparison is needed for those context changes.

This is a new comparison to register before running it, not an adopted fallback
or permission requirement. Qualified USC and other reuse tasks remain independent.
The two fresh sections are now development evidence for this intervention; do not
reuse them as untouched evaluation cases for later tuning.

## Reproduction and limits

- `freeze.py` selected and pinned the sources, copied the unchanged reader and
  captured its output. `label.py` wrote the manually reviewed paths before B ran.
  Both use exclusive writes to preserve their original captures.
- `candidate.py` is test-only and directly reuses RefSpec's private lexer. A
  production dependency would need an appropriate public interface; no such
  interface was introduced on this failed gate.
- `comparison.json` and `comparison.log` retain all cases, candidate passages,
  errors and changed context requests. `comparison-direct.json` is the independent
  rerun using direct source imports for RefSpec as well as Rulespec.
- The first comparison used source Rulespec and the installed RefSpec lexer.
  [Verification](verification.json) confirms the installed and source grammar
  hashes agree and both full outputs are equal. This is replay/import parity,
  not a new semantic sample or a wheel build for the candidate.
- Existing production package tests and a candidate wheel were not run: the
  address/ambiguity gate already failed and no production change was adopted.
  Source-map export and later model-context acceptance checks remain unperformed
  for this candidate; text coverage alone does not establish them.

Rerun the comparison with a new output path, leaving captures intact:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src:/Users/mikewolfd/Work/RefSpec/src \
  .tools/document-poc-venv/bin/python \
  thoughts/experiments/2026-09-11-local-paragraph-addresses/compare.py \
  --output /tmp/local-paragraph-comparison.json
```
