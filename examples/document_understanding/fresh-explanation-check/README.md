# Explanation accuracy on fresh documents

**Keep dedicated logic and modality explanations out of production.** Neither
passed the preregistered accuracy gate on three fresh regulatory sections. Logic
produced no repair beyond both controls. Modality produced one such repair, but
also introduced failures elsewhere. These results do not justify adding either
field to the default extraction schema.

Twelve fresh calls compared four versions on each source:

- Current production statement-first schema and prompt.
- Omission-only cleanup, without an explanation field.
- The already-tested logic explanation plus that same omission cleanup.
- The already-tested modality explanation plus that same omission cleanup.

All used Gemini 3.8 Flash, temperature 0, low thinking, 16,384 maximum output
tokens and the complete section in one window. Each cell had one call. No guidance
was changed after retrieval or results; no repairs, audits or retries were added.
Native CUE generation confirmed that each explanation variant differs from the
omission-only schema solely by its required-nullable first explanation property.
The [plan](PLAN.md) and [30 source-based checks](REVIEW.md) were frozen before calls.

## Accuracy findings

Counts below cover the selected checks on these sections, not a general accuracy
percentage. Every independent statement was reviewed; a complete neighboring
record or explanation could not repair a missing qualification.

| Source | Current extraction | Omission only | Logic explanation | Modality explanation |
|---|---:|---:|---:|---:|
| Oxygen, 8 checks | 8 | 7 | 8 | 7 |
| Employee alarms, 10 checks | 8 | 9 | 8 | 9 |
| Procurement, 12 checks | 12 | 12 | 11 | 11 |

**Logic: no unique accuracy gain.** It retained the oxygen exemption's lower
boundary that omission-only lost, but current extraction already retained it.
On procurement, it labeled a descriptive possibility as permission: a proposals
method “may result in either a fixed-price or cost-reimbursement contract” became
`may` rather than `possible`. Both controls got that distinction right. Both
contract types remained in its statement; this was a classification failure.

**Modality: one useful repair, offset by failures.** It was the only alarm output
to retain the “all employees can hear” guard in the separate backup-system
exemption. Both controls lost that guard. However, its separate oxygen exemption
omitted the inherited **above FL350** boundary, leaving only **at or below FL410**;
current extraction retained both. Its procurement output omitted the entire
descriptive contract-type possibility. It also omitted other material, including
the sealed-bid definition/preference and written fixed-price award to the lowest
responsive/responsible bidder. Lower token use on that output is not a quality win.

The alarm device-rotation rule adds an interpretation-sensitive issue: current,
logic and modality outputs dropped the preceding non-supervised-system setting
when splitting the rule, while omission-only retained it. Our standalone-scope
rubric treats this as a failure. **Excluding that check does not change the
decision:** logic still has no gain over both controls and loses a procurement
classification; modality still has only one-source gain and loses oxygen and
procurement meaning.

The gate required at least two field-relevant repairs across at least two sources
against both controls, with no new named failures or unsupported material notes.
Logic had zero qualifying repairs; modality had one on one source. Both fail.
This is evidence against adopting these exact explanation variants, not proof
that explanations can never help.

## What the explanations actually contributed

Logic produced 11 populated notes and 60 nulls: seven notes on oxygen, four on
procurement and none on alarms. Some correctly described AND/OR and override
relationships, but the controls already preserved those relationships. An oxygen
note itself omitted the lower altitude boundary even though its matching statement
retained it. First-position notes were not a reliable account of all extracted
qualifications.

Modality populated 66 of 67 notes. Most mechanically repeated explicit must,
shall, may or need-not wording. Its successful alarm-exemption note merely said
that “need not” signals exemption; it did not explain the inherited hearing
condition that appeared in the improved statement. The run-level improvement
therefore does not establish that an explicit condition-binding explanation caused
the repair. A note used ambiguous “bimonthly” while its statement correctly said
every two months. Notes remain interpretation, never authoritative source evidence.

## Tokens and mechanical validation

| Version | Output tokens | Change versus omission only | Populated notes | Note nulls |
|---|---:|---:|---:|---:|
| Current extraction | 11,109 | +37.3% | — | — |
| Omission only | 8,092 | — | — | — |
| Logic explanation | 8,935 | +10.4% | 11 | 60 |
| Modality explanation | 6,824 | −15.7% | 66 | 1 |

Current extraction emitted 277 other optional nulls; the three omission-policy
versions emitted none. Populated enrichment, segmentation and omissions also
changed, so token differences are not the isolated cost of explanation strings.
Reported input tokens totaled 9,050 for current extraction and 9,209 for each
other arm. All twelve calls used 71,637 total reported tokens; thinking-token counts
were unavailable. No dollar-cost estimate is inferred from those counts.

All 289 emitted records were accepted, with no schema/response errors, refusals or
rejections. All twelve Core graphs validated; unresolved reference records remain
(2–14 per run). Actual schema contents, property order, model and request settings
were verified. These checks establish mechanical validity, not complete or correct
document understanding.

## Sources, limits and reproducibility

The official eCFR API supplied these full sections as of **2026-09-04**:

- [14 CFR 91.211 — Supplemental oxygen](https://www.ecfr.gov/on/2026-09-04/title-14/section-91.211).
- [29 CFR 1910.165 — Employee alarm systems](https://www.ecfr.gov/on/2026-09-04/title-29/section-1910.165).
- [2 CFR 200.320 — Procurement methods](https://www.ecfr.gov/on/2026-09-04/title-2/section-200.320).

The retrieval log includes exact API URLs. Initial annual-edition HTML/OSHA-page
retrievals were unavailable; the API rejected September 8 as beyond its available
date, so September 4 was used. No extraction call occurred until the successful
XML retrievals and review criteria were frozen. XML HEAD/P text was joined with
blank lines, removing markup and trimming boundary whitespace. Original XML and
prepared text/digests are saved together; no model generated the test documents.

No prior occurrences of these section numbers/titles were found in the experiment
records, thoughts or extractor tests searched before retrieval. This is freshness
relative to repository evaluation, not training-data novelty. These are three
selected sections, not random corpus sampling or full-manual validation.

Statement and modality judgments were saved under randomized opaque IDs before
notes or arm labels were read. Existing optional fields can hint at assignment,
so blinding is imperfect. The reviewer was Codex; labels are revisable, not human
gold. One call per cell measures neither repeatability nor a population error rate.

[Statement judgments](statement-review.json), [note review](explanation-review.json)
and [metrics](metrics.json) preserve the evidence and the failed gates. The original
requests/responses, sources, runtime/schema hashes and all earlier experiments are
preserved. This trial changes no production code or UI and makes no commit.

Replay verifies pinned inputs, exact requests and identical parser/Core results
without provider calls. From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python examples/document_understanding/fresh-explanation-check/run.py replay
```

Stop this explanation-field hypothesis branch. Keep these sections frozen rather
than tuning against the observed failures. The remaining actionable problem is
faithful standalone conditions and semantic coverage; a future approach should
show a benefit over current extraction before adding more default output fields.
