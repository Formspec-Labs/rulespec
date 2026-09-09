# Paired checks of extraction guidance

Neither instruction variant is ready for the default extractor. Both improved
specific failures while losing meaning elsewhere. The current default stays in
place; this directory preserves the experiment and its source review.

This experiment tests two explanations from the raw-output diagnosis without
changing the production extractor: ambiguous negative classifications and
inconsistent distribution of meaning across fields.

The predeclared design has nine Gemini 3.8 Flash calls at temperature 0, with no
retries and one observation per cell:

| Source | Control | Classification guidance | Field-consistency guidance |
| --- | --- | --- | --- |
| Baggage restrictions | Yes | Yes | Yes |
| Invented negative-force contrasts | Yes | Yes | — |
| Passport photos | Yes | — | Yes |
| Leave eligibility | Yes | — | Yes |

Only the appended instructions vary. The original CUE-generated provider schema,
field order, splitting instructions, source, model, parser, Core conversion and
output budget stay fixed. The baggage control is shared by the two comparisons.
There is no combined treatment in this experiment.

`design.json` pins the source and runtime hashes. `criteria.json` records the
review criteria before calls. The classification treatment tests a conservative
profile choice: statements that a particular policy does not prohibit an action
remain descriptive statements about that policy, without inventing absence of a
duty or universal permission. That mapping is an explicit application choice,
not a claim that no other legal representation could be defensible.

The normal extractor records every request and response and freezes its actual
prompt and runtime. A small runner changes only `PROMPT` for the selected cell.
Run each declared cell once; an existing run directory refuses an accidental
repeat. Replay uses the same selected instructions and makes no provider call:

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/meaning-consistency-experiment/experiment.py \
  replay baggage classification --output .tools/classification-probe-replay
```

## Results

| Source | Variant | Accepted statements | Reported tokens |
| --- | --- | ---: | ---: |
| Baggage | Control | 6 | 5,817 |
| Baggage | Classification | 5 | 12,125 |
| Baggage | Consistency | 6 | 5,725 |
| Invented negative-force contrasts | Control | 11 | 4,248 |
| Invented negative-force contrasts | Classification | 10 | 3,613 |
| Photos | Control | 11 | 10,149 |
| Photos | Consistency | 10 | 8,742 |
| Leave | Control | 10 | 8,314 |
| Leave | Consistency | 8 | 7,188 |

Nine calls used 65,921 reported tokens, including model thinking. No retries,
repair calls or model review calls were made. Statement count measures output
size, not quality or coverage.

The classification instructions produced the intended distinction between
absence of a duty and absence of a prohibition. However, in the invented case,
the registration duty and tool prohibition lost their exceptions from their
baseline statements. The exceptions survived only as separate statements.
Baggage rules also merged, reducing independent referenceability.

The consistency instructions restored the firearm declaration's recipient,
content, timing and oral-or-written alternatives in its statement. Its logical
evidence now includes the complete four-condition list. But another baggage
scope lost all three applicability cases. In leave eligibility, governing
evidence improved while the definition lost explanations of the flight-crew
and outside-US cross-references; their bare citations remained.

Fresh controls already corrected some previous photo and leave failures.
Their request JSON is identical to the corresponding saved adoption requests,
yet their responses differ. Temperature 0 did not make these observations
repeatable. One observation per cell cannot separate a prompt effect from
ordinary variation or establish a general improvement.

All nine captures replayed to identical compiled books without provider calls.
All passed Core graph validation, with no parse failures or rejected candidates.
Raw statement, scope, kind and modality values survived compilation unchanged.
These checks establish reliable processing; the source review still finds
semantic errors.

See [source-review.json](source-review.json) for twelve findings with source and
output evidence, and [verification.json](verification.json) for replay, request
comparison and token accounting. [design.json](design.json) and
[criteria.json](criteria.json) preserve the predeclared experiment.

The next candidate is an output-order-only comparison: generate the complete
statement before its classification and supporting fields, keeping field
meanings and instructions fixed. That hypothesis remains untested here. No
treatment from this experiment changed production code.
