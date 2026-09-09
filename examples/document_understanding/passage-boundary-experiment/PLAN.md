# Passage boundary diagnostic

Decision: Is a larger exact passage worth investigating as a way to preserve the
notice permission's governing qualifications? This is an experimental presentation
change, not a production segmentation policy.

Observation: in the previous eight-call description experiment, both raw notice
permissions selected F004 and omitted scope. A source blank line splits the
governing sentence between “comply with” (F003) and “the employer's…” (F004).
F004 itself includes the unusual-circumstance and emergency exceptions. Both
pieces are supplied and the existing resolver permits F003:F004.

Hypothesis H1: presenting the governing sentence in one exact passage improves
selection of its lead-in and preservation of its conditions in the permission's
statement. Two complete treatment statements with relative baseline improvement
in both pairs, without false dependencies in controls, support further investigation.

Alternative H2: this boundary chiefly affects evidence selection. Treatment may
retain the lead-in in its quote while the statement still omits conditions.
Alternative H3: example/different-modal-force splitting persists regardless of
passage boundaries. Statements may remain unchanged under both arms. H2 and H3
overlap if only quotations change; this test cannot establish hidden reasoning.
Baseline success without relative improvement weakens evidence for the intervention.

Arms: B uses the current passage catalog and production schema. T joins the two
specified adjacent catalog entries into the first ID, using their exact outer
offsets and unmodified intervening whitespace; the second ID disappears. All other
entries stay identical. This changes catalog granularity/ID presentation together.
It does not normalize text, infer scope, change statement guidance, add examples,
or modify the document's stored source passages. Patch only the existing catalog
function for this diagnostic and reuse normal extraction and replay.

Cases and criteria fixed before calls:
- Two fresh pairs on the complete saved 4,360-character 29 CFR 825.303 source.
  Join only F003/F004 in T. A designated-number permission, grouped or separate,
  must preserve unforeseeability and unusual-circumstance/emergency limitations
  in its statement. Assess scope and evidence separately. All three emergency
  recovery prerequisites must survive: stabilization AND phone access AND ability.
  Preserve the information alternatives, first/subsequent notice distinction,
  source force and other reviewed meanings. A quote-only change is not a semantic
  fix. Existing uncertainty about “expected” modality is tracked separately.
- One pair on a constructed same-actor document: “Staff must sign each report.”
  and “Staff may use a blue pen.” Separate exact paragraphs in B; joined in T.
  Both meanings must survive, with no waiver of the signing duty or invented
  precondition. A combined complete statement is acceptable.
- One pair on a constructed different-actor document: “Visitors must file a notice
  on arrival.” and “Staff may work remotely.” Separate exact paragraphs in B;
  joined in T. No arrival condition may transfer to staff remote work, and neither
  actor's force/action may transfer to the other. Both meanings must survive.

The real case is repeatedly used development data, and controls are constructed,
short and deliberately simple. These are revisable extraction-quality judgments,
not legal authority or independent evaluation gold. New-source generalization and
a generic safe sentence-boundary policy are outside this diagnostic.

Held constant: gemini-3.8-flash, temperature 0, low thinking, no numeric thinking
budget or application output cap, 24,000-character windows, source bytes, schema,
instruction/examples, parsing and Core conversion. The prompt differs only in the
catalog. Eight calls total: notice B1/T1, notice T2/B2, same-actor B/T, different-actor
T/B. Existing five-minute request timeout; no retries, audits or repair. Temperature
zero is not a determinism guarantee. Repeats measure this case's variability only.

Decision rule: support further investigation only if both notice treatment runs
meet the standalone criterion with relative improvement over their paired controls,
no material meaning regression in notice, and no invented dependencies or lost
meanings in either constructed control. Otherwise report partial grounding benefit,
no measured improvement, regression, or unresolved as appropriate. Do not adopt
production changes under this diagnostic even if it passes.

Capture every request, raw response, refusal and derived record. Verify the actual
catalog intervention, unchanged settings/schema, raw-to-record preservation and
exact offset grounding. Mask/randomize arms for initial primary-agent review; then
unmask and report the self-review limitation. Replay locally without provider calls.
Stop after eight calls; preserve this preregistration, including failed predictions.
