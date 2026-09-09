# Whitespace matching recovers six judgments but fails the broad acceptance gate

The experimental exact-first, whitespace-only fallback recovers all six refused
judgments from the saved notice-section audit. It preserves every raw verdict and
rationale and all 30 previously accepted claim/unit judgments. But it also accepts
two constructed quotations that join separate table cells or list entries. This
supports a bounded recovery improvement, not general automatic acceptance.

No production resolver changed, and no provider calls were made. The
[plan](PLAN.md), [23 counterexamples and controls](cases.json),
[results](results.json) and [verification](verification.json) are preserved.

## Actual audit effect

The same source, raw responses, claims, inventory and assessment code ran twice;
only evidence alignment differed. Exact matching remains first. The fallback
changes whitespace runs only, requires one match in supplied focus/context ranges,
checks inserted source-map text, and returns the original source slice and offsets.
An experiment receipt retains the model quotation and matching method. No words,
numbers, punctuation, case or verdicts are changed.

| Result | Existing exact matcher | Experimental fallback |
|---|---:|---:|
| Accepted claim judgments | 15 | 18 |
| Accepted unit judgments | 15 | 18 |
| Covered units | 13 | 15 |
| Partial units | 2 | 3 |
| Unknown units | 3 | 0 |
| Review accounting complete | No | Yes |
| Overall audit status | Failed | Failed |

The recovered C0014/U0014 judgment correctly remains a reported overbroad
permission under the saved assessment. The other two recovered pairs retain
covered verdicts. Recovering evidence makes the existing findings available; it
does not repair the draft or independently validate the model's interpretation.
Every stored span exactly matches original text at its saved Unicode offsets.

## Counterexamples, including failures

All cases below are constructed diagnostics with declared expectations. `\n`,
`\t` and `\r` denote actual newline, tab and carriage-return characters; JSON
preserves the precise strings. The layout cases include an author-intent note in
`cases.json`; this tests a boundary of automatic acceptance, not a population rate.

| Case | Source → proposed quotation | Exact | Fallback |
|---|---|---|---|
| Wrapped prose | `Staff must\n    file notice.` → `Staff must file notice.` | Refused | Accepted as intended |
| Thin space after section sign | `See § 825.303(c).` → `See § 825.303(c).` | Refused | Accepted as intended |
| Missing negation | `Staff must not enter.` → `Staff must enter.` | Refused | Refused |
| Changed number | `File within 30 days.` → `File within 3 days.` | Refused | Refused |
| Changed conjunction | `Provide A and B.` → `Provide A or B.` | Refused | Refused |
| Changed punctuation | `Pay 1,000 dollars.` → `Pay 1000 dollars.` | Refused | Refused |
| Stitched quotation | `Staff must file. Managers may waive this. Within 30 days.` → `Staff must file. Within 30 days.` | Refused | Refused |
| Repeated equivalent text | `Staff  must file.\n\nStaff\tmust file.` → `Staff must file.` | Refused | Refused |
| Overlapping matches | `a  a  a` → `a a` | Refused | Refused |
| Separate table columns | `May\tNot enter` → `May Not enter` | Refused | **Accepted against expectation** |
| Separate list entries | `may\nnot required` → `may not required` | Refused | **Accepted against expectation** |
| Already-exact fragment with lost negation context | `A replacement is not required.` → `required.` | Accepted | Accepted |

The table example has separate column headings identifying permission wording and
the subject of a restriction. Collapsing a tab can make two cells look like one
modal statement. The list example contains separate permission categories.
Unlike omitted intervening words, the separation itself is whitespace, so this
algorithm cannot distinguish those cases from a legitimate prose line wrap.

These are not false character matches: the returned source slices exist and retain
their original layout. The failure is accepting the model's quotation as an adequate
representation of that structured source without assessing the lost relationship.
Passage IDs would also require a meaning check; this experiment does not establish
them as universally safer or better.

Of 17 expected-refusal controls, 15 remain refused and the two layout cases are
accepted. All six expected-acceptance controls succeed under the fallback; four
are recoveries and two were already exact. Additional controls include Unicode
nonbreaking spaces/CRLF, repeated exact matches, context-only allowed evidence,
out-of-focus text, unsupplied gaps, inserted separators, empty/whitespace-only
quotes, changed case and zero-width characters. See `results.json` for every case.

The final fragment example demonstrates a separate limit shared by both arms:
locating `required.` in `not required.` does not establish that a replacement is
required. This control intentionally expects a literal match, not semantic approval.

## Decision and reproducibility

**Do not adopt a general whitespace fallback from this result.** The tested rule
failed its predeclared layout-sensitive rejection gate. The real-document recovery
is useful, but safe automatic acceptance across document structures remains
unresolved. A narrowly defined prose-only policy or reviewable alignment suggestion
would require its own explicit scope and tests; neither was implemented here.
No implementation was tuned after observing the failures.

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/whitespace-evidence-experiment/experiment.py replay
```

The runner reuses the shared evidence result type, source guard, judgment parser
and evaluator, patches the resolver only inside the experiment, and checks the
saved runtime and artifact hashes. Replay must reproduce the counterexample
failures as well as the recovered audit. Original captures and their manifests
remain unchanged. Labels are agent-authored, revisable interpretations; results
are not an independent semantic accuracy benchmark.
