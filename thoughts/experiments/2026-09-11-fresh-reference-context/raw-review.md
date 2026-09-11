# Manual review of live outputs

Completed. Read the actual provider JSON against the frozen source review and
labels. The reader display may omit null-valued keys for space; the raw response
retains them. No automatic semantic scorer supplies these judgments. Counts are
per saved window, not document accuracy. Do not change frozen inputs or labels.

## Title 29, observation 1

Read all terms and every non-null field of all 28 A and 23 B raw extractions.
Null-valued fields remain in both provider outputs. The A component refusal and
Core validation were inspected; remaining per-cell/export checks follow below.

- **Primary opportunity: no gain in either arm.** A row 17 and B row 13 retain
  the State-agency definition, the 49l–2 exception and the limited defined use,
  but both stop at the section-49c citation. B supplies the complete target yet
  does not add Governor designation, State-statute basis or cooperation powers.
  This observation weakens source availability alone as a sufficient intervention.
- **Core focus duties:** both preserve 49b(a)'s coordination duties; 49b(b)'s
  requester categories, request/as-appropriate conditions and all three information
  categories; 49b(c)'s four duties; colocation; and the optional national-tools
  authority with State consultation and its delivery-system alternatives.
- **No observed new false inheritance in these rows:** B does not import the
  appropriation-acceptance or 1946 property-waiver conditions. It also does not
  turn 49f(a)'s spending uses into independent focus duties. The frozen positive
  still fails; absence of these errors alone does not establish a passing result.
- **Real baseline grounding defect:** A row 21 invents an ellipsis in
  `actor_quote` rather than quoting contiguous source. The existing parser records
  `component_quote_outside_request` and withholds that component while retaining
  the statement. Its Core graph passes, illustrating why graph validity is a
  different measurement from extraction/source quality. B quotes the actor exactly.
- **Omissions outside the primary opportunity:** B drops A's short-title permission,
  1974 District-of-Columbia transfer and associated ongoing relationship duty,
  and the two notes importing section-3102 definitions. Some are historical
  metadata rather than operative duties, but the ongoing duty and short-title
  identity have possible user value. Neither arm captures the full historical
  material in this focus. Do not count lower row count as a quality improvement.
- **Potential term-scope issue to examine:** A attaches its defined `State agency`
  to the information-sharing row even though that definition is limited to use
  without further description, while the requesting agency is further described
  by its program. B does not attach that term there. This may be an overbroad
  concept link; it is a separate semantic question, not a proven new B gain.

## Title 29, observation 2 and downstream retention

Read all terms and all non-null fields of the 17 B and 22 A raw extractions;
separately reread the first three A rows after a display truncation. Both arms
again retain only the State-agency cross-reference, so the frozen primary
opportunity has **no gain in both observations**. Both group the seven externally
defined terms into one definition unit and omit them from the term registry;
their meaning remains in a sentence but individual concept identity is unavailable.
This differs from observation 1's seven registered terms and illustrates run
variability in the same temperature-zero profile.

B again omits the short-title/DC-transfer/definition-note units that A emits.
Both retain the main focus operational duties without importing 49c/49f conditions.
A's permission wording compresses the three information categories more than its
separate duty statement; B preserves their detail more explicitly. Neither
recovers the remote State-agency meaning. The scoped-term issue also appears in
B observation 2, so it is not a stable B improvement.

**Verified pipeline loss in all four outputs:** the national electronic tools
unit correctly references the supplied `F109:F111` range and retains consultation
and both delivery-system alternatives in raw output. All four Core compilations
reject it as `Main quotation is absent or ambiguous in the pinned source`.
Inspection of `core._claim` → `_evidence` shows an additional refusal condition:
any inserted source-map character inside the complete quotation rejects the main
evidence. The parser's whole-range quote can be exact in prepared text while
crossing inserted paragraph separators. The existing discovery source path
already splits evidence at source-map boundaries, but `_claim` requires one main
fragment. This is a downstream representation gap to test with saved candidates,
not an excuse to alter either context arm or change the frozen model results.
The exact range/source-map confirmation and export checks still need recording.

Exact confirmation: the rejected quote spans prepared positions [18612,19046)
and equals that exact prepared-text slice. It crosses the inserted space
[18656,18657) and two inserted newlines [18868,18870). The rejection wording
therefore hides a distinct source-map case; the quote is present and located.

## Title 38, both observations

Read all terms and non-null fields of all 50 A1, 50 A2 and 49 B2 raw rows. B1 hit
`MAX_TOKENS`: the inspection-only reader decoded its 46 complete prefix rows,
which were also read, without sending that prefix to compilation or calling it
a successful output. The original incomplete remainder is retained.

- **Primary opportunity: no recovered meaning.** All four outputs stop at the
  713(d) reference for the section-727 position definition. B1 explicitly attaches
  `C000` as context but leaves the primary statement unchanged; B2 downgrades it
  from a registered definition to a plain statement and omits that term's identity.
  Supplied context is not sufficient for the declared semantic gain here.
- **Source controls:** raw statements preserve the removed/departed employee
  must/may distinction, final felony determination and notice/deadline branches;
  30 business days versus 30 days; report contents; written signed reassignment
  approval; knowing purchase-card misuse; and first/second whistleblower-retaliation
  penalties. No output adds 7401(4) or imports section-713 misconduct into the
  reassignment rule. This avoids particular regressions but does not recover the
  definition. Several complete raw rules do not survive downstream processing.
- **Classification variability:** A1 calls the appeal opportunity and entitlements
  permissions; A2 and both B observations classify them as requirements with the
  beneficiary as `actor`. The statements themselves still express the right, but
  actor/modality fields may tell an operational consumer the beneficiary must act.
  This is an existing ambiguity, not a stable context-caused gain or loss. B1
  calls the closed list of reporting costs descriptive `possible`; other outputs
  use `may`. No statement claims that listing those costs authorizes payment.
- **Definition identity:** B2 registers six terms versus twelve in each A output;
  several external-by-reference definitions become plain statements. Meaning is
  partially retained in prose, while explicit local concept links are lost.
- **Output capacity:** B1 has 16,370 reported answer tokens and incomplete JSON;
  the production parser accepts no prefix, so it yields zero candidates. B2
  finishes at 13,192 answer tokens; A1/A2 finish at 14,092/13,961. The single
  capacity failure must remain in cost and outcome accounting. These observations
  do not establish that every request with extra context will truncate.
- **Processing losses:** A1/A2 each parse 47 candidates and accept 26; B2 parses
  46 and accepts 25. The raw arrays are larger because three unit ranges are
  refused before Core. Many further terms/components become unresolved. Preserve
  the distinction between those failures, Core's 21 rejected main quotations per
  completed response, and the semantic quality of statements actually generated.
  The unit-range and exact-source reasons need their own focused replay checks.

## Title 20, both observations

Read all terms and non-null fields of all four complete raw outputs, 26 rows
each. All register only the local `satisfactory site` definition.

- **No gain on any of the three declared opportunities:** both arms and both
  observations retain only the income, set-aside and training citations in the
  relevant focus statements. B does not add the supplied allocation limits,
  allowable-purpose/vote/amount conditions, or training/upward-mobility components.
  The additional source is available but the default reading does not consume it.
- **Repeated new modality defect:** row 18/F077 describes the State licensing
  agency as authorized to select the location/type with approval and regulations.
  Both A observations use `authority`/`may`; both B observations use
  `authority`/`must`, despite retaining `is authorized` as their literal modality
  evidence. This is a critical structured-meaning regression under the declared
  gate. The sentence remains an authorization; the field is inconsistent with it.
- **Shared source distinctions:** statements retain State-agency alternatives,
  citizenship and health/lottery conditions, annual versus periodic duties,
  indefinite licenses and conditional termination, building branches, both
  insufficient-user/private-building exception conditions, the separate leasing
  effort duty, and the limited satisfactory-site definition. No output invents
  the unprovided section-107e blindness threshold or imports vending-income
  exclusions into the general authorization or building duties.
- **Qualification splitting still varies:** B2 includes the leasing-effort proviso
  inside the private-building exemption and also emits it separately. The other
  three outputs emit it only as a separate duty. A2 includes license termination
  in the indefinite-license statement and separately; other outputs split them.
  These are differences in standalone completeness/repetition, not gains on the
  preregistered remote-context opportunities. The base pass does not create
  exception links, so a relationship consumer must still connect the conditions.
- **Shared defects and omissions:** all classify the general licensed-person
  authorization as `authority`/`must`. All silently use the editorial suggestion
  `Commissioner` in the training/evaluation paraphrase where the source spells
  `Commission`; the literal capture still retains the spelling and footnote.
  Historical short-title/findings material is not extracted in these outputs.
- **Downstream loss:** only 15, 16, 15 and 15 candidates survive Core for A1, A2,
  B1 and B2 respectively. The rejection reasons must distinguish kind/modality
  contradictions from main quotes crossing inserted source characters. Many
  inherited-actor duties use growing ranges F063:F064 through F063:F071 to keep
  the Secretary lead-in; this retains meaningful source but increases evidence
  overlap and crosses the current single-fragment restriction.

## Decision and completed replay checks

No case recovers a complete declared missing meaning in either observation.
The two-case adoption threshold fails, and title 20 supplies a repeated new
modality regression. One B response is incomplete. Keep the selector experimental;
do not change production context, prompt, schema or model defaults from this result.
The saved-output verification subsequently passed exact request, candidate/refusal,
Core and discovery replay checks for all twelve cells. Source records and exported
fragments are preserved. A uses 128,904 total reported tokens; B uses 140,402
(8.9% more). Separate thinking-token counts were not reported.

The completed diagnostics distinguish 103 exact main quotations rejected across
inserted whitespace, seven kind/modality contradictions, and nine unit-range
refusals across omitted newline-only catalog entries. These are repeated output
events, not distinct rules. The missing entries are `F054`, `F076` and `F178`.
No literal `"null"` field strings occur in the parsed raw outputs. The incomplete
title-38 response's 621-character tail was also read; it remains incomplete and
unaccepted. See [processing-checks.json](processing-checks.json) and the
[result](README.md) for the bounded decision and follow-up work.

## Capture and preparation history

The first freeze command failed before controls ran because `uv run` received
`-c` without an executable. The corrected freeze uses the saved experiment entry
point, passes boundary controls and a no-op mutation, and replays all actual
context selections. Original failed output remains saved. No provider attempt
was spent on that failure.

The generic runtime freezer predates the new USLM/reference modules. This
experiment explicitly snapshots those six additional application/native modules
and verifies their installed hashes before live calls. General capture coverage
needs a separate R1/R4 check: source transformation replay already compares the
saved text and source map, so missing module capture is not by itself proof that
bad evidence can pass validation. No production capture code changed here.
