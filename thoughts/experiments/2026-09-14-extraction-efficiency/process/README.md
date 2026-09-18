# Source assembly saves model tokens but does not replace complete meanings

**Decision: do not adopt this alternative as the production extraction path.**
Four fresh calls show a real local token reduction and eliminate one observed
paraphrase omission, but they also lose governing context and break an alternative
into two apparent duties. The predeclared no-regression gate fails. A source-only
discovery view remains useful; it must not masquerade as a complete workflow rule.

The tested change is a deliberate bundle: ask the model to select main clauses,
governing passages and background passages, then let code render their exact text.
It removes generated statements and scope/choice prose. It is not a new passage-ID
idea: production already uses IDs for evidence. The new question is whether the
model needs to rewrite every source meaning at all.

## What happened

The same complete 9908 and 9910 section windows from the CSBG retest were supplied
to current extraction A and source assembly B. Sources include editorial notes.
All four calls ended normally, validated against their requested schemas, and
selected only resolvable source references. Each arm had one observation per
source. These are known development cases, not an independent benchmark.

| Measure, two calls per arm | Current extraction A | Source assembly B |
|---|---:|---:|
| Reported input tokens | 12,121 | 9,967 |
| Reported answer tokens | 9,959 | 4,193 |
| Reported total tokens | 22,080 | 14,160 |
| Summed request seconds | 25.3 | 10.0 |
| Raw records | 32 | 33 |
| Records accepted in Core compatibility rehearsal | 32 | 31 |
| Words in the default reading | 2,159 generated | 3,643 copied locally |

B used **35.9% fewer reported total tokens** and **57.9% fewer answer tokens**.
The provider did not separately report thinking tokens; missing values are not
assumed to be zero. Total measured consumption across the four calls was 36,240
tokens. Actual requests used `gemini-3.8-flash`, low thinking, 16,384 generation
tokens and provider-managed sampling. There were no retries or audit/checker calls.
The latency observation is one run, not a service-level promise.

Removing model-written prose did not shorten what a user or downstream AI reads.
Repeated governing quotations made the assembled default readings **68.7% longer**
than A's statements. Selected main-plus-governing evidence was smaller than A's
own expanded evidence (22,356 versus 27,098 characters), but it is still repeated
text. Store shared passages once and expand only the required reading.

## Manual source review

These are source-based judgments by the investigating agent, not expert-approved
labels. The radically different output shapes reveal the arm. We assessed raw
text, not a model-checker's score. See [READINGS.md](READINGS.md), which preserves
every statement and every selected quotation by role.

| Frozen check | A | B |
|---|---|---|
| Thirteen State-plan contents separately addressable | 13/13, item 1 split into three | 13/13, item 1 one large selection |
| Urban-origin best practices and widespread-replication methods | Loses urban origin and methods | Exact full wording retained |
| Low-income service beneficiaries, b(5) | Retained this time | Retained |
| On-request submission and optional coordinated assessments, b(11) | Retained | Retained |
| Performance alternatives and FY2001 timing, b(12) | Retained | Retained |
| State-plan assurance/content framing | Retained; timing sits mainly in supporting lead-in | Retained in selected lead-in plus clause |
| Permission to revise vs duty to submit | Both in one permission/may record | Same failure |
| Reduction-only redistribution not applied to termination | Correctly separate | Correctly separate |
| Private nonprofit CSBG scope for appointive-official clause | Nonprofit scope in statement; CSBG largely implicit | Nearer lead-in selected, full governing eligibility paragraph omitted |
| Public-board route OR other State mechanism | Both routes in one complete alternative | Split into two must records; each lacks the other route |
| FY2000 transition override | Separate correct transition; not attached to b readings | Separate exact transition; not attached, and invalid condition/must classification |

The last three checks expose why location validation is not meaning validation.
B's record 2 in 9910 selects `F006` with governing `F005`, which still points to
"the board referred to in paragraph (1)." It does **not** select `F003`, where
the private nonprofit CSBG eligibility setting is stated. Its background headings
include "Private nonprofit entities," but background is not governing evidence,
and even that heading does not supply the CSBG condition.

B's public-organization record 7 is more dangerous. Its complete assembled reading
is exactly:

> (b) Public organizations In order for a public organization to be considered to
> be an eligible entity for purposes of section 9902(1) of this title, the entity
> shall administer the community services block grant program through—
>
> (2) another mechanism specified by the State to assure decisionmaking and
> participation by low-income individuals in the development, planning,
> implementation, and evaluation of programs funded under this chapter.

Every quoted word is real, yet the result reads as a mandatory other mechanism.
The `or` and the tripartite-board route were left in the preceding record. B does
not import the private nonprofit elected-official quota into public organizations,
but it still fails the more important alternative-preservation check. A keeps both
routes together correctly.

The urban-practices result explains the appeal of assembly. A writes "document
best practices for widespread replication," losing the origin and methodology
detail. B's large item-1 selection preserves "document best practices based on
successful grassroots intervention in urban areas, to develop methodologies for
widespread replication." It succeeds by copying all the selected words, at the
cost of a much larger reading and coarser action segmentation.

Further observations, beyond the main frozen checks:

- B assigns actors in only 13/33 records, versus 29/32 for A. In particular, all
  thirteen plan-content records leave actor null even though their selected lead-in
  names the State. The actor is recoverable to a reader but absent for filtering.
- Two B records use `condition/must`, which existing Core correctly rejects as a
  kind/modality contradiction. They are the legislative hearing and FY2000
  transition. Reusing schema descriptions does not alone preserve all guidance
  from the longer current prompt. This is a bundled intervention, so neither the
  new prompt nor removal of prose is isolated as the cause.
- B preserves notes in input but selects no explanatory editorial-note records;
  neither A does here. "Source retained" remains separate from "meaning extracted."
- Both versions keep literal references to absent bodies. B explicitly selects
  passages containing unresolved references; it does not resolve them. Some such
  passages also contain locally available references, so this field is deliberately
  coarse and is not a replacement for current reference scanners.

## Existing pieces to reuse

| Capability | Status and concrete reusable code |
|---|---|
| Immutable text, native structure, source passage IDs | Already implemented: `documents.source_passages`, `uslm.SourceIndex` |
| Shared source/evidence for discovery | Already implemented: `discovery.export_discovery`, including all unextracted passages and a shared evidence table |
| Exact selection and source-bound evidence | Already implemented: `extraction.passage_catalog`, `extraction.resolve_passage`, `core.evidence_parts` |
| Actor, term, kind and modality definitions | Already implemented in CUE; pilot reused generated field definitions |
| Governing vs background evidence | Already implemented: `ApplicabilityScope`, evidence functions `definesScope`/`providesContext`; model still has to assign their meaning correctly |
| Bounded context and available linked bodies | Already implemented and optional: `context.export_context`, `references.scan_references`, explicit reference source attachment |
| History, preview, correction and export | Already implemented: `ReviewStore`, current Core compilation and discovery export |
| Source-assembled default reading | Experiment only: deterministic rendering into current fields is mechanically possible; no production mode or schema change |
| Reliable independent meaning after source splitting | Still missing: correct dependency closure, branch/alternative preservation and selected-span completeness |

The [Core compatibility rehearsal](core-compatibility.json) runs the current parser
and Core compiler after explicitly adapting B's selections into quoted `statement`
and `scope_text` values. It creates no production records, performs no semantic
repair and preserves both classification refusals. No new Core ontology is needed
for this representation. Adopting a mode would still require an authoritative CUE
application profile, provenance identifying its generated-vs-copied reading,
review/export presentation and tests for omitted governing context. The pilot
does not justify that infrastructure yet.

## Useful process direction

1. **Keep source retrieval first-class using the existing export.** Search can
   return source passages even when no statement was extracted. Do not make
   generated prose the sole discovery text or silently concatenate repeated
   whole-rule evidence into every embedding. Prior retrieval pilots already found
   indiscriminate concatenation harmful.
2. **Test demand-driven standalone rewriting only if a real consumer needs it.**
   A search index may need source units, tags and relationships; a workflow author
   needs complete readable requirements for the selected workflow. Generating that
   richer prose only for selected/edited items might avoid rewriting an entire
   chapter. This is an untested product architecture, not measured whole-document
   savings. Reuse context export and review history instead of adding automatic
   multi-pass auditing.
3. **If revisiting annotation, test meaning boundaries and dependencies first.**
   The next decision is whether a selection can keep both alternatives and all
   governing clauses, including misleading sibling controls. A better display or
   larger token allowance cannot repair a source selection that omits `or`.
   Do not restore broad automatic ancestor inheritance; prior studies and this
   pilot show why scope needs an explicit, testable relationship.

The concrete low-effort action is to use the existing shared source/evidence
export at the consumer boundary. There is no experimental production patch to
integrate from this branch. The source-assembly redesign reaches a stopping point
here: lower model cost, worse standalone rule behavior, no adoption.

## Reproduction and artifacts

- [Frozen plan](PLAN.md), [inputs](inputs.json), [schemas](schemas.json), [source/runtime pins](pins.json)
- [Raw captures](captures), [all readings](READINGS.md), [structured results](results.json)
- [Usage](usage.json), [size accounting](sizes.json), [verification receipt](verification.json)

From the repository root, `run.py summarize` rebuilds readings and results, and
`verify.py` verifies input pins, actual SDK settings, exact selections, and the
Core compatibility rehearsal without contacting the provider. `run.py capture`
refuses a second execution because the four-call ledger already exists. No
production files, original captures, review history, credentials, or git commits
were changed by this investigation.
