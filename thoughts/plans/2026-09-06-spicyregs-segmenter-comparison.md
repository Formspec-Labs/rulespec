# SpicyRegs segmenter: recovery and comparison

Date: 2026-09-06. Read-only source/archive comparison; no extraction or model
benchmark rerun. Supplements `2026-09-06-reusable-segmentation-research.md`.

## Decision

Use the preserved SpicyRegs structure-aware segmenter as the local baseline before
rebuilding that capability. The archive contains considerably more evaluation
machinery than the earlier `fc24e06` source inspection revealed. It does not yet
provide open-ended requirement/exception discovery. LangExtract remains a
candidate for that separate semantic extraction stage.

Recover from the named pre-strip ref, adapting selected code into Rulespec without
a SpicyRegs or DocSpec runtime dependency. Do not adopt the historical winning
configuration as a proven optimum: the archived replay and scoring caveats matter.

## Where it survives

Repository: `/Users/mikewolfd/Work/spicy-regs`.

| Recovery point | Verified finding |
| --- | --- |
| `refs/heads/archive/pre-strip-2026-08-26` and `refs/snapshots/pre-strip-2026-08-26`, commit `57d46bf73bcc47617514ce270c2908a551e2353b` | Preferred recovery state: segmenter plus five-strategy experiment, evaluation code, tests and later remeasurement documentation. |
| `refs/heads/archive/integrate-payload-prereqs-pre-reorg`, commit `a6ab98aa35825ce993023ad9b237a28d04bb153e` | Identical production segmenter. Complete tracked source also preserved as a tar archive. |
| `refs/tags/archive/local-work-2026-08-09`, commit `6dbe181ccec7afedd92c1b63772a7b2e27705435` | Agent verified identical production segmenter. |
| Previously inspected `fc24e06ade915ead1209483733b1aec5cd824d1c` | Same production segmenter, source parser, extraction runner and relation task as pre-strip, but lacks `corpora/segmentation_experiment.py` and `segmentation_evaluation.py`. |

`src/spicy_regs/docpipeline/segments.py` is 43,997 bytes with SHA-256
`c1fb7a972e2ad55c26c14ddf703a77e76875bd6508ac9263029186dcaf9d88e4`.
Root compared the bytes at fc24e06, pre-strip, pre-reorganization, the tar member,
and all three located salvage copies; all match.

The standalone preserved copies are under:

- `/Users/mikewolfd/Work/corpora/_nuggets-2026-08-27/sweeps/2026-08-27-archive-surface/source-snapshots/`
  - `spicy-regs-integrate-payload-prereqs-a6ab98a.tar.gz` contains the tracked source.
  - `spicy-regs-local-history-2026-08-27.bundle` preserves local Git history;
    its companion README records the archived refs and prior verification.
- `/Users/mikewolfd/Work/corpora/_salvage-2026-08-28/dead-session-scratch/dfe597f2-citation-bridge/`
  - `greenfield-review/pkg/spicy_regs/docpipeline/segments.py`
  - `greenfield-rev2/v3/src_current/spicy_regs/docpipeline/segments.py`
  - `greenfield-rev2/v3/src_reverted/spicy_regs/docpipeline/segments.py`
- `/Users/mikewolfd/Work/corpora/_nuggets-2026-08-27/source/src/spicy_regs/corpora/segmentation_experiment.py`
  is byte-identical to the pre-strip version. This is the experiment harness,
  distinct from the production segmenter.

Read without checking out or changing the repository:

```sh
git -C /Users/mikewolfd/Work/spicy-regs show archive/pre-strip-2026-08-26:src/spicy_regs/docpipeline/segments.py
git -C /Users/mikewolfd/Work/spicy-regs show archive/pre-strip-2026-08-26:src/spicy_regs/corpora/segmentation_experiment.py
git -C /Users/mikewolfd/Work/spicy-regs show archive/pre-strip-2026-08-26:docs/evidence/document-segmentation-remeasurement-2026-08-02.md
```

No new duplicate source archive is necessary; save these exact recovery locations
and hashes. Existing bundles were located, not restored or reverified this turn.

## What we would reuse

| Component | Existing behavior | Rulespec use and limitation |
| --- | --- | --- |
| `docpipeline/segments.py` | Structure-first token packing; oversized-region splitting, overlap, exact source-field slices, parent/neighbor context, identities and coverage checks. | Strong local processing-window baseline. A segment can carry several source slices. It does not classify a passage as a requirement. |
| `docpipeline/source.py` | Native markup/prose regions, headings, tables and source coordinates. | Select parsing/location mechanics for actual input formats; preserve parser failures and fallback decisions. |
| `corpora/segmentation_experiment.py` | Five arms across token budgets: structure-first, structure-overlap, paragraph/sentence, embedding boundaries, model-guided boundaries; cached embeddings, provider records and metrics. | Reuse comparison ideas and selected mechanics. About 3,841 lines with historical dataset/runtime dependencies: not a small library to import wholesale. |
| `docpipeline/extraction.py` | Structured tasks, provider execution, stored requests/responses, rejection and replay. | Compare reusable parts with LangExtract before building execution machinery. |
| `docpipeline/relation_task.py` | Checks a supplied relation, with conditionality, polarity, attribution and exact supporting text. | Useful semantic design precedent; needs new behavior for open-ended discovery and multiple evidence spans. |

Compared with semchunk, the local segmenter already carries richer source-field
and context bookkeeping. Compared with DocSpec's current bounded segmenter, it
can retain multiple field slices and uses Unicode character coordinates compatible
with Rulespec's current quote verifier. Compared with LangExtract, it solves an
earlier stage: selecting model input rather than extracting typed semantic units.
These are capability comparisons, not performance measurements against those tools.

## Preserved experiments: inspected actual Parquet metrics

Base directory:
`/Users/mikewolfd/Work/corpora/_preserved-2026-08-27/spicy-regs-output-complete/`.

Root read `experiment_config_metrics.parquet` in:

- `segmentation-experiment-document-bge-v3/`: 153 artifacts, 15 configurations.
- `segmentation-experiment-document-openai-v3/`: 153 artifacts, 15 configurations.
- `segmentation-experiment-document-bge-2026-08-02/`: 153 artifacts, 5 configurations.

All use 35 labeled spans/queries. The later run's source-dataset identity differs
from the July runs; do not call the complete sealed datasets byte-identical.
For each of these three outputs, SHA-256 of all five declared Parquet files
matched the experiment manifest: metrics, segments, embeddings, provider calls,
and retrieval candidates (15 files total). This verifies preservation against
their manifests, not correctness of every recorded interpretation or full replay.

At the 1,800-token budget, corpus Recall@50 (whether the relevant passage appears
in the first 50 search results) is:

| Strategy | July BGE | July OpenAI | August 2 BGE | August segments | Recorded contained gold |
| --- | --- | --- | --- | --- | --- |
| Structure-first | 28/35 | 29/35 | 28/35 | 1,260 | 35/35 |
| Structure + overlap | 28/35 | 29/35 | 28/35 | 1,296 | 35/35 |
| Paragraph/sentence | 28/35 | 29/35 | 28/35 | 1,276 | 35/35 |
| Embedding boundaries | 28/35 | 30/35 | 31/35 | 1,594 | 34/35 |
| Guided boundaries | 31/35 | 32/35 | 32/35 | 1,764 | 34/35 |

All displayed rows record zero token overflows and zero uncovered characters.
**BGE runs use a deterministic boundary heuristic for the arm labeled
`llm-guided`; that arm is not evidence of LLM boundary performance.** The separate
OpenAI run uses model-based boundary selection. BGE embedding-based splitting
selects low-similarity adjacent-unit boundaries within token bounds.

These measure passage retrieval and span containment, not requirement extraction
accuracy or correct attachment of exceptions. Thirty-five queries cannot establish
a universal winner or expected passport-manual accuracy.

## Historical findings that change the recommendation

The August 2 remeasurement document at the pre-strip ref explicitly leaves the
frozen baseline gate failing: structure-overlap produces 1,296 segments instead
of the July 1,302. The saved metrics corroborate those counts. The historical
analysis reports identical segmenter code under both runs and suspects interpreter
or parser behavior; the exact environmental cause was not proved. This turn did
not rerun that diagnosis. Do not assert that pinning Python fixes it.

The same historical analysis disputes its own containment criterion. One synthetic
gold phrase crosses two evidence slices within a single segment. Slice-level
scoring marks it missed despite the complete phrase remaining in that segment.
This disqualifies embedding/guided strategies under the old selection rule.
The archived report establishes a concrete issue to investigate; root did not
independently replay that individual gold case this turn.

The old `structure-overlap-1800` selection therefore is a reasonable baseline,
not a settled winner. The report also finds no established advantage over
structure-first on this small corpus. The modern task needs its own evaluation:
can the extractor see and correctly connect the required evidence?

## Next implementation decision

1. Recover the small production segmentation path and its focused tests into an
   isolated Rulespec experiment; remove old storage/profile dependencies at the
   boundary rather than restoring the old platform.
2. Preserve headings as evidence, Unicode coordinate conventions, exact source
   text, parser versions and explicit fallback records.
3. Define containment over the actual text visible to the model, retaining the
   mapping to original slices. Separately check whether accepted claims have all
   required supporting spans; a processing window is not a semantic rule.
4. Run this baseline and a minimal alternative on the same representative chapter
   before deciding whether overlap, embeddings, or model-selected boundaries help.
5. Evaluate LangExtract or a small Rulespec extraction task on those inputs for
   requirements, conditions, exceptions and definitions. Attach RefSpec terms
   after source-grounded extraction.

No code adoption, installs, paid calls, commits, or changes to the archived data
were made during this research. Only this comparison document was added.
