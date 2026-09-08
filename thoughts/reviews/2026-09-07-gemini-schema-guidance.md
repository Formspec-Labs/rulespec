# Gemini schema decision for the quality iteration

Use one explicit, shared semantic-unit JSON Schema through LangExtract's native
JSON Schema adapter. Preserve every meaning and evidence field. Require the
fields, close the classifications with enums, and explain their meanings with
descriptions. A smaller schema is useful here because it removes repeated
definitions, not because conditions or alternatives are dispensable.

## Guidance checked

Google recommends descriptions, specific types and enums; supports required
properties, arrays and additional-property constraints; and warns that schema
validity does not establish semantic correctness. Large or deeply nested schemas
can be rejected. [Structured-output guide](https://ai.google.dev/gemini-api/docs/generate-content/structured-output?hl=en).

The API distinguishes its OpenAPI-style `responseSchema` from JSON Schema.
Its JSON Schema subset includes `anyOf`, references and definitions; `oneOf`
is interpreted as `anyOf`. Do not depend on exclusive-union semantics here.
[GenerationConfig reference](https://ai.google.dev/api/generate-content#v1beta.GenerationConfig).

LangExtract supports explicit schemas independently of example-derived schemas.
Gemini's explicit path preserves JSON Schema keywords such as
`additionalProperties`. Its extraction wrapper still uses an `extractions`
array. [LangExtract explicit-schema documentation](https://github.com/google/langextract/blob/main/docs/examples/output_schema.md).

The SDK recommends avoiding duplicated JSON schemas or JSON-output examples in
the prompt. The implementation retains invented semantic demonstrations as
plain text; the provider schema defines the JSON output.
[Python SDK guidance](https://googleapis.github.io/python-genai/#json-response-schema).

Checked against installed LangExtract 1.6.0 and google-genai 2.22.0. Locally,
`GeminiSchema.from_examples` sends `response_schema`;
`GeminiSchema.from_schema_dict` sends `response_json_schema`. The current web
guide also shows `response_format`, which the installed SDK does not expose as
a typed `GenerateContentConfig` field. The documented native JSON Schema path
is supported by this installation and was tested live; no SDK upgrade was
needed. These findings were checked on 2026-09-07.

## Controlled request-acceptance experiment

All four probes used Gemini 3.8 Flash, the same empty-input instruction,
temperature 0, one candidate and 256 output tokens. Request and response files
are retained in
`examples/document_understanding/quality-iteration/schema-investigation/probes-01/`.
The script records sanitized error classes/codes without provider error strings
or credentials.

| Schema | API field | Serialized size | Result |
| --- | --- | ---: | --- |
| Eleven repeated kind-specific shapes | `response_schema` | 10,955 | HTTP 400 INVALID_ARGUMENT |
| Same shapes, nullable converted to JSON Schema | `response_json_schema` | 10,867 | HTTP 400 INVALID_ARGUMENT |
| Shared shape, example-derived | `response_schema` | 1,141 | Accepted |
| Shared shape, all fields required, closed objects/enums | `response_json_schema` | 1,922 | Accepted |

Both successful responses named model version `gemini-3.8-flash` and returned
an empty extraction list as instructed. These probes test request acceptance,
not extraction quality. They implicate schema shape/complexity and rule out
changing the adapter alone as a sufficient fix for this request. They do not
establish Google's exact internal rejection limit.

Before the probes, a real extraction with the shared example-derived shape
produced 14 accepted records and no refused records. Its raw output retained
the five document alternatives and the inherited emergency branch conditions.
Detailed semantic evaluation is separate and remains necessary.

## Implementation and compatibility

The extraction schema adds descriptions beyond the strict probe. It retains
kind, modality, conditions, context, choices, alternatives, thresholds in
`logic_text`, territorial scope, component evidence and relationship targets.
The deterministic application parser and Core compiler remain authoritative
for local validation. Schemas do not decide which parent condition governs a
child or whether an exception has the right baseline.

New runs record the native schema field and plain-text example format.
Reprocessing older captures reconstructs their original OpenAPI schema and
JSON-example prompt exactly. Captures are copied unchanged to new output
directories; old extraction or review records are not rewritten.
