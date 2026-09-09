# Explanation fields have different outcomes

**Logic produced the most selective substantive explanations. Modality produced
inspectable classification justifications. Actor was mostly null. Applicability
mostly produced generic summaries and did not repair the known condition miss.**
No field demonstrated a repair on its predefined matching statement checks;
production remains unchanged. These are separate outcomes, not a single score
for whether more explanation is good or bad.

## What was tested

The [plan](PLAN.md) and [field-specific rubric](REVIEW.md) were frozen before
fifteen fresh Gemini 3.8 Flash calls: five arms on the same full passport, notice
and waste sources, one call per cell. Each used temperature 0, low thinking,
a 16,384-token output allowance and the same extraction prompt. Dispatch order
was randomized. No retries, repairs, audit calls or extra experiments were made.

Four treatments each added exactly one field before `statement`:
`actor_explanation`, `modality_explanation`, `logic_explanation` or
`applicability_explanation`. The field was required but nullable, with instructions
in its schema description to give at most two concise, source-grounded sentences
only when the field needed interpretation. The baseline used current production
schema and prompt unchanged. These are per-field bundles of name, guidance and
required nullable slot, not isolated tests of naming or requiredness.

Each schema was generated using the existing native CUE exporter from an isolated
copy of the canonical application profile. Removing the one new field reproduces
the baseline schema exactly. No production schema or parser was modified.
Experimental notes are retained by raw row; the unchanged production parser
receives the response with only that new field removed, after trial-schema
validation. Notes do not become source evidence or accepted Core assertions.

## Field-specific results

| Field | Non-null notes | Matching statement checks, baseline → treatment | Observed behavior |
| --- | ---: | --- | --- |
| Actor | 1/47 | 5/5 → 5/5 | Correctly explains literal `you`; otherwise null. Named actors were already correct. |
| Modality | 28/46 | 5/5 → 5/5 | Usually grounded in modal wording; many explanations repeat explicit must/may. |
| Logic | 7/48 | 6/6 → 6/6 | Selective explanations of AND/OR, exceptions and deadline alternatives; controls already passed. |
| Applicability | 46/47 | 4/5 → 4/5 | Mostly descriptions of what paragraphs do, rather than why conditions attach to a unit. |

Each row has its own criteria; do not combine these unequal counts into a general
accuracy estimate. The actual notice failure reproduced in the baseline and all
four treatments. Other named baseline controls mostly passed already, limiting
what this sample can establish about repairs. Row counts vary with segmentation.

All 188 required explanation slots were present and appeared before the statement.
That establishes slot/order adherence. It does not establish that the note was
substantive, correct or useful; 106 slots were null and applicability frequently
missed the requested interpretive task despite non-null text.

### Logic: substantive and selective, with no measured extraction gain

Waste R09 row 8 explains that labeling "cumulatively requires both" the words
Hazardous Waste and an indication of hazards. Rows 2, 7 and 9 correctly explain
alternative antecedents, nested venting exceptions and the three-day compliance/
removal choice. Passport R05 explains approval exceptions and consultation/contact
alternatives, mostly by restating the rule. All notice logic notes were null.

These notes are plausible review aids. The corresponding baseline statements
already preserved the tested logic, so the notes did not demonstrate a repair.
The logic waste statement also omitted illustrative hazard-label methods and
citations that the baseline retained. The mandatory AND relationship remained
correct; this is a separate completeness regression in this sample.

### Modality: inspectable classifications, with an uncertainty signal

Notice R03 row 16 explicitly describes "may not be required" as a possibility
depending on circumstances, and uses `possible`. The baseline used `not_required`
while preserving "may not be required" in the statement. This is a useful signal
for preserving uncertainty in structured classification, but the exact label was
preregistered as uncertain rather than independent gold; it does not change the
five unambiguous checks above.

The notes also distinguish descriptive possibilities from permissions. Many
simply explain that `must` establishes a duty or `do not require` an exemption.
Those correct explanations add little when the underlying classification is
already explicit. Interpreting "expected" conduct as `should` remains a revisable
classification, not an established answer because the model justified it.

### Actor: no demonstrated need on these controls

Passport R06 row 2 notes that the source uses the unadorned pronoun `you`.
The statement preserves it. Every other actor slot was null, including the notice
and waste documents. The baseline already distinguished agencies/centers, posts,
employee/employer, spokesperson and generator categories. This sample does not
test whether the field helps a genuinely difficult actor-attribution failure.

### Applicability: the note did not perform the intended job

Notice R10 row 14 says:

> Illustrates permissible employer requirements for notice procedures.

It does not identify the unforeseeable-leave setting or unusual-circumstances
qualification. Both are also absent from the standalone statement. This is generic
description rather than the requested condition-binding explanation, so the
historical failure remains unrepaired.

Some waste notes correctly identify parent exemption/excess context; many other
notes say Identifies, Specifies or Establishes without explaining the governing
relationship. Passport R01 row 2 introduces `adjudicator` in its explanation even
though the source says `you`; the final statement still preserves `you`. This is
inferred role wording in the note, not a source-established title.

## Output cost and a null-placeholder side effect

| Arm | Reported input tokens | Output tokens | Change from baseline | Unrelated optional null fields |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 8,359 | 6,951 | — | 16 |
| Actor | 8,359 | 11,134 | +60.2% | 302 |
| Modality | 8,359 | 11,209 | +61.3% | 308 |
| Logic | 8,359 | 11,251 | +61.9% | 311 |
| Applicability | 8,359 | 10,540 | +51.6% | 191 |

Adding a required-nullable field coincided with many existing optional properties
being explicitly emitted as null instead of omitted. For example, the actor
passport response supplies nearly every optional key even though its only non-null
explanation is 65 characters long. The 60% actor output increase is therefore not
the cost of a long actor explanation. Other populated fields and segmentation
also changed. This experiment does not isolate the cause of null proliferation.

The provider reported identical input token counts across schema variants for
each source. These are recorded usage values, not proof that schema tokens are
unbilled. Total reported usage across fifteen calls was 92,880 tokens. Thinking
counts were null/unavailable, not established zero. Exact requests, usage and
field counts are preserved in [metrics.json](metrics.json) and the raw captures.

## Decision and verification

Do not adopt a general explanation field or these four treatments. The required
slots made response behavior measurable, but the matching repair criteria were
not met. Logic deserves separate consideration as an inspectable explanation;
modality may help expose uncertain classifications. Neither result establishes
better extraction or downstream user benefit. Applicability needs a different
approach to actual condition attachment, not more generic explanation text.
Resolve null-placeholder overhead before considering a broad deployment of any
required-nullable note.

The [statement review](statement-review.json) was saved under opaque randomized
IDs with experimental notes, arm names, generation order and usage hidden. The
subsequent [explanation review](explanation-review.json) inspected the notes and
could see field identity. These are revisable Codex judgments on reused development
documents, not an independent human benchmark. One call per cell does not establish
repeatability. Secondary observations remain recorded, including standalone posts
duties that lost a modification qualification retained in neighboring permissions.

All 234 raw rows passed their native trial schema and were accepted after current
parser/Core processing, with zero extraction refusals; all fifteen graphs passed
validation. Nonfatal Core issues remain in the saved results. Passing these checks
does not establish semantic completeness.

Offline checks verified native one-field changes, identical prompts, null/nonempty
notes, missing-required-slot refusal, and unchanged Core meaning when only note
content changes. All fifteen recorded requests match intended settings and ordered
schemas. All fifteen captures replay identically without provider calls. Runtime,
build inputs, sources, schemas, reviews and results are pinned in the outer manifest.
Earlier experiments and production files remain unchanged.

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python \
  examples/document_understanding/field-explanation-check/run.py replay
```

No adoption, commit, push or deployment is part of this experiment.
