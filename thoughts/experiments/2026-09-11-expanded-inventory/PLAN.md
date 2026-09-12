# Does broader source inventory improve qualification assessment?

Decision: whether expanded-context inventory merits a broader evaluation before
connecting it to the optional audit. No production adoption or automatic edits.

Observed failure: the saved 14 CFR 91.213 extraction captured the opening
prohibition and paragraph (e)'s special-flight-permit override separately. The
previous comparison received (e) in expanded context but approved the opening
statement. It shared a narrower source inventory across arms.

Hypotheses and predictions:

- H1, inventory coverage: inventorying the expanded source produces the missing
  qualification and preserves its effect in the affected inventory meanings;
  comparison then identifies the specific omission more reliably.
- H2, attachment failure: expanded inventory captures the qualification as a
  separate unit but does not connect its effect to the affected meaning; comparison
  still approves an incomplete statement. More inventory alone is insufficient.
- H3, comparison failure: the inventory explicitly preserves the qualification
  for the affected meaning, but comparison still misses the statement's defect.
- H4, false inheritance: expanded inventory or comparison attaches a limited
  exception to unrelated duties. Any gain comes with a semantic regression.

This small test cannot identify hidden model reasoning or separate all sources
of variability. It can distinguish source availability, inventory retention and
downstream use through their observable outputs.

Arms: A inventories the existing first 3,000-character focus window with ordinary
context. B inventories all passages in the existing context export for that same
window. Reuse the existing inventory prompt and CUE-generated schema. Both
comparisons receive identical expanded source material, the complete fixed
rulebook and the existing comparison prompt/schema; only their inventories vary.
Use the complete fixed book in both arms so B's extra units have real counterparts
and are not declared missing merely because their claims were outside the former
focus. This common comparison setup differs from the previous window-only CLI
comparison: a success in both arms is not evidence for the inventory intervention.

Cases (selected before provider calls):

1. **Saved development failure:** exact previous annual 14 CFR 91.213 source and
   untouched provider extraction. Target: paragraph (e)'s effect on C0000. Retain
   paragraph (d) and (a)'s conditions; do not generalize the special-flight-permit
   permission beyond its source. Historical captures remain unchanged.
2. **New provider case:** complete 14 CFR 61.56 from locally captured eCFR title 14.
   Preserve (a)'s (b)/(f) exceptions and (c)'s (d)/(e)/(g) exceptions; the limited
   ground-training exemption in (f) must not become a complete flight-review
   exemption. Simulator approval for landings under (i)(2) must not remove the
   separate approved-course and rated-aircraft requirements. These are natural
   counterexamples to attaching every qualification to every nearby rule.
3. **New provider case:** complete 29 CFR 1910.132 from locally captured eCFR
   title 29. Paragraph (g) restricts (d) and (f), not all duties in the section.
   Payment exceptions must not remove adequacy/maintenance, safe-design or damaged
   equipment duties. Paragraph (h)(5) distinguishes lost/intentionally damaged PPE
   from ordinary replacement. Preserve off-job-site permission in (h)(2).

No prior occurrences of 61.56 or 1910.132 were found in experiment/example notes,
harnesses or case manifests in the targeted preflight search. These are selected
new sections, not an independent benchmark. The native section XML is a retained
subtree of each captured title; source-title hashes and publisher capture metadata
will be saved. An XML serialization/subtree is not the original title byte stream.
No external target documents or current-law conclusions are part of this test.

Generate one normal, untouched low-thinking extraction for each new section, then
manually inspect its raw draft and freeze claim-level labels before any inventory
or comparison call. Do not introduce constructed defects if the draft is faithful.
Keep any rejected claims and preparation failures in the accounting. Source labels
and later reviewer judgments remain revisable and stay outside model requests.

Common experimental decoding: native XML includes inserted formatting whitespace.
Use existing Core `evidence_parts` to validate complete selected source spans in
both arms, retaining the original pieces beside the assessment. The current audit
helper's blanket rejection of inserted whitespace is a known separate mismatch;
record how many spans would encounter it. Do not modify production or weaken the
refusal of inserted substantive content. All single-source passage IDs resolve
through the existing resolver. No new meaning schema or fuzzy matcher.

Held constant: Gemini `gemini-3.8-flash`, temperature 0, one candidate, 32,768 output
allowance, low extraction and medium inventory/comparison thinking, no thinking
budget. One observation per arm per case, alternating AB/BA request order.
At most **14 calls**: 2 fresh extractions, 6 inventories, 6 comparisons. No retries,
prompt tuning, replacement cases or repairs after observing results. Stop starting
calls after 30 minutes of provider work or 300,000 recorded tokens. A running call
may finish beyond the elapsed-time/token boundary; retain it. A failed extraction
removes its downstream case; a failed inventory removes that arm's comparison.

Capture: exact source, source-map/reader and application versions, frozen requests,
schemas, raw provider responses, failure/refusal details and usage. Log actual
settings from the SDK request. Reuse existing capture, parsing, Core compilation
and evaluation helpers. Freeze downstream requests after dependencies are available.
Randomize anonymous output review order and hide arm labels for semantic assessment;
save the assessment before opening the arm key. Inventory volume may make masking
imperfect; do not claim otherwise.

Measures, assessed separately: exact source grounding and usable schema; whether
the target qualification is retained in inventory; whether its affected meaning
contains the qualification; specific supported comparison findings; missed defects;
false inheritance and other false alarms on every current claim; token/latency cost.
An error verdict without identifying the specific defect is not a hit. Extra
quotations, more units and reciprocal links alone are not semantic gains.

Decision rule: recommend broader evaluation only if B improves a prelabelled
meaning/qualification defect on at least one new source, detects the equipment
override omission, and introduces no confirmed false qualification or critical
regression relative to A, with usable grounded captures. If B retains more source
meaning but comparison does not use it, report bounded inventory improvement and
the overall task as not solved. If new drafts have no relevant defects, report
the downstream benefit as unresolved and still assess fidelity/false alarms.
No measured gain, failed gates and failures stay visible; narrow gains do not pass
the broader gate. One observation per case cannot establish a general success rate
or stable cost ratio. Stop and consolidate when the bound is reached.

Pre-audit implementation note: the first freeze attempt stopped because it compared
request-local passage alias names. Context export renumbers after whitespace-only
entries; the normal catalog can leave gaps in those numbers. The harness now
checks identical ordered source spans/text, while each decoder resolves the IDs
from its actual request. No inventory/comparison calls occurred before this fix;
the two original extraction captures and pre-extraction harness hash remain saved.
