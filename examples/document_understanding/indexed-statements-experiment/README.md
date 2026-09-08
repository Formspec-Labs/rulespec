# Shared indexes, statements, and keyword guidance

The combined trial is **not ready to replace the current extractor**. It produced
slightly more direct wording and useful shared citation IDs, but invented a role
label, retained no explicit exception links, and lost one accepted rule through
an inexact component quotation. The ordinary extractor was not changed.

## What was tested

Four Gemini 3.8 Flash requests, all at temperature 0: current versus experimental
schema on the same name-change and photo excerpts. One request per cell, no retries,
audit, refinement, or additional provider calls. These are known development cases,
not a blind holdout; the combined changes cannot isolate individual effects.

The experimental [CUE schema](experiment.cue) puts roles, citations, and concepts
before the extracted units. It reuses the current profile's meaning/evidence types
and Core component definitions. The units use `statement` rather than `summary`,
with direct-writing guidance. Conversion maps that field and index references into
the existing candidate/Core format; it does not introduce another Core schema.

Keyword guidance is in the `#Response` description and survives native generation
into the actual request schema:

- `unless`, `except`, `other than`: inspect possible exceptions.
- `if`, `when`, `provided that`, `only if`: inspect governing conditions.
- `must`, `shall`, `should`, `may`, `not required`: preserve source force.
- `either`, `one or more`, `all of`: retain grouping.
- `within`, `before`, `after`, `at least`: retain timing and thresholds.
- `means`, `refers to`, `defined as`: inspect definitions.

The guidance explicitly treats words as clues, not automatic legal operators.
This trial did not add a separate keyword-scanning process.

## Observed results

| Output | Current | Indexed statements |
| --- | --- | --- |
| Names: raw / accepted units | 13 / 13 | 12 / 11 |
| Photos: raw / accepted units | 10 / 10 | 11 / 11 |
| Explicit qualification links, both documents | 0 | 0 |
| Total reported tokens, both documents | 21,542 | 23,622 |

The treatment used about 9.7% more reported tokens. Its extra thought tokens
contributed most of the difference. The whole experiment used 45,164 tokens across
four calls. No current dollar-price lookup was made. Usage and request timing are
preserved in each `runs/*/stats.json` and consolidated in `verification.json`.

**Roles:** The names trial produced this shared entry:

```json
{"id":"role-passport-agent","label":"Passport Examiner / Adjudicator",
 "title":"","aliases":["you"],"quote":"you"}
```

The supplied source does not establish that title. Keeping `title` empty did not
stop the same invention appearing in `label` and the human-readable ID. Statements
still said “you.” The baseline also retained “you,” so this added an unsupported
interpretation rather than solving an observed error in this comparison. Photo
role references sometimes identify the person discussed despite an empty actor
field. A valid ID does not prove the reference means the right thing.

**Citations:** The names index contains all six distinct cited FAM/CFR references
and DS-11; the photo index contains its CFR citation. The baseline already retained
these legal labels in per-unit references. Shared IDs and repeated-occurrence
accounting are the new capabilities, not demonstrated citation recall improvement.
One defect remains: normalized `Form DS-11` differs from source `form DS-11`, so
exact label matching finds no occurrences despite a correct quote field.

**Concepts:** Global references share one name-change topic and two photo topics,
compared with 13 and ten local topics in the baselines. That reduces repeated
definitions but may erase useful topic distinctions. This trial does not establish
better tagging or cross-document concept identity.

**Wording:** The definition changes from “A material discrepancy is defined as…”
to “A material discrepancy is…”. This is cleaner. Most baseline wording was already
direct, and the trial still has long conditional sentences. Renaming alone did not
produce a large readability change.

**Meaning and links:** Both variants retain the previous-name exception in prose
but neither creates a separate exception link. Both preserve the tested emergency
and recent-change conditions and the photo recommendation's `should`. The names
identity explanation moves from a standalone unit into context; the photo trial
gains a standalone statement of the infant-photo goal and keeps the certificate
timing caution. The infant goal's `possible` classification remains debatable.

**Refused content:** The trial contains all six name-document options in raw meaning,
but its court-order option quote joins source lines and changes markers. Existing
exact-evidence checks refuse that entire unit. Its married-name exception remains
in `scope_text` but is absent from the direct statement. This is a raw grounding
failure plus an acceptance loss, not proof that the model omitted all six options.

## Verification and artifacts

- `design.json` fixes the comparisons and review questions before requests.
- `experiment.cue`, `provider.schema.json`, and `native-export.json` preserve the
  experimental schema and native CUE output. `build/` pins imported CUE sources.
- `runs/*` contains exact requests/responses, decoded output, mapped candidates,
  unresolved index observations, refusals, compiled rulebooks and validation.
- `assessment.json` records source-review findings and evidence pointers.
- `verification.json` records identical offline decoding, conversion, and Core
  graphs for all four captures, matching request schemas and runtime hashes.
- Three offline adapter/schema tests pass. All four Core graph validations pass.
  These checks establish mechanics; the semantic failures above remain.

LangExtract rejected the initial experimental wrapper name `statements` locally
before either experimental request was sent. Its supported schema interface
requires the outer array to be called `extractions`. The wording field remains
`statement`, and the indexes still precede it. `preflight/` preserves that initial
configuration; `amendment.json` records the wrapper correction and two remaining
requests. `frozen/` retains both runner versions. This was not a provider retry.

The initial run manifest covers the acquisition and processing artifacts; later
assessment and verification files are separate review products. Preserve them all.

## Decision

Keep this as evidence for a smaller next iteration. Direct statement wording and
an exact citation index are promising. Roles need verbatim source labels and a
clear distinction between participants and responsible actors. Exception links
likely need a representation the model can fill naturally, such as qualifications
attached to a statement and converted deterministically, rather than further
keyword reminders to emit duplicate units. None of those follow-up changes is
silently adopted by this experiment.
