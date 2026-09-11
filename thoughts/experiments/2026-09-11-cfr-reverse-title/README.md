# Written CFR titles now resolve the preceding coordinates

**Delivered locally:** RefSpec now reads `§ 1954.3(d)(1)(i) of title 29, Code of
Federal Regulations` as the stated title, section and pinpoint. The existing
Rulespec reference and discovery commands use the new reader without a new
application parser or model field. Source, isolated-wheel and working command
outputs agree exactly. The [delivery receipt](delivery.json) and
[wheel inputs](wheel-inputs.json) identify the installation.

## The actual source improved

The title-41 variance paragraph previously produced three incomplete title-29
readings. The same XML now produces:

| Written reference | Before | After |
| --- | --- | --- |
| `part 1910 of title 29, Code of Federal Regulations` | Title 29 only | 29 CFR part 1910 |
| `§ 1954.3(d)(1)(i) of title 29, Code of Federal Regulations` | Title 29 only | 29 CFR 1954.3, pinpoint `(d)(1)(i)` |
| The later repeated `part 1910` reference | Title 29 only | A separate occurrence of 29 CFR part 1910 |

The paragraph is retained as publisher XML in the
[application fixture](../../../packages/rulespec-extrapolator/tests/fixtures/cfr-reverse-title.xml).
Its original full-title digest, native ancestry and paragraph XPath are preserved
in the preceding [native-context experiment](../2026-09-11-cfr-native-context/README.md).
The new reader uses the title written in each citation; it does not use the
document's title number. This directly addresses one of that experiment's
counterexamples without adopting its unsafe native-title default.

Lists preserve their individual source slices and shared title context. A single
complete citation gets one quotation, with no duplicate context quote. Source
spans grow to include the written suffix, so reference IDs change from the earlier
title-only readings; repeated occurrences remain distinct. Older captures and
reviews are preserved. The changed reader digest is visible to strict replay.

## What was reused and checked

The change stays in `refspec.registry.citation_grammar`. The existing longhand
title matcher establishes the code and title; existing coordinate, list, range
and qualifier code reads the preceding body. Qualifier handling is shared between
forward and reverse spellings. A body must meet the title directly through `of`;
intervening prose, paragraph breaks and overlapping explicit citations prevent
that association. Existing source-order/interval techniques replace repeated
overlap scans; no new hierarchy parser or source index was introduced.

- **862 upstream checks pass**, including 98 focused reverse-title checks.
- **645 application tests pass** from source and independently from the installed
  wheels outside the checkout. Existing rdflib/pyparsing warnings remain.
- Across the **33 original cases**, including eleven real publisher paragraphs,
  only the two predeclared inputs change: the variance paragraph and its
  constructed reverse-title control. The replaced dispatcher and callback are
  copied into a test-only oracle; their syntax trees match the pinned prior commit.
- There are **32 targeted constructed controls**, including repeated unit labels,
  parts, sections, pinpoints, ranges, compound parts, notes before/after the title,
  impossible titles, competing citations, unrelated prose and paragraph breaks.
  These are diagnostic/regression cases, not an independent accuracy benchmark.
- The normal `references` and `discovery-export --references` JSON outputs match exactly across
  source, fresh installation and working installation. Discovery uses a declared
  empty extraction run to test the command; it is not a model extraction result.
- All **409 Python files from the seven pinned wheels** match each installation;
  all **170 RefSpec Python source files** match the new wheel. Dependencies pass.
  Only RefSpec was rebuilt. The existing extractor runtime wheel is unchanged;
  its installation instructions and application tests were updated in the repo.

Two failures found during implementation remain in the evidence:

1. A repeated `§` label initially caused only the last list member to survive.
   The reverse group now reuses the unit labels and list separator to preserve
   both members. See [failure](repeated-label-failure.log) and
   [follow-up](repeated-label-followup.log).
2. A note attached to one member before the shared title initially affected
   earlier members. Its refusal now stays with that member. A note after the
   shared title remains a group qualification. See
   [failure](member-note-failure.log) and [follow-up](member-note-followup.log).

Raw [reader comparisons](source-final/reader-comparison.json),
[source references](source-final/references.json), and
[installed discovery output](isolated/discovery-with-references.json) retain the complete results.
The initial candidate, harness and tests are retained separately; the
[verification receipt](source-verification.json) confirms their frozen identities
and reconstructs the initial code from its patch and pinned Git base. The final
[source freeze](source-freeze-final.json) matches the delivered files.

The final artifact review caught an incomplete CLI check: the original harness
omitted `--references`, so its `discovery.json` outputs contain no reference scan.
Those captures and their original parity receipt remain unchanged. The separate
[corrected check](check-discovery-references.py) reuses the same saved runs with
reference scanning enabled. It verifies all three readings, their identities and
exact source evidence, with identical complete JSON from source, isolated and
working installations. The old baseline still returns title-only readings. See
the [corrected parity receipt](discovery-references-parity.json). No runtime change
was required; the direct discovery-export application test already passed.

The small timing probe used three repetitions at 400, 800 and 1,600 repeated
citation groups. Median times at 1,600 were about **65 ms before and 39 ms after**;
at 400, the new reader was slower, about **7.7 ms versus 6.1 ms**. The new reader
does more work by identifying coordinates. These are single-machine synthetic
observations, not general performance or user-latency claims. See
[raw timings](source-final/timings.json).

## Remaining work

The [R9 native-title comparison](../2026-09-11-cfr-native-context/README.md) still
failed adoption. Bare citations, quoted contextual wording, heading conflicts
and native part-scope checks remain separate work. This feature requires a
written longhand CFR title and does not infer one from headings or filenames.

The existing `to the same extent` range/prose defect also remains open. Address it
upstream against ordinary prose and real/unread ranges; do not treat every failed
range as permission to accept its first coordinate. Target existence, paragraph
lookup, applicability and historical edition matching remain separate from
recognizing this citation's printed identity.

No model calls, API charges, publication or deployment were involved. Upstream
implementation commit: `84bc634d`; application validation commit: `67563ac`.
Full reuse work remains active.

To reproduce the comparison, copy `capture.py`, `PLAN.md`, `source-freeze.json`
and `wheel-inputs.json` into a fresh directory under `thoughts/experiments`, and
select the pinned source versions. The `baseline` mode needs the preceding verified
[eCFR RefSpec wheel](../2026-09-11-ecfr-text/wheel-inputs.json); `source-final`
uses the frozen new RefSpec source on `PYTHONPATH`. `isolated` and `working` check
the selected installed wheel bytes before running the commands. The
[installation commands](install-isolated-commands.json) preserve all dependency
inputs. Output files use exclusive creation to protect earlier observations.
After the original capture, run `check-discovery-references.py MODE` in the same
environment to exercise reference-enabled discovery. The original harness stays
frozen, including its missing flag, so the correction remains explicit.
