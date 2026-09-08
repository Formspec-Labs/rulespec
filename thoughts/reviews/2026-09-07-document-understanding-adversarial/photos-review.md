The accepted claims do not fully preserve the selected passport-photograph source. The strongest defects are omitted acceptance permissions and an applicant re-execution duty stripped of its case limits. These defects already appear in the raw model responses. Every emitted source field survives into candidates and accepted claims; this review found no downstream field loss.

This is a bounded review of one 4,982-character selected input and one development run. It compares the output with a source-only inventory sealed before output access. It is an AI review, not human gold or a general accuracy estimate. “Accepted” names the artifact bucket; claims retain `origin: aiSuggested`.

1. **F01 (High): Explicit permissions and the applicant-signature exemption are missing.** These statements appeared in the actual request but have no equivalent in any raw extraction:

   | Source annotation and input offsets | Exact source |
   | --- | --- |
   | PH-003, `[104,208)` | “(1) It is acceptable if the infant's eyes, particularly a newborn's, are partially or completely closed;” |
   | PH-005, `[330,370)` | “Head tilt is acceptable for infants; and” |
   | PH-012, `[778,941)` | “A photograph showing a change in hairstyle or facial hair from the identification document submitted is acceptable if it still is a good likeness of the applicant;” |
   | PH-020, `[1755,1787)` | “Immaterial damage is acceptable;” |
   | PH-021, `[1789,1889)` | “(c) The applicant does not need to sign the photograph, as this often causes creases or smudges; and” |

   All five are in `attempt-0000.request.json`. Its raw response extracts infant head support (C00), the parent-face prohibition (C01), damage definitions (C06–C07), and the acceptance-agent signing duty (C08). None supplies the omitted permissions or exemption. The infant omission matters because a later open-eye baseline is retained. A rule set assembled from these claims loses reasons to accept a photograph and a protection against unnecessary applicant signing.

   Equivalent grouped output would have been acceptable; neither grouped nor separate output covers these propositions. This is a model-output omission, not a parser rejection. Regressions R01–R05 require the permissions and exemption while preserving neighboring limits: no general adult eye-closure permission, no parent face, no universal applicant-signature prohibition, and no mandatory car-seat example.

2. **F02 (High): Re-execution becomes an unqualified DS-11 duty.** Source `[4677,4782)` says “Passport specialists must suspend a form DS-11 received without a photograph from an acceptance facility.” It then says “The applicant must re-execute the form DS-11” at `[4783,4827)`. The second sentence inherits the described case.

   C31, raw `attempt-0002.response.json` extraction 9, instead contains:

   ```json
   {
     "summary": "The applicant must re-execute Form DS-11.",
     "logic_text": "",
     "relation": "none",
     "applies_to": []
   }
   ```

   Accepted claim `c244cad1e84ea499f8aeaa85760628a14f442f4fec732f880bc17bc7f8557ae7` also has no targets and an empty `issues` list. Actor and action are correct. The missing-photograph and acceptance-facility limits are absent from this record. C30 preserves them for suspension but does not carry them to C31.

   Nearby source and unresolved `IRL 975-04` may help a human reconstruct the intended case; neither makes C31 a scoped claim. R08 must carry both inherited limits and preserve the different actors. An otherwise complete DS-11 must not acquire this re-execution duty.

3. **F03 (High): Coordinated photograph standards and the temporary-eyeglasses recommendation disappear.** No raw extraction represents the sentence at `[579,777)`:

   > “(2) The photograph should be taken within six months of submitting the application, be a good likeness of and satisfactorily identify the applicant at the time of the application (see 22 CFR 51.26).”

   Capture age, likeness, and satisfactory identification are distinct predicates. A likeness reference inside a damage definition does not substitute for the general standard. The mandatory replacement-request lead-in survives, while this part of its listed requirements is absent.

   Window 1 also omits the recommendation at `[3000,3189)`: “NOTE: A limited-validity passport using endorsement 46 should be issued when the medical circumstance that requires eyeglasses is temporary and the applicant has urgent or emergency travel.” The same window omits “a. The applicant’s expression should be natural.” at `[3251,3299)`.

   These sentences use `should`, but still state guidance and qualifications. Other `should` statements were extracted in this run. The remedy must retain weak force, not silently convert it to `must`. R03 requires all three coordinated standards, the separate mandatory replacement consequence, and six **months** without an invented fixed day count. R06 requires temporary medical need **and** urgent **or** emergency travel, limited validity, and endorsement 46, without importing an unstated one-year duration.

4. **F04 (Medium): Retained `should` statements are typed as the prompt’s `must do` category.** The actual prompt defines `requirement (must do)` and supplies no recommendation kind. Yet these records use `kind: requirement`:

   | Candidate | Input offsets | Preserved output summary |
   | --- | --- | --- |
   | C23 | `[3731,3809)` | “Both of the applicant's eyes should be open and visible in the photograph.” |
   | C26 | Main quote `[4093,4184)`; qualification `[3975,4091)` | “You should request a signed medical statement if it is unlikely that closed eyes or exaggerated expression are due to a medical condition.” |
   | C28 | `[4238,4497)` | “Processing, communications/customer service, or consular personnel should refer applications lacking photos to their supervisor.” |

   This is a conflict in categorical force. The quotations and summaries still say `should`; this review does not claim they were rewritten to `must`. A consumer relying on `kind` would lose the distinction. C28 has no issues, and C26’s generic logic issue does not specifically identify force.

   An internal vocabulary could use “requirement” broadly, but the actual prompt’s `must do` definition creates the observed conflict. R07 should compare these recommendations with C13’s genuinely mandatory medical-eyeglasses statement request. Where the representation cannot express weak force, it should preserve that uncertainty explicitly. No executable enforcement was inspected.

5. **F05 (Medium): The material-damage summary broadens the definition’s functional threshold.** At `[1385,1633)`, damage must make the photograph “no longer a good likeness” or “impedes the functioning of facial recognition.” C06, raw window 0 extraction 6, summarizes this as:

   > “Material damage is defined as damage to the facial area affecting likeness or facial recognition functioning.”

   “Affecting” is broader than losing a good likeness or impeding recognition. Harmless facial-area damage can affect an image without crossing either source threshold. C06 has `logic_text: ""`, and its only issue is `unknown_actor`.

   The full exact source definition remains in evidence. This is a summary/structured-logic defect, not loss of the quoted definition or an objection to grouping its two branches. R05 should preserve the functional threshold, facial-area scope, alternative tests, illustrative examples, and explicit immaterial-damage acceptance. It must not require both impairment tests simultaneously.

6. **F06 (Medium): Context is reduced in the return option and disability permission.** C10, raw window 1 extraction 0, quotes `[2130,2261)` and retains earlier apparent acceptability. It omits the preceding explanation that a defect may appear when the passport is printed. Its fields are `action: "returned to adjudication to request"` and `object: "a new photograph"`, although the item being returned is the **passport application** and requesting a photograph is the purpose. Its summary does still name the application.

   C22, raw window 2 extraction 0, summarizes `[3633,3730)` as permission “if the applicant has a physical or mental disability.” Source `[3393,3632)` describes disabilities that may prevent a natural or unexaggerated expression. C22 keeps only `logic_text: "in these circumstances"` and does not carry the functional context into its evidence. Its summary can be read as applying to any disability.

   Both have generic logic review issues, which disclose uncertainty without restoring the antecedents. C10’s `may be returned` could describe an allowed procedure or a workflow possibility; the object/context observations do not require choosing between those readings. C22’s source says “may not be able,” so this review does **not** invent a mandatory diagnosis or proof-of-inability threshold. R12 should preserve the returned application, destination, printing-defect context, and purpose without inventing a separate `must request` command. R10 should retain the described expression-ability circumstances.

7. **F07 (Medium): Facial-expression exceptions are not connected to their baseline rules.** The actual request boundary separates ordinary expression text in `[1982,3393)` from disability text in `[3393,4982)`. C22 remains a standalone permission with `relation: none`; C21 retains the general unusual-expression/squinting prohibition. C24/C25 correctly preserve medical eye-closure acceptance and its trigger, but neither modifies C23’s open-eye baseline as an exception.

   C23 preserves `8 FAM 402.1-1` and explicitly marks it unresolved. The target infant provision exists in the selected input but was omitted from window 0 output. Leaving an absent-window reference unresolved follows the prompt; it is not a fabricated reference or a demonstrated compiler defect. The gap is the incomplete baseline/exception structure of the available claims. Presence of C24/C25 limits the loss of the medical case.

   R01, R10, and R11 should check the relationship or an explicitly unresolved **exception** role, without inventing absent target quotations. A single run does not establish that window splitting caused every relationship omission. No emitted local target points to the wrong claim.

8. **F08 (Low): Advisory and reference context is lost.** The best reasonably obtainable infant-likeness goal at `[40,102)` and certificate-photo timing caution at `[1102,1326)` are absent. These are weaker guidance omissions than the explicit permissions. The latter distinguishes recent certificate issuance from recent photograph capture.

   At `[4604,4671)`, the source says “See 8 FAM 1001.2 regarding importing photographs for forms DS-5504;”. C29 keeps the section identifier on the DS-11/DS-82 counter prohibition, but loses the import topic and its DS-5504 association. Unresolved status is appropriate because the target procedures were not supplied. R13 should preserve that local reference context while leaving the target unresolved. R15 should distinguish advisory guidance from descriptive `may wish` or `may have`. The PH-014/PH-050 actor-descriptor error belongs to the inventory erratum, not to the output.

The stage checks establish where the findings arise. Each actual request window exactly matches its stated selected-input slice: `[0,1982)`, `[1982,3393)`, and `[3393,4982)`. Raw text contains 10, 12, and 11 extractions, respectively, and agrees with each response’s stored `parsed` value. All 33 raw records retain all their fields in `candidates.json`, and all candidate fields retain their values in the 33 accepted claims. There are no rejected candidates. These observations establish correspondence for this run; counts and exact evidence do not establish completeness or meaning.

Every emitted condition/exception target was checked for meaning as well as quote resolution:

| Record and resolved targets | Meaning assessment |
| --- | --- |
| C03 → C02 | Correct trigger: unmet following requirements trigger a replacement request. The requirements set remains uninterpreted. |
| C09 → C08 | Correct scope: hand-carry cases limit the acceptance-agent signing task. |
| C12 → C11 | Correct exception: medical inability to remove glasses qualifies the eyeglasses prohibition. |
| C14 → C15, C16, C17, C18 | Correct children for the medical-acceptance lead-in. `prerequisite` versus applicability `scope` is taxonomy uncertainty; no executable interpretation was inspected. |
| C19 → C18 | Correct prerequisite: the medical statement must indicate the necessity of dark/tinted lenses within that permission. |
| C25 → C24 | Correct trigger for medical eye-closure acceptance. The separate exception relation to C23 is missing. |
| C27 → C26 | Correct unlikely-medical-cause trigger. `Rare` appears in C26’s main logic even though the shorter trigger record omits it. |

The five references to `8 FAM 402.1-1`, `8 FAM 1001.2`, and three IRLs are explicitly unresolved. Unseen target contents are not extraction obligations. C29’s external reference is incomplete in local topic context, while C31’s IRL cannot be assumed to restore its missing scope. C32 correctly preserves both IRLs without claiming an exclusive mapping to individual forms.

Several negative controls keep the conclusions narrow. Blank actors on photograph-property or passive statements are appropriate uncertainty; no named reviewer should be invented from context absent from a request window. C08’s hand-carry duty and the medical-eyeglasses links are positive examples. Dark/tinted necessity, eye-obscuring qualifications, medical cause, and one-or-both-eye alternatives remain. C26 preserves **rare** and **unlikely**; there is no polarity reversal or aggregate rare-case loss. Grouped form alternatives, shadows/refraction, and definition categories are not errors merely because the inventory separates them. C19’s “medical statement” is a grammatical condition subject, not an invented human official.

The audit accounts for all 54 frozen annotations and all 33 accepted candidates. The inventory contains 47 substantive annotations and 7 context/scope annotations, including overlapping predicates, guidance, definitions and exceptions. Those are **not 54 independently enforceable rules**, and no aggregate accuracy percentage is calculated. Each candidate has a full claim ID, exact source/output snippets, zero-based raw extraction index, stage checks, target assessment, emitted issues, and linked findings in the audit JSON. Fifteen concrete regression cases include positive expectations and negative controls; they are proposals, not implemented tests.

The source inventory remains unchanged at SHA-256 `953b97fd334d27da5e980dcf802f6c919c6850d0a445b246f364ca303ec5bb5c`. A separate erratum corrects only PH-014/PH-050’s shared actor descriptor: “Be aware” and “See” imply an addressee but do not contain the literal pronoun `you`. The reviewer disclosed that error after sealing and before output release; the separate erratum was written after phase-2 output access began. It is not scored as an output defect.

Access was limited to the four authorized source files, the frozen inventory, three released request/response pairs, `candidates.json`, `claims.json`, and this review’s erratum. Directory listing exposed other released filenames, but their contents were not read. No memories, prior reports or labels, other agents’ work, repository implementation code, provider calls, network calls, or production edits were used. Outside-input dimensions, contact-lens rules, one-year emergency validity, reference contents, and separate responsibilities are not counted as omissions. No executable policy graph or real applicant decision was inspected; severity describes the potential effect of relying on the affected representations.

The supporting artifacts are [the coverage and claim audit](/Users/mikewolfd/Work/rulespec/thoughts/reviews/2026-09-07-document-understanding-adversarial/photos-coverage-claim-audit.json), [the frozen source inventory](/Users/mikewolfd/Work/rulespec/thoughts/reviews/2026-09-07-document-understanding-adversarial/photos-source-inventory.json), and [the inventory erratum](/Users/mikewolfd/Work/rulespec/thoughts/reviews/2026-09-07-document-understanding-adversarial/photos-inventory-erratum.json).
