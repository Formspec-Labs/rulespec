# Next extraction iteration: preserve meaning and expose gaps

Status: implemented and assessed locally, 2026-09-07. The
[execution results](../../examples/document_understanding/quality-iteration/README.md)
record the delivered data workflow, all 30 case decisions, temperature comparison,
remaining semantic failures and reproducibility checks. The
[capability assessment](../reviews/2026-09-07-extraction-capability-assessment.md)
preserves the preimplementation mapping that guided the work. The sequence below
is the approved plan; it does not imply that every extraction-quality case passes.

All five implementation steps have demonstrations. Conditions, modal force and
document alternatives survive in the final matched examples. The checker exposes
deliberately omitted alternatives and incorrect exception targets. Automatic
extraction still omits qualified statements and explicit relationships; a saved
confidential-name correction demonstrates the correct representation and history.
The reference assessment passes 17 of 29 automatic cases at temperature 0 and 16
at 0.2, with one separate correction-process case passing. These overlapping
development cases do not establish general accuracy. Default temperature remains 0.

Verification: 223 tests and 101 subtests pass; seven new extraction runs and eight
audits replay without provider calls; the built wheel compiles and validates with
packaged Core data. All five historical v1 runs reprocess and replay, and all
1,406 protected original files remain unchanged. Work is local and uncommitted.

**Keep the milestone and the existing foundation.** Improve how the extractor
retains complete meanings and identifies missing content. The result should be
useful source-linked units for search, tagging and conceptual relationships,
and a better starting point for reviewed workflows and forms. The same flexible
approach supports both uses: discovery can use imperfect drafts and accumulate
user feedback; a tool-building effort can apply closer human review.

Start with the existing contiguous name-change section,
[8 FAM 403.1-4(a)–(d)](../../examples/document_understanding/manual-slice/source/section.json).
Its saved runs, source assessments and correction examples provide a direct
before/after comparison. The photograph cases broaden the checks. These are now
development material; use new passages for a fresh independent assessment.

## What we will reuse, extend and build

| Status today | Decision |
| --- | --- |
| **Already implemented:** exact evidence, assertion identity, provenance, raw captures, replay, immutable corrections, evaluation judgments and Core validation | Reuse these paths. Extend their explicit field lists and checks when meaning fields change. |
| **Already implemented:** condition/exception target resolution and `EvidenceBinding` with `qualifies` | Preserve them and improve what the extractor supplies, including the evidence for the governing condition and target. |
| **Available but not connected:** `definesScope`, `providesContext`, `ApplicabilityScope` and `hasApplicability` | Connect the evidence functions; use a scope record where the source information fits it. Extend the application validator before emitting that record type. |
| **Partly implemented:** modal meaning, alternatives, logic text and coverage accounting | Extend the small application profile, deterministic compiler and existing local evaluator. Adapt release-accounting principles without importing release-specific dependencies. |
| **Genuinely missing:** governing-context selection and automated source-first omission discovery | Build these bounded capabilities around the existing extraction and evaluation paths. |

The assessment contains the detailed
[meaning → application field → Core → validation → uncertainty mapping](../reviews/2026-09-07-extraction-capability-assessment.md#meaning--application-fields--core--checks--uncertainty),
including conditions, exceptions, alternatives, thresholds and component evidence.
Core supplies ways to represent this information; it does not determine which
condition governs which rule.

## Implementation sequence

### 1. Repair the three reproduced foundation defects

Turn [W1/W2/I1](../reviews/2026-09-07-document-understanding-adversarial/FINDINGS.md#reproduced-application-defects)
into regression tests and fix their narrow paths:

- Overflow in a refused row must leave a terminal, recoverable run with the raw
  response, valid neighboring candidate and serializable refusal preserved.
- A fully judged total omission must report a completed review and failed
  extraction quality as separate facts.
- Compilation must preserve a valid explicit child-section ID regardless of
  section-array order, with a defined fallback when no section is supplied.

**Reuse:** existing capture, finalization, evaluation and source validation.
**Extend:** their error and boundary checks. No model calls are needed.

### 2. Pin the small profile and demonstrate its Core conversion

Extend `CANDIDATE_SCHEMA` and compiler fixtures before changing live extraction.
Represent must, should, may, must not, not required and descriptive possibility
unambiguously. Preserve uncertainty or absence of modal meaning for statements
that do not fit; do not force definitions or context into an obligation type.
Use compatible kinds for recommendations, standalone exemptions and descriptive
statements. Keep actor/action/object optional in meaning when the source does
not establish them.

The proposed additions are `modality` with supporting text, scope text and
quotes, context quotes, and alternative quotes with the source's choice wording.
Keep thresholds and complex AND/OR, timing and negation in supported text unless
a specific normalization is justified by a fixture. The model returns small
fields and exact quotations; the compiler creates Core records and identifiers.

**Reuse:** `ValueAssertion`, `RelationshipAssertion`, `SourceFragment`,
`EvidenceBinding` and existing revision artifacts. Keep `qualifies` for linked
modifiers. **Connect:** `definesScope` for governing conditions and
`providesContext` for explanatory text. Evidence bindings target assertions,
not scope objects directly.

Use `ApplicabilityScope` where a supported applicability description fits its
fields. Do not invent jurisdiction or dates to fill it. Its condition text is
audited rather than semantically validated. First prove a scope-only correction
preserves the earlier scope and records the changed proposition/revision; the
current assertion hash does not include `hasApplicability` metadata. Include
the evidence function in new binding identities so different roles cannot
collapse into one record.

**Extend:** `core.py` field handling, graph generation and validator type list;
`review_store.py` reconstruction; and `evaluation.py` judgments and comparisons.
Carry every new field through revision identity, export, corrections and stale
judgment checks. Version the profile, parser, examples and recorded processing.
Preserve original v1 artifacts and their frozen interpretation. Reprocessing
old responses must not invent new semantic information that they never supplied.

### 3. Extract focused passages with their governing context

**Extend:** the pinned section/source-map model in `documents.py` with paragraph
and list-item relationships. Preserve exact text, offsets and source IDs.
**Build:** selection of relevant parent lead-ins and neighboring antecedents;
wire it into `plan_windows` and request construction in `extraction.py`.

Distinguish the focused passage from supplied context. Keep paragraph/list
groups coherent and preserve multiple evidence spans when conditions and duties
occur in different sentences. A processing window must not define rule identity
or make one accepted claim stand for every meaning in its paragraph.

Update the prompt and independent examples to identify context's role explicitly.
Simply sending more text is insufficient: the saved runs already lose conditions
that were present in the same request. Do not apply a nearby condition to all
rules or flatten a nested alternatives list into unrelated choices.

### 4. Expose omissions and challenge extracted meaning

**Reuse:** the existing evaluator's source-bound units, claim judgments, digests
and missing/partial/unknown states. **Extend:** local passage accounting using
the release validators' principles: reconcile source IDs, dispositions, reasons,
failures and counts against actual records. Keep this local to Rulespec.

**Build:** a bounded source-first checker that inventories substantive statements,
options and qualifications before seeing the draft, then proposes gaps. A
claim-first check challenges the draft's components, modal meaning, conditions
and exception targets. Both produce evidence-backed observations through the
existing evaluation path. Record model attribution; neither is evaluation gold
or an implicit human decision.

Keep processing completeness, assessed semantic coverage and review completeness
separate. A processed passage may still contain an omitted alternative. A
clean schema report cannot establish that nothing was missed. `ClosureClaim`
remains disabled; local diagnostics are sufficient for these observations.

Start with visible findings. Any automatic repair uses bounded attempts and
retains the original draft, proposed change and outcome. Explicit corrections
or later user feedback reuse `ReviewStore`; invalidate affected judgments and
recheck relationships after edit/split/merge/add actions. Browser work is limited
to showing the source context, component evidence and open issues needed here.

### 5. Demonstrate improvement on the saved adversarial cases

Exercise all 30 saved semantic cases:
[photographs R01–R15](../reviews/2026-09-07-document-understanding-adversarial/photos-coverage-claim-audit.json)
and [names NREG-01–NREG-15](../reviews/2026-09-07-document-understanding-adversarial/names-adversarial-regressions.json).
Retain their positive cases and negative controls. Show raw output, compiled
meaning, evidence and assessment together for the following outcomes:

| Outcome | Required demonstration |
| --- | --- |
| Conditions survive splitting | Photograph DS-11 re-execution retains the missing-photo/acceptance-facility case. Name-change duties and emergency permission retain their distinct timing, DS-11 and ID branches. Check neighboring cases where the condition is false, and context across a window boundary. |
| Exceptions retain meaning and targets | Preserve the confidential-name exception and its both-names baseline; distinguish descriptive possibility from permission. Retain the recent-ID exemption without linking it to the older-change duty. Check existing positive local links and rejected/unresolved cases. |
| Recommendations remain recommendations | Preserve `should`, weaker guidance, “generally,” and “might.” Do not strengthen these into requirements or lose no-obligation statements. |
| Omitted alternatives become visible | Preserve the name-document list and its nested grouping/one-or-more wording. Deliberately remove an option from a fixture and show the omission checker flags it; show whether fresh extraction actually retains it. |
| Components and thresholds retain meaning | Keep DS-11 as application context rather than the object of a name change; preserve the photo likeness/damage threshold, timing and conjunctions. |
| Corrections preserve history and neighboring meaning | Reproduce the three saved corrections in a new result, inspect the remaining gaps, and verify prior revisions, original attribution and current targets survive. |

After freezing the changed outputs, assess previously unused source passages.
Keep their evaluation expectations outside extraction and repair requests.
Do not describe an improvement created by explicit correction as an improvement
in automatic extraction.

## Acceptance and delivery

The three defect regressions and compiler/history/evidence checks must pass.
The named demonstrations must establish that the new fields survive extraction,
compilation and corrections, with semantic results assessed against the source.
Every saved case gets an explicit result and rationale; an unrun, ambiguous or
still-failing case remains visible. A targeted behavior still failing its source
check is unfinished work, not a pass because the graph validates.

Compare the saved baseline and fresh runs using omissions, overbroad or
unsupported claims, condition/exception errors, modal errors and uncertainties.
Report automatic extraction separately from checker findings and corrections;
finding an omission is useful progress but does not mean the omission was fixed.
The milestone should show measured improvement on these cases without claiming
general accuracy from this small, overlapping sample.

Human review and perfect section completeness are not prerequisites for every
discovery use. The same evidence and issue history support later feedback or
closer review before tool construction. Human time savings remain unmeasured.

Deliver the revised profile, connected compiler, context-aware extraction,
bounded gap checks and a runnable before/after example. Preserve all original
captures, sealed review material and correction history. Rulespec owns the
workflow; RefSpec supplies optional terms/tags. Broader formats, embedding or
workflow/form consumers, and arbitrary executable policy logic are later work.
