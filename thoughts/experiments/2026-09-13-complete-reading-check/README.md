# Complete-reading checker: bounded improvement, adoption gate failed

The shared construction task improved the checker on request-content requirements
and unnecessary enrichment. It still accepted a notice rule that omitted its
incoming exception in both repetitions. Do not adopt it as a completeness gate
or proceed to M5 using its verdicts as the sole quality measure.

| Measure | Current checker after input fixes | Shared task + selected decisions |
|---|---:|---:|
| Correct judgments against frozen labels | 10 / 18 | 22 / 24 |
| Selected no-change decisions assessed | 0 / 6 | 6 / 6 |
| Correct no-change judgments | Unassessed | 4 / 6 |
| Valid evidence selections | 18 / 18 | 24 / 24 |
| Missed notice exception on unchanged baseline | Unassessed | 2 / 2 |

The denominators differ because the current optional path checks edits only.
On the same eighteen edited candidates the shared task scores 18/18, versus
10/18 for the current checker. The remaining six assessments are no-change
controls. There are twelve distinct candidate alternatives across three source
contexts, two repeats per arm; these are development diagnostics, including
constructed answers, not twelve independently sampled documents. The bundle
changes both task definition and coverage; no individual instruction gets credit.

## What the raw data shows

The old checker rejects a complete electronic-request reading as improper
conflation: the name/reference-number requirement is already in another record.
It nevertheless approves filling empty action/object fields without incorporating
that requirement. With the shared task, it accepts the complete reading, rejects
the enrichment and incomplete no-op, and leaves the complete inspection permission
alone. Both arms reject assigning the agency's reporting duty to applicants and
both reject changing pension eligibility from 2007 to 2008.

The remaining false acceptance is specific and repeated. The new checker calls
notice C0000 “independently complete” after assessing Subparagraph (A) in isolation,
even though the supplied source contains (B)'s infeasibility exception. It correctly
understands the exception when checking the exemption candidate itself. Thus the
source is present and understandable; applying that knowledge to the baseline
reading remains unreliable. A plausible next hypothesis is that source-first
accounting of which provision changes which baseline will outperform a verdict
on each existing statement. This experiment did not test that approach.

## Identifier diagnostic: mechanical fix, unresolved semantic defect

The internal revision ID no longer appears redundantly as proposed source meaning.
The model-facing `qualifies` aliases still resolve to exactly the same internal
revision, and original captures remain unchanged. Draft `applies_to` values use
those aliases as well. Both diagnostic responses avoid the old spurious internal-ID
objection.

However, the fresh current checker accepts both the original bad action/object
pair and the matched component-cleared control. The original has action “provide
…the notice” but object “Subparagraph (A),” the waived legal provision. That pair
remains wrong. The declared M3 semantic diagnostic failed. In the main experiment,
the same current checker detects it once and misses it once. Cleaner identifiers
remove a real input inconsistency; they do not prove a more accurate checker.
Retaining the mechanical fix is a narrower decision than passing M3's full gate.

## Integrated scope

- New calls omit deprecated sampling parameters and unsupported `candidate_count`
  at the SDK boundary, including defaults inserted by LangExtract. Thinking effort
  and output limits remain explicit. CLI temperature control was removed.
- Core `AILineage` permits an omitted temperature; graph/review provenance no longer
  invents one. CUE, generated Rust, hand-authored SHACL, the specification and
  fixtures agree. Existing numeric capture metadata remains intact.
- Model-facing relationship identifiers are consistent. Reference-navigation
  wording separates local location, canonical resolution and semantic applicability.
- TASK.txt, the selected-decision checker and constructed controls remain here as
  experimental artifacts. Initial extraction prompts and the production checker
  policy have not adopted the complete-reading treatment. No new default pass.

## Validation and accounting

Fifteen calls total: twelve paired checker calls, two identifier diagnostics and
one extraction smoke. Recorded totals: 111,870 tokens (54,769 input, 6,000 visible
output, 51,101 thinking), 179.7 seconds summed call time, no retries or provider
failures. All requests actually omit temperature/top-p/top-k/candidate-count.
Checker calls use medium thinking; the extraction smoke uses the ordinary low
thinking setting. Provider-managed sampling means the historical temperature-zero
run is not a contemporaneous settings control.

The smoke produces three grounded records with no rejected claims or parser
refusals. Its baseline says “unless an exemption applies” without explaining that
exemption, so compatibility success is not independently complete extraction.
Its original run replays with the provider blocked; sequential review observations,
a stale-revision refusal and source-context export also succeed. These observations
make no semantic approval. Combined application of newly generated meaning edits
remains a later integration check if a repair treatment qualifies for adoption.

All fourteen checker captures re-decode identically with provider access blocked.
The prior notice capture reprocesses and replays with current code while preserving
its exact request/response bytes and original temperature-zero metadata. Original
historical runtime replay still requires that original runtime; reprocessing is
explicitly a new processing record.

Local checks: 709 extractor tests pass; the strengthened actual-SDK request tests
pass in the 123-test extraction suite. Core fixture validation, negative fixtures,
CUE-derived constraint parity (zero Core divergences), reference-corpus validation
and `rkaf-core` compilation pass. Constraint parity still reports its two existing
adversarial documentation findings. The local conformance package was rebuilt and
installed so the usual extraction environment uses the updated schema.

## Next decision

Keep M5 on hold: a smaller edit response cannot be judged trustworthy by this
checker yet. First test whether explicit source-to-baseline applicability accounting
catches incoming exceptions without inventing dependencies between unrelated duties.
Include unseen sources before treating any result as a general accuracy estimate.
Do not add another prompt patch to make this notice example pass in isolation.

## Reproduce

Use the repository's document-poc Python environment with
`PYTHONPATH=packages/rulespec-extrapolator/src`. `run.py prepare` freezes a new
experiment before calls; `run.py capture` performs the bounded recorded calls.
Existing captures are never replaced. `verify.py verify` rechecks the retained
checker data and historical reprocessing without provider access. `verify.py smoke`
is a single-use live smoke with a frozen procedure receipt. The original plan,
labels, cases, raw review and arm key remain separate artifacts.
