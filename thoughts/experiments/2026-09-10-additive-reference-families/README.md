# Five additional reference families: bounded test passed

The existing SpicySearch detector can add useful reference occurrences when restricted to public laws, Statutes at Large citations, executive orders, dockets, and Regulatory Information Numbers (RINs). The tested change preserves the current CFR/USC scan and appends candidates from those five kinds. It introduces no new parsing grammar or model call.

This supports a small integration proposal. It does not establish broad document accuracy or change production behavior.

## Results

The [design](design.md) and [case labels](cases.json) were fixed before executing the two arms. Each arm used the same source text and installed dependencies. A second execution reproduced the first exactly.

| Group | Cases | Expected added occurrences | Correct additions | Unexpected additions | Baseline changes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Prior development cases | 32 | 5 | 5 | 0 | 0 |
| New constructed diagnostics | 17 | 10 | 10 | 0 | 0 |
| Newly scanned saved documents | 3 | 0 | 0 | 0 | 0 |
| Total | 52 | 15 | 15 | 0 | 0 |

All added occurrences matched the predeclared kind, normalized value, and original character span. All five allowed kinds contributed correct additions. The registered gate passed. These counts concern additions; they do not erase existing baseline errors.

## What the raw review showed

- `🧭 Pursuant to Pub. L. 117–58, action may follow.` retained the original Unicode source span `[14, 28)` while normalizing the value to `Public Law 117-58`.
- Two occurrences of `E.O. 12866` remained two occurrences, at `[0, 10)` and `[20, 30)`. Repeated identity does not justify discarding separate evidence.
- A mixed public-law, Statutes at Large, and executive-order sentence yielded three correct candidates.
- Incomplete identifiers, fused suffixes, and unsupported continuations added nothing on the fixed controls. A Regulations.gov document identifier was not shortened into a docket identifier.
- The full Ohio Administrative Code 3745-52-15 source exposed a real reason to restrict the detector: it interpreted `3745-205`, `3745-256`, `3745-266`, and `3745-267` as Federal Register document identifiers. The five-kind filter excluded all four. These are state rule references in their source context.

The manual review covered every saved case, both arms, the unfiltered detector output, and all three full source texts. The unfiltered output remains saved so exclusions are inspectable.

## Limits and decision

All 15 positive added occurrences are constructed examples. The three full documents—29 CFR 825.110, 49 CFR 1540.111, and Ohio Administrative Code 3745-52-15—contain no positive examples for the five allowed families. They provide evidence about noise on these documents, not recall for the added families. These saved documents were new to this parser comparison, but had already been used in other extraction experiments.

The counterhypothesis was not observed on these cases: filtering by kind was sufficient here. It remains plausible on a broader corpus, particularly for ambiguous bare identifiers. Detection also does not establish that a cited instrument exists, identify its governing version, resolve a target, or prove semantic completeness.

The baseline's unresolved qualifier and local-reference gaps remain. This experiment does not justify replacing the baseline with a general query parser, expanding the allowed kinds, or claiming that all reference errors are fixed.

Recommended next step: validate the same unchanged filter on independently selected real documents containing positive examples of each allowed family before production adoption. If that succeeds, reuse the detector through a thin candidate-only adapter, retaining original text, offsets, kind, and normalized value. Keep target resolution separate. No upstream grammar change is indicated by this bounded test.

No production code was changed or committed. No provider calls were made, so this experiment incurred no model API cost. No latency conclusion is drawn.

## Evidence

- [Raw outputs](raw.json), [identical replay](replay.json), and [readable raw review](review.txt)
- [Per-case assessment](assessment.json) and [summary](summary.json)
- [Runtime and input hashes](run.json)
- [Case construction](freeze.py), [runner](run.py), and [pinned documents](documents/)

The runner writes observations exclusively and should be copied to a new experiment directory for a new run; do not overwrite these observations.
