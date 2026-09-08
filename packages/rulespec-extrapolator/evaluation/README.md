# Source-reviewed evaluation

This evaluation reports whether a named reviewer found faithful meanings,
correct actors, complete selected content, supported claims, correct scope and
links, and usable rule boundaries. It does not infer semantic correctness from
matching words or valid evidence coordinates.

The corpus contains 12 short excerpts from the U.S. Department of State's
Foreign Affairs Manual (FAM): six development excerpts from
[8 FAM 402.1, Passport Photographs](https://fam.state.gov/FAM/08FAM/08FAM040201.html)
and six held-out excerpts from
[8 FAM 403.1, Name Usage and Name Changes](https://fam.state.gov/FAM/08FAM/08FAM040301.html).
[8 FAM 103.1, Responsibilities](https://fam.state.gov/FAM/08FAM/08FAM010301.html)
provides shared context for the manual's addressed adjudicator. The selected
text includes definitions, shared qualifications, exceptions, cross-section
references, numeric wording, and distinct actors.

## Source and label boundaries

- `corpus/manifest.json` lists source URLs, exact file paths, capture receipts,
  SHA-256 digests, section labels, and excerpt coordinates.
- `corpus/original/` preserves the HTML bytes fetched with certificate
  verification enabled. The pages declare ISO-8859-1. Preparation decodes that
  encoding strictly, resolves HTML entities, collapses paragraph whitespace,
  and preserves paragraph order. It does not interpret the rules.
- `corpus/prepared/` retains the full page text for neighboring context.
  Excerpt offsets index Unicode codepoints in these files. Each excerpt file
  is the exact selected substring. Embedded example photographs and page
  layout are outside this text evaluation.
- `development-labels.json` contains 32 agent-authored expected units, source
  spans, actor notes, qualifications, references, and boundary notes. These
  provisional source reviews are **not human gold**.
- `holdout-labels.json` contains separately authored labels. Keep this file
  outside extraction prompts, tuning, repair, and other workers' inspection
  until the integrator freezes the extraction output files and their digests.
  `holdout-seal.json` pins the label bytes before output inspection. The seal
  records a workflow boundary; it is not access control and cannot establish
  absence from a model's pretraining data.

The source itself may be supplied to extraction. Independence concerns when
answer labels influence development. Full-page context does not expand the
coverage targets beyond the selected excerpts. A reference to another section
does not establish that its meaning has been resolved.

To verify preparation from the saved originals without network access:

```sh
python3 packages/rulespec-extrapolator/evaluation/build_corpus.py
```

The builder refuses to replace different pinned bytes. A new source edition
needs a new corpus directory and a new source review. Initial acquisition uses
`--download-missing`; ordinary evaluation and replay need no network or model.

## Rubric

Review every accepted claim, including claims that match no expected unit.
For each dimension, record `correct`, `error`, `unknown`, or an applicable
`not_applicable`. Missing dimensions remain `unknown`. Summary, support, and
boundary judgments cannot use `not_applicable`.

| Dimension | What the reviewer checks | Typical error |
| --- | --- | --- |
| `summary` | The complete claim preserves the source's meaning, modality, negation, actions, and numeric wording. | A fee requirement replaces a suspension duty while the original quotation remains. |
| `actor` | Each action belongs to the stated or supported inherited actor. Keep the applicant, adjudicator, specialist, and medical signer distinct. | An applicant receives the specialist's suspension duty. |
| `support` | Every substantive part is supported in the selected source/context; inspect unmatched and additional claims too. | An unrelated subscription duty accompanies otherwise correct rules. |
| `scope` | Conditions and exceptions attach to the correct rules with their grouping intact. Preserve unsupported logic verbatim with explicit uncertainty. | A medical exception becomes unconditional, or OR alternatives become an AND list. |
| `links` | Target references and shared qualifications point to the intended rules. Missing context remains unresolved. | An infant exception is attached to a general applicant rule with its age scope lost. |
| `boundary` | Splits, merges, and duplicate occurrences preserve independently reviewable meanings and qualifications. | One actor/action disappears inside a merged summary, or a split exception loses its target. |

For each expected unit, separately record `covered`, `partial`, `missing`, or
`unknown`, with reviewed claim IDs. A claim may cover several units and several
claims may represent one unit. `covered` requires current claim judgments with
no semantic errors or unknown dimensions. `missing` requires an explicit
reviewed omission judgment; the absence of a judgment remains `unknown`.

Evaluate nuanced wording as written. A `should` is not automatically a `must`.
Examples need not become separate rules. Definitions do not always have an
acting party. Verbatim complex logic with an explicit unresolved issue may be
faithful even when the application cannot execute the logic. Do not reward an
invented precise numeric or logical interpretation.

## Interface and review records

```python
from rulespec_extrapolator.evaluation import (
    claim_digest, content_digest, evaluate, compare_runs, subset_expected,
)

scoped_labels = subset_expected(expected_labels, ["fam-photos-06"])
report = evaluate(rulebook, scoped_labels, judgments)
unreviewed_report = evaluate(rulebook, expected_labels)
differences = compare_runs(first_fresh_rulebook, second_fresh_rulebook)
```

`rulebook.accepted` contains immutable application revision IDs. Judgment
records also pin exact claim content, the full rulebook, and the label file's
canonical JSON. These digests use Rulespec's existing `canonical_json` helper.
Changing the summary, actor, evidence, or any reviewed content invalidates the
earlier judgment even if the caller retains the same ID. Adding a claim also
changes the rulebook digest and requires an updated assessment.

`subset_expected` restricts expected units to explicit excerpt IDs and retains
pinned source text needed for context. The returned labels record the selection
and parent digest. Use judgments bound to that returned label digest. Unknown,
empty, or duplicate selections fail visibly. Selecting held-out labels still
requires the output freeze; the helper does not change the sealing protocol.

`expected_labels` uses `schema_version: rulespec-evaluation-labels/1`, exact
`sources` with `id`, `text`, and `sha256`, `label_provenance`, and
`expected_units`. Each expected unit includes `id`, `excerpt_id`, `meaning`,
and nonempty `source_spans`.

`judgments` uses this shape:

```json
{
  "schema_version": "rulespec-evaluation-judgments/1",
  "review_provenance": {
    "reviewer": "Named reviewer",
    "reviewer_kind": "aiAgent",
    "method": "source_review"
  },
  "rulebook_sha256": "content_digest(rulebook)",
  "labels_sha256": "content_digest(expected_labels)",
  "claim_judgments": [
    {
      "claim_id": "immutable application revision ID",
      "claim_sha256": "claim_digest(claim)",
      "unit_ids": ["expected unit ID"],
      "dimensions": {
        "summary": "correct",
        "actor": "correct",
        "support": "correct",
        "scope": "correct",
        "links": "not_applicable",
        "boundary": "correct"
      },
      "rationale": "Explain what was checked against the cited source.",
      "source_spans": [
        {"source_id": "source ID", "start": 0, "end": 5, "quote": "exact"}
      ]
    }
  ],
  "unit_judgments": [
    {
      "unit_id": "expected unit ID",
      "status": "covered",
      "claim_ids": ["immutable application revision ID"],
      "rationale": "Explain the reviewed match or omission.",
      "source_spans": [
        {"source_id": "source ID", "start": 0, "end": 5, "quote": "exact"}
      ]
    }
  ]
}
```

Use `humanUser` only for an actual identified human reviewer. Record
agent-generated review and demonstration effort as `aiAgent`. Exact source
spans prove that the reviewer referenced pinned text; the evaluator cannot
prove the reviewer's semantic judgment is sound.

The report returns per-dimension correct/error/unknown counts, explicit
omissions and partial coverage, error examples, integrity issues, and reviewer
provenance. It returns `passed` only for complete, internally consistent review
with no reported semantic errors or omissions. `failed` means reviewed errors
or omissions exist; `needs_review` means no known failure was recorded but
review remains incomplete. `review_complete` is separate from the outcome.

No composite accuracy score is produced. The small corpus and agent-authored
labels support debugging and a review workflow, not a general accuracy claim.

## Fresh runs and review effort

Freeze both fresh held-out runs before exposing labels. Record each original
`rulebook.json` digest and the freeze timestamp. Only then compare output with
the sealed labels and save explicit source judgments. Corrections belong in
new review records; preserve the frozen output. A repair informed by held-out
labels is a follow-up development result, not another held-out measurement.

`compare_runs` reports changes in exact material fields and duplicate counts,
ignoring run-specific IDs. It describes differences, not semantic equivalence.
Review paraphrases against the source before judging repeatability.

Use `review-effort-template.json` for both an assisted correction pass and a
manual extraction pass on comparable text. Record actor kind, source sample,
start/end time, active seconds, pauses, edits, splits, merges, rejections,
approvals, and unresolved units. Report observed counts and time with the
comparison limitations. Agent demonstration time is not human reviewer time
and cannot establish human time savings. No human timing study has yet been
performed for this corpus.

## Verification and findings

The isolated evaluator checks pass in
`packages/rulespec-extrapolator/tests/test_evaluation.py`. The tests retain an
exact quotation while replacing every summary with a false fee duty or
replacing actors with commercial photographers. Old judgments become stale;
fresh negative source judgments report the relevant semantic errors. An
unreviewed invented extra claim blocks a pass even when all expected units
are covered. These tests address the prototype's unchanged 20/20 blind spot.

```sh
PYTHONPATH=packages/rulespec-extrapolator/src:packages/rulespec-projection/src:src \
  .tools/document-poc-venv/bin/python -m pytest \
  packages/rulespec-extrapolator/tests/test_evaluation.py -q
```

Source acquisition initially hit a web-fetch 502 and a Python certificate-store
error. System `curl` fetched all three official pages with certificate
verification enabled. No insecure TLS fallback was used. The saved corpus
reproduces from original HTML without network access.
