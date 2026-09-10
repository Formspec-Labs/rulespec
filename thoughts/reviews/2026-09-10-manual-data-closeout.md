# Manual data review of the consistency update

The user requested direct data inspection instead of the blocked final browser
pass. This review reads existing source, captured outputs, review events, exported
records and retained test databases. No new provider calls or test executions were
made. It does not claim that the remaining browser interactions were exercised.

## Data behavior confirmed

- **Names and senses:** the constructed source defines access record and annual
  report, both abbreviated AR. The exported registry retains two IDs and explicit
  library/finance definitions. The comparison statement links both; finance duties
  link the annual-report sense. Definitions do not link themselves as uses.
- **Partial enrichment:** in the actual captured enrichment, the existing access-
  record link remains and the missing annual-report link is added. The statement
  remains “An access record is not an annual report.” The edit records the actual
  model, request/input digests and source capture. See
  [captured result](../../examples/document_understanding/consistency-transfer/partial-enrichment/capture/step-0000/result.json).
- **Actor correction:** Staff is proposed but withheld because the word occurs
  twice in the paragraph. This is location ambiguity, not evidence that the actor
  is unknowable. The later correction uses “Staff must file the access record.”
  at offsets 1069–1103. The reviewed export contains actor Staff with that evidence,
  keeps the logical rule ID, uses a new revision, and remains pending. The earlier
  observation remains a Core Finding against the old revision. A separate ambiguous
  modality warning remains; fixing the actor does not falsely clear it. See
  [reviewed data](../../examples/document_understanding/consistency-transfer/partial-enrichment/reviewed.json)
  and [consumer export](../../examples/document_understanding/consistency-transfer/partial-enrichment/reviewed-discovery.json).
- **Editorial edit versus replacement:** read retained SQLite events from the
  completed tests `test_editorial_definition_and_0` and
  `test_replaced_or_rejected_defi1` under pytest-3777. Removing RN as an alias and
  rewording its definition retains term ID `4306251d…`. Explicit replacement omits
  the old ID and produces `013af271…`; the old use still references `4306251d…`.
  This preserves the distinction between correcting a sense and replacing it.
  These are constructed regression fixtures, not provider-quality evidence.
- **Qualification targets:** read the actual saved events for
  `test_qualifications_require_co0`. The road-closure qualification initially
  targets departure revision `9665e897…`. Editing the departure statement creates
  `16342292…` with the same rule ID; the next explicit qualification edit targets
  that new revision. The stored history retains both transitions. This supports
  identity-based target confirmation, not automatic semantic linking.
- **Real review history:** read the isolated passport preview SQLite database in
  read-only mode. Its second edit removes IRLs from aliases while retaining term
  ID `11bb3bb3…`; the third event rejects the edited defining revision. Earlier
  names, evidence and edits remain recorded. The first edit was a no-op and remains
  visible rather than being rewritten out of history.

## Meaning still needs work

The current paragraph passport capture says “Posts must use the cleared language
in the IRLs.” Its local-modification authorization appears in the following claim.
The source joins them with “but”; retrieving the first claim alone loses that
qualification. Its empty issues list does not establish semantic correctness.
See [captured output](../../examples/document_understanding/consistency-transfer/cells/cell-01/raw-model-text.txt).

The first-aid data keeps the clinic-proximity condition on training, but leaves
supplies as a separate unconditional statement. Whether that second sentence
inherits the condition is a source-reading uncertainty, not something this review
resolves by assertion. The live audit also accepts an imprecise optional scope
phrase, “to employers in these circumstances.” The recorded correction makes that
scope explicit while retaining the already self-contained statement and possible
modality. The audit separately reports missing introductory background content;
its failed verdict is retained, with no processing errors.

The recording definition preserves the 14 first-aid alternatives and major
exclusions. But explicit term uses are incomplete: the medical-treatment checkbox
statement mentions both medical treatment and first aid while linking only medical
treatment. Better-defined concepts do not automatically yield complete concept links.
See [paragraph result](../../examples/document_understanding/consistency-transfer/cells/cell-08/raw-model-text.txt).

## Repetition and interpretation cautions

The discovery export shares evidence offsets and omits empty optional statement
fields. It is leaner than the full review record, but not fully normalized:
`terms[id].definition` repeats the defining statement, and evidence roles still
include both `defined_terms:0` and `defined_terms:0:source:0` when both use one span.
The full review representation also repeats the main defining paragraph in
`quote`, definition evidence and `source_quotes`. Those local copies do not prove
extra model output tokens; the raw model emitted passage references instead.

Full history/graph exports intentionally contain prior revisions and findings.
Consumers should distinguish current statements from historical observations. An
observation tied to an old revision is historical after an edit; that fact alone
is not proof its underlying semantic problem was repaired. In the Staff case,
the new explicit evidence supplies that proof for the actor field.

## Conclusion

The inspected data supports identity continuity, explicit replacement, retained
provenance, visible refusals and deterministic target confirmation. The remaining
quality risks are incomplete standalone meanings, missed term uses, ambiguous
component locations and avoidable serialization repetition. These findings support
closing the implementation/data verification work; they do not establish a general
accuracy rate or semantic completeness. The separate sentence-reference experiment
already closed with no adoption. Further extraction tuning is a separate decision.
