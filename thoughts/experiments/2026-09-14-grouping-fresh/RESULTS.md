# Grouping saves input tokens; extraction granularity remains inconsistent

**Keep production unchanged.** Explicit section grouping achieved a real input-
token saving on every case and used 17.3% fewer total tokens across all four pairs.
It also changed how information was split into individually referenceable records.
The cost criterion passed; the predeclared granularity criterion did not. This
round therefore stops without a full-document qualification run or adoption.

The findings are more favorable to grouping's semantic fidelity than the original
pilot alone suggested. Most substantive content survives. The health-safeguards
pair shows a bounded comparable-output gain, and the CSBG repeat improves the
previously ambiguous report reference. The issue is not a demonstrated general
loss of meaning whenever sections share a request.

## Comparison and observed results

Three new pairs of complete sections from the 2025 annual CFR and the known CSBG
9913/9914 pair were tested. Each case used two fresh separate requests versus one
fresh grouped request. Grouping reused the pilot's task directive without tuning,
the current CUE schema, the same source coverage, and current native decoding.
Every group contained at most 6,000 focus characters. Arm order alternated by case.

| Source pair | Separate tokens | Grouped tokens | Total-token change | Separate / grouped records | Meaning and user value |
|---|---:|---:|---:|---:|---|
| Drug production records, 211.188/211.192 | 5,965 | 7,528 | **26.2% more** | 7 / 20 | Same list contents; grouping makes the thirteen contents individually referenceable and improves investigation naming. |
| Aviation instructions/signals, 91.123/91.125 | 8,610 | 4,408 | **48.8% fewer** | 21 / 8 | Both preserve every signal mapping; grouping places the entire table in one long statement. |
| Health-information safeguards, 164.310/164.312 | 11,657 | 10,215 | **12.4% fewer** | 24 / 24 | Comparable duties, conditions and required/addressable qualifications survive. |
| CSBG training/monitoring repeat | 10,571 | 8,281 | **21.7% fewer** | 17 / 17 | Grouping improves several local references, including the evaluation-report trigger; some shared dependencies remain. |
| **All four** | **36,803** | **30,432** | **17.3% fewer** | **69 / 69** | Equal aggregate counts conceal different granularity by case. |

For only the three fresh cases, total tokens fall from 26,232 to 22,151: **15.6%**.
That meets the proposed 15% aggregate cost threshold. However, excluding aviation
as a post-hoc sensitivity check, the other two fresh cases use 0.7% more total
tokens. This is not an alternative selection of winners; it shows how much the
headline saving depends on the table's coarser output.

Across all four pairs, input tokens fall from 19,764 to 13,103 (**33.7%**), while
answer tokens increase slightly from 17,039 to 17,329. Repeated input setup is a
real source of overhead. The effect on answer tokens depends on segmentation.
Summed provider-call duration falls from 47.3 to 41.5 seconds, an observation of
about 12% lower duration in this run, not a service-level forecast. Request count
halves from eight to four; latency does not halve.

## The material differences

### Drug records become easier to use, at greater cost

The separate 211.188 output places all thirteen record contents in one long
requirement. The grouped output supplies one record for each content, preserving
the batch-record and significant-step framing. For example, the dates requirement
now identifies what those dates document instead of being merely one field buried
in a composite statement. A form-building consumer can address each requirement.
The separate version did not omit these words; the gain is granularity.

Grouping also changes the investigation extension from "The investigation shall
extend ..." to "The investigation into any unexplained discrepancy or failure of
a batch or component shall extend ...". This identifies the investigation more
clearly, but still omits "to meet any of its specifications" from that standalone
description. The supporting quote and the main investigation duty retain it.
This is an improvement with a remaining precision limit, not perfect independence.

### Aviation's cheaper result changes the addressable unit

Both outputs preserve all twelve signal/aircraft-setting mappings, including
surface versus airborne meanings, the follow-on steady-green qualification and
the airborne "not applicable" cell. Grouping does not lose or scramble the table.

The separate output gives each mapping a record. Grouping gives the entire table
one statement of roughly a paragraph's length. The frozen criterion allowed a
complete record per signal or per setting; a single record for all signals does
not meet that referenceability criterion. Someone looking for one signal gets a
much larger unit. The separate version also contains a low-value table-pointer
record, and grouping omits the nonoperative OMB approval statement.

This is a granularity tradeoff, not evidence of missing signal meanings. The seven
operative clearance/instruction meanings retain their separate exceptions, actors,
report-request condition, notification timing and report recipient in both arms.

### Safeguards provide the cleanest fresh bounded gain

Both versions preserve the same 24 meanings, including physical/technical access
distinctions, covered-entity/business-associate actors, required/addressable labels,
as-needed and whenever-appropriate limits, and the 164.306 qualification. Grouping
uses more consistent wording than the separate technical section's awkward "is
addressed to implement." No new substantive loss was found in the grouped reading.

External 164.306 is absent from both inputs. The experiment does not interpret its
policy or establish that every addressable specification is an unconditional
executable duty. Both store modality as must while retaining qualifications in
text/evidence. The structured-domain limitation is shared, not solved by grouping.
Some target scope also remains inherited: a logoff record names the access-control
standard without independently stating that it concerns systems maintaining
electronic protected health information. Parent quotations recover that setting
in both arms. Comparable output here does not mean every statement is self-sufficient.

### The original CSBG report regression does not recur

The new separate output says "On receiving the report". The new grouped output
says "On receiving the evaluation report submitted by the Secretary" and improves
other local section names. The original pilot had the opposite relative result
for report clarity. Its exact grouped request was reused byte for byte here.

This demonstrates variation across calls and a better observation, not a
deterministic fix. The full evaluation setting, some paragraph pointers and some
chapter references remain dependent on context. All seventeen records and the
four separate monitoring duties survive in both new outputs.

## Independent review reconciliation

A separate reviewer inspected all 138 decoded records and populated fields against
the complete supplied source and frozen checks. Set order was randomized per case;
the reviewer did not receive arm names, prompts or costs. Its saved report was
hashed before the assignment key was opened. Output shape can still hint at an
arm, so this is anonymized review rather than a guarantee against every cue.

After unmasking, the independent findings agree with the parent reading: grouping
improves drug-list referenceability and CSBG reference naming; separate aviation
extraction provides individually referenceable signal meanings; both safeguard
outputs preserve the declared source details. It also highlights shared inherited
scope in safeguards and the narrower drug specification-failure wording still
needed in the follow-on investigation records. No table meaning was missing.

These are independent judgments on the same outputs, not extra statistical samples
or expert-approved labels. See [review](review/REVIEW.md) and the
[unmasking receipt](review-receipt.json).

## What is worth preserving for a later decision

The strongest new hypothesis concerns **consistent meaning units**. The additional
directive speaks of independently actionable duties and list children. It may
explain why the drug list split more usefully while the descriptive signal table
remained one unit. That is an observable hypothesis, not a claim about internal
model reasoning. Window grouping and the granularity instruction remain bundled.

A different, small future test could apply only the granularity instruction to
the existing separate-section workflow. It would ask whether independently usable
units improve without introducing shared windows. A counterexample must preserve
alternatives as one complete choice and prevent unrelated duties from inheriting
neighboring conditions. No such follow-up was run or added to production here.

Do not derive a table-skipping production heuristic from this one example, or add
a planner model, mandatory audit, new schema or automatic splitting layer. Current
source/evidence facilities remain the foundation. Narrow gains are retained as
research even though this broader qualification gate was not met.

## Evidence, scope and reproducibility

- Twelve provider calls, **67,235 total reported tokens**, no retries, no truncation
  and no parser refusals. Every response finished with STOP and passed its actual
  requested schema. Thinking and cached-token counts were not separately reported.
- Actual model: `gemini-3.8-flash`; low thinking; 16,384 generation-token allowance;
  sampling controls omitted. Critical installed runtime files matched the checkout.
- All twelve native parser replays matched. All 138 candidates across both arms
  were accepted in the Core compilation rehearsal, and all eight graphs conformed.
  These checks do not establish semantic completeness or qualify a new public CLI.
- One observation per case/arm; three locally fresh section pairs and one known
  repeat. These are selected cases, not a population benchmark or entire documents.
- Official annual XML was retained with URL/hash receipts. Its SECTION bodies were
  rendered as research plain-text snapshots, preserving every non-whitespace source
  character and table cell order. The installed XML entry point rejects the annual
  wrapper; this comparison does not qualify annual XML ingestion or publisher-
  coordinate replay. CSBG reuses the original native document unchanged.
- Source preparation was identical across arms. The extra context available in a
  grouped request is part of the tested intervention. No source body was omitted
  to make grouping fit. Sources are pinned 2025 text, not claims about current law.

Sources: [drug records](https://www.govinfo.gov/content/pkg/CFR-2025-title21-vol4/xml/CFR-2025-title21-vol4-sec211-188.xml),
[record review](https://www.govinfo.gov/content/pkg/CFR-2025-title21-vol4/xml/CFR-2025-title21-vol4-sec211-192.xml),
[aviation instructions](https://www.govinfo.gov/content/pkg/CFR-2025-title14-vol2/xml/CFR-2025-title14-vol2-sec91-123.xml),
[signal table](https://www.govinfo.gov/content/pkg/CFR-2025-title14-vol2/xml/CFR-2025-title14-vol2-sec91-125.xml),
[physical safeguards](https://www.govinfo.gov/content/pkg/CFR-2025-title45-vol2/xml/CFR-2025-title45-vol2-sec164-310.xml),
[technical safeguards](https://www.govinfo.gov/content/pkg/CFR-2025-title45-vol2/xml/CFR-2025-title45-vol2-sec164-312.xml).

Local evidence: [frozen plan](PLAN.md), [source expectations](EXPECTATIONS.md),
[actual usage](accounting.json), [native replay verification](verification.json),
[Core rehearsal](core-compatibility.json), [equal source coverage](coverage-check.json),
[parent manual review](ROOT-REVIEW.md), [independent review](review/REVIEW.md),
and complete decoded readings for [drug records](drug-records-readings.md),
[aviation](aviation-readings.md), [safeguards](health-safeguards-readings.md),
and [CSBG](csbg-repeat-readings.md).

Production, schemas and defaults are unchanged. Research is saved and uncommitted.
