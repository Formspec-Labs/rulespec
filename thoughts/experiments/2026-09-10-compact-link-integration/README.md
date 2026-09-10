# Compact existing-exemption links integrated locally

The relationship proposal schema accepts a small `link` operation alongside full
condition/exception additions and edits. A link names the existing exemption,
target aliases to add, and rationale. Code copies the current meaning fields from
the CUE-generated schema and the source quotation, retains existing targets, and
expands the request into the existing review edit. No new Core record or persistent
meaning field was introduced. Recovery keeps its existing complete proposal format.

This adopts the bounded efficiency result from the parallel copying experiment.
Compression, candidate enumeration and actor-reference fields remain experimental.
Independent per-target challenge judgments remain an untested proposal.

## Verification

All 440 extractor package and schema-generator tests passed. Added checks exercise
invalid/missing/self targets, attempted meaning changes, preservation of existing
targets, unchanged packets, stale claim identities, concurrent review revisions,
mixed valid/invalid rows, stage-specific schemas and complete recorded refinement
replay. The ordinary source challenge and preview/application checks remain in use.

A two-call real endpoint check used the original saved railroad packet with the
new combined proposal schema and current relationship prompt. Gemini 3.8 Flash
returned five compact `link` proposals; all five decoded, passed source challenge,
and applied in an isolated copy. Original meaning and evidence remained identical.
Saved decoding replay made zero provider calls, and ReviewStore reload matched.
This is a one-case integration check, not a new accuracy or savings comparison.

Recorded tokens: proposal 24,983 input / 515 answer / 31,391 total; challenge 28,094
input / 660 answer / 30,306 total. Two calls, no retry. Raw model selections remain
in the response capture; normalized full review edits remain in result/history.

See [check.py](check.py), [result.json](result.json), [run.log](run.log), and raw
requests/responses under `proposal/` and `challenge/`. Historical experiments and
the original extraction are unchanged. Runtime sources are frozen with this check.
Whole-run replay with the new shape is covered separately by the simulated-provider
integration test; this saved live check replays decoding and verifies store reload.

The change reduces model copying. It does not resolve whether a source exception
qualifies an entire grouped rule or only one action within it.
