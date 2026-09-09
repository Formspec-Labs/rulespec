# Hierarchy and window-boundary experiment

**Retain the parser fix; keep model-facing parent hints experimental. Prioritize
keeping a governing list together when it fits in one request.**

This experiment found a concrete input problem: the selected baggage split leaves
neither request with all four firearm conditions. Adding parent aliases cannot
restore source text that was never supplied. The model also omits some conditions
that are supplied as context, so input completeness and semantic fidelity require
separate checks.

## Changes and design

`documents.source_passages` incorrectly treated CFR-style `(b)` as a child of a
preceding `(3)` and failed to attach Roman grandchildren such as `(ii)` and
`(iii)`. The correction distinguishes dotted-letter lists from parenthesized-letter
lists and preserves the numbered/Roman hierarchy. Source characters, offsets and
passage identities remain unchanged. [parser-preflight.json](parser-preflight.json)
records the before/after relationships. The parser is still a bounded heuristic;
ambiguous plain-text numbering and unsupported layouts need independent checks.
In particular, a sequential top-level `(i)` after `(h)` takes precedence over a
possible Roman child. Structural parenthood does not establish legal scope.

Both live variants use this corrected parser. The control receives the existing
passage catalog; the treatment adds `structural_parent_refs` naming only supplied
passages, with an unavailable-parent flag when necessary. It changes no schema,
field order, model instructions or source text. No automatic scope inheritance
is added. The live comparison does **not** measure old versus corrected parsing.

Two sources were frozen before calls: the saved baggage excerpt and a new invented
public-display permit policy. Each was processed twice under both catalog variants
and both windowing modes. Whole-document mode uses the normal 6,000-character limit;
the stress test uses 1,900 for baggage and 1,300 for the permit policy. Each split
has two requests. Runs reverse control/treatment order in the second repeat, with
at most three independent groups executing concurrently.

[design.json](design.json) pins the runtime, inputs and sixteen runs;
[criteria.json](criteria.json) records review criteria. The design makes exactly
24 provider calls to Gemini 3.8 Flash at temperature 0 with a 16,384 token allowance.
There are no retries, repair calls or model reviews.

## Results

| Source / windowing | Control: completed runs | Parent hints: completed runs |
| --- | ---: | ---: |
| Baggage / whole | 2/2 | 2/2 |
| Baggage / deliberately split | 1/2 | 0/2 |
| Permit policy / whole | 2/2 | 2/2 |
| Permit policy / deliberately split | 0/2 | 1/2 |

All eight whole-document runs completed. Six of eight split runs ended partially:
the second request returned `MAX_TOKENS` and malformed JSON. Those windows produced
no accepted records; their original responses and refusal reasons remain saved.
This does not mean six normal default runs failed: both short sources fit within
the default whole-document window. Completion is also not an accuracy score.

Reported usage was **250,785 tokens**, including thinking: 63,160 for whole inputs
and 187,625 for split inputs. Splitting used twice as many requests and incurred
six exhausted responses. This is a result for these selected boundaries, not a
general claim that smaller windows always cost more. The reason for the model's
extended thinking is unverified.

The source review distinguishes three failures:

- **Unavailable input:** the first baggage request lacks lock/key; the second
  lacks the declaration. The first permit request lacks storm authorization.
- **Ignored supplied context:** every first baggage result also drops the
  hard-sided-container condition, although it is supplied as `C000`. Several
  permit outputs drop the wind condition from the statement despite supplied
  context containing it.
- **Incomplete extracted meaning despite complete input:** the one completed
  second permit request receives the entire storm rule but extracts authorization
  expiry without the full storm exception or wind condition. Whole outputs also
  retain an investigation extension separately while omitting it from the
  baseline retention statement.

Parent hints improve applicability scopes in both first baggage split requests.
That benefit does not repeat consistently with whole inputs; one hierarchy result
loses applicability from scope, and classification/evidence defects remain.
No parent-hint treatment is promoted on these observations.

[source-review.json](source-review.json) contains ten findings with source text,
raw rows, accepted identifiers and evidence. [source-availability.json](source-availability.json)
and [window-preflight.json](window-preflight.json) show what each request could see.
These are revisable agent assessments on selected development cases.

## Verification

All sixteen runs, including the six partial outcomes, replay to identical books
without provider calls. Paired requests differ only by the declared parent
metadata. All 162 accepted statements pass Core graph validation; every parsed
statement, scope, kind and modality matches its accepted representation. There
are no Core-rejected candidates. The six malformed responses remain refused,
with no attempt to salvage their prefixes.

The package suite passes **308 tests**. Seven context tests cover the existing
dotted style, both saved CFR lists, nested context supply and section boundaries.
The final fixture-path cleanup was followed by another passing context run.
[verification.json](verification.json) records all replay and provider outcomes;
[test-verification.json](test-verification.json) records deterministic checks.

Replay one capture with a new output directory:

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/hierarchy-boundary-experiment/experiment.py \
  replay baggage split control 1 --output .tools/hierarchy-boundary-replay
```

## Concrete next change

Before splitting inside a list, move the boundary before its governing parent
when the whole group fits within the configured limit. Reuse the corrected
passage tree. For these sources, earlier boundaries keep the relevant complete
lists in focus with **the same two requests and unchanged character limits**:

- Baggage: split at position 1,376 instead of 1,842.
- Permit policy: split at position 1,034 instead of 1,226.

[boundary-candidates.json](boundary-candidates.json) verifies the proposed ranges
fit. This boundary change is **not implemented or tested with the model yet**.
Larger groups still need bounded context and explicit accounting for unavailable
material. Test source availability, retained conditions, duplicates, unrelated
scope leakage and completion separately before adoption.

All previous captures remain unchanged. The parser correction and research are
local and uncommitted.
