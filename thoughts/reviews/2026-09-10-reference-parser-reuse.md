# Reference parsing reuse: RefSpec and Spicy Regs

**Reuse RefSpec's citation grammar before building another federal citation parser. It is not yet a resolver for local CFR paragraph addresses.** Spicy Regs contains an older related grammar and a useful section catalog. Neither should become a mandatory dependency of Rulespec validation.

Inspected current source, callers, tests, and representative raw source paragraphs. Ran twelve capability probes against both current grammars, plus a U.S.C. pinpoint probe. These selected examples are an API inspection, not a benchmark or proof of general accuracy. No model calls, catalog rebuilds, source downloads, or external-repository edits were performed.

## Existing capabilities and their fit

| Capability | Existing implementation | Fit for Rulespec |
| --- | --- | --- |
| Explicit CFR and other federal citation recognition | [RefSpec `citation_grammar.py:2528`](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/citation_grammar.py:2528), also consumed by `unified_agenda_parquet.py` | Implemented, not connected to this context selector. Consolidates earlier SpicySearch/Spicy Regs grammars, with explicit prose versus structured-field list handling. Preferred starting point. |
| Named Act section → U.S. Code identity | [`find_act_relative_citations`](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/citation_grammar.py:3709) and [`resolve_act_relative_citation`](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/act_resolution.py:844) | Implemented using pinned popular-name/classification/source-credit data with unresolved/conflict results. Useful for “Clean Air Act section 111”; this is a different form of relative reference from “paragraph (b) of this section.” Source-reviewed; resolver artifacts were not loaded for this inspection. |
| U.S.C. subsection pinpoint and existence checks | [`usc_section_pinpoint`](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/citation_grammar.py:1704), [`UscSectionOracle.subsection_verdict`](/Users/mikewolfd/Work/RefSpec/src/refspec/registry/usc_section_oracle.py:1360) | Existing specialized behavior worth preserving. Pinpoint helper was called successfully. The oracle/recodification tables are U.S.C.-specific, not a CFR paragraph index; not exercised here. |
| Publisher-supplied reference links and source ancestry | [`extract_uslm_reference_edges.iter_edges`](/Users/mikewolfd/Work/RefSpec/tools/extract_uslm_reference_edges.py:489) | Existing tool for U.S. Legislative Markup XML. Retains source anchor, target path, target level, and operative/history/notes context. Prefer such publisher links when that source format provides them. It is not a packaged general HTML/CFR reader and does not produce Rulespec's plain-text character offsets. |
| CFR section identity, edition, heading and canonical location | [Spicy Regs `cfr_sections.py`](/Users/mikewolfd/Work/spicy-regs/src/spicy_regs/sources/cfr_sections.py:1), [`build_cfr_sections._shape`](/Users/mikewolfd/Work/spicy-regs/src/spicy_regs/transforms/build_cfr_sections.py:113) | Existing catalog lookup inputs for locating a cited section. Explicitly metadata-only; it does not fetch full section bodies or index subsection positions. Source-reviewed; no live catalog lookup performed. |
| Older CFR grammar | [Spicy Regs `parse_cfr_citation`](/Users/mikewolfd/Work/spicy-regs/src/spicy_regs/ontology/citations.py:626) | Implemented and callable, but the RefSpec consolidation handles the inspected section-list example better. Do not create another fork from this older copy. |
| Same-document paragraph address → exact source ranges | Current Rulespec section-label matching plus structural passages | The remaining gap. I did not find a callable general local-CFR resolver in the inspected RefSpec/Spicy Regs paths. Existing Rulespec links resolve exact supplied section labels, not nested prose addresses. |

## Actual behavior, including the counterexamples

- Constructed `40 CFR 82.154(a)(2)` is recognized by both grammars as title 40 / part 82 / section 154. **Neither CFR result contains `(a)(2)` or an occurrence span.** The public `CfrCitation` fields cannot substitute for evidence that identifies the precise paragraph.
- Constructed `40 CFR §§ 82.155, 82.156, and 82.157` returns all three sections in RefSpec. Spicy Regs returns section 155 plus a part-only 82 result, losing the remaining section detail.
- The actual refrigerant compliance paragraph states “the applicable practices in §§ 82.155 and 82.156” and continues through certification and reclamation requirements. Neither grammar returns a CFR result for that paragraph: the title is supplied by document context, not the citation text. This needs explicit context-aware handling, not guessed title insertion into the evidence string.
- The actual seatbelt booster paragraph contains two local `§ 91.107(...)` addresses and a parenthetical `49 CFR 571.213`. Both grammars return only the explicit external `49 CFR 571.213` citation. Finding a citation in a paragraph does not mean all its dependencies were found.
- The actual label parent says `paragraph (a)(3)(iii)(B)( 4 ) of this action`. Both return nothing. Preserve that exact source wording and its spaced labels; do not silently repair “action” to “section.”
- Constructed `paragraphs (b)(1) through (4), (c), and (d)(1) of this section` returns nothing from both CFR parsers. Ranges and shared prefixes therefore still need local-address work.
- Both refuse to turn `3 CFR, 1977 Comp., p. 123` or `5401-5405` into an ordinary CFR section. Those refusal cases should travel with any reuse.
- `usc_section_pinpoint('49 USC 1651(b)(2)', '1651')` returns `(b)(2)`. That is useful existing functionality, but not evidence of support for CFR prefixes or spaced parentheticals.

## Consequences for the next iteration

1. Keep the full-short-section comprehension comparison. Citation parsing cannot discover an unlinked exception that has no explicit address back to the baseline rule. This review does not overturn that experiment's outcome.
2. When references are needed, prefer explicit publisher links, then RefSpec's existing grammar for the forms it supports. Use Spicy Regs section metadata to locate candidate source editions where useful. Preserve raw citation text, source position, parsed identity, and unresolved details separately.
3. Before extending support, test actual local CFR forms against the upstream grammar with **explicit document citation context**. Retaining occurrence spans and CFR subsection paths is a concrete upstream improvement to assess; do not clone the regex grammar into Rulespec. Resolving those addresses to pinned source ranges still belongs with Rulespec's source index.
4. Keep parsing, locating, and meaning separate. A recognized identifier does not prove the target exists in the pinned edition; a located target does not prove its conditions govern the current rule. Reuse evidence roles and preserve unresolved dependencies.
5. Respect the dependency direction: RefSpec's package already depends on Rulespec conformance/artifacts. Do not add a mandatory full RefSpec or Spicy Regs dependency to Rulespec core. Reference candidates can arrive through optional enrichment; Rulespec must remain able to validate its own captured evidence independently. If the pure grammar must become core, settle shared ownership upstream rather than introducing a circular package dependency.

## Verification and saved evidence

- RefSpec HEAD: `abe338423532d08c4de97dfdce329c1ce1e043eb`.
- Spicy Regs HEAD: `bf10365b333c014a83610132732fef44a7499abd`.
- Checked grammar files were clean; their exact hashes and probe outputs are saved in [results.json](../experiments/2026-09-10-reference-parser-inspection/results.json).
- Focused existing RefSpec tests: **27 passed, 183 deselected**, covering selected CFR, pinpoint, XML href classification and context tests. This is not the full suite or a production extraction evaluation.
- Rulespec's POC environment initially could not import Spicy Regs because its ontology package imports `pyarrow`. Re-running in Spicy Regs' existing environment succeeded. No packages were installed; the failed attempt is recorded in the probe result.
- [Probe script](../experiments/2026-09-10-reference-parser-inspection/inspect_parsers.py) retains actual source paragraphs alongside constructed controls. Re-running compares exact results without overwriting them:

```sh
PYTHONPATH=/Users/mikewolfd/Work/RefSpec/src:/Users/mikewolfd/Work/spicy-regs/src /Users/mikewolfd/Work/spicy-regs/.venv/bin/python thoughts/experiments/2026-09-10-reference-parser-inspection/inspect_parsers.py
```

No parser integration, upstream change, production modification, or commit was made in this review.
