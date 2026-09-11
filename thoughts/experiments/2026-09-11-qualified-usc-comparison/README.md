# Qualified USC comparison: prepared, first execution deferred

The comparison is preregistered in [design.md](design.md). Its 29 frozen cases
contain three first-matching publisher paragraphs and 26 constructed development
diagnostics, including eight unchanged cases from the earlier broad comparison.
No production parser or installed package changed during preparation.

The raw surrounding sections were read before labeling:

- **5 CFR 6.8(d):** two distinct citations, `5 U.S.C. 3105` and
  `5 U.S.C. 5372(b)`, among appointment dates. The dates are not more USC targets.
- **5 CFR 302.303(b)(3):** `5 U.S.C. chapter 81, subchapter I` qualifies the
  employment-list eligibility provision. Dropping subchapter I would broaden
  the stated target. Neighboring paragraphs describe other eligibility categories.
- **5 CFR 315.608:** `50 U.S.C. 403j` and `50 U.S.C. 402, note` appear within an
  employment-category list. The note marker belongs to section 402; the adjacent
  public law and Berlin Tariff Agreement do not supply additional USC sections.

[Selected sources](selected-sources.json) identify the pinned source file, its
digest, source byte bounds, and saved surrounding XML. [Cases](cases.json) retain
the exact paragraph text and revisable written-target expectations.

Current code inspection already establishes useful boundaries, without treating
them as measured parser outcomes:

- SpicySearch strict mode now preserves compound section tokens and stated ranges;
  the older head-only limitation belongs to its permissive query mode. Its native
  output has no appendix, note, chapter or pinpoint fields.
- RefSpec `AuthorityCitation` already represents appendix, note, chapter and range
  interpretation, but its authority API returns deduplicated readings without
  occurrence positions. Its subsection helper searches by normalized section and
  intentionally returns no unique pinpoint for competing occurrences. It is not a
  substitute for an occurrence API with original positions.
- RefSpec's existing CFR reader demonstrates a shared match recorder that can
  preserve source positions without changing the identity-only caller. Reuse that
  design when R6 proceeds, preserving the existing authority grammar and its
  whole-field consumers.

The two reader source files match their working installed copies by SHA-256.
The comparison runner records all loaded sibling source hashes and original native
results, serializes execution under the existing measurement lock, and stops
waiting after five minutes. The first attempt reached that limit before any parser
call: host load stayed above the required threshold of 4 and finished at 8.91.
The [execution refusal](not-run.json) preserves the input hashes, resolved modules,
source hashes and repository state. The process exited with code 1; no job remains
running, and no raw parser results were produced.

No parser outcome is claimed until a new attempt produces raw results that are
manually reviewed. Preserve `not-run.json` when retrying, and give another failed
attempt its own output path. A load refusal is an execution limit, not evidence
for either hypothesis. R5/R6 remain open on the
[task list](../../plans/2026-09-10-reference-integration-task-list.md).
