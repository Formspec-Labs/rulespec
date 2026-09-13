# Fresh sources: narrower recovery focus did not produce repairs

**Do not adopt a focused recovery pass from this result.** All eight recovery
calls returned no proposals. The narrower input did not fix either fresh
default-reading gap or either saved IEP omission. Existing reference navigation
located the correct records, and every source character was supplied in both
arms. No extra schema or missing source text explains these observed no-ops.

This is a negative generation result on selected cases, not a general extraction
accuracy estimate. The broader gate failed, and production behavior is unchanged.

## What the fresh extractions showed

Three previously unused excerpts from pinned USLM release 119-102 produced
seventeen accepted statements. Prior-use searches covered the repository's
research, examples and evaluation paths; model training familiarity is unknown.
The original source and all raw outputs remain intact. No planted omissions or
handwritten replacement statements were needed.

| Source | Original default reading | Separately captured meaning | A: whole-source recovery | B: native-group focus |
|---|---|---|---|---|
| 15 USC 9009a(d), grant expenses | Ordinary expense period, except as provided in clause (ii) | Supplemental-grant condition, either-grant scope and June 30, 2022 extension | No repair | No repair |
| 29 USC 1083(f)(1), pension balances | Carryover election for a plan described in clause (ii) | Both 2007 eligibility criteria and year-end positive-balance measurement | No repair | No repair |
| Saved IEP development case | Attendance agreement / excusal consent without parent's writing qualification | Parent-writing requirement for both provisions | Neither repaired | Neither repaired |
| 15 USC 637(d)(16), reporting control | Agency collection/reporting and periodic review, separate from contractor credit | Existing agency duties and credit branches | No change | No change |

Both arms repair **0/2 fresh primary gaps and 0/2 saved IEP gaps**. The secondary
grant repayment exception also remains behind a bare clause pointer in both.
There are four primary opportunities per arm, not eight independent failures.
Each case/arm has one sample.

The fresh statements generally preserve their quoted source meaning. A statement
that retains “clause (ii)” is not automatically false. It fails the declared
product criterion when the user needs its governing local meaning in the default
reading without another AI resolving and interpreting that clause. The whole
book still contains the separate source-backed criteria. Keep this distinction
when labeling the result.

## Intervention and controls

Both arms used the unchanged recovery prompt and CUE-based schema, the same
claims and the same reference-to-claim navigation. A marked the complete source
as focus. B marked the preselected complete native group as focus and supplied
all other characters as context. The existing code also restricts B from editing
context-only claims; this experiment cannot isolate that restriction from the
attention effect of focus. It did not reduce the total supplied source.

All eight responses finished normally, parsed and contained zero proposals.
The checker therefore made zero calls. Five responses were entirely empty;
three returned six `already_represented` observations about existing actors,
modality and reporting duties. None addressed the primary missing default-reading
qualifications. The [raw review](ANONYMOUS-REVIEW.md) was saved and hashed before
opening the arm key. No proposal was lost in parsing, preview or checking.

There was no new false credit prerequisite, actor transfer, deadline confusion
or change to unrelated records. Inactivity also occurred on every positive
case, so this does not demonstrate semantic discrimination. The earlier
[supplied-repair test](../2026-09-12-fixed-repair-check/README.md) demonstrated
some checker recognition; it was not automatic generation and was not repeated
as a substitute for these fresh no-op results.

The [baseline review](BASELINE-REVIEW.md) retains other issues separately: six
grant term-component refusals, unresolved actor/modal evidence, a duplicated
prohibition, purpose mixed with scope, and a `may only` statement classified
as `must`. Those cases are not certified clean merely because their main text
is faithful. No fields or original review histories were repaired for this test.

## Decision and the next different hypothesis

H1 was not supported: narrowing focus did not increase repair generation. H3's
predicted unsupported edits were not observed, but there were no supported edits
either. H2 remains plausible; the current objective may accept separately stored
meaning as sufficient. The observations concern other fields and cannot prove
why the model declined the targeted repairs.

Stop varying context size or navigation for this recovery objective on these
cases. The next useful hypothesis concerns the requested operation: explicitly
construct a self-contained default reading for a selected reference group,
preserving the current statement's correct meaning and deciding which referenced
details govern it. Test that operation through existing fields and review code
against ordinary recovery, with false-prerequisite controls and new source cases.
Require actual generated replacements, source support and correct counterexamples;
do not infer success from a supplied answer or an empty assessment.

That would be a new experimental task objective, not another production pass or
an instruction to copy every related duty into every record. Existing navigation
stays useful for discovery, and the existing representation can retain the
complete reading plus component evidence. These results justify no automatic
repair, new meaning schema or relaxed qualification guard.

## Cost, integrity and reproduction

Eleven calls used **92,995 reported tokens**: three ordinary low-thinking
extractions and eight medium-thinking recovery calls. A's recovery calls used
37,917 tokens; B used 42,983, **13.4% more**, with no measured repair gain. This
is a single sample per cell; most of the difference was reported thinking tokens,
not a significant reduction or expansion of source input. Recorded capture
operations totaled 96.93 seconds, including their local setup/processing.
These are token counts and observed operation times, not dollar-price estimates.

Model: `gemini-3.8-flash`, temperature 0. Extraction used current production low
thinking and 16,384 output cap; recovery used medium thinking, no numeric thinking
budget, 32,768 cap. The 19-call ceiling included conditional checker calls that
were unnecessary. No provider retry, incomplete response or missing usage record.

One [local preview setup failure](HARNESS-REPAIR.md) occurred after the first saved
recovery response. The temporary helper lacked the full extraction manifest.
The experiment now copies complete original captures into temporary directories;
the manifest guard remains intact. The saved response was reused, and the frozen
original harness and labels were preserved. Use the resume wrapper for replay.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src \
  .tools/document-poc-venv/bin/python \
  thoughts/experiments/2026-09-12-fresh-focused-repair/resume.py verify
```

All three original extractions replay identically with model creation blocked.
All eight recovery responses replay through the current decoder and temporary
review setup. [Actual-request verification](request-verification.json) confirms
matching prompt/schema/settings, identical source/claims/navigation between arms,
the exact native focus ranges and unchanged original books.

[Plan](PLAN.md), [sources and provenance](source-receipt.json),
[initial extractions](extract/), [repair captures](captures/),
[aggregate results](RESULTS.json), [usage](usage.json).
