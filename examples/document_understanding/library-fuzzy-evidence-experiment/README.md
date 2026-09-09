# Known-library fuzzy alignment: configuration matters

This comparison uses **fuzzysearch 0.8.1** and the already installed
**LangExtract 1.6.0**. It is a library comparison, unlike the preceding handwritten
whitespace-only experiment. Nine configurations ran against all 29 controls and
the same saved 36-judgment audit. No provider calls or production changes were made.

The most useful result is that LangExtract's strict token alignment recovers all
six failed judgments while rejecting the seven deliberate content-change cases.
A follow-up with fuzzy alignment disabled produces exactly the same controls and
audit results. Thus these recoveries need token-exact alignment, not permissive
character edits. Repeated matches and layout-sensitive quotations still need
separate handling before automatic acceptance.

## What was configured

[fuzzysearch](https://github.com/taleinat/fuzzysearch) searches for approximate
substrings and returns source offsets and edit distances. The grid uses its actual
`find_near_matches` API: one or two character edits; 5%, 10% or 15% of quote length
(floored and capped at 64 edits); and a separate insertion/substitution/deletion
configuration. No custom edit-distance implementation was written.

LangExtract uses its existing public `Resolver.align` API, with LCS token
coverage/density pairs 0.75/one-third, 0.95/0.95 and 1.0/1.0, always with
`accept_match_lesser=False`. Coverage is the fraction of extraction tokens matched;
density compares matched tokens to the selected source span. Neither is confidence
in the rule's meaning. Its token-exact stage runs before fuzzy alignment and can
ignore whitespace and case differences even when fuzzy alignment is disabled.

All arms retain exact-first comparison matching, supplied source ranges, the
existing inserted-text guard, and original source text/offsets. They record every
returned candidate and matching details. The adapter accepts one returned location;
that is explicitly not an exhaustive uniqueness test. Fuzzysearch consolidates
some overlapping matches; LangExtract returns a selected alignment rather than all
possible occurrences. The repeat controls expose those limitations.

## Measured tradeoffs

The seven content-change cases alter negation, numbers or AND/OR, omit intervening
words, or insert/drop negation in a long quotation. The table does not count mere
case, comma or zero-width-character differences as established meaning errors.

| Configuration | Saved judgments recovered | Content-change cases accepted | Ambiguous cases accepted | Layout cases accepted |
|---|---:|---:|---:|---:|
| fuzzysearch-1 | 2/6 | 2/7 | 1/3 | 2/2 |
| fuzzysearch-2 | 2/6 | 2/7 | 1/3 | 2/2 |
| fuzzysearch-5pct | 2/6 | 3/7 | 0/3 | 0/2 |
| fuzzysearch-10pct | 4/6 | 4/7 | 0/3 | 2/2 |
| fuzzysearch-15pct | 6/6 | 4/7 | 0/3 | 2/2 |
| fuzzysearch-insertions32-substitution1 | 6/6 | 5/7 | 3/3 | 2/2 |
| langextract-0.75-0.333 | 6/6 | 7/7 | 3/3 | 2/2 |
| langextract-0.95-0.95 | 6/6 | 3/7 | 3/3 | 2/2 |
| langextract-1-1 | 6/6 | 0/7 | 3/3 | 2/2 |

All configurations preserve the previously accepted judgments and their verdicts.
Settings recovering all six produce 18 reviewed claims, 15 covered units, three
partial units and no unknown units. Review accounting becomes complete; the audit
still fails because substantive findings remain. These results do not establish
the correctness of the original model's verdicts.

The asymmetric fuzzysearch configuration was noticeably slower and was still
CPU-bound when the process was observed after 80 seconds. It completed naturally
before an attempted interruption; no configuration timed out or was excluded.
Timing was not instrumented per configuration, so this is not a performance
benchmark. The complete fixed grid was preserved.

## Counterexamples and useful recoveries

| Source → proposed quotation | Example observed behavior |
|---|---|
| `File within 30 days.` → `File within 3 days.` | fuzzysearch accepts at one edit; strict LangExtract refuses |
| Long source says `must not disclose` → quotation says `must disclose` | 5% character budget and 0.95 token setting accept; strict token setting refuses |
| Real long C0006 quotation changes `employee is pregnant` to `employee is not pregnant` | 5% character budget and 0.95 token setting accept; strict token setting refuses |
| `Provide A and B.` → `Provide A or B.` | LangExtract 0.75 accepts; stricter token settings refuse |
| `Staff must file a notice.` → `Staff must file a notcie.` | Two-edit fuzzysearch recovers this intended typo; strict token alignment refuses |
| `employer` → `ernployer` in a sentence | Two-edit fuzzysearch recovers this constructed OCR confusion; strict token alignment refuses |
| Two occurrences of `Staff must file.` | Strict LangExtract still selects one rather than establishing uniqueness |
| Separate table cells `May<TAB>Not enter` → `May Not enter` | Strict token alignment still accepts a span across cells |
| Separate list entries `may<NEWLINE>not required` → `may not required` | Strict token alignment still accepts a span across entries |

The layout cases preserve actual coordinates; they concern how a quotation can
change relationships when separators disappear. The returned original source text
still retains those separators. An already-exact fragment such as `required.`
inside `not required.` also remains a match in both the baseline and every arm;
evidence location alone is not an assessment of meaning.

The loose LangExtract setting also accepts the unsupplied-gap control by matching
only the `must file.` portion inside one supplied context slice. It does not
actually cross the unavailable gap; it accepts an incomplete alignment. Stricter
settings refuse it. All cases and returned spans are in `cases.json` and
`results.json`; policy-only formatting cases are separated in `summary.json`.

## Follow-up: turn fuzzy matching off

All six recovered LangExtract judgments initially carried `match_exact`, meaning
token-exact rather than character-exact. The separately preregistered follow-up
sets `enable_fuzzy_alignment=False`, retaining `accept_match_lesser=False` and the
same source, controls and parser. It recovers all six and reproduces the strict
setting's 29 control results and complete audit exactly. This directly tests
whether the fuzzy stage is needed for these failures.

This makes **reuse of LangExtract's token aligner** a concrete candidate for the
next implementation, with explicit ambiguity and layout policy. No tested arm
passes all the earlier rejection expectations, so none was silently adopted.
Character-edit matching remains useful for locating possible typo/OCR evidence,
but the tested edit budgets do not distinguish those repairs from changed rules.
No comparison against passage IDs or independent corpus-wide evaluation was run.

## Replay observation

The full grid replay reproduced its recovery and acceptance counts but failed exact
result equality. A focused recheck of the 26 short controls found the asymmetric
fuzzysearch setting select offsets `0:16` for repeated text where the first run
selected `18:34`. Both are occurrences of `Staff must file.`. The library collapses
overlapping match groups and breaks best-match ties by distance/length, with no
explicit location tie-break. A single returned candidate therefore does not certify
an unambiguous location. Other differences in the failed full replay have not been
exhaustively excluded because its in-memory results were not saved.

The strict LangExtract follow-up and its replay reproduce all 29 control records
and the audit identically. The full-grid replay command intentionally retains its
strict equality assertion and may expose the recorded fuzzysearch tie variation;
it should not be described as an all-green replay.

## Reproduction

The experiment reuses the earlier control/audit harness, the shared evidence result
type and the existing evaluator. Versions and installed library files are pinned;
original captures and manifests remain unchanged. Install the experimental
requirements in the existing environment; no package dependency file was changed.

```sh
uv pip install --python .tools/document-poc-venv/bin/python -r examples/document_understanding/library-fuzzy-evidence-experiment/requirements.txt
.tools/document-poc-venv/bin/python examples/document_understanding/library-fuzzy-evidence-experiment/experiment.py replay
.tools/document-poc-venv/bin/python examples/document_understanding/library-fuzzy-evidence-experiment/exact_tokens.py replay
```

`PLAN.md` records the original nine-arm grid before execution.
`token-exact-plan.md` records the separate follow-up before its execution.
Thresholds and case labels were not changed after observing results. These are
selected diagnostic cases, not a general error-rate estimate or independent gold.
