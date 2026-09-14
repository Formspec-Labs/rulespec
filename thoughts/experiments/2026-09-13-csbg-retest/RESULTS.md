# CSBG retest: section focus delivers a much better requirements draft

**Decision: use the existing section-focused option for this CSBG source, with
source review still required.** It independently addresses all thirteen State-plan
contents; eleven retain the tested detail and two remain partial. Normal extraction
again turns those contents into one generic paragraph reference. Section focus
also avoids a truncated broad-window response elsewhere in the chapter. It costs
56.5% more total recorded tokens in this complete-source comparison.

This is a bounded improvement, not solved extraction. No production prompt,
schema, default, audit, refinement, or review history changed. This retest is complete.

## What was run

Both arms freshly processed the same complete **42 USC Chapter 106, Community
Services Block Grant Program**: 135,797 characters, 979 source passages, 26 statutory
sections, including their historical and editorial notes. The extra section-mode
window holds the chapter preamble. Section 9908 is the application and State-plan
provision. This is the statutory application framework, not a State's completed
application or the latest legal edition. The source is the original pinned USLM
release 119-102, with its [receipt](../2026-09-12-csbg/source-receipt.json).

The [plan](PLAN.md), runtime/source hashes and windows were saved before calls.
Both arms ran the installed public CLI outside the checkout with `PYTHONPATH`
unset, using source-matching files at commit `fbcdce6`:

- **A:** normal extraction, six windows.
- **B:** the same command with `--section-windows`, 27 windows.

Both sent `gemini-3.8-flash`, low thinking, a 24,000-character focus limit and
16,384 generation tokens per request. Gemini managed sampling; temperature,
top-p/top-k and candidate-count settings were absent from actual requests.
There were 33 requests, no retries, and no model audit or repair passes. The two
whole-document processes ran concurrently. This is one observation per arm on
development material; it is not a new-document benchmark or causal comparison
with the historical provider/runtime.

## State-plan content quality

The [manual review](BLIND-REVIEW.md) was frozen before opening the randomized
arm key: packet 1 was B, packet 2 was A. Output shape makes masking imperfect.
The reviewer read the complete application section and the source and outputs
for all 24 earlier checks. Judgments remain revisable, not expert approval.

| Measure | A: normal | B: section-focused |
|---|---:|---:|
| Thirteen contents independently addressed | 0/13 | 13/13 |
| Content-specific records | 0 | 15 |
| Contents faithful at the tested detail level | 0/13 | 11/13 |
| Contents with subordinate gaps | 0 | 2 |
| Contents replaced by a generic pointer | 13 | 0 |

B has three records for item (1)'s A/B/C branches and one for each remaining
top-level item. It preserves that these are **assurances, descriptions or information
required in the State plan**, rather than turning every downstream program into
an unconditional direct duty.

The stronger output preserves the community-needs assessment and funding condition;
Secretary submission **only on request**; optional coordinated assessments; notice,
record hearing and prior-year proportional funding protection; the representation
petition trigger; where-appropriate energy coordination; maximum-extent-possible
partnerships; and the performance-system alternatives and FY2001 deadline.

Two gaps remain:

1. **9908(b)(1), B record 73:** the source calls for documenting best practices based
   on successful grassroots intervention in urban areas and developing methodologies
   for widespread replication. The output compresses this to "document best
   practices for urban replication." It changes the relationship between where
   practices originated and where they should be replicable. Emergency assistance
   does retain its immediate/urgent-needs limitation this time.
2. **9908(b)(5), B record 79:** the output retains service and workforce coordination,
   but drops the explicit **low-income individuals** who must benefit from effective
   service delivery. This is absent from both its default statement and scope field.

The previously observed missing information/referrals/case-management/followup
detail in item (3) survives in B record 77. The prior focused comparison had ten
faithful contents; this observation has eleven. That small difference is not
evidence that a particular intervening code or prompt change caused improvement.

A record 51 still says only "including the assurances and information specified
in paragraphs (1) through (13)." Its main evidence contains the entire list.
This response finished `STOP`; the list compression is **not** the separate
truncation failure described below.

## Surrounding rules and remaining review work

The 24 original, overlapping meaning checks yield 16 faithful, two partial and six
missing for A; 20 faithful and four partial for B. These are targeted check outcomes,
not a chapter accuracy percentage. See [assessment.json](assessment.json) for source
identifiers, record IDs, statuses and notes.

Both retain the 90% funding floor, >20% recapture condition, redistribution options,
public-board alternative, hearing requirements, FY2000 transition and review clocks.
B separates lead-agency duties, monitoring duties and corrective-action steps.
Its discretionary quality-improvement-plan allowance is correctly classified as
`permission/may`, unlike the earlier focused experiment's mixed `must` wording.

The stronger output still has practical defects:

- **An exception loses its governing context.** B record 103 separately permits
  appointive officials when too few elected officials are available, but omits
  that the rule concerns private nonprofit CSBG boards. Its companion composition
  record 102 retains that scope; independently retrieving 103 remains unsafe.
- **Some statements remain opaque pointers.** Both arms leave the administrative-
  expense exclusion as activities under paragraph (1)(A), without saying training
  and technical assistance. B also leaves the near-area entity in record 96 as
  "an entity described in paragraph (1)(B)" and the triggering report in record 138
  as "the report." A spells out those two antecedents more clearly.
- **Finer windows do not eliminate compression.** B's optional statewide-activity
  list also omits innovative-program purposes that A retains. This was observed
  outside the preregistered 24 checks and is reported separately.
- **Classification remains uneven.** A combines permission to revise a plan and
  the duty to submit the revision under one `permission/may` record. B separates
  them. B instead classifies the administrative accounting exclusion as
  `exemption/not_required`, although its text states that the cost shall not be
  considered administrative. The text and classification need separate review.

## Where losses occur

The [raw traces](raw-traces.json) show that A's generic plan pointer, B's two plan
detail gaps, and B's incomplete board permission already exist in the original
model responses. Their default statements are unchanged by conversion into Core.
The relevant source is in the supplied focus, so missing source preparation does
not explain these examples.

There is also a distinct conversion refusal: A combines the poverty-line definition,
revision duty and formula into one `definition/must` candidate. Core refuses that
contradictory classification. The meanings exist in the raw response and retained
rejection but not the accepted rulebook. B separates them into accepted records
12–14. Do not call A's missing accepted definition a source omission by the model.

Evidence selection remains broad. B's fifteen State-plan content records select
cumulative main-evidence ranges beginning with the parent lead-in. Their selections
total **86,421 characters across 8,648 unique source characters**, about tenfold
repetition. This includes earlier unrelated items and makes short actor/modal
quotations ambiguous. The model emits passage IDs for these ranges; the expanded
local evidence copies are not extra billed model output. Repeated wording in the
model's statements and scope fields does consume output tokens.

## Whole-document processing and consumption

| Measure | A: normal | B: section-focused |
|---|---:|---:|
| Requests | 6 | 27 |
| Responses ending `STOP` | 5 | 27 |
| Truncated responses | 1 | 0 |
| Parsed candidates | 143 | 282 |
| Accepted records | 142 | 282 |
| Rejected records | 1 | 0 |
| Parser/refusal entries | 10 | 7 |
| Core component-evidence issues | 54 across 41 records | 159 across 114 records |
| Input tokens | 70,772 | 121,039 |
| Output tokens | 58,413 | 81,119 |
| Total recorded tokens | 129,185 | 202,158 |
| Whole extraction-process time | 134.7 seconds | 214.9 seconds |
| Source passages preserved in export | 979/979 | 979/979 |

Both run statuses are `partial`; B's status reflects supporting-component refusals,
not a truncated or missing whole response. Three of B's refusals are non-verbatim
modal quotes such as `no part ... may be used`; four concern a Secretary term that
lacks a valid defining statement. These do not remove its main statements.
The component issue totals are unresolved evidence locations, not demonstrated
semantic-error counts.

A's fourth window, source offsets 71,392–95,330, ends `MAX_TOKENS` and contains
incomplete JSON. It overlaps sections 9916–9921 and yields no usable candidates.
The raw response and both incomplete-response/malformed-JSON refusals remain saved.
The CLI exits zero despite the documented partial run; callers must inspect the
run status rather than treat process exit alone as completeness.

The complete comparison consumed **331,343 recorded tokens**. B used 56.5% more
total tokens and took 59.5% longer as a process. It also delivered much more usable
output. B reported 4,600 cached input tokens within its input total. No billing
invoice or dollar estimate is inferred from these counters. Unlike the earlier
selected-section comparison, both current arms attempted identical whole-source
coverage; A's failure remains included in the accounting.

## Verification and stopping point

[Verification](verification.json) confirms exact current prompts and generated
schemas in every request; matching source/runtime hashes; gap-free whole-source
focus coverage in both plans; Core and SHACL validation; and identical replay of
both saved runs with model setup disabled. Both reference-enabled discovery exports
retain every one of the 979 source passages and their IDs. Reference recognition
is independent of the extraction arm and does not make missing statements complete.
Passages without linked statements are retained, not counted as proven omissions.

The retest supports selecting `--section-windows` for this dense, structured CSBG
source. It does not support changing the universal default, adding a mandatory
audit, or claiming workflow-ready completeness. Use the B output as the better
reviewable draft. Its remaining plan-detail and context gaps are concrete review
targets, not a reason to restart another prompt-tuning cycle here.

Saved artifacts: [B rulebook](B/rulebook.json), [B discovery export](B-discovery.json),
[application-section review](review/packet-1/9908.md), [A raw captures](A/),
[B raw captures](B/), [settings and source pins](setup.json).
