# Can the existing audit detect the remaining capture gaps?

Decision: After integrating an explicit section-window option, determine whether
the existing source inventory and semantic comparison can identify the remaining
CSBG omissions before building another capture or review mechanism. No automatic
repair or production audit/prompt/schema change is authorized by this test result.

Hypotheses:
- The independent inventory names subordinate meanings that initial extraction
  compressed, and comparison flags them as partial/missing in the focused draft.
- Alternatively, the inventory repeats the compression, or comparison credits
  broad source quotations as captured meaning. These predict different failures.
- A stricter audit may also flag faithful alternatives or qualification prose.
  Count these false positives separately from useful observations.

Arms: Historical broad and focused drafts from the completed five-call focus
experiment, both assessed by fresh calls with the SAME source inventory per
section. No new extraction. This compares diagnostic behavior on known different
draft quality, not a new audit algorithm against the old algorithm.

Cases: Complete State-plan (9908), board (9910), and corrective-action (9915)
sections in the same pinned chapter and original coordinates. Use the exact
saved focus windows, existing audit prompts/schemas/request assembly, source
resolver, parsing and judgment accounting. Custom selected-window diagnostic;
do not label it a whole-document audit or invoke whole-document accounting.

Primary checks frozen before calls:
- Broad plan: the thirteen content meanings absent behind a generic pointer
  should be flagged, despite their presence in source quotations.
- Focused plan: identify the omitted emergency immediate/urgent-needs limitation
  and urban-intervention/replication details in (b)(1), information/referrals/case
  management/followup methods in (b)(3), and low-income recipients in (b)(5).
  Count the three groups separately; name specific recovered and missed details.
- Focused private-board claims: summary lacks private/nonprofit scope, but the
  optional scope field retains it. Distinguish summary quality from whole-record
  omission. Do not report the scope as absent everywhere.
- Focused correction: identify the misleading `must, at its discretion` modality
  without pretending that the output omitted discretion or proves an unconditional
  duty. This is a representation concern with interpretive uncertainty.

Counterexamples: selected faithful plan contents (6) where-appropriate,
(9) maximum-extent-possible, (10) petition trigger/parties, (11) funding/needs
assessment/Secretary-request/optional coordination, (12) performance alternatives;
board shortage substitution, democratic selection/residence and public board OR
mechanism; correction assistance/report branches, unless-corrected, 60-/30-day
clocks and 90-day documentation trigger. Distinguish true new defects from false
alarms by manually checking the original source and whole explicit meaning.

Held constant: gemini-3.8-flash, temperature 0, medium thinking, no numeric thinking
budget, 32,768 output tokens; existing production audit prompts and schemas.
Three inventory calls followed by six comparison calls in randomized order.
One observation per draft/section. Stop after nine calls or 15 minutes, whichever
comes first. Keep all failures and STOP/truncation status; no retries or repairs.
Pre-call source/runtime/config hashes and actual SDK requests are retained.

Decision rule: If the audit catches all three focused plan gap groups, correctly
distinguishes optional scope/discretion, and introduces no substantive false
positives on the named controls, recommend it as optional diagnosis for this
failure class. Otherwise report bounded useful detections, missed details and
noise; do not promote it to a completeness gate or add another mandatory pass.
Even passing does not establish generalization: these are selected development
cases and saved extraction outputs, not fresh independent documents.

Review: Randomize and hide broad/focused labels in paired comparison outputs.
Hash the manual review before revealing the key. Structural differences may
reveal a draft, so masking is partial and labels remain revisable assistant
judgments. Replay parsing/judgments with model setup disabled. Preserve both
completed experiments and their manifests exactly.
