# Interpretation fields before or after the statement

**No measured improvement on the predefined statement checks. Do not adopt this
prompt/order change.** All three arms passed 17 of 18 selected checks and missed
the same standalone notice qualification. The early arm omitted interpretation
on both real documents, so this did not establish whether a substantive explanation
generated first would improve those statements. The late arm produced more
explanations, but also more output and incomplete structured scopes.

## Comparison

The [plan](PLAN.md) was saved before calls. [Review criteria](REVIEW.md) were
expanded into explicit checks before inspecting outputs. Nine fresh calls used
Gemini 3.8 Flash, temperature 0, low thinking and a 16,384-token output allowance:
one call per arm on each full notice, waste and constructed-control document.
No retries, audit calls, repairs or additional runs were made.

- **B, current:** unchanged current CUE-generated schema and extraction prompt.
- **L, interpretation late:** added an instruction to use existing `scope_text`
  and `choice_text` for inherited conditions and nontrivial choices. Existing
  schema order keeps them after `statement`.
- **E, interpretation early:** identical to L, moving scope/choice and their
  evidence fields before `statement`. Only schema property serialization order
  differs between E and L. Field types, requiredness and descriptions are identical.

No new reasoning field, schema definition, parser or production code was added.
The experiment reuses native CUE-generated types and existing request capture,
passage resolution, parsing and Core validation. The focused instruction remains
experimental. Exact schemas, settings and dispatch order are in [design.json](design.json).

## Results

| Arm | Selected statement checks | Interpretation rows | Input tokens | Output tokens | Output change |
| --- | ---: | ---: | ---: | ---: | ---: |
| Current B | 17/18 | 4/40 | 7,858 | 5,731 | — |
| Early E | 17/18 | 4/38 | 8,368 | 5,876 | +2.5% |
| Late L | 17/18 | 17/38 | 8,368 | 6,996 | +22.1% |

These checks are hand-selected development assertions, not overall accuracy.
Row counts reflect different segmentation choices, not semantic completeness.
All 116 rows passed the generated schema, parsed without refusals, and were
accepted by Core; all nine graphs passed validation. Nonfatal issues remain
below. The provider reported 43,197 total tokens across nine calls. Thinking
token counts were null/unavailable, not established zero. Usage is preserved in
[metrics.json](metrics.json) and every raw response.

The actual requests retained the intended ordered schema. All emitted keys
followed the corresponding schema order. However, most early rows omitted the
interpretation fields, making a key-order pass uninformative about the proposed
mechanism:

| Case | B interpretation rows | E interpretation rows | L interpretation rows |
| --- | ---: | ---: | ---: |
| Notice | 0/18 | 0/18 | 1/18 |
| Waste | 0/15 | 0/13 | 11/13 |
| Constructed controls | 4/7 | 4/7 | 5/7 |

Only four E rows actually emitted scope/choice interpretation before the
statement, all on the synthetic control. E's absent interpretation on the real
documents is instruction non-adherence, not evidence that successfully performed
early interpretation cannot help.

## Raw source/output findings

Every notice arm still extracted the designated-number/person permission without
its unforeseeable-leave setting and unusual-circumstances qualification. E added
"As an example of usual and customary requirements" but still omitted both limits.
The preceding rule retained them; the independently referenceable example did not.
This reproduces the actual historical miss rather than replacing it with an easier
test. Stabilization/phone conditions, first-time versus repeat requests, and the
qualified practicability expectation survived in all three arms.

All waste arms retained the tested quantity proviso, remote exceptions, container
venting alternatives, both labeling components, three-day deadline and removal
destinations. All constructed-control statements retained the right branches,
credential alternatives, recommendation and descriptive fact.

There were useful secondary differences, which do not change the predefined
17/18 scores:

- L explained the nested venting options and three removal destinations correctly.
  Those meanings were already retained in the statements in B and E, so this is
  added explanation rather than a demonstrated repair.
- Several L waste scopes repeated only the satellite-exemption parent while
  omitting local conditions/exceptions. The statements were complete on those
  checks, but the separately populated scope fields were incomplete under the
  existing ALL-conditions guidance. E's temporary-pass control scope likewise
  omitted imminent travel while its statement retained it.
- E waste statements omitted parent satellite-exemption framing on several later
  rules; B and L explicitly retained it. This is a standalone-applicability risk,
  not evidence favoring early placement.
- B waste omitted illustrative hazard-label methods from the explicit statement;
  E and L retained them. Both mandatory label components remained in B, so W4
  passes. This selected example-retention difference does not establish a stable
  improvement or satisfy the no-incomplete-interpretation adoption condition.
- L's constructed credential explanation says entry "requires" either credential,
  while the source describes permission to enter with either. Whether that implies
  unsupported necessity needs review. Its statement remained source-faithful.
- Notice modal classifications varied for expected conduct and "may not be
  required"; the statements retained the source wording. These are unresolved
  classifications, not silently assigned gold answers.

Core retained 24 nonfatal issues across the nine outputs: ambiguous modal-word
evidence, scope evidence without populated scope meaning, and verbatim logic
marked for review. In particular, B waste emitted scope references without scope
text on nine rows. Passing schema/graph validation does not mean every optional
field pair is coherent or semantically complete. Original issues are retained.

## Interpretation and decision

The requested intervention did not reliably produce substantive interpretation
on the actual failure. The late instruction increased interpretation population
on waste, but the known notice miss persisted. The output-order intervention
also changed which optional fields were emitted; this experiment cannot isolate
a benefit of explanation placement conditional on equal explanation content.
It does not reveal the model's internal reasoning.

Keep production unchanged. This result weakens the proposal to encourage/reorder
the existing fields as a general extraction improvement. It leaves the original
idea of a distinct, brief interpretation note unresolved: that field was not
tested. If pursuing it, first test whether the model actually emits a specific
condition-binding explanation on the known failing notice example, then assess
its statement and counterexamples. Do not count an explanation as a substitute
for retained rule meaning, or keep adding prompt patches without a new prediction.

One call per cell does not measure within-case variability. These documents have
been used for development, and the synthetic controls partly overlap existing
prompt demonstrations. Codex reviewed canonicalized outputs under randomized
opaque IDs without arm labels, output order or usage before unblinding. Behavior
itself can make a treatment recognizable; this is not an independent human
review. The saved [blind review](blind-review.json) contains revisable judgments,
row references and separate primary/secondary observations.

## Verification

Offline checks verified identical E/L prompts and schema content, differing
ordered schema hashes, baseline provider configuration, normal Core processing,
and refusal of a null required statement. Live request checks verified model,
temperature, thinking level, output allowance and ordered schema delivery.

All nine captures replay identically with zero provider calls, including parser
results, refusals, Core graphs, validation, raw field order and usage. Runtime,
schemas, sources and review artifacts are hash-pinned; the runtime snapshot is
under `frozen/`. Earlier extraction captures and production files remain unchanged.

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python \
  examples/document_understanding/interpretation-order-check/run.py replay
```

No production adoption, commit, push or deployment is part of this experiment.
