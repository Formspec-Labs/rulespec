# Context selection comparison — before scoring

Decision: Should the next context improvement connect existing relationship/reference records, supply the complete enclosing section, or first repair missing structure/dependencies?

Hypotheses: (H1) Relevant remote evidence is already linked but not delivered; one-hop expansion recovers it. (H2) Missing links/structure are the bottleneck; only the complete section recovers it. (H3) Extra context includes unrelated duties, so availability gains have a measurable reading cost and do not establish governing scope. This test measures supplied evidence, not interpretation or hidden reasoning.

Arms:
- A: current `with_context(2400)` plus the focus and its verified existing evidence, matching the prior context pilot.
- B: A plus verified evidence from existing incoming/outgoing `target_ids` relationships and resolved `reference_links` sections, one hop only. Use current records without correcting missing links. Preserve and report unresolved references/targets. No new reference parser or model pass. This tests a bundle of existing dependencies, not each dependency type separately.
- C: A plus the complete smallest declared section enclosing the focus. If the source has only one declared section, label the fallback as the whole supplied document. No hidden subdivision or answer-directed section selection.

Cases: three unchanged failing historical focuses (refrigerant default prohibition, child-restraint dated labeling, child securing/Part135 ambiguity); two new source-selected focuses in pinned 2025 government sections 29 CFR 1910.39 and 1910.165, contingent on retrieval; the previous constructed misleading-parent case; one new constructed local-reference/unavailable-external-reference control. Seven cases maximum. New natural focuses are manual source selections, not new model extractions; their empty relationships must be explicit. Previously unseen source does not make agent-authored labels independent gold. Read source and freeze exact required/irrelevant spans before scoring. Do not open existing sealed holdout labels.

Held constant: pinned raw text, focus positions, existing claims and dependencies, same exact source-span checks. No model calls; one deterministic scoring run plus replay; no tuning after scoring. Whole ranges are retained and duplicate source positions counted once. No arbitrary context cap on B/C: expansion size is an outcome. These arms do not isolate size from selection strategy. Stop after the seven cases and report any source acquisition failure without substituting an easier case.

Measures: required source spans delivered completely; all-required cases; context unique characters and overlap removed; predefined irrelevant duty spans included; preserved unresolved references; full-document fallback. Required spans include full conditions/alternatives, not just cue words. Local dependency delivery and semantic applicability are separate.

Decision rule: investigate B as a sufficient solution only if it recovers every known required remote clause, has no lost required span compared with A, preserves unresolved references, and uses at most 75% of C's aggregate unique characters. If C alone recovers missing clauses, prioritize a section-context comprehension comparison before building a general resolver. If both miss required context or the structure lies outside the supplied source, record that limit. Merely supplying an unrelated duty is not a false legal inheritance; this zero-model test cannot measure whether a consumer incorrectly applies it. No production adoption, commit, or model calls are authorized by passing this pilot.

Preserve the frozen plan and labels if raw review exposes an assessment error. Record any revised interpretation separately; do not silently change the gate.
