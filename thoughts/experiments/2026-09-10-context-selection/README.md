# Context selection: test full sections before a more elaborate selector

**Existing links alone do not recover the missing context in the saved failures. Complete enclosing sections do.** The next informative comparison is comprehension with full short sections and resolved local references, rather than another prompt change or a general reference parser. This experiment did not change production or call a model.

| Source-selection outcome | A: current context | B: existing dependencies | C: enclosing section |
| --- | ---: | ---: | ---: |
| Required spans supplied completely | 11/23 | 12/23 | 22/23 |
| Cases with every required span | 1/7 | 2/7 | 6/7 |
| Unique source characters, summed across cases | 4,016 | 4,098 | 20,838 |
| Preselected unrelated duty spans included | 2 | 2 | 7 |

These are passage-availability measurements, not answer accuracy. Five cases use natural government text; two are constructed controls. The three old focuses are unchanged saved provider outputs. Two new focuses were selected manually from government sections not found in the prior experiment notes; they have no model extraction or fabricated relationships. These are not independent gold labels or an extraction benchmark.

## What happened in each case

| Focus | Current A | Existing dependencies B | Whole section C |
| --- | --- | --- | --- |
| Refrigerant default prohibition | Missing substitute list, complete de-minimis routes, and independent service duty | Same: no existing qualifying link into this focus | All selected source requirements present |
| Dated child-restraint label | Existing child-use evidence present; outer aircraft scope and global exclusion absent | Same | Both outer scope and exclusion present |
| Securing a child restraint | Local operator/conditions present; outer scope and competing exclusion absent | Same | Both potentially competing clauses present; interpretation still unsettled |
| Fire-plan responsible employee names | List lead-in present; section's applicability condition absent | Same; manually selected focus has no extracted links | Applicability and list condition present |
| Alarm backup means | Immediate maintenance neighbors present; section scope and small-workplace backup exception absent | Same; manually selected focus has no extracted links | Selected scope and potentially relevant exception present |
| Constructed visitor permission | Complete required context already supplied, alongside unrelated staff duties | Same | Same |
| Constructed annex reference | Referenced annex absent | Existing resolver supplies annex; external reference remains unresolved | Opening section alone misses annex |

Full-section C falls back to the whole supplied document in six cases. The natural supplied documents are single legal sections or a pinned section excerpt, 1,674–5,260 characters long. This result does not justify supplying an entire long manual. The repeated seatbelt document is counted once per focus because those are separate hypothetical consumer requests; the cost is not deduplicated across requests.

## Manual review and important limits

1. **None of A's context selections reported a budget omission.** The missing material was outside the selected ancestors/neighbors, not cut off by the 2,400-character budget. Increasing that limit alone would not select new passages under the current algorithm.
2. **B followed zero existing qualification relationships across these focuses.** Its sole gain is the constructed resolved annex. This is an observation about these frozen records, not a test showing relationship traversal fails when useful relationships exist. The two new manual focuses intentionally contain no extraction output; they cannot assess whether a fresh extraction would discover those links.
3. The current list parser recognizes a bounded set of lowercase/numbered forms. The seatbelt source also contains uppercase and spaced markers. Existing evidence supplies some ancestry the structural selector does not. The full section avoids reliance on recovering every such path for these short inputs; no parser fix was tested.
4. Both notwithstanding and Part135 exclusion are required as potentially competing evidence. Merely delivering them does not settle their interaction. Likewise, the alarm backup exception is potentially relevant context; this test makes no legal finding about its effect on the out-of-service duty.
5. Whole sections also include more unrelated duties. Inclusion is not false inheritance, and absence of a model means this experiment cannot show whether a consumer would misapply them. That is the next comprehension test's counterexample requirement.
6. Some scope labels deliberately contain broad paragraphs, including more than the immediate condition. Counts reflect these frozen source requirements, not minimum sufficient context or semantic completeness. Every failed required span was missing substantive text, not just whitespace.

## Preserved label error

The first scored run exposed a bug in manual label construction: a newline/indentation stop pattern reduced five new-source labels to `(a)`, `(c)`, `(d)`, or `(e)` rather than the complete paragraph. Original [cases](cases.json), [results](results.json), [plan](PLAN.md), and frozen hashes remain unchanged.

[label-correction.json](label-correction.json) records each original label, its replacement with the complete pinned XML paragraph, and rescoring of the **unchanged selections**. The corrected totals equal the original totals. This post-score correction repairs the assessment; it does not retroactively make the original labels sound. The broader gate still fails. Both original results and corrected assessment replay exactly.

## Decision and next bounded experiment

**Not solved by existing dependencies:** B uses only 19.7% of C's unique characters and preserves the unavailable external reference, but fails the frozen requirement to recover all known remote clauses. Do not promote B as the solution.

**Availability gain with additional reading cost:** C supplies the missing clauses on all five natural focuses at about 5.2 times A's total unique characters. C still misses the constructed cross-section annex, which B resolves. No combined C+B arm was run, and no model comprehension gain was measured.

Next, freeze new comprehension questions and compare current context against the complete short enclosing section plus already-resolved local references. Retain exact source positions, deliver overlapping text once while preserving roles, and explicitly distinguish context from established applicability. Include both conflicting clauses, an unrelated duty that must not transfer, and the unavailable external reference. Stop at a small declared call budget; assess grounded answers and false inheritance separately from usage. Use this evidence before deciding whether a more sophisticated selector earns its complexity. Do not add another extraction/audit stage by default.

Production files, original captures, and review graphs were not modified. No commit was made. The separate target-decision and retrieval experiments proposed previously remain future work.

### Subsequent sibling-repository check

[RefSpec/Spicy Regs reference parsing review](../../reviews/2026-09-10-reference-parser-reuse.md) found a consolidated callable federal citation grammar in RefSpec, named-act resolution, and publisher-link extraction, plus Spicy Regs CFR section metadata. Reuse those capabilities before writing another citation parser. Current CFR grammar outputs do not retain subsection paths or resolve the local paragraph forms in these failures. The full-section comparison remains useful; local address resolution is a distinct missing connection. This later finding does not change the frozen arms or scores above.

## Sources and replay

New sources are pinned 2025 government XML: [29 CFR 1910.39](https://www.govinfo.gov/content/pkg/CFR-2025-title29-vol5/xml/CFR-2025-title29-vol5-sec1910-39.xml) and [29 CFR 1910.165](https://www.govinfo.gov/content/pkg/CFR-2025-title29-vol5/xml/CFR-2025-title29-vol5-sec1910-165.xml). Raw XML, URLs, and text are saved in `sources/`. Prepared text joins each XML `P` element's `itertext()` with two newlines, retaining its internal whitespace. Browser retrieval failed; direct downloads succeeded. These are pinned evaluation inputs, not a claim about current law.

The [frozen inputs and runtime helper hashes](freeze.json), [all selected raw spans](results.json), and [replay receipt](replay.json) preserve the comparison. No credentials were read.

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-context-selection/correct_labels.py --replay
```

This read-only replay checks frozen hashes, recomputes all original selections, and reproduces the corrected assessment. Existing receipts are preserved.
