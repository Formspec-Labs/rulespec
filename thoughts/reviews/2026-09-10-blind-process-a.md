# Independent end-to-end process review

My judgment: the baseline extraction is already useful for finding and reading relevant material. The additional relationship process offers some useful links, but its cost, duplication, and unresolved interpretation are disproportionate to what these two examples demonstrate. I would use this output as a source-backed discovery aid and a starting point for human workflow design. I would not treat the resulting graph as a complete account of applicability.

This is an independent artifact review, not an assessment of live model quality across a corpus. Initial observations were saved in `2026-09-10-blind-process-a-initial.md` before reading process code or any experiment report. I did not read previous assessment/conclusion files. I inspected both supplied source texts, baseline raw requests/responses and parsed records, all four raw proposal/challenge responses, the rail initial audit's raw outputs, review history, final discovery, and core graph. No API calls, production edits, or fresh extraction runs. Code observations refer to the experiment's frozen source, not concurrently changing production code.

Paths below are relative to `thoughts/experiments/2026-09-10-parallel-compression/`, except where stated.

The observed path is source text → passage catalog → structured model response → exact-passage resolution and candidate validation → review snapshot/core graph → relationship proposal → structural preview → second-model challenge → supported edits → discovery export. `experiment.py:112–158` performs the last stages; frozen `application/refinement.py:_decode_checks` validates verdict shape and evidence references, not the truth of the reasoning. The rail packet reuses an earlier two-call inventory/comparison audit; the fresh phone packet has no audit judgments. This experiment is therefore a controlled relationship-pass slice of the broader process, not a fresh full pipeline run for both documents. Frozen `application/refinement.py:378–500` shows the broader optional path adds initial audit, recovery proposals/challenges, relationship proposals/challenges, and final audit.

## What works

The raw statements are substantially better than disconnected keyword extraction. Rail preserves the 15–50 foot limits; stop/listen/look/ascertain order; all vehicle categories; the green signal **and local-law permission**; signs marking abandonment; and State/local consent for Exempt signs. Phone preserves both responsible actors and the driving definition, including traffic delays and the moved-aside **and safely halted** exclusion. I did not find an obviously omitted substantive paragraph in either selected section. That is a finding about these short sources, not completeness evidence for larger documents.

Evidence: `inputs/*/book.json`, `fresh-extraction/attempt-0000.response.json`, and `cells/cell-01/workspace/attempt-0000.response.json`. The summaries are generally readable and faithful. Keeping the rail placard list together is sensible; creating one rule per classification would make it harder to read. Keeping the sign-erection duty separate from the stop exemption is also right.

The system retains exact source locations, raw responses, and model provenance. Final discovery retains every passage and explicitly says `semantic_completeness: not_established`. All final claims remain pending human review. Core graph assertions use `statisticalInference`, `reviewQueueOnly`, and `draft`. These are useful, honest boundaries. They prevent a successful parser or automated edit from becoming human approval.

## Where the meaning still breaks down

1. **A complete section is not a complete standalone statement.** Phone C0000 says simply “No driver shall use ... while driving a CMV”; its emergency exception exists elsewhere. Cell-00 ends with no structured connection at all. Rail's main statement references (a)(1)–(6) and (b), but those references remain unresolved even though the relevant paragraphs are present locally. The vehicle categories are ordinary isolated statements. A reader seeing the complete section can recover the meaning; a search result or workflow consumer seeing one statement cannot reliably do so. Evidence: `inputs/rail-crossings/book.json` accepted records 0–8; `cells/cell-00/discovery.json` statements. This matters more than adding another classification field.

2. **The rail exception target is too coarse for workflow use.** Both rail cells connect all five stop exemptions to C0000, which combines stopping, listening, looking, and ascertaining no train approaches. Paragraph (b) says a **stop** need not be made. The output names no affected component. A consumer treating an exception edge as cancellation of its entire target could cancel more than the wording expressly excuses. I am not deciding the legal reach of paragraph (b); I am identifying a missing interpretation boundary in the representation. Evidence: `cells/cell-01/proposal/attempt-0000.response.json`, its challenge response, and final `after.json` target IDs. The challenge repeatedly calls the combined target a “stopping duty,” which conceals this distinction.

3. **The phone disagreement is substantive, not just malformed data.** Cell-00 proposes an emergency exception linked to driver and carrier prohibitions. Its challenge rejects the whole proposal because the text explicitly permits driver use and does not explicitly permit carriers to allow/require it. Cell-03 links only the driver and succeeds. A conservative target is defensible; the challenge's categorical “does not qualify” is stronger than the narrower “not expressly established here.” The experiment shows model disagreement about interpretation, not proof that one interpretation is correct. Worse, rejecting the combined proposal discards the supported driver link as well. Evidence: the two cells' proposal/challenge responses and `result.json` outcomes.

4. **Final export hides that rejected interpretation work.** Cell-00 has no review history, no current issues, four pending claims, and no exception target. Its rejected proposal and rationale survive in `result.json` and captures, but do not surface as a final discovery issue. A consumer sees a clean-looking draft without knowing that a relationship was actively disputed. Generic “pending” is less useful than an explicit unresolved relationship. Evidence: `cells/cell-00/{result,after,discovery}.json`.

5. **The audit gives more precision than it establishes.** The rail initial comparison marks `links: correct` for C0000 while its local references remain unresolved. It marks all 14 dimensions “correct,” including absent action/object/concepts. This may mean “no detected semantic defect,” but reads like verified structure. The inventory itself calls the vehicle categories conditions while the baseline calls them statements. Those readings can coexist, yet the all-green dimensions hide the difference between retained prose and connected applicability. Evidence: `thoughts/experiments/2026-09-10-exemption-end-to-end/cases/rail-crossings/refinement/initial-audit/comparison/attempt-0000.response.json` and sibling `inventory/attempt-0000.response.json`.

## Process weight versus product value

The captured baseline prompt explicitly excludes topic concepts, normalized values, action/object fields, and relationship records. Empty fields therefore are not parser failures. They do mean these runs demonstrate readable extraction and a small relationship graph, not automatic tagging or a rich domain knowledge graph.

The optional process duplicates work. The rail audit independently writes 15 meanings, compares 15 claims across 14 dimensions, then the relationship proposal rewrites five complete records merely to add five links. The phone relationship prompt explicitly requires a companion exception while preserving the permission; cell-03 consequently gives the user two near-identical emergency statements. This duplication is induced by the instructions, not evidence that the source contains two separate actions.

Evidence selection also grows unnecessarily: rail raw extraction uses `F025:F030` for the fifth exemption, thereby including all preceding exceptions, then repeats paragraph (a) as context. Discovery attaches statements to overlapping passages. As a result, broad evidence increases incidental source-to-statement links. I would prefer separate lead-in and item evidence, with roles preserved, over treating sibling paragraphs as main support.

Measured usage from provider captures:

| Path | Baseline total tokens | Proposal + challenge tokens | Result |
|---|---:|---:|---|
| Phone cell-00 | 2,810 | 27,941 | No applied change |
| Phone cell-03 | same shared baseline | 13,184 | One companion and link |
| Rail cell-01 | 6,563 | 43,912 | Five exemption links |
| Rail cell-02 | same reused baseline | 62,473 | Same five exemption links |

These totals exclude the rail audit; its inventory and comparison add 18,577 tokens. Caching differs, so these are not dollar-cost comparisons. The files alone do not prove acceptable latency or spending at scale. The phone cell-00 proposal alone reports 18,255 thinking tokens for 614 visible output tokens. For these small documents, the additional work has not demonstrated a matching increase in user value.

The final phone cell-03 source is 867 characters, discovery is 26,252 bytes, and the review snapshot is 275,597 bytes. Rail cell-01 is 2,907 source characters, 120,523 discovery bytes, and 750,758 snapshot bytes. Provenance accounts for useful storage; repeated full state should not become routine model input or reviewer reading material.

## Practical direction

For discovery, retain the source passages, readable statements, explicit definitions, provenance, and uncertainty. Evaluate actual search/tagging utility with user tasks before making all audit/refinement passes mandatory. The current source-backed discovery output is promising enough to use experimentally; tagging accuracy and retrieval benefit are untested here.

For human-reviewed workflow construction, present the source beside a grouped rule, its applicability categories, conditions, exceptions, and unresolved interpretations. Make relationship review specific: which action changes, under what condition, and what remains applicable. Keep model rejection/unknown outcomes visible. Use one displayed emergency statement with its permission and exception relationship, rather than two repeated statements.

My untested simplification hypothesis is that a strong baseline plus targeted review of unclear relationships would produce most of the value of this pipeline at substantially lower cost. Test that against real reviewer correction time and errors, not just schema validity, number of edges, or model agreement.
