# Extraction quality decision after the September 9 experiments

Keep the current extraction workflow. The experiments support using it for
source-backed discovery and the audit for review triage. They do not justify
another prompt patch or automatic acceptance of complete executable rules.

| Question | Observed result | Decision |
|---|---|---|
| Does stronger standalone-statement wording fix the known omissions? | No relative target improvement in eight calls | Do not adopt the description change |
| Does joining a split governing sentence fix the standalone statement? | Full logic context recovered in 2/2 treatments; statement fixed in 0/2 | Do not adopt a general merge policy from this diagnostic |
| Can the current audit distinguish incomplete wording from complete logic? | Original failure missed 2/2; complete-logic variant inconsistently assessed; complete statement accepted 2/2 | Keep audit findings advisory; a pass is not completeness |
| Does audit catch explicit semantic contradictions beyond that notice case? | Four planted actor/negation/alternative/deadline changes detected; four original targets accepted | Reuse existing audit for review triage, with limited evidence about general reliability |

Evidence: [description experiment](../../examples/document_understanding/standalone-qualification-experiment/README.md),
[passage boundary](../../examples/document_understanding/passage-boundary-experiment/README.md),
[audit field distinction](../../examples/document_understanding/audit-field-distinction/README.md),
and [mutation sensitivity](../../examples/document_understanding/audit-mutation-sensitivity/README.md).
The 26 model calls across these four experiments used 568,045 provider-reported
tokens. All their comparisons/extractions replay; one comparison harness needed
a documented manifest-verifier correction with its original runner preserved.
Replay and exact source grounding do not establish semantic completeness.

For search, tagging and knowledge-graph discovery, use the existing low-thinking
extraction with source passages and `logic_text` retained. This matches the user's
tolerance for useful imperfect records and later feedback. Do not make the broad
audit mandatory merely to get a green status; the experiments show that its pass
can overlook the specific completeness criterion.

Before deriving a workflow or form, use audit findings to prioritize a source
review. Pay particular attention to who a rule governs, inherited conditions,
exceptions, alternatives and relative deadlines, including records the audit
accepted. The original evidence and review history remain the foundation; a
schema-valid record or model verdict is not a final approval.

The latest evidence adds no production feature. Passage-reference reliability and
source-preserving discovery were already integrated before these experiments.
Adding new schemas, a fuzzy layer, another blanket instruction or automatic
condition inheritance is not supported by these results. A useful next product
step is to exercise the existing workflow on an actual downstream task and record
which source-backed corrections users need, rather than keep retuning the same
development sentence.

Limits: sources and mutations were selected development cases; reviewers were
agents with revisable judgments; the masked reviews were not independent blind
validation. Mutations measured clear planted contradictions, not naturally
occurring error frequency. Repeats were small. One audit explanation overstates
either/or as exclusive, and inherited qualification failures persist. No claim of
general extraction accuracy, comprehensive coverage or release readiness follows.

This is a tested recommendation, saved locally and uncommitted. The user subsequently
requested an aggregation of changes to propagate after completing the experiment.
The [production propagation plan](../plans/2026-09-09-production-propagation.md)
separates ready documentation/evaluation updates, an explicit thinking-default
decision, already-integrated capabilities and unsupported changes. No further
provider calls are pending. Do not manufacture a semantic change to turn a negative
experiment into an implementation milestone.

## Subsequent implementation

The user authorized the propagation plan. Research and the maintained evaluation
index are committed in `beb3fbf`; the operating guide now reflects the completed
checks. CLI/library thinking defaults are low extraction and medium audit. This
is configuration promotion, not a demonstrated semantic improvement. See the
[implementation check](../../examples/document_understanding/production-defaults-check/README.md)
for fresh verification and the retained failures. Original reports and captures
preserve their historical decisions.
