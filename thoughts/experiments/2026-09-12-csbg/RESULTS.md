# CSBG: useful evidence, incomplete rule-by-rule extraction

**Decision:** Rulespec provides a useful foundation for source-backed discovery,
but this harder document exposes a material gap in the original segmentation
goal. It can preserve a dense requirements list as evidence while replacing its
meaning with a short reference to the list. Keep linked evidence. Independently
usable requirements are a core acceptance criterion for the other half of the
product: another AI should be able to use them to propose a form or workflow for
human review. This run does not meet that criterion reliably. No production
behavior changed in this experiment.

## What we tested

The complete **42 USC Chapter 106, Community Services Block Grant Program**,
including historical and editorial notes, from the pinned official USLM release
119-102. This is the CSBG statute, not a completed State application or a CFR-only
regulation. Section 676 of the Act is codified at 42 USC 9908, the application and
State-plan provision. The pinned edition is not asserted to be the latest law.

The existing native RefSpec reader prepared **135,797 characters, 979 passages,
and six normal extraction windows**. The [source receipt](source-receipt.json)
distinguishes the source archive/member from the serialized chapter and records
their digests. The chapter is about 6.7 times the length of the largest selection
in the preceding simple-path experiment. A search of existing research notes found
no prior CSBG evaluation; this run now becomes development evidence.

The [plan](PLAN.md), [24 meaning checks](cases.json), [12 discovery questions](questions.json),
source, settings and harness were pinned before calls. The installed package ran
outside the checkout with `PYTHONPATH` unset. Defaults were unchanged:
`gemini-3.8-flash`, low thinking, temperature zero, 24,000-character windows and
16,384 output tokens per call. One observation per window; no retry, audit,
refinement or model comparison.

## Processing and grounding

| Measure | Observed result |
|---|---:|
| Provider calls | 6 |
| Complete responses ending `STOP` | 6 |
| Raw extracted units | 209 |
| Accepted statements | 208 |
| Rejected statements | 1 |
| Source passages preserved in discovery export | 979 / 979 |
| Provider-recorded input tokens | 70,772 |
| Provider-recorded output tokens | 59,099 |
| Total recorded tokens | 129,871 |
| Extraction process time | 165.8 seconds |

All outputs were structurally complete, with no truncation. Core/SHACL validation
passed and installed-package replay reproduced the original rulebook exactly
with model setup disabled. This establishes reproducible processing, not complete
or correct legal meaning. See [verification](verification.json).

The run status is `partial`. Twelve component problems were recorded: six
non-exact modality quotations and six definition/reference-index problems. For
example, the model emitted `no part ... may be used` as a quote; the literal
ellipsis is absent from the source, so that supporting component was withheld.
The statements and primary source evidence survive.

Core separately records **90 component-evidence issues across 70 accepted
statements**: 53 modality, 36 actor and one context issue. These are unresolved
support locations, not 90 demonstrated semantic errors. Broad source selections
can contain multiple occurrences of a short actor or modal phrase. The main
State-plan selection, for example, contains two occurrences of its actor quote
and five of `shall`; the statement retains the actor/modality values, with their
support flagged for review.

One faithful reporting-cap sentence, 42 USC 9917(b)(3), was rejected because the
model labeled it `kind=threshold` and `modality=must`, a combination the current
Core check rejects. The sentence limits reporting funds to $350,000. Its original
source, raw candidate and rejection remain available. This is a classification
failure, distinct from the large-list omission.

The export marks 519 passages `processed` and 460 `needs_attention`, reflecting
whole-window status when a component problem occurred. All six windows received
responses; 460 is not a count of omitted passages. The 571 passages without linked
statements include headings and notes and are not a semantic omission count.

## What the manual review found

The [meaning review](meaning-review.json) contains **17 faithful, two partial and
five missing checks**. These are overlapping, targeted assistant judgments, not
an accuracy percentage. We reviewed all raw units touching 9908 and the named
neighboring checks, including their accepted output and relevant evidence/issues.
We did not conduct an exhaustive semantic audit of the entire chapter. A faithful
textual reading can still contain an unexpanded legal cross-reference and need
assembly before becoming a workflow.

The strongest failure is concentrated in **9908(b)**. One extraction selects all
8,648 characters, but its 524-character statement concludes with:

> including the assurances and information set forth in paragraphs (1) through (13).

The actor, submission deadline and one-to-two-year plan period are retained.
The thirteen required plan contents are not expressed individually. The
[item-by-item review](state-plan-content-review.json) records all thirteen native
subsection identifiers and their source text; each overlaps only this one claim.
For example, the meaning omits:

- The community-action-plan funding condition, community-needs assessment, and
  requirement to submit that plan to the Secretary **only on request**.
- Procedures for people or organizations to petition for adequate representation.
- The prior-year proportional-funding assurance and its notice/hearing conditions.
  Separate definitions of reduction versus termination cause are retained elsewhere.
- Optional program examples and qualifications such as **where appropriate** and
  **to the maximum extent possible**.

The broader performance-system rule is retained independently under 9917, but
its existence does not recreate the missing State-plan assurance, named ROMA
alternative, and required plan descriptions under 9908(b).

The loss happens **in the model's original response**, before deterministic
conversion. Every nonempty source line from all thirteen items was present in the
actual request, and all meaningful text remains in the accepted main evidence.
The affected call generated 9,737 tokens against a 16,384-token cap and ended
`STOP`. This rules out input omission by preparation and output truncation for
this particular failure. It does not establish why the model chose this level of
detail. [Request checks](request-content-check.json),
[raw response](extract/attempt-0001.response.json), and
[accepted rulebook](extract/rulebook.json) preserve the trace.

There are strong counterexamples to a general inability to handle logic:

- The private-board elected-official shortage exception and low-income member
  residence requirements remain intact.
- The public organization's tripartite-board **or** State-specified-mechanism
  alternative survives, without imposing the private-board rules on both branches.
- The corrective-action statement retains appropriate assistance **or** a reasons
  report, a **discretionary** quality-improvement plan, its 60-day period, the
  separate 30-day response deadline, and proceedings **unless** the entity corrects
  the deficiency.
- The FY2000-only transition survives the extraction-window boundary with its
  time limit. The State's permission to revise a plan remains distinct in wording
  from the requirement to submit the revision.

Those examples are sometimes long combined statements. Their meaning is useful,
but their actions still need separation for fine-grained tagging or form/workflow
construction. Forcing every list into one statement would not solve that need.

User clarification after review: downstream form/workflow preparation is half of
the original goal. Its output can require human review, but the downstream AI
should not have to rediscover the thirteen requirements from an undifferentiated
quotation. The original checks and results stay unchanged; this clarification
changes the priority assigned to the observed failure. Human review does not
compensate for failing to produce the intended intermediate requirements.

## Linked evidence and references still add value

The unchanged BM25 top-three diagnostic ranks the same source records in both
primary arms. It measures retrieval of exact expected support, not answer quality.

| Retrieval arm | Fully supported questions | Returned evidence characters |
|---|---:|---:|
| Source alone | 7 / 12 | 9,897 |
| Same source hits plus linked evidence | 8 / 12 | 60,077 |
| Summaries-only, separate diagnostic | 6 / 12 | 31,133 |

Linked evidence recovers the public-board alternative and its context: Q10
improves from one to all three required support passages. There are no losses.
This is another bounded positive result on a new, harder source; twelve selected
questions cannot establish the frequency or size of the benefit more broadly.

Crucially, source-based discovery still answers the community-action-plan and
performance-system support checks whose extracted meanings were missing. That
is the practical value of preserving the source. It does not make the missing
rule records available for independent tagging or workflow assembly.

Four questions remain incomplete: funding termination, revising a plan, the
obligation period accompanying recapture, and the training/technical-assistance
exclusion from administrative expenses. The first two are largely ranking misses
in this lexical diagnostic; no embedding or real downstream consumer was tested.
The roughly 6.1-times evidence-character total includes repeated evidence and
roles across hits. It is not billed output tokens, unique coverage, or measured
consumer latency. See [retrieval results](retrieval.json).

The deterministic native reference scan retains **573 publisher references**:
102 occurrences resolve to 50 targets within the selected XML and 471 are outside
this chapter. For example, 9908(b)(8)'s reference locates 9915(b), and the eligible-
entity definition locates the board section. Located targets in the
[reference-enabled export](discovery.json) are separate from the draft statement's
textual reference status; they do not automatically attach missing qualifications.

## What this changes about the assessment

The infrastructure is at a useful stopping point: source identity, native
references, captures, refusal reporting, replay and source-preserving discovery
work on a substantially larger document. The model's segmentation is less
dependable than that foundation. This chapter supplies a concrete, high-value
failure to address: dense mandatory lists can become reference-only summaries.

The next experiment should isolate that failure on the saved input. Compare the
unchanged baseline with a focused extraction of the complete State-plan content
list, retaining its parent, before adopting any new splitting rule. Measure
whether all thirteen requirements emerge with conditions intact, and use the
faithful board/corrective-action cases as controls against harmful fragmentation.
This is a proposed test, not evidence for a new production heuristic. There is
no reason from these results to remove linked evidence or add a mandatory audit.

The user subsequently clarified that immediate work should focus on capture,
deferring form/workflow mapping. Required content, responsible actors, conditions,
alternatives and supporting sources must survive in the extracted records. Reuse
existing Rulespec records and evidence relationships before considering schemas.

The context question has two distinct cases. All thirteen CSBG plan contents
were already in the focus request; duplicating their text as extra context does
not address the observed omission. A focused follow-up should make those contents
the extraction target. The current model request and resolver permit new main
statements from `F` focus passages only; `C` context passages support interpretation.
Supplying a paragraph only as context is not permission to extract its own rules.
For a referenced paragraph outside a request, the existing
reference resolver and `context-export` can assemble located target text and its
surroundings. That export is not automatically supplied to ordinary extraction,
audit or refinement. `documents.with_context` adds bounded parent/adjacent text;
later checks also include selected claim evidence. Neither generally traverses
citations to fetch missing paragraphs. Testing that integration is separate from
the already-present CSBG content failure; no new context behavior was adopted here.

Stop here with the original run preserved. No production code, schema, prompt,
model settings or review history changed. [Verification notes](verification-notes.json)
retain an early check launched before finalization and corrected comparison
assumptions about passage labels and trailing whitespace. No provider request was
repeated to obtain the final result.
