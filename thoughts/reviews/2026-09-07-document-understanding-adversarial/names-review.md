# Independent names extraction review

The four runs retain many individual duties, but none provides complete, self-contained coverage of its exact input. The main defects are missing document alternatives, loss of weaker guidance, and missing conditions inherited from adjacent sentences. Most problems are already present in the raw model response. One additional loss occurs downstream: a correctly described recent-ID exemption is rejected because its exception relationship is invalid.

All three saved correction actions improve their targeted meaning. I found no new substantive falsehood introduced by those local edits. The corrected set still omits two substantive source statements and retains component and negative-force ambiguities described below. It remains a set of pending, AI-suggested claims, not a validated complete rulebook.

## Evidence and counting

I froze the source-only inventory before opening outputs. Its SHA-256 remains `509c90334a8102a9d8902594323285f04486718e8db0a9c7a11ace456556084f`; no inventory erratum was needed. I then read all four actual requests and raw response texts, candidates, accepted/rejected claims, and finally the released correction actions/current claims/revisions. I did not read prior rationales, graphs, findings, memories, repository documentation, or other agents' work. No provider calls or production edits occurred.

| Run | Exact input | Raw candidates | Accepted | Rejected | Inventory propositions in that input |
| --- | --- | ---: | ---: | ---: | ---: |
| holdout-01 | Six selected excerpts | 32 | 31 | 1 | 50 |
| holdout-02 | Same six selected excerpts | 29 | 29 | 0 | 50 |
| section-01 | Contiguous 8 FAM 403.1-4(a)-(d) | 14 | 14 | 0 | 24 |
| section-02 | Same contiguous paragraphs | 13 | 13 | 0 | 24 |

These are structural counts, not accuracy scores. The inventory deliberately separates some parent propositions, alternatives, and exceptions; 50 propositions are not 50 independent duties. A single faithful grouped claim can cover several units. I did not pool overlapping inputs into general accuracy. Court, spacing, suffix and applicant/minor-definition content is absent from the contiguous input and cannot be scored as omitted there.

Every candidate quotation and accepted evidence span matches its input exactly. Raw extraction fields match `candidates.json`, and accepted semantic fields match their candidates; downstream processing adds evidence, issues and relationships without changing those fields. The two requests within each input pair are identical. All 87 accepted claims, the one rejected candidate, each in-scope inventory unit, and all emitted modifier links have individual records in [names-coverage.json](/Users/mikewolfd/Work/rulespec/thoughts/reviews/2026-09-07-document-understanding-adversarial/names-coverage.json). Indices below are zero-based **candidate indices**, not positions in the accepted array.

## Findings

**1. Every raw run loses the actual acceptable-document alternatives.** The documentation obligation survives in holdout candidates 4 and section candidates 2, with wording such as “one or more of the documents listed in this section.” No raw extraction identifies the listed options: name change orders, divorce decrees, certificates of naturalization, marriage certificates, documentation of operation of state law, or customary usage. The parent court-order/decree grouping is also absent. These are N007–N014, at selected `[988,1332)` / contiguous `[731,1075)`, full source `[15333,15677)`. The marriage-exception reference remains in the larger quoted obligation, so I do not count the mere absence of a separate exception node as another wholesale omission. The missing options themselves are substantive: a consumer cannot tell which documents qualify from the extracted statements.

**2. Both holdout runs omit weaker spacing guidance and both qualified rewrite rules.** No raw candidates cover N038–N039, N041–N045, or N049–N050: previous-passport spacing, spacing from nationality evidence or ID when no prior passport exists, family consistency and its preference exception, special-issuance sponsor matching, or spacing/suffix rewrite rules. Source spans are selected `[4391,4702)`, `[4867,5371)` and `[5708,5874)`. The source says “you should add a space,” “should match,” and “generally not sufficient cause … unless.” These must not become mandatory actions or absolute rewrite prohibitions. The request asks to preserve force but offers no guidance/recommendation kind. That is a representational limitation visible in the actual request; it is not a reason to erase the source or promote `should` to `must`.

**3. Every run omits two nuanced statements.** N019 says identity evidence “might be required in accordance with Department guidance,” citing `22 CFR 51.23(c)` (selected `[1755,1927)`, full source `[16100,16272)`); N022 says the applicant “generally will need” documentation to change the name on ID (selected `[2366,2463)`, full source `[16711,16808)`). Neither appears in any raw extraction, and both remain absent after the saved corrections. These are qualified statements, not unconditional applicant duties. Separately, the inventory records explanatory content such as the name/identity rationale and uppercase-spacing explanation; their absence is identified separately rather than inflated into missing independent obligations.

**4. The emergency permission loses its inherited branch in all four runs.** The source places the limited-validity permission in the same `(d)(1)` case as a material change more than one year before a DS-11 application with unchanged ID: selected `[1933,2360)` / contiguous `[1676,2103)`, full source `[16278,16705)`. Holdout candidates 10–11 and section candidates 8–9 retain the local time shortage before urgent/emergency travel, but their summaries, quotations, logic and incoming links do not carry the older-change/DS-11/unchanged-ID scope. For example, section-01 candidate 8 says, “A limited-validity passport may be issued in the requested name if there is insufficient time to request acceptable ID before urgent or emergency travel.” Its trigger links to that permission, while the older-change trigger links only to the separate suspension claim. The local endpoints are correct; the inherited scope is missing. The source document still allows a reviewer to recover it, so this is a claim-representation defect, not evidence that the original text has been destroyed or that a passport was improperly issued.

**5. The recent-documentation duty also loses inherited scope in all four runs.** N026 refers back to applicants with a material name change within one year of applying on DS-11. Its second sentence alone says, “However, if the ID has not yet been changed, they must submit their name change documentation” (selected `[2814,2908)`, full source `[17159,17253)`). Holdout-01 candidate 14, section-01 candidate 12 and section-02 candidate 11 summarize a broad unchanged-ID duty. Holdout-02 candidate 13 restores the one-year condition in summary but still omits DS-11. The additional unchanged-ID modifier in each run does not recover the missing antecedent. This is already present in the model output; downstream processing preserves it.

**6. The recent-ID exemption has three different failure modes.** The source says recent DS-11 applicants “do not need to submit ID in the new name” (selected `[2681,2813)`, full source `[17026,17158)`). Holdout-01 raw candidate 13 faithfully summarizes the exemption but emits `kind: exception`, `relation: none`, and no target. Downstream explicitly rejects it: “An exception must use the exception relationship.” That rejection is structurally justified; nevertheless, accepted coverage loses true source content. Holdout-02 and section-02 omit the exemption from the raw response entirely. Section-01 candidate 11 preserves a correct not-required summary and quotation, but emits `kind: permission`, `action: submit`, and `logic_text: do not need to`. The negative force is present but uninterpreted; a simple permission-to-submit triple is different from absence of a submission duty. I therefore flag a representation ambiguity, not a false natural-language summary. Attaching this recent-change exemption to the older-than-one-year suspension duty would not be a sound repair: the source describes different timing classes, not an exception within the older class.

**7. Holdout-02 converts a descriptive possibility into a permission and loses a real exception.** N032 begins “EXCEPTION: You may receive a court order in which the applicant's former name is made confidential” (selected `[3521,3662)`, full source `[21820,21961)`). Holdout-02 candidate 20 starts its quote after `EXCEPTION:`, labels the sentence `permission`, and has `relation: none` and no target. Its accepted ID is `urn:rulespec:document-understanding:revision:c6fde9b1847d4b64aac967a2d21d03ed228bb3548e7bb910bdebbe27896c461a`. Possible receipt is not an assigned power, and the preceding both-names document requirement is left without its confidentiality exception. Holdout-01 candidate 21 correctly uses `exception` and links to candidate 20, the both-names court-document rule. Thus the source permits a correct local relationship, but the second run does not produce it.

**8. Both holdout runs omit confidentiality scope from the additional-evidence permission.** N034 follows the confidential-court-order exception (selected `[3766,3912)`, full source `[22065,22211)`). Holdout-01 candidate 24 and holdout-02 candidate 23 say officials may request additional nationality or identity evidence, preserve both regulatory references, and have no incoming confidentiality condition. Their exact quotations begin at “You may request.” The local passage supports the permission in its paragraph context; the unresolved regulations might authorize broader requests, but this review cannot assume their contents. This statement is not in the contiguous correction case and is not a missing item in that corrected set.

**9. Exact component strings do not prove correct actor/action/object meaning.** Section-01 candidate 7 (`urn:rulespec:document-understanding:revision:eb13d28aeb5bddb53bf37c6b9af2d19a0a3729a48330505ddee044dbbb6d316f`) has action `has had a material name change` and object `form DS-11`, even though the form is application context, not the object of that action. Its full trigger and local target are otherwise correct. This record remains in the corrected current set. Holdout-01 uses a court order/decree as actor in candidates 16 and 20; that is an object constraint with no explicit human duty bearer. It is an ambiguity if `actor` means grammatical subject, and a type error if it means responsible party. Section-01/02 unchanged-ID condition components also use positive `been changed` while negation survives in logic/quotation. I keep these distinctions explicit and do not treat every empty actor, source-supported pronoun, or generic review issue as a semantic failure.

Smaller losses are recorded per claim: holdout-02 candidate 1 omits “For purposes of this chapter”; candidate 0 retains DS-2060 only in its quote. Holdout-01 preserves the Señor-prefix meaning in linked summaries but does not quote the antecedent itself; holdout-02 omits both that meaning and the imperative to follow ranks-and-titles guidance. The spacing-preference records preserve their local alternatives, but do not explicitly link the outer multipart-name scope; that remains a narrower context-representation limit rather than a demonstrated false local preference rule. Both holdout runs correctly assign the ordinal-number fragment to the suffix section through metadata; I found no evidence that the parser misfiled it as name spacing.

## The three saved corrections

The released case is based on **section-01 only**. All 12 current claims and all 17 revisions were inspected. The five replaced original records are marked superseded. The two remaining current modifier links point to current records; no dangling current targets were found. Every current source and component evidence span matches the contiguous input.

| Action | Original candidates | Independent judgment | Remaining limit |
| --- | --- | --- | --- |
| 0: edit documentation claim | 2 | Improves faithfulness: restores all alternatives, the nested court grouping, one-or-more choice, marriage-exception reference, and `22 CFR 51.25`. | Alternatives remain grouped inside one claim and uninterpreted logic; that is sufficient content retention, not executable choice semantics. |
| 1: merge emergency permission and trigger | 8, 9 | Improves faithfulness: adds the older-than-one-year DS-11 and unchanged-ID branch, keeps insufficient time for acceptable ID before urgent/emergency travel, and retains `may` and limited validity. | No explicit new condition nodes are created, but the complete scope is now stated and quoted. The separate suspension duty remains current. |
| 2: merge documentation duty and trigger | 12, 13 | Improves faithfulness: restores the within-one-year DS-11 applicant class, unchanged-ID condition, and required name-change documentation. | The original recent-ID exemption remains a separate current record with its existing negative-force representation ambiguity. |

New revision IDs, in action order:

- `urn:rulespec:document-understanding:revision:a084ebe284a7e43aa609ab2b89fdce2fa06ecfd3283cb46bf60e78bfd3f6ba2c`
- `urn:rulespec:document-understanding:revision:62dfefead27bebcdaeecb3c6d11ace13c19ebbc98df2d8fcc105a87dc6afa48d`
- `urn:rulespec:document-understanding:revision:8e12969b59b75ca10b70ab60f60f318f9baa604f1989067a14a517d1c73f6cef`

The wider evidence quotations do not introduce a new unconditional suspension or documentation duty: those operations remain distinct in current claims, and the corrected summaries preserve their local force. No substantive error was identified in the three new records. The current set is still incomplete because N019 and N022 remain absent. Its original object-of-name-change error and negative-force ambiguity also remain. All current review statuses are pending.

## Every emitted modifier link

Each row below has the correct modifier-to-main direction and the correct local target identity. Full target IDs and exact target quotations are in the JSON audit. Correct endpoints do not imply that every inherited parent condition has been carried forward.

| Run | Modifier candidate | Relation | Target candidate | Local meaning |
| --- | ---: | --- | ---: | --- |
| holdout-01 | 7 | exception | 6 | Specific documentation permission qualifies previous-name prohibition |
| holdout-01 | 9 | prerequisite | 8 | Older DS-11 change plus unchanged ID qualifies suspension |
| holdout-01 | 11 | trigger | 10 | Insufficient time before urgent/emergency travel qualifies limited-validity permission |
| holdout-01 | 15 | prerequisite | 14 | Unchanged ID qualifies documentation duty; recent DS-11 parent is missing |
| holdout-01 | 21 | exception | 20 | Confidential former name qualifies both-names court-document rule |
| holdout-01 | 23 | trigger | 22 | Confidential-court-order case triggers application-name disclosure |
| holdout-01 | 26 | scope | 25 | Multipart name scopes determination of appearance |
| holdout-01 | 28 | prerequisite | 27 | Clear verbal/written spacing preference qualifies spacing permission |
| holdout-01 | 31 | prerequisite | 30 | Identified Señor meaning qualifies direction to titles guidance |
| holdout-02 | 7 | exception | 6 | Specific documentation permission qualifies previous-name prohibition |
| holdout-02 | 8 | trigger | 9 | Older DS-11 change plus unchanged ID triggers suspension |
| holdout-02 | 11 | trigger | 10 | Urgent/emergency time shortage qualifies limited-validity permission |
| holdout-02 | 14 | trigger | 13 | Unchanged ID triggers documentation duty; full recent DS-11 parent is missing |
| holdout-02 | 22 | trigger | 21 | Confidential-court-order case triggers application-name disclosure |
| holdout-02 | 25 | trigger | 24 | Multipart name triggers appearance determination |
| holdout-02 | 27 | trigger | 26 | Clear spacing preference qualifies spacing permission |
| section-01 | 5 | exception | 4 | Specific documentation permission qualifies previous-name prohibition |
| section-01 | 7 | trigger | 6 | Older DS-11 change plus unchanged ID triggers suspension; component object is wrong |
| section-01 | 9 | trigger | 8 | Urgent/emergency time shortage qualifies limited-validity permission |
| section-01 | 13 | trigger | 12 | Unchanged ID triggers documentation duty; recent DS-11 parent is missing |
| section-02 | 5 | exception | 4 | Specific documentation permission qualifies previous-name prohibition |
| section-02 | 7 | trigger | 6 | Older DS-11 change plus unchanged ID triggers suspension |
| section-02 | 9 | trigger | 8 | Urgent/emergency time shortage qualifies limited-validity permission |
| section-02 | 12 | prerequisite | 11 | Unchanged ID qualifies documentation duty; recent DS-11 parent is missing |

For `prerequisite` links, the defensible reading is applicability of this particular rule; the source does not establish that the condition is the only possible reason for the action in all cases. A trigger attached to a permission must not turn `may` into `must`. Holdout-01 candidate 13 has no emitted link and is validly rejected for its invalid exception relation. Holdout-02 candidate 20 has no modifier link because the raw model instead classified it as a main permission. These are different failure paths, not wrong endpoints of existing links.

In the corrected current set, the previous-name exception still targets the previous-name prohibition, and the older-change condition still targets the suspension rule. The merged emergency and recent-documentation records carry scope internally. I found no reversed link, silent retargeting, or new dangling target in the released correction state.

## Regression boundary

The companion `names-adversarial-regressions.json` supplies exact source snippets, actual failing record references or explicitly synthetic negative examples, expected invariants, and permitted uncertainty. Priorities are preserving document alternatives; treating weak modal language without force promotion; carrying neighboring-sentence scope; keeping absence of obligation distinct from permission to perform an action; and validating the meaning and target of an exception despite exact text support.

The source does not define exact one-year date arithmetic, fully resolve the interaction between family preference and special-issuance sponsor spacing, or provide the contents of remote guidance. Regressions should preserve those uncertainties rather than manufacture a single resolved policy. This audit evaluates the supplied artifact chain; it does not establish runtime execution or publication behavior outside that chain.
