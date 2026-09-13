# Raw review before aggregate scoring

Read all sixteen response payloads in cell order, plus the complete source and
selected record for the disputed leave response. Arm names were not used while
reviewing responses, but candidate counts and IDs reveal likely arms. This is an
agent assessment using the frozen criteria, not independent human ground truth.

| Cells | Raw assessment |
|---|---|
| 01, 04 | Billing: correctly reject unchanged unexplained subparagraph (B), reject the changed acknowledgment deadline, and accept the complete repair. Incoming repeated-allegation limit is recognized. |
| 02 | Leave: correctly accepts the medical-treatment notice reading, preserving inherited scope, 30-day notice and practicable-notice exception. |
| 03, 10 | Hazard: correctly accepts the complete reporting rule. Cell 10 correctly leaves the separate use-immunity provision in its own record. No need to fill the withheld actor component. |
| 05, 13 | Hazard candidate comparisons: correct unchanged, knowledge-standard, plain-fill and cosmetic-fill judgments. |
| 06 | Billing without competing edits: correctly identifies that the available alternatives behind subparagraph (B) remain unexplained. |
| 07 | Leave: rejects unchanged prose because it does not announce that external references are unavailable and because exact actor/modality evidence entries remain unresolved. Those status facts do not identify a missing supplied condition or an incorrect actor/modal meaning. This fails the frozen complete-reading control. |
| 08, 09 | Offset: correctly identifies the missing four prerequisites despite their presence in the neighboring record. |
| 11, 15 | Offset comparisons: accept the complete repair; reject actual-execution-of-agreement overreach and the incomplete unchanged reading. |
| 12 | Billing: correctly rejects the unexplained available subparagraph (B). Its additional demand to label external references unavailable repeats cell 07's boundary issue, even though the main verdict is correct here. |
| 14, 16 | Leave candidate comparisons: correct unchanged, removed-exception, plain-fill and cosmetic-fill judgments. |

Cell 07's metadata concern is real: `component_evidence_unresolved` is retained
for actor and modality, and reference status is unresolved. The actor is still
explicitly supplied by the paragraph (2) lead-in; the notice duty and its exception
are supplied by (B), and the selected summary retains both. Repeated short quotes
cause evidence-location ambiguity. The record already identifies unresolved
references in `reference_links` and current `link_issues`. The experiment's labels
distinguish these facts from source-faithful, independently usable meaning for the
available source. A stricter evidence-readiness assessment could legitimately
remain unresolved, but this test did not label traceability as a prose omission.
Do not relabel the case or suppress its genuine warnings to obtain a pass.

The two request shapes differ by both competing candidates and current link-status
details. The model's explanation makes conflation of meaning with metadata a
plausible hypothesis; it does not isolate whether status salience, removal of
counterexamples or ordinary variability caused the changed judgment.

Every response decodes with valid source selections. Keep that mechanical success
separate from correct classification and faithful rationale. No prompt adjustment,
model retry or post-response label change was made.
