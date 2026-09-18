# Blind source-based quality review

Set 2 improves independent referenceability for the drug and aviation cases. Both safeguard sets preserve the declared source details. Set 1 resolves more of the CSBG local references, but both CSBG sets retain material dependence on neighboring source text. No set should receive a blanket quality pass based on its record count.

These are revisable assistant judgments against the supplied source, not expert-approved labels. “Set 1” and “Set 2” are only the input labels; this review does not identify or infer the experimental arms.

## Review basis and interpretation

I reviewed every record and every populated decoded meaning/evidence field in `inputs.json` against each complete supplied source, `EXPECTATIONS.md`, and the subsequently supplied `CSBG-CHECKS.md`. The latter supplied the original C1–C14 criteria without arm information. I did not read experiment settings, captures, keys, prior reviews, or git history, and made no API calls or production changes.

Record numbers below are one-based within the named case and set. The input's `summary` is assessed as the default standalone statement. I distinguish:

- **Source detail:** Whether the correct action, actor, condition, object, or alternative survives anywhere in the candidate records.
- **Standalone meaning:** Whether a reader can identify the duty and its scope from that record's statement without reconstructing neighboring source text.
- **Structured fields and evidence:** Whether the actor, modality, scope, references, and attached quotations preserve or recover the meaning. A complete quote can rescue interpretation without fixing an incomplete standalone statement.
- **Granularity:** Whether distinct duties or triggering situations can be referenced independently. A long but accurate list is not missing content; it may still fail the declared referenceability requirement. Repeated source quotations are not themselves duplicate duties.

## Drug records: 21 CFR 211.188 and 211.192

**Set 1 retains the substantive source contents but fails the declared list referenceability check and leaves investigation referents implicit. Set 2 provides each listed record element separately and names the investigation, with a remaining precision issue in its abbreviated description of specification failure.**

### Material differences and remaining defects

1. **Set 1 R3 combines all thirteen required documentation elements; Set 2 R4–R16 make them separately referenceable.** Set 1 R3 explicitly includes “(1) Dates” through “(13) Results of examinations made in accordance with § 211.134.” This is complete content, not a generic list pointer. However, all thirteen elements share one record, so an individual labeling, sampling, personnel, or investigation-record requirement cannot be referenced as its own statement. That fails D3's explicit requirement. Set 2 R3 retains the overarching significant-step documentation duty, and R4–R16 each retain their batch-record framing. For example, R9 requires records to include “inspection of the packaging and labeling area before and after use” as part of significant-step documentation, grounded in § 211.188(b)(6). The parent duty and its independently stated contents are a useful hierarchy, not gratuitous duplication.

2. **Set 1 R6–R7 depend on an unnamed investigation; Set 2 R19–R20 partly resolve it.** Set 1 R6 says “The investigation shall extend,” and R7 says “A written record of the investigation shall be made.” Their full § 211.192 quotes preserve the antecedent, but neither statement nor their empty scope/reference fields identifies it. R6 therefore fails the standalone part of D9; R7 has the same recoverable dependency while preserving both conclusions and followup under D10. Set 2 R19–R20 instead say “the investigation into any unexplained discrepancy or failure of a batch or component,” a material improvement in standalone meaning.

3. **Set 2 R19–R20 still abbreviate the failure trigger too broadly.** The source identifies “the failure of a batch or any of its components to meet any of its specifications.” R19–R20 say only “failure of a batch or component.” Read alone, that formulation does not expressly restrict the failure branch to specification nonconformance. The complete source quote and R18 preserve the correct limitation. This is a residual standalone precision defect, not an omitted investigation duty or proof that the set as a whole asserts a different rule. D9's referent is substantially improved, but the safest independently usable wording would retain “to meet specifications” in R19–R20.

### Coverage and counterexample ledger

| Checks | Set 1 records | Set 2 records | Finding |
|---|---|---|---|
| D1 | R1 | R1 | Preparation for every produced batch and complete production/control information survive. |
| D2 | R2 | R2 | Accurate master-record reproduction, accuracy check, date, and signature all survive. |
| D3–D4 | R3 | R3–R16 | Both preserve accomplishment of significant steps and all thirteen contents. Only Set 2 makes each listed content independently referenceable. |
| D5 | R3, item (11) | R14 | Both preserve performers and direct supervisors or checkers, with the automated-equipment alternative identifying the human checker. Neither turns the alternative into cumulative staffing duties. |
| D6 | R3, items (12)–(13); R4–R7 | R15–R20 | Both retain §§ 211.192 and 211.134 and the § 211.68 personnel reference without inventing absent section bodies. |
| D7 | R4 | R17 | Both preserve all production/control records, packaging/labeling, quality control unit review **and** approval, approved written procedures, and timing before release **or** distribution. |
| D8 | R5 | R18 | Both retain unexplained discrepancies, the yield example, batch/component specification failure, thoroughness, and already-distributed batches. |
| D9 | R6 | R19 | Both retain extension to other batches of the same drug product **and** potentially associated other drug products. Standalone referent defects are described above. |
| D10 | R7 | R20 | Written record, conclusions, and followup survive; standalone investigation identification remains the difference above. |

I checked D4's contents individually: dates (Set 2 R4), individual major equipment/lines (R5), each component/in-process batch identity (R6), weights/measures (R7), both control-result types (R8), before/after area inspection (R9), actual and percentage theoretical yield at appropriate phases (R10), complete labeling records with specimens/copies of all labeling (R11), containers/closures (R12), sampling (R13), personnel (R14), investigations (R15), and examinations (R16). Set 1 R3 preserves the same details in its enumerated statement.

Neither set imports the release deadline into the investigation duty. Both correctly leave the passive investigation and record-making actors unspecified; the quality control unit actor appears only on review/approval. Historical amendment credits produce no manufacturing duties. The broad § 211.192 quotes cover several duties, but I found no cross-duty scope leak in the populated scope fields.

## Aviation: 14 CFR 91.123 and 91.125

**Both sets preserve all seven clearance/instruction rules and all twelve light-signal table cells. Set 1's single table record fails the declared independent referenceability condition. Set 2 makes the cells independent and adds a low-value table-pointer record.**

### Material differences

1. **Set 1 R8 is content-complete but combines six different signals and both aircraft settings into one statement.** It correctly says, for example, steady green means takeoff on the surface and landing in flight; it also retains the flashing-green follow-on steady green “at proper time.” No table cell is missing or switched. The problem is granularity: the declared checks allow one complete dual-setting record per signal or separate setting records, while Set 1 offers one record for the entire table. Separate signals have distinct triggering situations.

2. **Set 2 R10–R21 preserve each signal/setting mapping independently.** The surface/flight setting appears in both each statement and its `scope_text`; the table quote preserves the column headers. R19 correctly states that flashing white is “not applicable” in flight and uses `kind: statement`, `modality: not_stated`, rather than inventing an airborne command. The other table records are also presented as signal meanings; I did not treat the absence of a newly inferred command modality as an error.

3. **Set 2 R9 adds a non-independent table pointer.** “ATC light signals have the meaning shown in the specified table” identifies neither a particular table nor any signal meaning in the standalone statement. Its quote is only the introductory sentence, so the record requires its neighboring table records. R10–R21 already carry the actual mappings and the introductory context. R9 is low-value duplication, not a missing duty or a false table interpretation.

4. **Set 2 R1–R7 have more explicit structured scope than Set 1 R1–R7.** Their default statements preserve the same source meaning. Set 1 stores the clearance setting, exceptions, request conditions, and timing in the statement/quote, leaving `scope_text` empty. Set 2 separately carries those conditions in scope fields. This is a structured-recoverability improvement, not a content improvement in the default statements. Set 2 R3's actor “that pilot” is resolved by its scope identifying the uncertain pilot; it is not an unsupported new actor.

### Complete rule and table ledger

| Check | Both sets' records | Finding |
|---|---|---|
| A1 | R1 | Obtained clearance; amended clearance, emergency, **or** resolution-advisory exceptions all survive. |
| A2 | R2 | Cancellation remains permission in VFR weather, excluding Class A airspace. |
| A3 | R3 | An uncertain pilot must immediately request ATC clarification. |
| A4 | R4 | ATC-instruction prohibition retains the controlled-area setting and only the emergency exception. |
| A5 | R5 | Both emergency and resolution-advisory deviations trigger notification as soon as possible. |
| A6 | R6 | Emergency priority, even without subpart-rule deviation, retains detailed report, 48 hours, ATC-facility manager, and ATC-request condition. |
| A7 | R7 | Other-aircraft radar clearance/instruction prohibition retains the ATC-authorization exception. |

| A8 signal | Set 1 | Set 2 surface / flight | Verified meanings |
|---|---|---|---|
| Steady green | R8 | R10 / R11 | Takeoff / land. |
| Flashing green | R8 | R12 / R13 | Taxi / return for landing, followed by steady green at the proper time. |
| Steady red | R8 | R14 / R15 | Stop / give way and continue circling. |
| Flashing red | R8 | R16 / R17 | Clear the runway in use / airport unsafe, do not land. |
| Flashing white | R8 | R18 / R19 | Return to starting point on airport / not applicable. |
| Alternating red and green | R8 | R20 / R21 | Extreme caution / extreme caution. |

The 48-hour report requirement is not applied to the as-soon-as-possible notification in either set. Set 2 R8 retains OMB approval as a non-duty statement; that adds source metadata but does not create a pilot reporting requirement. Neither set converts historical amendment text into a duty. I found no source-meaning error shared by both sets in this case.

## Information safeguards: 45 CFR 164.310 and 164.312

**Both sets retain H1–H14 at the declared level, including every Required/Addressable label in the default statements. Their equal counts do not establish that result; each of their 24 records was compared with its source duty. Set 1 has awkward, non-source modality wording in five statements. Both have limits when only the small structured fields or only an inherited-scope statement is consumed.**

### Differences and shared limitations

- **Set 1 R16, R17, R20, R23, and R24 say the actor “is addressed to implement.”** The source uses the label “(Addressable)” and an imperative under the introductory “must, in accordance with § 164.306.” “Is addressed to” is not source terminology and does not clearly express a recognized duty or permission. Each statement nevertheless explicitly retains “Addressable,” the § 164.306 qualification, and the correct action; the corresponding `modality` is `must`. I classify this as a clarity defect with potential modality confusion, not proof that those five source duties were omitted or made optional. Set 2 consistently uses “As an addressable implementation specification … must, in accordance with § 164.306,” avoiding that invented expression.
- **Both sets flatten Required and Addressable in the narrow structured classification.** All 24 records have `kind: requirement` and `modality: must`. None puts “Addressable” in `scope_text`; the distinction survives in the statement and quote. Thus a consumer reading only actor/modality/scope cannot distinguish those qualifications. This is a shared field-level limitation, not a claim that the complete records silently drop Addressable. The supplied source does not contain § 164.306, so the review cannot establish the missing external policy or reinterpret Addressable as optional.
- **Both retain some inherited scope by a named standard rather than fully spelling out its target.** For example, R11 refers to hardware/media movements “under device and media controls,” without repeating that the relevant hardware/media contain electronic protected health information. R14 and R16 refer to “access control” without restating the parent standard's systems-maintaining-electronic-protected-health-information setting; R16 otherwise reads as an electronic-session rule. Their attached parent quotations recover these limitations. These are shared standalone-scope dependencies, not differences between sets or missing H-check details. R3's “the facility” likewise relies on the named facility-access standard and attached parent evidence. A downstream display that strips that context should not treat these statements as rules about every device, session, or facility.

### Record-by-record coverage ledger

The record mapping is the same in each set; each row below applies independently to both.

| Check | Records | Verified source content |
|---|---|---|
| H1–H2 | R1; actor/qualification throughout R1–R24 | Covered entity **or** business associate; § 164.306 qualification; limited physical access with properly authorized access allowed. |
| H3 | R2–R5 | Four addressable specifications: restoration access under both plans and implement-as-needed; physical access/tampering/theft; role/function, visitors, software testing/revision; security-related repairs/modifications. |
| H4 | R6–R7 | Proper workstation functions, manner, physical surroundings, workstation/class with protected-information access; separate physical safeguards restricting authorized users. |
| H5 | R8 | Hardware/media containing protected information; receipt/removal into/out of facilities and movement within. |
| H6 | R9–R10 | Required final disposition of information and/or its hardware/media; required removal before media reuse. |
| H7 | R11–R12 | Addressable movement/person records; retrievable exact copy when needed before equipment movement. See inherited-scope limitation above. |
| H8 | R13 | Technical policies for systems maintaining protected information; only people/software with rights under § 164.308(a)(4). |
| H9 | R14–R15 | Required unique name and/or number for identification and tracking; required emergency information access with procedures implemented as needed. |
| H10 | R16–R17 | Addressable inactivity-based predetermined logoff and both encryption/decryption. See Set 1 wording and shared inherited-scope limitations above. |
| H11 | R18 | Hardware, software, and/or procedural mechanisms; both record and examine; systems containing or using protected information. |
| H12 | R19–R20 | Improper alteration/destruction protection; addressable corroboration against unauthorized alteration/destruction. |
| H13 | R21 | Claimed identity of the person/entity seeking access to protected information. |
| H14 | R22–R24 | Electronic-network transmission protection; addressable modification detection until disposal; addressable encryption whenever deemed appropriate. |

No physical/technical access confusion, hardware-movement timing leak, alternative split into cumulative mandates, unsupported actor, lost action, or gratuitously duplicated duty was found. Set 1's extra labels and Set 2's movement of some parent quotations from scope to context do not change the source actions. Neither set supplies invented requirements from the absent external sections.

## CSBG repeat: 42 USC 9913 and 9914

**Both sets retain the substantive C1–C14 source details and keep the statutory permissions as permissions. Set 1 is stronger on independently identifying local sections and the State's incoming report. Both retain unresolved pointers, and neither fully satisfies C15–C18 as a group.**

### Material independence differences

1. **C17 has a shared failure in R2–R3.** Both R2 statements say distribution is “in accordance with subsection (c),” without identifying § 9913(c). Both R3 statements say “The activities described in paragraph (1)(A) may be carried out,” without identifying § 9913(a)(1)(A) or spelling out those activities. The structured `references` retain the same local pointers. This matters because the grouped source contains multiple sections and multiple subsections (c). Set 2 R3 adds the full activities text in `context_quotes`, so its record's evidence is more self-sufficient than Set 1 R3's; its default statement and scope text remain unresolved. The source places these provisions in § 9913(a)(1)(B) and (a)(2), respectively.

2. **Set 1 R6–R7 resolve distribution and recipient eligibility to § 9913(c); Set 2 R6–R7 do not.** Set 1 R6 says activities “under 42 U.S.C. 9913(c),” providing a clear home for its remaining “paragraph (2)” recipient pointer; R7 directly names “42 U.S.C. 9913(c)(2).” Set 2 R6 says only “under subsection (c),” and R7 says “paragraph (2) of subsection (c).” These preserve the source content but fail C17's section identification in isolated statements. Set 2 R7's context is merely the generic eligible-entities heading and does not repair the namespace. Both sets preserve direct distribution, the exact reserved-fund citation, all purposes, eligible recipient types, demonstrated expertise, and low-income families/communities.

3. **Set 1 R4–R5 identify § 9913; Set 2 R4–R5 say “this section.”** This is an additional standalone-scope difference. Both faithfully retain feasible attention to eligible entity/program needs, financial-management quality, and ongoing input from national and State networks. Set 2's statements and quotes do not identify which supplied section governs the training-determination process. No wrong State actor or monitoring timetable is imported, but the local reference remains unresolved.

4. **C18: Set 1 R12 identifies § 9914; Set 2 R12 does not.** Set 1 permits assistance “as needed to comply with the requirements of section 9914.” Set 2 says “the requirements of this section”; its populated scope repeats that phrase. Both preserve the State's permission, Secretary as the request recipient, training and technical assistance, and the need-related limit. Only Set 1 makes the governing section explicit in the default statement.

5. **C15: Set 1 R15 improves report identity but does not fully identify § 9914(c); Set 2 R15 is unbound.** Set 1 says “On receiving the evaluation report submitted by the Secretary.” Set 2 says “On receiving the report,” and repeats that unbound phrase in `scope_text`. The source's preceding sentence identifies the Secretary's report to each evaluated State with evaluation results and improvement recommendations. Both records attach the complete § 9914(c) paragraph, which recovers the correct trigger. Set 1 has meaningfully clearer standalone authorship and report type, but still omits the § 9914(c) evaluation/funds context; I grade its precise independence as partial, not an unqualified pass. Set 2 fails the standalone report-identity check. Both retain receipt as the trigger, the plan of action, Secretary as recipient, and response to the report's recommendations.

6. **C16: Set 1 R14 identifies the State evaluations; both R16 statements leave the evaluations unnamed.** Set 1 R14 names each State evaluated “under 42 U.S.C. 9914(c),” while Set 2 R14 says only “each State evaluated” and “such evaluations.” Both R16 statements begin “The results of the evaluations shall be submitted annually.” Neither statement nor its scope/reference fields identifies the relevant § 9914(c) evaluations of State use of funds. The § 9917(b)(2) citation identifies the annual report vehicle, not which evaluations are its subject. Full paragraph quotes recover this in both sets. Both retain annual timing, both congressional recipients, and § 9917(b)(2). Set 1 R16 additionally attaches the source's committee-name change as context; Set 2 preserves that change in R17 instead.

### Source-detail and record ledger

| Original checks | Both sets' records | Source-detail result, distinct from independence |
|---|---|---|
| C1 | R1–R2 | All listed activities, corrective-action/monitoring purpose, reporting/data collection, reserved funds, and distribution direction survive. |
| C2 | R3 | Grants, contracts, or cooperative agreements with appropriate entities remain permission for the referenced activities, not a new duty. Local activity identification is defective as described above. |
| C3–C4 | R4–R5 | Eligible-entity/program needs, financial-management quality, maximum feasible extent, local responsiveness, and ongoing national/State-network input survive. |
| C5–C6 | R6–R7 | Direct distribution, § 9903(b)(2)(A), recipient restriction, all improvement/local-needs purposes, demonstrated training expertise, and low-income families/communities survive. |
| C7 | R8 | State full onsite review of each eligible entity at least once per three-year period survives. |
| C8 | R9 | Newly designated entity review immediately after its first funding year completes survives. |
| C9 | R10 | Followup includes prompt return visits to entities and programs failing State goals, standards, and requirements. |
| C10 | R11 | Other reviews remain as appropriate; other grants terminated for cause are included, with this chapter's assistance excluded. |
| C11 | R12 | State assistance request remains permission, as needed. C18 independence differs. |
| C12 | R13 | Secretary evaluations in several States each fiscal year, investigations, use of funds, and chapter compliance especially § 9908(b) survive. |
| C13 | R14–R15 | Report to each evaluated State, results, improvement recommendations, benefits to people in need, and receipt-triggered State plan survive. C15–C16 independence differs. |
| C14 | R16 | Annual submission, both congressional recipients, and § 9917(b)(2) survive. The evaluation subject remains unbound. |
| Historical-note counterexample | R17 | Both label the committee-name change as a statement with no duty modality. |

No source duty is lost merely because a local reference is unresolved: the complete supplied source and, for the evaluation records, the attached paragraph preserve it. But that recoverability does not make each default statement independent. Conversely, R8–R11 repeat the common State review purpose while stating four distinct reviews and triggers; this is useful framing rather than gratuitous duplication. I found no wrong modality, cumulative splitting of alternatives, unsupported State actor in § 9913, or imported monitoring deadline.

## Decision implications

The strongest demonstrated differences are **separate referenceability** in drug Set 2 and aviation Set 2, and **better local-reference resolution** in CSBG Set 1. The safeguard comparison supports retained declared meaning in both sets, with a clarity advantage for Set 2 and shared limits in abbreviated structured fields and inherited-scope statements.

This review does not establish general equivalence, legal correctness beyond the supplied source, or superiority of an unidentified experiment arm. Its remaining repair targets are concrete: identify specification failure precisely in drug Set 2 R19–R20; remove or bind aviation Set 2 R9's table pointer; preserve safeguard qualifiers whenever fields or statements are displayed without their context; and resolve the specific CSBG section, report, and evaluation references listed above.
