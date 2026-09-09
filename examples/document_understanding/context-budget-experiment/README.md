# Larger input and generation budgets

**Keep larger source windows available, preserve fitting lists, and make generation
allowance configurable.** The tested 32K allowance works, but it did not consistently
improve semantic quality over 16K. None of these limits is a model capacity claim.

The normal source default is now 24,000 characters, up from 6,000. Callers can set
`--max-chars` higher. The default generation allowance remains 16,384; use
`--max-output-tokens 32768` for more room for thinking and the answer. Both limits
are recorded and verified during replay.

Google's [long-context guidance](https://ai.google.dev/gemini-api/docs/long-context)
supports supplying relevant information up front. Its
[token guidance](https://ai.google.dev/gemini-api/docs/generate-content/tokens)
distinguishes model input/output limits. Our earlier small windows were application
stress settings, not evidence that modern models require such short context.

## Experiment

The full saved 2025 edition of 29 CFR 825.110 supplies 6,919 characters, paragraphs
(a)-(e). This extends the previously studied (a)-(b) excerpt. It exceeds the old
application window but is far below model context capacity; this experiment does
not measure long-context retrieval at model-scale limits.

The same source, schema and prompt were run twice for each combination of:

- Input: 6,000 characters, producing two requests, or 24,000, producing one.
- Generation: 16,384 or 32,768 tokens, independently varied.

Four additional runs repeated the saved baggage and invented display cases at
their old small limits and 16K generation allowance, with corrected list boundaries.
These packing comparisons use saved prior controls rather than a fresh old-code
rerun. All runs use Gemini 3.8 Flash at temperature 0. Twelve runs made exactly
20 provider calls, without retries, repair calls or model reviews.

[design.json](design.json) pins the inputs and runtime before calls;
[criteria.json](criteria.json) records review checks. Original XML and the precise
text transformation are saved in [source.json](source.json).

## Results

| Input characters | Generation allowance | Statements, repeats 1 / 2 | Total reported tokens, repeats 1 / 2 |
| ---: | ---: | ---: | ---: |
| 6,000 | 16,384 | 18 / 19 | 14,003 / 13,015 |
| 6,000 | 32,768 | 20 / 19 | 13,850 / 13,483 |
| 24,000 | 16,384 | 17 / 18 | 11,816 / 9,220 |
| 24,000 | 32,768 | 11 / 17 | 7,280 / 8,612 |

All eight leave runs completed. Larger intact input used one request instead of
two and fewer reported tokens in these observations. However, grouping and
omissions varied. The first whole-input 32K result combined many independent
meanings into eleven statements. Both whole-input 32K results omitted the explicit
one-time/intermittent/reduced-schedule distinctions and August/December example
from paragraph (e); all four smaller-focus results retained them. Whole-input 16K
results retained the schedule distinctions and generalized the example into a
qualified rule. These selected outcomes do not prove a general context-length
effect or that increasing the generation allowance causes compression.

Other issues remain at both sizes and budgets: inherited provisos can survive
only in scope or only in the statement; reference topics can disappear while
citations remain; examples and independent meanings can merge. A higher maximum
allows more generation, but does not require the model to produce a more complete
or more detailed answer.

## Fitting lists: a concrete improvement

The planner now moves a fitting list group into the next window instead of
splitting its children. It reuses the source passage tree, preserves every original
character and keeps the configured hard limit. Oversized groups can still split.
The fuller source also exposed `(c)(1)` markers; these now reset the prior group
and preserve the combined structural levels.

| Case | Saved old-boundary controls completed | New boundaries completed | Target baseline |
| --- | ---: | ---: | --- |
| Baggage | 1/2 | 2/2 | All four firearm conditions in both new statements |
| Display policy | 0/2 | 2/2 | Roof, wind and agency authorization in both new statements |

Request counts and source/generation limits stay the same in these four recovery
runs. The baggage cut moves from 1,842 to 1,376; the display cut from 1,226 to 1,034.
This puts the complete targeted list in focus. Neither recovery requires the
higher generation allowance.

Baggage still loses conditions from its scope field and sometimes misclassifies
non-prohibition. The second display scope omits the storm exceptions while its
statement retains them. Its logical evidence still selects only the lead-in.
The retained boundary fix improves supplied input and the target statements; it
does not establish complete semantic fidelity.

## Verification and use

All twelve runs replay to identical books without provider calls. All twenty
responses are complete JSON. All 191 accepted statements pass Core graph checks,
and raw statement, scope, kind and modality match the accepted values. There are
no extraction refusals or Core-rejected candidates. Recorded total usage is
**153,753 tokens**, including thinking.

The package suite passes **317 tests**. The final compound-marker boundary
adjustment also passes all eleven context tests. Tests cover exact Unicode
coverage, hard limits for oversized groups, fitting-list boundaries and preserving
a nondefault generation allowance through capture, replay and reprocessing.

```sh
rulespec-understand extract prepared.json \
  --max-chars 24000 --max-output-tokens 32768 \
  --env-file /path/to/local.env --output my-run
```

[verification.json](verification.json) records replay and request comparisons.
[source-review.json](source-review.json) contains ten findings with raw rows and
source evidence. Reviews are revisable agent judgments, not absolute gold labels.
No schema or prompt changes were introduced by this experiment. Previous captures
remain unchanged. Implementation and research are local and uncommitted.

The next useful evaluation is a broader collection of genuinely longer documents,
with semantic coverage checked across their beginning, middle and end. The current
results justify removing unnecessary small-window constraints; they do not select
an optimal context size for every document or demonstrate accuracy near model limits.
