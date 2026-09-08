# A manual section becomes a reviewable rulebook

The local extraction and correction workflow runs end to end. Its results also
make the remaining semantic work clear: exact quotations and valid Core records
coexist with omitted rules, missing alternatives, and lost conditions.

Use the [application instructions](../../../packages/rulespec-extrapolator/README.md)
for installation and commands. Open the bounded section from the repository root:

```sh
.tools/document-poc-venv/bin/rulespec-understand serve \
  examples/document_understanding/manual-slice/reprocessed/section-01
```

The [core correction demonstration](review-demo/README.md) repairs three
representative problems through saved review actions. It is an explicit
post-evaluation agent correction, not a fresh model result or human review.

## What went in

- Six development excerpts from the passport photograph instructions.
- Six held-out excerpts from the name-usage instructions.
- One contiguous section: 8 FAM 403.1-4(a)–(d), 2,651 Unicode codepoints.

The [source corpus](../../../packages/rulespec-extrapolator/evaluation/README.md)
retains original Department of State HTML, preparation instructions, source
digests, and coordinates. Prepared input JSON is under `source/`. The selected
text is a pinned research example, not a current legal interpretation. Images,
PDF layout, and a whole chapter were not evaluated.

Worked model examples were invented independently of these documents. The
evaluation worker sealed the source labels before extraction; outputs were
frozen in [frozen-outputs.json](frozen-outputs.json) before those labels opened.
The same evaluation agent authored the labels and later source judgments.

## Recorded extraction results

All five runs used Gemini 3.8 Flash. These are compiler and processing counts,
not semantic accuracy scores.

| Run | Model windows | Accepted | Refused by Core conversion | Unresolved | Processing / overall result |
| --- | ---: | ---: | ---: | ---: | --- |
| `development-01` | 3 | 33 | 0 | 5 | Complete / complete |
| `holdout-01` | 1 | 31 | 1 | 10 | Complete / partial |
| `holdout-02` | 1 | 29 | 0 | 10 | Complete / complete |
| `section-01` | 1 | 14 | 0 | 8 | Complete / complete |
| `section-02` | 1 | 13 | 0 | 5 | Complete / complete |

The refused candidate in `holdout-01` describes a recent-name-change ID waiver.
Its exception classification lacked the required exception relationship. Its
text and reason remain available. In other fresh runs the same source waiver
was retained as a permission or omitted entirely.

Each `runs/` directory preserves the original acquisition. Later `reprocessed/`
directories apply corrected Core history and text-loading code to those exact
saved responses, with explicit predecessor hashes and processing records. The
originals are unchanged. All five final outputs strictly replay without a
provider call; all accepted claim arrays and source documents match their
originals. See [reprocessing verification](reprocessing-verification.json).

Strict replay checks the frozen runtime as well as recorded data. It correctly
refuses the original pre-fix runtime under current code. Reprocessing is the
explicit way to change processing code; it is not permission to ignore drift.

## What source review found

An independent agent inspected all 87 accepted claims in the four held-out and
contiguous-section outputs. All four require correction. Counts below concern
source-reviewed expected units, which can require several extracted claims.

| Run | Covered | Partial | Missing | Unknown |
| --- | ---: | ---: | ---: | ---: |
| `holdout-01` | 11 | 5 | 7 | 6 |
| `holdout-02` | 8 | 8 | 8 | 5 |
| `section-01` | 4 | 4 | 1 | 1 |
| `section-02` | 5 | 3 | 1 | 1 |

The document alternatives disappear; urgent-travel and unchanged-ID rules lose
shared conditions; weaker spacing guidance and rewrite limits disappear; one
exception becomes an unlinked permission. Actor uncertainty also remains. The
inputs overlap, the sample is small, and the judgments are uncalibrated. Do not
combine these counts into a general accuracy claim.

The [full findings](../../../packages/rulespec-extrapolator/evaluation/results/FINDINGS.md)
include concrete source examples, per-dimension reports, fresh-run comparisons,
and limitations. The evaluator explicitly transferred unchanged judgments to
the final processed outputs only after checking every claim, source, and label
digest and independently replaying the outputs. Those
[transfer receipts](../../../packages/rulespec-extrapolator/evaluation/results/reprocessed/transfer-manifest.json)
do not rescore or improve the extraction.

## Verification and review evidence

The [verification record](verification.json) pins the implementation files and
records the completed checks.

- The application suite passes 167 tests. Existing POC and projection regressions
  pass 50 tests plus 101 subtests. The warnings concern a deprecated rdflib API.
- The installed wheel was tested outside the checkout with isolated Python:
  reprocessing, strict replay, Core validation, review storage, and packaged HTTP
  assets pass. See [wheel-verification.json](wheel-verification.json).
- Playwright exercised source inspection and actual split, merge, addition, and
  reopening in the browser. The [saved export](browser-review-export.json)
  contains those three agent-attributed events; the addition recovers an omitted
  infant eye-closure permission. Other review operations, concurrent edits, and
  tampering are covered by API/store tests.
- The [independent implementation review](../../../thoughts/reviews/2026-09-07-document-understanding-implementation-review.md)
  records the defects found and their remediation evidence.

Browser and core demonstration events identify `aiAgent`. No human review study
or comparable manual pass occurred. Human correction time and time savings
remain unmeasured. SQLite files are local working state; the saved action and
export JSON files retain the demonstrations for inspection and reconstruction.

## Next extraction work

1. Account for each source paragraph or list item explicitly, so a reviewer can
   find text with no candidate. This is processing accounting, not proof that
   every rule was understood.
2. Carry shared conditions into each resulting rule, with exact evidence for
   the surrounding branch. Test nested time, form, and ID conditions using
   development fixtures before another blind source evaluation.
3. Represent document alternatives and weaker language such as `should` and
   `generally` explicitly. Preserve their force and list structure.
4. Keep exception targets stable through extraction and review. Expand nearby
   context and cross-window assembly only after these bounded cases improve.
5. Measure a real reviewer's correction time against a comparable manual pass.

The browser is intentionally a small supporting tool. The next work should
improve faithful, complete extraction rather than expand the interface.
