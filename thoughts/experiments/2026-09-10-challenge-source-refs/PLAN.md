# Challenge source-reference integration check

Decision: verify the production passage-reference change against the saved railroad
challenge failure. Reuse the identical five prepared proposals and source packet
from evidence-catalog cell-05; change the challenge to the existing source-reference
schema/resolver. One live challenge call, current normal settings, no retry or tuning.
Keep source, raw request/response, decoder failures and applied results in a new
isolated workspace. The original experiment remains unchanged.

Expected: all five judgments select valid supplied passages, including the no-stop
condition, exemption and targeted rule. Exact retrieved evidence retains U+2009;
model verdicts must be assessed separately. Unsupported/unknown verdicts must not
apply. Unit controls cover bad references, unsupplied gaps, repeated locations and
inserted text. This smoke check cannot establish broader semantic improvement or
repeatability. A constructed reference response in the unit test verifies the
resolver only; it is not a recovered provider response.
