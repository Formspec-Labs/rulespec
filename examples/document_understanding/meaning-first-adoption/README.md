# Meaning-first extraction in the normal workflow

The normal command now produces complete source-backed statements without asking
for concepts, claimants, normalized values, actor/action/object fields and explicit
relationships on every pass. Those capabilities remain in the same CUE profile
and Core/refinement code. Source passages, scope, context and unresolved work are
also available through `discovery-export`, without another model call.

The final four live calls completed with 35 accepted statements, no parsing or
compilation refusals, valid Core graphs and identical provider-free replay.
This establishes working data flow, not perfect extraction. Direct source review
still found grouped meanings, incomplete statement-only phrasing, and one wrong
modal classification.

## What changed

- `#FirstMeaning` selects existing CUE types. `statement` becomes Core `summary`;
  full defaults and optional refinement use generated `meaning.schema.json`.
- Focus (`F`) and context (`C`) passage references resolve to exact Unicode offsets.
  A main selection must be one focus passage or a contiguous focus range.
  Disconnected lead-ins belong in scope support. No fuzzy quotation repair.
- Logical evidence uses `logic_quote`, a passage selection copied exactly into
  Core `logic_text`. The model supplies the interpretation separately in the
  statement, scope and choice fields.
- Bad optional references or modal quotations are withheld with their original
  row and field-specific issue. A valid grounded statement survives. Main evidence,
  required fields, types and kind/modality consistency remain strict.
- Discovery exports reuse the tested source/context record builder. They retain
  every source passage, linked proposed statements, review status and processing
  counts. An unlinked passage is a candidate for inspection, not proof of omission.

## Live check

Eight Gemini 3.8 Flash requests were made at temperature 0: four initial calls
and four follow-up calls on the same excerpts. Each call had one attempt and no
retry. Both versions preserve their original source, requests, raw responses,
outputs, manifests and frozen runtimes in `initial/` and `final/`.

| Source | Initial accepted / issues | Final accepted / issues | Final total tokens |
| --- | ---: | ---: | ---: |
| Passport names | 12 / 7 | 12 / 0 | 7,281 |
| Passport photos | 11 / 0 | 10 / 0 | 5,883 |
| Leave eligibility | 10 / 2 | 7 / 0 | 5,990 |
| Baggage restrictions | 4 / 5 | 6 / 0 | 5,442 |

“Issues” in this table counts parsing/component refusals, not semantic mistakes
or ordinary review flags. Different grouping explains much of the record-count
change. The final calls used 24,596 reported tokens: 4.5% more than this iteration's
initial calls, and 22.9% fewer than the earlier four-document meaning-first trial.
The requests and grouping changed; this is a small development comparison, not a
controlled estimate of general accuracy or dollar cost.

The initial run exposed rewritten logical quotations and two baggage rows with
comma-separated main references. The follow-up replaced logical quote writing
with selection, constrained main-reference syntax in CUE, and clarified how
inherited lead-ins and trailing provisos should be retained.

## Direct source review

The complete [case review](source-review.json) binds the judgments to source
criteria and final rulebook hashes. These are revisable agent judgments.

The final outputs retain all six name-document alternatives, the emergency
passport permission's inherited limits, photo recommendations at `should`, the
leave eligibility conjunction and both prior-service alternatives, and the
checked-baggage conditions. The nonconsecutive-months statement now keeps its
`provided` qualification and has a consistent exemption classification.

Remaining issues matter for downstream use:

- The ammunition statement correctly says this section does not prohibit carriage,
  but labels that meaning `exemption / not_required`. Absence of a prohibition is
  not absence of a duty; a valid kind/modality pair can still be semantically wrong.
- Some independent facts and rules are grouped: identity fact plus possible
  evidence requirement, USERRA absence counting plus prior-service counting, and
  photo re-use context plus the recency caution.
- Some complete qualifications appear only in companion fields. The unloaded
  firearm statement abbreviates the declaration's recipient/content; scope and
  choice retain them. The nonconsecutive-months statement keeps the proviso, while
  its scope field omits it. The certificate caution needs its scope to identify
  which certificates it concerns.
- The remote married-name exception retains its reference, but its statement
  phrasing can still sound broader than the unavailable exception text.

The existing retrieval diagnostic recovered expected source support for 9 of 10
answerable questions at rank 3 using source/context evidence, versus 8 of 10 with
statements alone. The two unknown queries remain outside that denominator. This
is source retrieval, not answer accuracy or proof of complete extraction.

## Verification and use

304 package tests, six schema-builder tests and native CUE regeneration passed.
The regressions include the three saved good statements lost through malformed
optional enrichment, unseen context, repeated quotations, Unicode/CRLF ranges,
refinement, replay and source retention. All four final runs replayed identically,
and the real discovery-export command retained every source character.
See [verification](verification.json), [comparison](comparison.json) and the
[retrieval check](discovery-check.json).

```sh
.tools/document-poc-venv/bin/rulespec-understand replay \
  examples/document_understanding/meaning-first-adoption/final/names \
  --output .tools/meaning-first-example-replay

.tools/document-poc-venv/bin/rulespec-understand discovery-export \
  examples/document_understanding/meaning-first-adoption/final/names \
  --output .tools/meaning-first-discovery.json
```

Strict replay requires the recorded runtime. The initial captures intentionally
have an earlier runtime; they remain intact and hash-verified. The final runtime
does not migrate that intermediate provider format. Existing audit/refinement
and review-history paths remain available when more detailed interpretation is
worth the effort. No routine second model pass or UI change was added.
