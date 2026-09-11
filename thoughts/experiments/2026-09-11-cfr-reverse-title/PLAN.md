# Explicit CFR coordinates before the title name

Decision: extend the owning RefSpec occurrence reader for coordinates followed
by `of title N, Code of Federal Regulations`, and deliver it through the existing
Rulespec reference/discovery commands if the comparison passes.

Hypothesis: the source already supplies the missing identity; connecting the
existing unit/list/range reader to the existing longhand title matcher will
recover complete references without native-title inference or input rewriting.
The actual title-41 variance paragraph names part 1910 twice and section
1954.3(d)(1)(i) once, all under its explicit title-29 suffix. The baseline returns
three title-only readings. Connecting an unrelated title, losing a qualifier or
turning an incomplete list/range into a definite first target weakens adoption.

Arms: copied pre-change dispatcher/source callback versus the shared upstream
implementation, followed by direct application imports and installed-wheel checks.
Retain the replaced code as a test-only oracle. No new application parser,
model-facing field, Core dependency or context-default mode.

Cases: all 33 frozen native-context cases, including eleven real paragraphs;
the known variance paragraph is a development case. Declared differences there
are `foreign-title-suffix` and constructed `other-title-suffix`; other original
cases must agree. Add constructed positives and counterexamples for sections,
parts, pinpoints, lists, ranges, note/open-ended scope, compound parts, repeated
occurrences, impossible titles, mixed explicit citations, unrelated intervening
prose, source paragraphs and ambiguity. Preserve any newly observed failures.

Held constant: source characters, item/qualifier semantics, public API shapes,
application evidence and optional source lookup. Factor existing qualifier code
only to share it; establish forward-reader agreement against copied code.
One deterministic run per arm per input. No model calls. Bound the first gate
to the original 33 cases plus at most 40 targeted controls and the relevant
existing regression suite. Any follow-up expansion gets its own recorded reason.

Decision rule: adopt only with whole written scope, correct stated titles,
exact occurrence/context evidence, no unlisted baseline differences, no new
unsupported accepted targets and relevant upstream/application checks passing.
Then rebuild/install the changed package, verify its bytes and compare the normal
application outputs. Keep the existing `to the same extent` range issue as a
separate defect; do not alter range semantics in this comparison.

Meaning: this recognizes a printed address and retains evidence. It does not
prove that the target exists, applies, or belongs to the intended edition. Native
title-default inference under R9 remains unimplemented and its failed gate stands.

Implementation follow-up: two repeated-label controls exposed partial results
for `§§ 82.155 and § 82.156 ...` and its repeated singular-label spelling. The
failures are retained; the reverse group now reuses the unit label and list
separator with optional repeated labels. There are 31 targeted controls plus
the original 33 cases, within the stated bound. Ordinary forward list policy is
unchanged. A shared interval check replaces repeated overlap scans; compare
400, 800 and 1,600 repeated explicit groups after correctness checks, recording
three timings each without treating them as general performance guarantees.
