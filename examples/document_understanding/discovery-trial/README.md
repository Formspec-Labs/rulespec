# Source discovery and component checks

Including source passages recovered explanations that summary-only search missed.
Adding verified scope/context evidence recovered one more question. Narrow component
checks also removed the unsupported issuer node found by the blind review, while
preserving all twelve original claimant suggestions for inspection.

This is a completed local experiment, not a deployed search service. No provider
calls were made. Original captures remain unchanged; reprocessed outputs have their
own provenance and frozen runtime.

## Fixed comparison

`questions.json` fixes twelve questions and exact supporting quotations before any
rankings were produced: four explanations, four rules, and four distractors. Ten
questions have supporting source; two have no established answer in these excerpts.
The author had seen the source reviews, so this is a development diagnostic, not a
blind or held-out benchmark. No queries or ranking settings were tuned afterward.

The standalone [trial script](../../../packages/rulespec-extrapolator/evaluation/discovery_trial.py)
uses the same simple BM25 lexical scorer for three views:

1. Accepted summaries, returning their main source evidence.
2. Exact source passages from `documents.source_passages`.
3. The same source ranking, with accepted units and verified main/scope/context
   evidence attached by source intervals. These associations do not assert legal
   relationships and do not use structural `parent_id` as legal scope.

The script never indexes the serialized meaning JSON, claimant suggestions, typed
values, or concept definitions. It does not generate answers. Source text and
model summaries can still be ambiguous; omitting structured suggestions is not a
general semantic safety guarantee.

| View | First capture pair | Second capture pair |
| --- | --- | --- |
| Summaries | 4/10 | 6/10 |
| Source passages | 8/10 | 8/10 |
| Source plus evidence | 9/10 | 9/10 |

These counts mean **all specified source support appears among the top three
results and their attached evidence**. They do not measure extraction accuracy,
answer correctness, or complete discovery. An exact quote may support a source
result even when the corresponding model summary omits or changes its meaning.
The two unanswered questions are marked unknown rather than counted as passes.

Both source views recover all four explanations, including why name-change
documents are needed for ID and the goal for infant photographs. Source evidence
also restores the governing older-name-change condition for emergency issuance.
Adding evidence recovers the six-month recommendation through the replacement-photo
trigger. No source support recovered by summary search was lost in the evidence view.

All three views miss the required color statement for “Are black and white passport
photographs acceptable?” The lexical scorer instead favors the white infant blanket
example. Both unanswerable questions still retrieve overlapping but insufficient
material. Search results must not be treated as answers or an abstention system.

Evidence has a size cost: mean returned evidence per question rises from 771
characters for source-only results to 1,998 and 2,250 for the evidence views. These
counts include overlap; broad quotations and repeated evidence need presentation
limits before a production integration. No downstream answer-model cost was measured.

## Component admission changes

`enrichment.check_components` now uses existing component issues and Core record
emission paths to withhold two classes of unsupported structure:

- A named claimant must introduce this unit's source quotation using a direct
  form such as `The Office states:`. Institution mentions, citations, negated
  speech, invented names, implied speakers, and document-issuer attribution are
  outside this narrow automatic check. Separate attribution context and verified
  issuer metadata need a later integration; they are not silently inferred.
- An `xsd:duration` must agree with a simple exact year/month/day expression:
  whole digits or one through twelve, a supplied comparator, and an optional
  copied reference event. `one year` admits `P1Y`, not `P2Y` or `P365D`.
  Compound, fractional, ranged, and differently expressed durations remain
  unresolved. Other numeric datatypes do not gain normalization checks here.

These are bounded checks, not a general proof of attribution or temporal meaning.
Original structured suggestions and full rule meaning remain visible. The compiler
does not delete a rule because one optional field is unresolved. Existing Core
schemas, evidence, review state, and capture format remain unchanged.

All twelve unsupported claimant suggestions in `names-repeat` now have issues;
none emits a `SourceClaimant`. All nine duration candidates across the four saved
captures remain admitted. Positive and adversarial tests cover explicit speakers,
mere mentions, cross-references, negation, changed quantity/unit/event, unsupported
conversion, and ambiguous duration wording.

## Evidence and reproduction

| Reprocessed run | Original capture under `extraction-polish` |
| --- | --- |
| `names` | `final-names-2` |
| `photos` | `final-photos-1` |
| `names-repeat` | `selected-names` |
| `photos-repeat` | `polished-photos-1` |

`results.json` and `results-repeat.json` save complete ranked results, admission
counts, input hashes, and the script hash. `verification.json` records identical
original document/request/response/candidate bytes, four passing graph validations,
and verified offline replay of `names-repeat`. `tests.txt` records 295 passing
package/schema tests, including 22 new adversarial and diagnostic tests. Native
CUE generation checks also pass.

From the repository root, write to a new output path:

```sh
.tools/document-poc-venv/bin/python packages/rulespec-extrapolator/evaluation/discovery_trial.py \
  --names examples/document_understanding/discovery-trial/names/rulebook.json \
  --photos examples/document_understanding/discovery-trial/photos/rulebook.json \
  --questions examples/document_understanding/discovery-trial/questions.json \
  --output /tmp/rulespec-discovery-results.json
```

Keep source passages as the inexpensive retrieval baseline. The small gain from
attached evidence warrants a held-out query test before production integration,
particularly for misleading lexical matches and evidence length. No prompt changes,
automatic legal-edge inference, additional extraction calls, or UI work are needed
to retain the verified component fixes and this experiment.
