# Why actor and definition enrichment produced mixed results

Follow-up interpretation of the frozen
[six-call comparison](../../examples/document_understanding/actor-definition-check/README.md).
No new calls or production changes. Original captures and judgments remain intact.

## Observations that narrow the explanation

Actors and defined terms were explicit in these selected sources. Both enriched
arms captured the checked roles, aliases and links correctly; null counterexamples
held. The baseline never requested these structures, so its empty actor fields
do not demonstrate a model comprehension failure.

All three passport arms already emitted both a Posts requirement and a separate
modification permission. The difference was not the number of rows: the baseline
also retained the permission's qualification in the requirement statement; both
enriched arms removed that overlap. The requirement became less faithful when
read alone even though the document's permission survived elsewhere.

Reinspection also separated new field cost from changed output style:

| Case | Arm | Nulls in pre-existing optional fields | Nulls in added fields |
|---|---|---:|---:|
| Passport | Baseline | 0 | 0 |
| Passport | Actors | 114 | 16 |
| Passport | Actors + index | 123 | 32 |
| Controls | Baseline | 0 | 0 |
| Controls | Actors | 0 | 12 |
| Controls | Actors + index | 73 | 23 |

The unchanged nullable fields were all emitted in three enriched outputs. Actor
fields alone did not always trigger this behavior: controls stayed sparse. The
reported token growth is therefore not the isolated price of useful role/link
values. Null counts are directly computed JSON observations, not token estimates.

## Competing explanations and predictions

1. Structured extraction favors individually typed propositions. A must row and
   a may row look internally tidy when their wording follows only their respective
   modality. This conflicts with the requirement that each statement preserve
   its own qualifications. Prediction: mixed obligation/permission and exception
   passages are more vulnerable than simple single-modality passages. The present
   data cannot establish that actor slots caused this change.
2. Required-nullable additions may encourage a complete-template output style,
   spreading null emission into optional fields that the baseline omitted.
   Prediction: holding source/meaning fixed, requesting only the enrichment or
   varying the added fields' requiredness changes empty-field output. Existing
   controls show this is not inevitable. Earlier omission experiments caution
   that suppressing placeholders may also suppress useful content.
3. Sampling variation may explain some or all statement differences. One call
   per cell cannot distinguish a reliable schema effect from an incidental one.
   Prediction: repeated controls sometimes show the same qualification loss.
   The agreement of two enriched cells is suggestive, not causal proof.

The early index cannot alone explain the qualification loss: actor-only also
lost it and kept the statement first. Its incremental link accuracy is supported
on these explicit definitions, but multi-sense terms, competing definitions and
cross-document resolution remain untested. Output was far below the 16,384-token
cap; these observations do not establish context overload or token exhaustion.

## Engineering implication

There are separate questions: can the model identify useful roles/terms, can it
preserve complete rule meaning while doing so, and can it emit only useful data?
These runs support the first on selected cases and expose risks in the latter
two. A next test can enrich frozen statement IDs without allowing rewrites and
compare cost, omissions and wrong links. That protects statement text by design;
it does not establish enrichment accuracy. Any integration must retain the
original evidence and source context and report unresolved relations explicitly.
