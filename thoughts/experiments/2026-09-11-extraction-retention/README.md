# Extraction retention: delivered result

The two deterministic fixes preserve more of the same generated output. They are
implemented, tested from source and installed wheels, and delivered to the working
environment. The original captures remain intact. No commit or publication occurred.

The [preregistered comparison](design.md) tests passage ranges crossing omitted
blank catalog entries separately from complete quotations crossing inserted
formatting. Both reuse current passage IDs, source maps and Core evidence records.
No model call, prompt change, model-schema change or new Core shape was needed.

| Processing arm | Parsed candidates | Accepted statements | Passage-range refusals |
| --- | ---: | ---: | ---: |
| Baseline | 334 | 224 | 9 |
| Range fix only | 343 | 224 | 0 |
| Original-source fragment support only | 334 | 327 | 9 |
| Both | 343 | 336 | 0 |

The twelve saved responses include one incomplete response, which remains empty.
These totals count repeated statement occurrences, not distinct legal rules.
Seven Core rejections remain for contradictory kind/modality fields. Optional
component refusals are separate. Recovering output does not establish its semantic
correctness or reverse the failed [context experiment](../2026-09-11-fresh-reference-context/README.md).

The [source suite](application-source-command.log) and
[isolated installed suite](application-isolated-command.log) each record 552 passing
tests, no skips and 10,463 retained warnings. Two subsequent constructed review
controls also pass and are now included in the application tests. They ran separately
after the full suite; this is not a claim that a 554-test full suite was executed.
The [final verifier receipt](verification-final-command.json)
records successful completion. Its [twelve-cell checks](checks.json) verify exact
source support, the compared pre-existing meaning fields, Core graphs, original
graphs and unchanged discovery source-record IDs/text. Negative controls retain
refusals for unseen content, fabricated evidence and invalid source references.

**Identity limitation:** reprocessing changes 52 previously accepted claim revision
IDs, including 48 rule IDs affected by candidate ordering. Original captures remain
unchanged. This qualifies the design's identity-preservation gate; it is not an
unqualified pass on unchanged IDs. The [review comparison](old-review-check.json) confirms identical
baseline/new-source outcomes: the latest normal saved run reloads unchanged, while
the older actor/term example fails in both. Installed controls now verify both
unchanged and changed IDs: original approvals and corrections survive, and the new
output remains pending without copied reviews. The normal saved run reprocesses and
replays successfully. The narrower delivery decision accepts explicit new-run
reprocessing with that review boundary; it does not claim identity continuity or
automatically transfer reviews. R18 retains any future continuity work.

The [pinned wheel inputs](wheel-inputs.json) include the rebuilt extractor and six
dependency wheels. The [delivery checks](delivery-checks.json) verify both
installations against all seven wheels, the extractor's source files, exact export
equality, normal replay and unchanged original captures. Installed commands ran
outside the checkout with source imports disabled. The working installation now
uses the verified retention wheel. Package-byte equality and executed behavior are
recorded separately.

Completed delivery tasks, tracked under R1/R4/R18/R23 in the
[canonical task list](../../plans/2026-09-10-reference-integration-task-list.md):

- [x] Run the isolated installed suite and dependency check outside the checkout.
- [x] Reprocess a normal saved run into a new directory; verify replay, reference/
  discovery export, review reload and the reviewed-claim identity boundary.
- [x] Update the working installation to the verified wheel and check its commands.
- [x] Finish [raw-review notes](raw-review.md) and the delivery receipt; seal the final manifest
  after logs finish. Keep the first attempts, failures and original source captures.

The [isolated command receipt](isolated-retry-delivery-command.json),
[working command receipt](working-delivery-command.json) and
[installation receipt](install-working.json) identify the executed checks. The
first review-control attempt used the wrong paragraph boundary; its original
fixture and failure are preserved and explained in the raw review.

The [progress record](progress.md) lists the earlier implementation checkpoints
and harness failures. Optional-reader runtime capture remains a separate R1
follow-up. No new model call, default change, commit, publication or deployment is
part of this delivery. The failed context-selector intervention remains deferred.
