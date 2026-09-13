# Raw response review before scoring

All sixteen raw response payloads were read against the supplied source and frozen
criteria before opening the arm key or running aggregate scoring. The observations
below were recorded before scoring. Candidate counts reveal standalone versus
multi-candidate requests, and warning text can reveal the status treatment; this
is not independent human blinding. The reviewer also designed the experiment.

## What the responses actually did

| Cell | Manual observation |
| --- | --- |
| 01 | Standalone hazard: accepts the unchanged reading with its actors, scope, exclusion, four alternatives, immediate reporting and actual-knowledge exception. Selects F000 and F002–F007. |
| 02 | Rich leave: rejects removal of the short-notice exception, accepts the complete unchanged reading, and rejects both unnecessary component fills. Selects F004 and F006. |
| 03 | Rich hazard: all four decisions match the criteria. Distinguishes actual knowledge from reasonable belief and rejects the two enrichments. |
| 04 | Standalone leave: accepts the unchanged actor, mandatory force, planned-treatment scope, thirty-day notice and practicable-notice exception. |
| 05 | Standalone leave: rejects the unchanged reading because actor/modal evidence locations remain unresolved. Does not identify missing or incorrect default meaning. |
| 06 | Rich leave: all four decisions match the criteria. The original is complete; the other candidates are wrong or unnecessary. |
| 07 | Rich leave: all four decisions match the criteria. The cosmetic-edit rationale calls shall-to-must an unnecessary modification despite source phrasing; it does not explicitly claim that this changes legal force. |
| 08 | Rich leave: all four decisions match the criteria. Explicitly recognizes that shall-to-must does not repair missing meaning. |
| 09 | Rich hazard: all four decisions match the criteria; correctly distinguishes actual knowledge from reasonable belief. |
| 10 | Rich hazard: all four decisions match the criteria. The two unnecessary-edit rationales select only F007 while asserting the whole reading is complete. The unchanged judgment separately selects F000 and F002–F007. |
| 11 | Standalone leave: accepts the reading and explicitly treats unavailable external provisions as properly unresolved. |
| 12 | Standalone hazard: accepts the reading; treats the prosecution limitation in C0001 as separate from the reporting duty. |
| 13 | Standalone leave: rejects the reading for failing to label external references unavailable in the summary and for unresolved component evidence. Does not identify an omitted condition available in the source. |
| 14 | Standalone hazard: accepts the reading, preserves unavailable references without inventing their contents, and keeps the separate prosecution provision independent. |
| 15 | Rich hazard: all four decisions match the criteria. Selects the full relevant passage set for completeness/necessity judgments. |
| 16 | Standalone hazard: accepts the unchanged reading and leaves unavailable external references unresolved. |

Every response supplies the expected judgments and passage selections; the saved
decodes report no errors. Mechanical request/redecode verification follows this
review. These observations do not establish that each rationale cites all the
evidence needed to substantiate every claim.

## Two disagreements with the frozen meaning labels

Cell 05 says:

> The unchanged reading does not meet the task because it lacks exact source evidence for key components that are readily available in the text: the actor ('the employee' in F004) and the modal auxiliary ('shall' in F006) are present in the source but left unanchored in the statement's evidence records, leaving open unresolved component issues.

Cell 13 says:

> The unchanged draft for C0002 does not meet the construction task requirements. Under the task instructions, the statement's summary must explain available referenced governing meaning and expressly identify unavailable material without inventing its contents; C0002 leaves references to subparagraphs (C) and (D) of subsection (a)(1) and subsection (a)(3) unresolved and unannotated as unavailable in the source text. In addition, exact supporting evidence spans for required components such as the actor and modality are omitted, leaving open audit issues.

The component-location issues are real. The draft already contains actor
`the employee`, modality `must`, and their quoted source words; the inherited scope
and main evidence support the meaning. The short component quotes have unresolved
locations. External `reference_links` already record unresolved status in every
arm. Neither response demonstrates missing or incorrect meaning in the default
statement relative to supplied source. Under the frozen product criterion these
are false alarms about the reading, while the traceability limitations remain
valid and must remain visible separately.

There is also a plausible task-boundary ambiguity: the common instructions say
to preserve exact source evidence and identify unavailable material, and define
no-change support as meeting the construction task. A model can interpret that
as requiring a fully resolved record or an inline availability disclaimer. The
observations support investigating that interpretation; they do not establish
that warning text is false, that the model simply failed to read the source, or
that optional populated components never need correction. Do not relabel these
cases after the results or conceal this tension in the aggregate score.

## Rationale evidence limitation

Cell 10's F007 covers immediate reporting, the actual-knowledge exception and the
separate prosecution limitation. It directly supports rejection of the changed
exception in P0001. It does not contain the opening product scope and all four
trigger alternatives. Selecting only F007 for P0002/P0003 is valid source lookup
and relevant to action wording, but it does not independently substantiate the
broader assertion that the whole existing reading is complete. The unchanged
judgment supplies the broader set. Record this as a rationale-evidence limitation,
not a changed verdict label or an evidence-location failure.

## Interpretation boundary before unmasking

Both meaning-label disagreements occurred in standalone requests. The arm key
has not yet been inspected, so this review does not attribute them to additional
link status or claim a repeated factor effect. Use the preregistered matched
contrasts after scoring. There are only two known source excerpts and two
repetitions per condition. Stop at this completed sixteen-call comparison; do
not revise the prompt or start another round inside this experiment.
