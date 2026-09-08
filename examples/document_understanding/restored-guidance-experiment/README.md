# Restored guidance with attached qualifications

Restoring the fuller extraction instructions improves the known failures while
keeping passage references and explicit parent links. On these two excerpts, the
emergency permission keeps its inherited limits, separate duties become separate
records, and the hairstyle allowance no longer waives photo recency. The trial
also introduces unsupported date candidates. Keep it experimental.

## Comparison

Two live Gemini 3.8 Flash calls at temperature 0, one per source excerpt, with no
retry, repair, or audit calls. Only the prompt instructions and invented examples
changed from the attached-qualifications trial. The provider schema, descriptions,
field order, source documents, passage catalogs, corrected conversion code, model,
and complete request configuration match that trial. Comparisons use its saved
responses and corrected conversions, without rerunning the controls.

| Measure, both excerpts | Prior attached trial | Restored guidance |
| --- | ---: | ---: |
| Baseline statements | 17 | 22 |
| Qualification links | 11 | 10 |
| Links judged supported in source review | 3 | 8 |
| Links judged misleading | 6 | 1 |
| Links judged uncertain | 2 | 1 |
| Reported total tokens | 16,301 | 20,054 |

Usage increased about 23% over the short-prompt trial. It remains about 7% below
the older production-prompt controls' 21,542 tokens, but that older comparison
also changes output shape. These are token counts, not dollar costs.

## What improved

- **Emergency permission:** Statement, scope, and qualification all retain the
  more-than-one-year name change, DS-11 application, unchanged ID, and insufficient
  time before urgent/emergency travel. Previously, the first three survived only
  in the supporting source paragraph.
- **Independent duties:** The recent-change exemption and conditional duty to
  submit documentation have separate records and appropriate scopes. The general
  explanation about needing documentation is separate from the notation duty.
- **Photo meaning:** Recency remains a recommendation. Hairstyle acceptance is a
  separate permission with a good-likeness prerequisite. Head support and head
  tilt are separate. The desire to reuse a photo and certificate timing caution
  remain descriptive possibilities, without false qualification links.
- **Evidence and target selection:** All six document alternatives survive with
  exact source formatting. The previous-name exception retains its correct target.
  Every generated qualification links to its explicitly selected parent.

## What remains wrong or uncertain

The remote married-name exception is still emitted as a local qualification even
though its contents are unavailable. The parent statement's wording also risks
implying a blanket married-name exclusion. The notation-before-returning deadline
is still typed incorrectly: it becomes a prerequisite of the notation duty itself.
Its readable meaning survives, but the relationship does not represent the order
of the two actions correctly.

The new output assigns `2026-03-10` as an effective start to all 12 names baselines,
using the document's CT header date. The supplied text does not establish that date
as legal effectivity. Existing checks retain all 12 raw candidates with review
issues and emit **zero `EffectivePeriod` nodes** because the values lack complete
timestamps. This rejection does not validate the date's semantic role; adding a
timezone would not establish that the rule took effect then.

Some smaller limitations persist: the identity fact remains combined with the
possible evidence requirement; explanatory wording still enters one photo
`scope_text`; and short copied component quotations can remain ambiguous. Passage
references currently replace only selected evidence fields. A valid main passage
does not resolve every actor, action, object, or modal-force quotation.

The source review covers all 22 baseline statements and all 10 qualifications,
with component and conversion findings in `assessment.json`. Its judgments are
revisable, not gold annotations or a population accuracy estimate. These are two
familiar development excerpts, and the invented examples target known failure
patterns. A fresh-document comparison is still needed before generalizing.

## How to compose the useful pieces

| Piece | What this trial supports | Remaining decision |
| --- | --- | --- |
| Passage IDs and exact-text lookup | Reuse deterministic evidence selection | Test smaller spans where whole paragraphs are too broad |
| Complete statements and scope guidance | Keep fuller conditions and separate-action instructions | Check omissions and inherited cases on fresh excerpts |
| Explicit parent binding | Reuse target selection independently of relation type | Full review-store integration remains untested |
| Qualification classification | Assess separately from target binding | Distinguish deadlines, remote references, and actual conditions |
| Dates, attributions, normalized values | Keep raw candidates and existing Core checks | Test optional enrichment independently of statement extraction |

The next proposed comparison is a statements-and-evidence pass followed by
targeted enrichment, against this all-fields pass. Measure preserved meaning,
omissions, relationships, and total usage separately. This is a proposal, not an
implemented pipeline change. The current trial keeps a single model pass per
document and leaves production defaults unchanged.

## Verification and reproduction

The unchanged adapter's seven tests pass. All 32 converted records are retained,
with no rejected baseline or qualification. Both Core graphs validate; semantic
review issues remain. Offline replay checks the raw decoding, mappings, exact
graphs, and conformance without provider calls.

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/restored-guidance-experiment/experiment.py replay
```

`design.json` freezes the comparison before provider calls. `runs/` preserves
requests, responses, decoded output, conversions, and validation. `frozen/` retains
the prompt, runner, reused adapter, schemas, and runtime sources. `verification.json`
records controlled settings and mechanical checks; `replay.json` records replay.
The runner imports the prior adapter and checks its hash on replay. Its frozen
copy is retained for recovery if that sibling file later changes.

The schema files are byte-identical copies of the prior native CUE exports;
their original build inputs remain in the sibling attached-qualifications trial.
The acquisition manifest precedes the assessment and replay artifacts. Review
findings do not modify the original captures or conversion history.
