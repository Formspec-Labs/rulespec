# Explicit construction helps, but does not close the completeness gap

Asking the model to construct a self-contained default statement produced three
faithful expansions across six targeted opportunities; ordinary recovery produced
none meeting the same criteria. Two expansions survived decoding, individual
review previews and the unchanged checker. The full gate failed. Production
prompts, schemas, validation, relationship rules and default passes are unchanged.

## What changed and what stayed fixed

A used ordinary recovery with an explicit selection of statements to evaluate.
B added the fixed instruction in [run.py](run.py): incorporate governing meaning
from other records into `fields.summary`, distinguish it from unrelated duties,
and explain a justified no-op. This is one task-definition bundle; the experiment
cannot attribute the result to one phrase.

The actual paired requests contain identical complete source, claims, navigation,
selected aliases and the same full CUE-derived 27-field replacement schema. All
eight generation calls used `gemini-3.8-flash`, temperature 0, medium thinking,
no numeric thinking budget and a 32,768 output cap. The checker was unchanged.
The baseline is contemporaneous and target-restricted; it differs from the
previous whole-book recovery comparison.

Cases comprise the saved pension failure, the previously constructed
request/inspection control and a previously unused native excerpt of
15 USC 6504(a)(2), pinned release 119-102. One fresh ordinary extraction of the
notice excerpt produced three accepted statements and natural gaps before the
comparison. No gap or proposed replacement was planted. Pension received two
repetitions per arm; the other cases received one. These are three source cases,
five distinct target readings and six positive opportunities per arm.

## Results

| Measure | A: recovery | B: explicit construction |
|---|---:|---:|
| Generation calls with proposals | 3/4 | 3/4 |
| Raw proposed edits | 6 | 3 |
| Decoded edits with valid individual previews | 6 | 2 |
| Checker-supported edits | 5 | 2 |
| Complete target readings in raw generated wording | 0/6 | 3/6 |
| Complete target readings with valid preview and checker support | 0/6 | 2/6 |
| Further partial target readings | 1 | 0 |

The [anonymous manual review](ANONYMOUS-REVIEW.md) was saved and hashed before
opening the arm key. Its strict completeness labels are revisable. In particular,
A's new notice wording makes progress but leaves the determining actor implicit;
a more permissive label would score A as 1/6. Both arms still fail the overall gate.

- **Pension:** B incorporated both 2007 eligibility criteria, the year-end account
  measurement, permission and until-zero limit in both repetitions. A did not.
  One B proposal failed because optional `logic_text` omitted the source's `(II)`
  marker. The otherwise faithful default statement was discarded with it.
- **Notice:** B correctly expanded the condition for notice at filing: the State
  attorney general determines that advance notice is infeasible. It still left
  the ordinary duty and exemption dependent on other records, incorrectly calling
  those readings complete under the requested criterion. A partially expanded the
  at-filing condition and proposed a useful exception link, but failed to produce
  complete independent readings.
- **Request/inspection:** neither arm incorporated the required applicant name
  and reference number. B explicitly judged the isolated request permission
  complete. A filled optional fields on both permissions without improving their
  default statements. Both preserved inspection's opening hours and avoided
  transferring agency reporting duties or request requirements to inspection.

All proposals stayed within the selected edit scope. Original records and history
remain unchanged. Previews were tested independently; this does not demonstrate
combined sequential application or a production approval decision.

## What the raw results explain

The task definition matters: the same source and schema can produce meaningful
construction. However, H1's prediction that ordinary recovery would remain
inactive was not met. A generated six edits, mostly optional-field enrichment.
**Useful completeness gains, output volume and checker approval are different
measurements.** The result supports a bounded change in what gets proposed, not
a complete explanation of previous no-ops or reliable general repair.

Two implementation details also surfaced:

1. One optional non-verbatim quote rejects an entire repair. In cell 3,
   `logic_text` is the only absent component quote. It dropped a list marker, so
   whitespace compensation would not fix it. Initial extraction already has
   component-withholding behavior, but refinement checks every populated quote
   and refuses the whole proposal. Investigate reuse without loosening evidence
   requirements or silently counting a repaired capture as the original result.
2. The checker saw an internal identifier as invented source content. In cell 6,
   the raw model selected `qualifies: ["C0000"]`; the application inserted the
   actual revision identifier into `applies_to` before checking. The checker blamed
   that identifier for having no basis in the statute. It also correctly objected
   to an action/object mismatch, so removing the identifier issue alone does not
   establish that this proposal should pass.

The smaller remaining question is how to preserve a useful default-statement
edit without inviting gratuitous component rewrites. A minimal changed-fields
response, derived from existing CUE definitions and completed deterministically
from the original record, is a candidate experiment, not an adopted schema.
Use unchanged captures to test the quote/identifier handling first; then use new
sources to compare task designs. Do not keep adding instructions for these cases.

## Cost and verification

Fourteen calls completed: one extraction, eight generation and five checker calls.
They reported **75,504 total tokens**, including 31,089 thinking tokens, with no
truncations, missing responses or retries. Cumulative capture time was 118.6 seconds;
this excludes manual review and is not total user-journey latency.

| Reported tokens | A | B |
|---|---:|---:|
| Generation | 22,116 | 24,298 |
| Checking | 15,499 | 10,894 |
| Combined | 37,615 | 35,192 |

B used 9.9% more generation tokens. Its lower combined total reflects fewer
checker calls, including one skipped after validation refusal; it is not proof of
better cost per successful document. The fresh extraction used 2,697 tokens.
These are usage receipts, not verified invoice amounts or general document rates.

The original `run.py verify` failed on newly generated preview event identifiers,
which change dependent revision/assertion identifiers. [verify.py](verify.py)
reuses each saved preview event identifier, then invokes the original verification
unchanged. No model output, semantic field, criterion or source was edited.
Extraction, decoded proposals, source checks and complete preview records then
replay exactly with provider creation blocked. The original failed verification
remains documented here; pinned capture code is untouched.

[analyze.py](analyze.py) verifies actual A/B requests differ only by the construction
instruction, pension repeat requests are identical, original books match their
saved captures, and the two implementation diagnoses above. It aggregates the
frozen manual labels into [RESULTS.json](RESULTS.json). Reproduce locally:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-explicit-rule-construction/verify.py
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-13-explicit-rule-construction/analyze.py
```

See [PLAN.md](PLAN.md), [baseline labels](BASELINE-REVIEW.md), [exact requests](expected-requests),
[raw responses](captures), [usage](usage.json) and [call ledger](calls.json).
This small comparison diagnoses obstacles; it does not establish general accuracy.
