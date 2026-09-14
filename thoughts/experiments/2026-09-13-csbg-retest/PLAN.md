# Whole-chapter CSBG retest

Decision: assess the current installed extraction pipeline on the entire saved
CSBG chapter, and whether the existing section-window option is the better
operating choice for independently usable State-plan requirements. No production
changes, automatic repair, or further tuning are part of this retest.

Hypothesis: section-focused extraction retains more independently usable plan
contents than normal broad windows, without losing their governing assurances,
conditions, alternatives, actors, or modality. The hypothesis is weakened if the
thirteen contents remain generic pointers, or if splitting introduces meaning
errors that outweigh the granularity gain. This comparison tests window selection
as a bundle; it cannot distinguish reduced competing text from extra generation
capacity per source passage.

Arms: A is a fresh installed-CLI normal extraction (six windows). B is the same
installed CLI with `--section-windows` (27 windows). Both process the same complete
135,797-character, 979-passage chapter, including historical/editorial notes.
Historical broad and selected-section results remain labeled historical; neither
is substituted for a contemporaneous control. Review packets will hide arm names
and randomize their order before manual source comparison. Output shape can still
reveal the treatment, so masking is imperfect.

Cases: reuse the original 24 source-based meaning checks and all thirteen required
contents in 42 USC 9908(b). Read the complete application section and all output
touching it, plus the source and output for the named funding, board, designation,
monitoring, and corrective-action controls. Assess default statements separately
from extra structured fields and evidence. Record any additional observed issue.
Passing means every required content is independently addressed with its tested
subordinate detail, correct scope, and force. A pointer to a paragraph, a quotation,
or a separate unrelated rule does not supply the missing statement meaning.
Labels are revisable assistant judgments, not gold. Whole-chapter processing is
tested; exhaustive semantic review of every historical note is not claimed.

Source: reuse the pinned full 42 USC Chapter 106 from USLM release 119-102 and its
original receipt. This is the statutory CSBG application framework, not a State's
completed application form and not a claim about the latest legal edition.

Held constant: installed runtime matching checkout; generated CUE schema, prompt,
examples, source coordinates; `gemini-3.8-flash`, low thinking, provider-managed
sampling, 24,000 focus-character limit, 16,384 generation tokens. One observation
per arm, no retries, no model audit/enrichment/refinement. At most 33 model requests
and 20 minutes per arm, run concurrently. Failures count and remain captured.

Decision rule: report processing, grounding, content granularity, meaning fidelity,
and whole-document token/time consumption separately. Prefer the section option
for this source if it materially improves independently usable contents without
material regressions; do not claim universal adoption or statistical significance.
Any material missing condition, invented duty, or missing required plan content
prevents a claim of readiness for unreviewed workflow use. Stop after this retest.

Verification: check actual requests and full focus coverage, preserve original
captures, replay both saved runs without provider access, and verify discovery
exports retain all source passages. Record refusals and unlinked passages without
treating their counts as semantic omission counts.
