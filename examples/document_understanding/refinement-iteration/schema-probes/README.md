# Refinement schema acceptance

Four controlled Gemini 3.8 Flash requests used identical empty-input instructions
and temperature 0. The proposal schema with `maxItems: 8` failed with HTTP 400
`INVALID_ARGUMENT`. The identical schema without `maxItems` succeeded, as did
the proposal-only variant and the existing extraction schema.

Keep all semantic fields, required properties, closed objects, enums and field
descriptions. The local parser continues to enforce the eight-proposal bound;
the prompt states it as well. This isolates a provider schema-acceptance problem,
not an extraction-quality improvement or a reason to remove meaning fields.
Requests, responses and sanitized results are retained here.

The earlier `slice-01` attempted six requests, including two rejected proposal
requests, and applied no changes. The next slice uses the same source and initial
state with the corrected schema transport.
