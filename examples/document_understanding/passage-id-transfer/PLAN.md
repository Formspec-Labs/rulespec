# Two new documents after comparison passage-ID integration

Decision: Does the integrated workflow transfer beyond the repeatedly tuned notice
case, and which remaining condition-preservation problem deserves work next?

Hypothesis: extraction → independent inventory → passage-ID comparison → discovery
will retain reviewable meanings and grounded evidence on both new sources. Missing
qualifications, wrong exception targets, omitted alternatives, semantic false
alarms or unresolved evidence weaken practical readiness even when schemas pass.

Arms: one integrated workflow, commit 83caace, on two new documents. There is no
fresh quote-based control; this is a transfer check, not a causal improvement test.
The historical notice comparison informs adoption but is not an unseen benchmark.

Cases, frozen before generation:

1. Complete 8 FAM 801.2-1 Introduction, from the official State Department HTML.
   Check full adjudication before suspension; agency/center prohibition on unilateral
   IRL changes, approval route and extenuating case-by-case management exception;
   posts' authority to adapt cleared language for local needs; IRLs not being
   adjudicative guidance; IN changes governed by their own approval/exception rule;
   INs not requiring a response or personalization; permission to consult resources.
   Preserve distinct agency/center and post actors. Treat examples as examples.
2. Complete Ohio Administrative Code 3745-52-15, from official state HTML. Check
   conditional permission and 55-gallon / one-quart / one-kg thresholds; all exemption
   conditions; immediate damaged/leaking-container transfer alternatives; compatibility
   and remote-rule exceptions; container closure with adding/removing/consolidating
   and necessary-venting exceptions; equipment-operation OR danger-prevention branches;
   both required label components; excess-accumulation trigger, three consecutive
   calendar days, compliance OR removal with all three destinations; interim duties
   and date marking; distinct small/large-generator preparedness requirements.

Selection: neither distinctive source appears in saved document/source experiment
inputs searched in this repository before retrieval. These are new to this local
evaluation, not guaranteed absent from model training or every historic context.
The passport case is one complete section, not the entire 801.2 subchapter. The
Ohio case is a complete rule with nested lists, unlike the passport prose/manual.
A first GovInfo download returned an HTML error page and was excluded before any
model calls; retain it as retrieval provenance, not source evidence.

Preparation: preserve raw HTML; decode paragraph text, collapse HTML layout
whitespace within each paragraph, retain order/list markers, separate paragraphs
with two newlines. Extract the declared complete subsection/rule deterministically.
Offsets refer to this pinned prepared text, not byte offsets into HTML. Preserve
source URLs, raw/prepared hashes and extraction method. No model-based preprocessing.

Held constant: gemini-3.8-flash, temperature 0, low extraction thinking, medium
inventory/comparison thinking, no numeric thinking budget, provider output allowance,
24,000-character windows. Each source must fit one window. One run per source,
three calls each: SIX calls maximum, existing five-minute per-request timeout,
no automatic retries, repairs or prompt/schema tuning. No new labels fed to models.
Use the existing full-workflow harness. Independent document runs may overlap.

Assessment: read original source and all raw extracted meanings, inventory meanings,
refusals and comparison judgments. Record grounded evidence, meaning/conditions,
coverage observations and cost separately. Expected checks are revisable source
judgments, not legal determinations or gold labels. Report disagreements explicitly.
No second judging model is planned, so arm masking is not relevant here. One run
per case cannot establish within-case variability or a general accuracy rate.

Decision rule: if both finish and evidence replay succeeds, the integration works
on these two cases mechanically. Practical usefulness additionally requires the
listed alternatives, exceptions and governing conditions to survive in explicit
meaning, with material omissions and false positives documented. Any failures stay
in accounting. Use the highest-impact concrete defect to define the next focused
condition-preservation task. Do not repair these cases during the transfer check or
claim schema validity means exhaustive rule discovery. Stop at the six-call bound.
