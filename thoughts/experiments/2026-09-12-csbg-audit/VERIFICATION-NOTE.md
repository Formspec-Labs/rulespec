# Correction to the local request checker

The first `run.py verify` invocation failed its request-equality assertion. Its
expected configuration omitted the adapter's `response_mime_type: application/json`.
The actual recorded requests include this normal SDK configuration field. Their
model, prompts, schemas, temperature, thinking level and output allowance match
the planned settings.

Keep the preregistered harness unchanged. `verify.py` below replaces only this
local verification operation, using the same Gemini schema adapter's full provider
configuration, as production replay does. It checks the complete actual request
and reproduces inventory and judgment parsing. No calls were repeated and no
captures, pins, criteria, model settings or production code were changed to make
verification pass. The separate receipt records this correction.
