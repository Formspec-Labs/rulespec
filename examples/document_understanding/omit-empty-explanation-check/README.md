# Omit empty logic and modality fields

The omission policy eliminated placeholders and reduced output tokens, but also
eliminated every explanation. Neither field passes the full adoption gate.
Production code, schemas and UI remain unchanged by this experiment.

Eight fresh calls compared required-nullable explanations (N) with optional,
non-null explanations and aligned omission instructions (O). Logic and modality
were tested separately on full notice and waste sources, with one repeat per cell.
Both used Gemini 3.8 Flash, low thinking, temperature 0 and 16,384 maximum output
tokens. The [preregistered plan](PLAN.md) defines the gates and the schema-plus-
instruction bundle; this does not isolate each individual change.

| Field | Source | Output tokens N → O | Reduction | Non-null notes N → O | Statement review |
|---|---|---:|---:|---:|---|
| Logic | Notice | 3,662 → 1,950 | 46.75% | 0 → 0 | Same named checks; known qualification miss persists |
| Logic | Waste | 4,749 → 3,092 | 34.89% | 1 → 0 | Named logic and applicability checks preserved |
| Modality | Notice | 3,937 → 1,789 | 54.56% | 12 → 0 | Same named checks; uncertain enum mappings changed |
| Modality | Waste | 4,857 → 2,991 | 38.42% | 14 → 0 | Parent applicability lost on five independent statements |

N emitted **438 JSON null values**, including 38 explanation slots and 400 other
optional fields. O emitted **zero JSON nulls, empty strings/lists/objects or literal
null/N/A placeholders**. These were JSON null values, not strings containing the
word null. O also omitted many populated scope/modality evidence fields, so the
token reduction cannot all be attributed to removing nulls.

The totals were 17,205 versus 9,822 output tokens (42.9% fewer). Provider-reported
input tokens were 12,230 versus 12,442; total tokens were 29,435 versus 22,264.
Thinking-token counts were unavailable. These are measured tokens, not a pricing
estimate or proof about how the provider bills schema text.

## What survived and what disappeared

**Logic:** the waste control supplied one useful explanation of the excess trigger,
three-day deadline, compliance-or-removal paths and three destination choices.
The omission run retained that meaning in the default statement but emitted no
explanation. Both retained the nested venting exceptions, both required label
components, and illustrative labeling methods. There was no explanation in either
notice run. Statement correctness on these checks therefore does not show that an
explanation improved extraction.

**Modality:** control notes made distinctions such as descriptive possibilities,
qualified expectations and possible consequences inspectable, alongside many
repetitive shall/may explanations. O emitted none. On notice, expected conduct moved
from `should` to `not_stated`, and “may not be required” moved from `not_required`
to `possible`. These remain interpretation questions, not adjudicated gold labels.
The original statement wording retained the qualifications.

The modality waste omission run also dropped the satellite-exemption setting on
rows 4–8: incompatible-waste, nearby-container, separation, closure and labeling
rules became more general when read independently. Their local conditions and
alternatives survived. Neighboring complete records do not repair those omissions.
One run per cell cannot establish that the omission policy caused this regression.

All four notice outputs still missed the inherited unforeseeable-leave and unusual-
circumstances limits on the designated-number/person permission (row 14).

## What the schema can enforce

The isolated CUE variants declare the explanation optional and non-null, with
`#NonemptyText`; only `statement`, `kind` and `modality` remain required. Other
optional enrichment rejects null, and present strings require at least one
character. Native CUE generation produced the provider schemas; no hand-written
replacement schema or production exporter change was introduced.

An offline pre-call check verified that omission is valid, null is invalid for
every optional property, and empty strings are invalid for optional strings. The
exact required-nullable control schemas matched the prior experiment. Actual
requests were checked for schema contents, property order and settings.

`list.MinItems(1)` exposed a current metadata-adapter limitation before any provider
calls: “Only homogeneous model-schema lists are supported.” The plan records the
adjustment. Empty lists remain structurally valid; their omission was requested
by the prompt and observed in these runs. No claim of schema enforcement for
empty lists, whitespace-only text, or literal placeholder strings is made.

Present control explanation keys preceded `statement`. O omitted those keys, so
field order alone did not activate the proposed explanation-first mechanism.

## Decision and next useful test

The zero-placeholder and 20%-token-reduction gates pass for every pair. Logic fails
useful-note retention on waste; modality fails note retention on both sources and
has an additional statement regression. Neither field passes across both sources.
Do not promote this bundled variant as an explanation-preserving improvement.

The next narrow test should separate two decisions. First retain the required-
nullable experimental explanation while making only the other enrichment fields
omit absent values. That isolates the 400 unrelated nulls without simultaneously
making the explanation disappear. Then test field-specific inclusion criteria:
nested alternatives/exceptions/deadline triggers for logic, and ambiguous or
qualified modal wording for modality. Keep straightforward classifications quiet.
This is a proposal, not additional work already run or a production schema design.

## Evidence and replay

Statements were reviewed under opaque IDs before explanations and arm labels.
Optional-key presence can hint at the arm, so this was label blinding, not guaranteed
reviewer blinding. [Statement judgments](statement-review.json) and
[explanation judgments](explanation-review.json) are revisable Codex assessments on
development sources, not independent human gold. [Metrics](metrics.json) include
per-run placeholder locations, key counts, token usage and gates.

All 132 emitted records were accepted, with no schema/response errors, refusals or
rejections; all eight Core graphs validated. Unresolved reference records remain:
two per notice run, and 31–35 per waste run. Validation does not establish semantic
accuracy or completeness. Raw requests/responses, normalized outputs, source
documents, runtime snapshots, generated schemas and judgments are preserved.

From the repository root, replay verifies pinned inputs, actual request settings
and deterministic parsing/Core results with **zero provider calls**:

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/omit-empty-explanation-check/run.py replay
```
