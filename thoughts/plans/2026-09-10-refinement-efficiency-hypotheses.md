# Competing ways to make refinement cheaper without losing meaning

## Question and evidence to collect first

Decision: which intervention should receive the next live test: fewer stages,
smaller input packets, smaller output proposals, or narrower source evidence?

Observed: two fresh full workflows added seven correct links, preserved all
original statements, and used 245,683 reported tokens versus 12,140 for their
initial extractions. Both recovery calls were empty. Repeated evidence is visible,
but that observation alone does not establish how much of the cost it causes.

First test is offline accounting of those saved captures. Attribute reported
tokens to stage and measure serialized sections of the actual model packets.
Do not count copied base runs, workspaces or replays. Keep missing usage fields
distinct from zero. Character counts describe packet size, not billed tokens.
Do not infer savings from removing a stage while assuming later calls stay unchanged.

Cases: the two immutable end-to-end captures, with no altered claims or provider
calls. Held constant: all historical request/response bytes. Stop after accounting
both runs. Preserve a small script and its results beside the captures. This only
prioritizes experiments; it cannot establish causal accuracy, latency or savings.

## Competing hypotheses and solutions

| Hypothesis | Candidate solution | Observable prediction | What would weaken it |
| --- | --- | --- | --- |
| Repeated source/evidence dominates input cost. | Send each exact source span once in a shared evidence catalog; claims refer to existing span identities and roles. | Smaller packets with identical reconstructed claim/evidence data; live linking remains faithful. | Savings are small, or indirection causes lost conditions/wrong targets. |
| Unnecessary stages dominate cost when the draft is already faithful. | Offer extraction → relationships → challenge for link enrichment; reserve recovery/coverage audit for completeness work. | Similar links at substantially fewer calls on faithful drafts. | Missing upstream meanings or audit context prevent correct links; streamlined mode is mistaken for complete review. |
| Complete replacement records make tiny edits expensive and fragile. | A model-facing link edit names only the current claim, targets and source-based justification; deterministic code fills unchanged fields through the existing edit path. | Shorter answers and no copy-induced refusal or meaning change. | Most cost is elsewhere, or omitted context harms target choice. |
| Source-range selection, rather than encoding alone, introduces distracting siblings. | Main evidence uses the child passage; inherited wording uses separately referenced parent passages. | Less irrelevant neighboring material and better component grounding. | Parent scope is lost, multi-passage support fails, or target accuracy declines. |
| Long audit histories distract relationship generation and repeat model judgments as facts. | Give the relationship task source, current claims and evidence; omit prior audit rationales while retaining them in the saved record. | Lower input cost and equal or better links. | Audit observations supplied needed omissions or governing scope. |
| Most qualifying relationships are already structurally explicit. | Resolve explicit local section references deterministically into target candidates, then have the model validate meaning. | Fewer model-selected targets and lower search effort on structural cases. | Cross-references are definitions/examples rather than governing scope; candidates omit valid remote targets. |

These causes can coexist. A shorter packet can reduce both input and reasoning
work; an uncontrolled before/after cannot attribute the two effects separately.
Likewise fewer stages changes the information available, not merely the bill.

## Reuse boundaries

- Keep Core claims, `RelationshipAssertion`, `EvidenceBinding`, revision history
  and review validation unchanged. No new storage schema is needed.
- Reuse `refinement._packet`, `_model_packet`, `_proposal_prompt`, `_decode_proposals`,
  `_decode_checks`, `_action` and ReviewStore, plus recorded provider capture/replay.
- The prior `retrieval-context/compact.py` merges overlapping exact source intervals
  and preserves member references. Its six-case display result was 27.5% fewer
  characters, not a proven reduction of these model requests. Adapt its consumer
  view rather than add another persistent evidence field.
- Current `_model_packet` already aliases IDs, and `_challenge_prompt` already
  removes a duplicate complete proposal copy. Do not count those as new changes.
- A specialized link-edit response would be a smaller application view built from
  the canonical schema, then expanded into existing edits. It is separate from
  lossless input compaction and needs its own experiment.
- Section references can nominate targets, not prove applicability. Preserve
  ambiguous/unresolved matches; keywords and proximity must not establish edges.

## First live comparison to run after the offline result

Test only lossless packet encoding first if the measured packet duplication is
material. This is the least semantic change; the alternatives above remain
competing follow-ups, not a combined patch.

Arms: A current relationship/challenge packet; B the same information with exact
evidence stored once and claim fields referencing it. Same prompt intent, output
schema, model settings, draft, source, audit history and decoder. Use a deterministic
expansion check to prove B reconstructs every original quote, offset, identity,
role, statement, condition and target before any live call. No fuzzy equivalence.

Cases: the two saved end-to-end initial drafts as development diagnostics plus one
untouched document from another family, selected and labeled before any extraction.
Use one shared fresh extraction for that new document. Include a remote governing
condition, a neighboring duty that remains binding, repeated identical wording at
different offsets, disjoint evidence, Unicode offsets and a nested OR/AND condition.
Do not edit these historical drafts to make a failed arm appear successful.

Freeze expected target sets and semantic counterexamples before calls. For each
case, run one fresh relationship proposal and, if mechanically valid proposals
exist, one fresh challenge per arm. Apply supported changes only in isolated review
workspaces, then compare final exported meaning and targets manually. Randomize
arm order and hide arm labels during judgment where possible. Keep every refusal,
wrong proposal and failed challenge. Historical outputs are not the control arm.

Bound: at most 13 live calls (one shared new extraction plus twelve proposal/challenge
calls), one sample per cell, 20 minutes before starting the next call, no retries.
Use the same current normal settings in both arms; preserve actual requests. Do not
compare medium-thinking candidates with provider-default-thinking controls.

Decision rule: all offline identity/evidence counterexamples pass; no new semantic
or target regression on any case; at least 20% lower aggregate recorded input tokens
in the paired stages. Compare answer, thinking, total tokens and latency separately;
do not hide a total-cost regression behind input savings. If either semantic safety
or the savings threshold fails, do not adopt. Smaller bounded benefits can motivate
a different explicit decision, not a retroactive pass. One sample cannot establish
stability or general accuracy.

This is a saved live-test design; the live comparison has not run. No default
workflow change, commit or deletion of original evidence was performed.

## Offline result and prioritization

The saved captures attribute 105,794 tokens (43.1% of the full run) to relationship
proposal/challenge, 86,114 (35.1%) to the initial/final audits, and 41,635 (16.9%) to
the two empty recovery calls. Extraction accounts for the remaining 12,140 (4.9%).
These are historical stage costs, not savings proven achievable by deleting calls.

The two model-facing relationship packets total 152,984 serialized characters.
Prior unit/claim judgments occupy 50,256 characters (32.9%); the raw focus source
occupies only 5,826 (3.8%). Claim objects occupy 73,812 (48.2%) and include evidence,
statements, source quotes and metadata. These categories are value sizes; punctuation
and top-level field names account for the small remainder. Character share is not
provider token share, and none of these numbers isolates repeated text alone.

This supports two separate small-input candidates: lossless evidence cataloging
and omission of prior audit judgments. It does not prove either is safe for model
accuracy. Keep the lossless candidate first because reconstruction is testable;
if it cannot meet the preflight size threshold, test audit-judgment omission next
as a separate information-removal intervention. Retain source, current statements,
all qualifications, exact evidence and unresolved findings outside the removed
judgment lists. Record any policy choice about whether omission findings are part
of the linking task; do not hide that scope change.

A smaller link-edit response remains useful for simplicity/copy reliability, but
answers across the two relationship proposals total only 4,695 tokens. Even an
impossible zero-token response would remove less than 2% of this full workflow's
reported tokens. It is not the leading whole-workflow cost hypothesis, although a
smaller task could also change reasoning cost, which needs a live comparison.

Accounting artifacts:
`thoughts/experiments/2026-09-10-refinement-cost-accounting/account.py` and
`results.json`. No new provider calls or production changes.
