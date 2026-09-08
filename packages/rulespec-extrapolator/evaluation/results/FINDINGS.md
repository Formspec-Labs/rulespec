# Frozen manual-extraction review

All four frozen outputs need correction and further review before they form a
complete, faithful rulebook. The application preserves exact source evidence,
many meaningful duties, and visible refusals, but those properties do not
establish semantic completeness. The second held-out run reports complete
processing while still omitting required source content.

This is an **agent-authored, uncalibrated source review**, not human gold or an
expert legal assessment. The evaluation worker wrote the labels from official
source text before inspecting outputs, kept them sealed until the producer
froze the runs, and then inspected every accepted claim and every in-scope
expected unit. The same agent authored the labels and later judgments. No
human accuracy or usability claim follows from these results.

## Results within the selected source

| Frozen run | Accepted claims inspected | Expected units | Covered | Partial | Missing | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `holdout-01` | 31 | 29 | 11 | 5 | 7 | 6 |
| `holdout-02` | 29 | 29 | 8 | 8 | 8 | 5 |
| `section-01` | 14 | 10 | 4 | 4 | 1 | 1 |
| `section-02` | 13 | 10 | 5 | 3 | 1 | 1 |

The held-out input combines six selected name-usage excerpts. The contiguous
section includes only 8 FAM 403.1-4(a) through (d); it is evaluated against
`fam-names-02` and `fam-names-03`, not the other excerpts. The two input shapes
share source passages, so their counts are not independent observations to
pool into an accuracy estimate.

`Covered` requires current reviewed claims with no semantic errors or unknown
dimensions. `Partial` identifies retained but incomplete or incorrectly scoped
content. `Missing` is an explicit source-reviewed omission. `Unknown` includes
units whose duty text survives while an acting role or interpretation remains
unresolved. Every accepted claim received a judgment; `review_complete: false`
means unresolved judgments remain, not that claims were skipped.

The individual reports include separate summary, actor, support, scope, link,
and boundary counts. Error dimensions overlap and must not be added together
as a count of distinct incorrect claims. These small-set counts are review
evidence, not a general model accuracy result.

## Errors that affect the resulting rulebook

1. **Document alternatives disappear in all four runs.** The source lists
   court orders/decrees, naturalization certificates, marriage certificates,
   state-law documentation, and customary usage as alternative means of
   documenting a material name change. Outputs retain a general instruction
   to submit one or more listed documents but do not represent that list.
   The married-name exception remains an unresolved reference rather than
   assembled scope. See expected unit `fam-names-02-u03`.

2. **Shared conditions do not consistently survive a split.** All four runs
   extract the urgent/emergency limited-passport permission without retaining
   its surrounding older-name-change/unchanged-ID branch. The documentation
   duty for an unchanged ID also loses some or all of the within-one-year
   DS-11 scope. The source quotation can remain exact while the displayed
   rule becomes too broad. See `fam-names-03-u03` and `fam-names-03-u05`.

3. **Weaker guidance and limits are omitted.** Both held-out runs omit the
   previous-passport and evidence/ID spacing defaults, family consistency
   guidance, special-issuance sponsor matching, and both spacing/suffix
   rewrite limitations. Several use `should` or `generally`, which may help
   explain the selection pattern; this is an interpretation, not a measured
   causal effect. See `fam-names-05-u02`, `u03`, `u05`, `u06`, `u07`, and
   `fam-names-06-u03`.

4. **An exception becomes a different kind of statement.** In `holdout-01`,
   the confidential-former-name exception points to the court-order name
   requirement. In `holdout-02`, it becomes an unlinked permission to receive
   a confidential-name court order. The exception no longer qualifies the
   requirement to list both names. Both runs also extract the additional
   evidence-request authority without its confidential-name scope. See
   `fam-names-04-u05` and `fam-names-04-u07`.

5. **Some information remains uncertain rather than wrong.** No confirmed
   incorrect actor assignment was recorded, but actor judgments remain
   unknown for 9 claims in `holdout-01`, 8 in `holdout-02`, and 5 in each
   contiguous-section run. Most are omitted actors on passive duties or
   permissions. Definitions and document properties use `not_applicable`
   where no acting party is needed. An ambiguous conjunction in one summary,
   an added court-order supplier interpretation, and an unclear action/object
   pairing remain unknown; they were not credited as correct.

The source authority is the pinned Department of State
[8 FAM 403.1 text](https://fam.state.gov/FAM/08FAM/08FAM040301.html), not a
current legal recommendation. Exact source paragraphs and label coordinates
are embedded in each `.expected.json`; each claim judgment includes the
reviewed source spans and a specific rationale.

## Fresh-run differences and failure visibility

- The recent-change ID waiver appears in `holdout-01` as a **rejected**
  candidate because its exception kind lacked an exception relationship. Its
  text, candidate, reason, and partial overall run state are preserved. The
  surviving documentation duty is accepted with reduced scope. A visible
  refusal therefore still leaves substantive review work.
- The same waiver is entirely omitted in `holdout-02`, retained as a
  permission in `section-01`, and omitted again in `section-02`. None of these
  changes requires a source change. The `section-01` waiver also carries a
  form identifier incorrectly classified as a section reference.
- `holdout-01` includes the `Sr.`/`Señor` distinction and ranks-and-titles
  direction; `holdout-02` omits them. The confidential-name exception also
  changes classification and linkage between those runs.
- Every planned model window has a visible terminal outcome. All four
  windows report complete processing; only `holdout-01` reports a partial
  overall run due to its rejected candidate. No provider refusal is recorded.
  Unresolved external references remain visible in all four outputs. These
  processing facts do not count as semantic coverage.

`holdout.repeatability.json` and `section.repeatability.json` compare exact
material fields and duplicate counts. Their differences include harmless
paraphrases and component choices as well as substantive errors. They do not
establish semantic equivalence; the examples above come from separate source
review. Two fresh runs at the recorded settings do not establish a general
repeatability distribution.

## Evidence and review effort

`unseal-receipt.json` verifies the original label seal and all four frozen
rulebook and source hashes. Each `.judgments.json` binds the immutable claim
IDs, every claim's content digest, the whole rulebook, selected labels, source
spans, named agent, and review timestamps. Each `.report.json` records the
deterministic accounting result. `source-review-decisions.json` preserves the
authored decisions separately from report generation.

`review-session.json` records a wall-clock audit interval for source reading,
inspection of 87 accepted claims, 78 scoped unit assessments, reasoning, tool
calls, and bookkeeping. Active reading time and per-run time were not
instrumented. No corrections, splits, merges, rejections, or approvals were
applied to the frozen output during this audit. No comparable manual pass or
human review was conducted; human time savings remain unmeasured.

To reproduce the reports without a model or network call:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src:packages/rulespec-projection/src:src \
  .tools/document-poc-venv/bin/python \
  packages/rulespec-extrapolator/evaluation/results/build_reports.py
```

The script expands explicit judgments and verifies their source and content
bindings. It does not infer semantic verdicts. It refuses to replace different
saved review bytes.

## Transfer to final compiler output

The original judgments were transferred to the final outputs under
`examples/document_understanding/manual-slice/reprocessed/` after all four
evaluated runs passed independent strict replay, including the final
compilation-recovery implementation. Earlier compiler-derived transfer records
were archived locally under `.tools/`; the
[refresh receipt](reprocessed/refresh-receipt.json) identifies that archive and
pins the current transfer manifest. Original frozen assessments were preserved.
Every one of the **87 accepted
claim records** was identical, including its immutable ID, components,
evidence, issues, and target links. Entire source documents and their metadata,
source-text digests, acquisition run IDs, and selected labels were also
identical. Only `run` and `graph` differed between original and reprocessed
rulebooks.

The corrected compiler and source-reading implementation therefore received
new whole-rulebook bindings; they did not receive new semantic judgments.
Every claim/unit judgment, error, omission, unknown, and coverage count remains
unchanged. The original assessments above remain intact. Reprocessing and
judgment transfer are not fresh model samples or evidence of better extraction.

- [Transfer manifest](reprocessed/transfer-manifest.json) pins all four new
  reports, selected-label files, judgments, and per-run transfer receipts.
- Reports: [holdout-01](reprocessed/holdout-01.report.json),
  [holdout-02](reprocessed/holdout-02.report.json),
  [section-01](reprocessed/section-01.report.json), and
  [section-02](reprocessed/section-02.report.json).
- Each `.transfer-receipt.json` records original/new file and canonical JSON
  digests, every unchanged claim digest, source and label checks, and the strict
  replay receipt. Replay reparsed preserved raw responses into identical
  candidates, then reproduced the complete rulebook and graph under the final
  recorded implementation. All four replay receipts record zero provider calls.
- [Transfer validation](reprocessed/transfer-validation.json) also records
  three negative probes: changed actor content, source text, or selected label
  meaning each refused transfer before replay or writing. These probes changed
  only in-memory test values; source and assessment artifacts remained intact.

To verify the existing transfer artifacts and repeat strict replay without
network or provider calls:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src:packages/rulespec-projection/src:src \
  .tools/document-poc-venv/bin/python \
  packages/rulespec-extrapolator/evaluation/results/transfer_reports.py --verify-only
```

The transfer helper checks all inputs before writing any new transfer. It
refuses changed claim/source/label content, changed original assessments, or
differences outside the recorded `run` and `graph` fields. It does not silently
update existing receipts or reinterpret the source.
