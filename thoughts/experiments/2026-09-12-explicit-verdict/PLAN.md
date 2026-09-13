# Explicit definitions and quote boundaries

Decision: Does the saved explicit assessment specification improve detection
enough to justify evaluation on fresh documents? Experiment only; no adoption.

Hypothesis: Clear definitions of item, complete statement, semantic actor, kind,
and modality, together with explicit quotation boundaries, reduce superficial
approvals and grammatical-subject objections. The competing prediction is that
the checker still approves locally plausible statements despite omitted governing
detail. This deliberately tests definitions, task clarification, and formatting
together; no result can identify a separate benefit of triple quotes or headings.

Arms: A is the previous composed-verdict prompt, including complete supplied
source repeated within each item. B uses the exact instruction block from
`thoughts/plans/2026-09-12-assessment-narrative-format.md` and its specified item
layout: `### Item R...`, a blank line, narrative surrounding exact source and
statement blocks enclosed by standalone `"""` lines, and clearly named short
actor/kind/modality values. All populated fields, evidence, and proposed terms
remain represented. The worked example and expected answer are NOT sent.

Cases: The same fixed iep-1 and lea-1 outputs: 21 items, three clearly flawed,
17 previously faithful and one uncertain. Failures include omitted transition
detail and omitted written parental agreement/consent. Conditional/optional LEA
provisions are overcorrection controls. The uncertain IEP item permits inspecting
the prior actor objection without treating its label as a known defect. Labels
remain pinned and revisable. These are selected development cases, not holdouts.

Held constant: Source availability and order, extracted meanings and record order,
gemini-3.8-flash, temperature 0, low thinking, no numeric thinking budget,
16,384 output cap, plain-text boolean/reason output. One fresh call per arm/output,
shuffled opaque IDs. No repetitions, retries, source selection changes, or model
rewrites. Enum spellings are explicit in B, rather than the prior display spaces.
Repeated full source deliberately avoids confounding a new relevance selector
with these instructions; it remains an expensive diagnostic input.

Bound: Four calls, ten minutes, or 75,000 reported total tokens, checked before
each call with one active call allowed to cross the bound. Retain all failures.

Decision rule: B merits fresh-document evaluation only if all decisions are
mechanically valid, it detects at least 2/3 clear defects, improves on fresh A,
and raises at most one false alarm on the 17 faithful controls. Report uncertain
items separately. Passing this development gate never authorizes production
adoption. If it fails, save the negative result and stop this prompt iteration.

Checks: Reuse the prior experiment's preparation, single-call capture, line
decoder, assessment and offline replay. Pin this adapter, the saved specification,
prior harnesses, source, fixed outputs, labels and runtime before calls. Check
each rendered B item contains every supplied source passage and all populated
semantic fields. Verify exact delimiter boundaries and newline behavior, every
quoted block, and absence of worked-answer leakage. Check actual SDK requests,
settings and response replay with provider creation blocked. Inspect every
negative reason and every known-defect approval against raw text.
