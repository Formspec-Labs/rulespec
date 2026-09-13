# Supplied IEP repairs are recognized; the broader gate still fails

The unchanged checker accepted both correct IEP repairs in both presentations
and rejected every deliberately wrong repair. It rejected the correct
request-content addition in both presentations as duplication of an existing
record. **Keep production behavior unchanged.** This result narrows the failure;
it does not deliver automatic repair or establish a general accuracy rate.

| Preregistered measure | Result |
|---|---|
| Supported candidates approved | 4/6 judgments: both IEP repairs twice; constructed request repair rejected twice |
| Wrong candidates rejected | 14/14 judgments across seven candidates |
| Decisions returned with exact, resolvable source references | 20/20 |
| Positive IEP decisions cite both governing provisions | 4/4 |
| Verdict agreement across reversed presentation | 10/10 candidates |
| Rationale quality | One unsupported extension of writing to agency consent; one rationale mentions an unselected passage |
| Full declared gate | Failed: two positive judgments rejected and one substantive rationale error |

Counts are two presentations of ten candidates, not twenty independent cases.
All ten edits were constructed before requests and passed independent temporary
review previews, including the intentionally wrong edits. Mechanical acceptance
does not establish their meaning is correct. See the [manual review](REVIEW.md).

## What this changes in our understanding

The preceding [recovery comparison](../2026-09-12-navigation-repair/README.md)
returned no proposed repairs. Here, once supplied, both IEP repairs received
source-supported approval from existing code. Selection or composition is still
an obstacle for that workflow; the checker is not uniformly unable to recognize
those repairs. Because the preceding calls are historical and the tasks differ,
this does not isolate why generation failed or establish a hidden model cause.

The constructed request case exposes a different problem. The checker explicitly
recognizes the content requirement but calls repeating it in the permission a
duplicate. Its single verdict combines factual support with whether a change is
needed. That distinction matters when interpreting `unsupported`: here it does
not mean the proposed requirement is absent from the source. The preregistered
standalone-reading criterion and the checker's record boundary differ.

H1 therefore receives partial support on IEP only. H2 fits the constructed
request responses but not the accepted IEP repairs. H3, indiscriminate approval,
was not observed among the seven deliberately wrong candidates. Explanations
remain fallible even when verdicts agree with the expected labels.

## Next work, without adding a routine pass

1. Preserve these as development regressions. Stop tuning this batch.
2. On previously unused real excerpts with resolvable local references, test
   whether focusing the existing recovery call on a referring provision and its
   target claims produces faithful repairs. Compare with the ordinary recovery
   input, keep the source and model settings constant, and reuse the unchanged
   checker and temporary review path. A supplied repair is a diagnostic control,
   not evidence that the generator succeeded. Include independent reporting duties
   and references that should not become prerequisites.
3. Before that comparison, state which related meanings belong in the default
   reading and which remain separately navigable duties. Score factual fidelity,
   standalone usefulness and edit necessity separately in the evaluation. Do not
   broaden all records, alter the qualification guard, or disable duplicate
   protection to make the constructed request case pass.

Existing `summary`, `context_quotes`, source references and `ReviewStore` can
already represent and preview the tested changes. No additional schema is
justified by this result. Automatic discovery, correct relationship assignment
and fresh-document benefit remain unproven.

## Capture and verification

Four calls used **60,685 reported tokens**: 42,420 prompt, 15,900 thinking and
2,365 visible response tokens. Total recorded capture time was 55.54 seconds,
including initial model setup; request timestamps span 54.31 seconds of provider
attempt time. These are token counts, not a dollar-price estimate.

Settings: `gemini-3.8-flash`, temperature 0, medium thinking, no numeric thinking
budget, 32,768 output cap. Four calls, no retries, normal completed responses.
The existing checker prompt, schema and decoder were unchanged. Expected labels
were absent from prompts; proposal IDs and presentation order were randomized.
Original books, runtime sources and frozen inputs retained their pre-call hashes.
Saved responses decode identically with model creation blocked, and all four
actual requests match their frozen prompt, schema and settings.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src \
  .tools/document-poc-venv/bin/python \
  thoughts/experiments/2026-09-12-fixed-repair-check/run.py verify
```

[Plan](PLAN.md), [expected labels](labels.json), [mechanical proof](mechanical-proof.json),
[raw requests and responses](captures/), [decoded judgments](decoded/),
[aggregate results](RESULTS.json), [usage](usage.json).
