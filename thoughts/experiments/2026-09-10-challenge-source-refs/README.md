# Challenge passage references integrated locally

**The live check accepted and applied all five saved railroad link proposals,
including the one previously rejected after the model changed a thin space.**
This is a bounded citation-reliability check, not a general accuracy result.

The refinement challenge now reuses `audit.SOURCE_REFS`, derived from the canonical
CUE schema, plus `extraction.passage_catalog`, `resolve_passage`, and the audit's
source-map guard. It supplies selectable source passages instead of asking the
model to copy quotations. Decoded judgments retain the model's reference selections
and exact original source spans. Both recovery and relationship challenges use
this shared implementation. Proposal quotation checks are unchanged; no fuzzy or
whitespace fallback was added. Shared quotation compression remains experimental.

## Verification

- All 427 extractor package tests and six schema-generator tests passed. Sixteen
  new cases cover the original thin-space quotation, repeated text at distinct
  offsets, layout preservation, empty/invalid/mixed references, unsupplied gaps,
  context and selected-claim evidence, inserted text, duplicate judgments, and
  supported/unsupported/unknown verdict preservation.
- Existing full refinement tests verified review history, refusal, source identity,
  and complete offline replay using a simulated provider. These are integration
  tests, not live-model accuracy measurements.
- One real Gemini 3.8 Flash challenge used the unchanged five proposals and source
  packet from the failed catalog cell. Temperature 0, normal provider-default
  thinking, 32,768 output cap; no retry. All five returned valid references and
  supported verdicts, and all five edits applied through the normal review store
  in an isolated copied workspace. Saved decoding replay and store reload matched.
- Reported usage: 27,976 input, 603 answer, 1,425 thinking, 30,004 total tokens.
  This was one integration call, not a paired cost comparison.

## Manual reading

P0000 selects F000 (the baseline) and F025:F026 (the no-stop parent and first
exemption). The resolver retrieves the original `§ 390.5` with U+2009 and original
offsets. P0001–P0004 select F000, F025 and their individual exemption passage.
The judgments identify the limited stopping exception; they do not target the
gear-changing or sign-consent requirements. The final records retain the original
meanings and change only the permitted qualification links.

All governing parent and target passages are present in the returned evidence.
This observation does not prove that another model call will select the right
passages or detect every missing relationship. The refrigerant target-discovery
omission was not retested or repaired here. The earlier catalog experiment remains
a failed adoption gate; this new check does not rewrite that outcome.

See [the pre-call plan](PLAN.md), [captured response](challenge/attempt-0000.response.json),
[decoded evidence](decoded.json), [applied events](outcomes.json), and
[verification](verification.json). The original captures remain unchanged.
