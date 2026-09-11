# RefSpec and SpicySearch reference-tool reuse

Tested the intended sibling citation tools through direct source imports, refined
RefSpec's missing occurrence output upstream, built both wheels, and used those
installed packages on the same probes and three pinned Rulespec documents.
This corrects the earlier source/wheel check, which tested Rulespec itself.

## What changed

RefSpec now exposes `find_cfr_citations()` and `CfrCitationOccurrence`. They reuse
the existing CFR grammar and add exact source text, codepoint offsets, attached
paragraph labels and the explicit title-bearing context for list continuations.
The new reader consumes attached pinpoints before continuing a plural citation
list, so `40 CFR §§ 82.155(a), 82.156(b)` retains both members. It does not infer a
document title, expand ranges or assert that a target paragraph exists.

The existing `parse_cfr_citations()` API retains its prior identity-only behavior.
A frozen copy of its original reader remains a test-only oracle. Existing
identity fields and downstream release shapes were not changed. RefSpec changes
are local and uncommitted; the wheel includes those edits, not merely HEAD.
SpicySearch source and vendored dependencies were not modified.

## What the probes established

- RefSpec retains `7 CFR 15a`; SpicySearch reads part `15`. RefSpec retains U.S.C.
  section `1395w-4`; SpicySearch reads `1395w`. SpicySearch's original outputs stay
  visible as comparison data, not fallback identities.
- The new RefSpec reader retains `(a)(2)` and spaced labels such as `(B)( 4 )`
  alongside their original spelling. Repeated identical citations keep distinct
  offsets, including after Unicode characters. A separated `(2025)` is not read
  as an attached paragraph label.
- Impossible titles retain their verdicts; compilation locators, bare numbers,
  uncited prose and unsupported local addresses do not become confirmed targets.
- The 24 selected probes include three actual pinned source paragraphs and 21
  constructed controls. Source and installed-wheel outputs match exactly. These
  selected probes are not an accuracy benchmark.
- The focused RefSpec grammar/occurrence suite passed 209 tests through `uv run`.
  The new occurrence suite passed 45 tests against the installed wheel outside
  the checkout. Changed RefSpec code and tests passed its configured lint.
  Mutations detected lost pinpoints, shifted offsets, invented local references
  and altered source text. See [verification.json](verification.json) and
  [installed-tests.xml](installed-tests.xml).

## Actual use and remaining gap

`scan.py` uses the installed tools on pinned document JSON, verifies the source
digest, and writes optional reference candidates with both tools' original
readings. It makes no model calls or database lookups. It is an experiment
consumer, not a new Rulespec Core dependency or production extraction default.
DocSpec is installed only because SpicySearch's wheel declares it; the scanner
does not use DocSpec for segmentation or validation.

The full seatbelt document yields its explicit `49 CFR 571.213` citation. The
refrigerant and railroad scans yield no explicit CFR candidates: their references
depend on document context. `§ 82.155` and “paragraph (b) of this section” remain
unsupported. **Empty output is not proof that there are no references.** Source
text, counterexamples and this limit stay in the saved scans. None of these
records creates an accepted qualification or establishes applicability.

Next work is explicit document-context parsing upstream and mapping local
paragraph addresses to Rulespec's pinned source ranges. Neither is implied by the
successful wheel check, and the experimental reference scan does not change the
current context selector.

## Reproduce

Source development probe (the user authorized these temporary source imports):

```sh
PYTHONPATH=/Users/mikewolfd/Work/RefSpec/src:/Users/mikewolfd/Work/spicysearch/src \
  .tools/document-poc-venv/bin/python \
  thoughts/experiments/2026-09-10-reference-tool-reuse/check.py --output /tmp/reference-source.json
```

The built wheels are in `dist/reference-tools-20260910/`; installed tools are in
`.tools/reference-tools-20260910/`. Their dependency check passes. To use them
without source imports:

```sh
env -u PYTHONPATH .tools/reference-tools-20260910/bin/python -I \
  thoughts/experiments/2026-09-10-reference-tool-reuse/check.py --installed \
  --compare thoughts/experiments/2026-09-10-reference-tool-reuse/source-results.json \
  --output /tmp/reference-wheel.json

env -u PYTHONPATH .tools/reference-tools-20260910/bin/python -I \
  thoughts/experiments/2026-09-10-reference-tool-reuse/scan.py path/to/document.json \
  --output /tmp/reference-candidates.json
```

Output paths must be new. Raw source/wheel probe results, complete input documents
and reference scans are saved beside this file. No package was published, no
SpicySearch vendoring changed, and no automatic rule links were added.
