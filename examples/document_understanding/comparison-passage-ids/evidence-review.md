# Evidence review after unmasking

The saved key maps R1→Q1, R2→Q2, R3→P2, R4→P1. The initial meaning review was
written before reading that key or the model evidence fields.

Both P runs select F001 for C/U0000–0004, F002 for C/U0005–0012, and F003:F004 for
C/U0013–0017. Inspection of all five catalog entries against all 36 judgments per
run finds relevant source support. Both runs include the governing unforeseeability
lead-in, unusual-circumstances qualification and emergency exceptions for C0014.
No unrelated or invented ID appears. The range resolver preserves original source
text and positions, including the XML whitespace gap. Evidence is broad: 55,292
characters summed over all judgments, versus 8,064–8,560 for complete quote-based
results. Repeated paragraphs in derived judgments account for much of this volume;
this is not 55,292 unique source characters or a measured user-review burden.

Q1 cites the appropriate statements, including the lead-in for C0013/C0014, but
collapses XML whitespace in those two quotes. This refuses C0013, C0014, U0013 and
U0014. Token alignment recovers them without changing any previously accepted
record, raw judgment or rationale. Other notice/timing quotes remain grounded.

Q2 copies C0013's split sentence as two exact source components, and all 36 rows
pass the existing matcher. For C0014/U0014, however, it quotes only the example:
“For example, an employer may require employees to call a designated number or a
specific individual to request leave.” The rationale diagnoses a missing governing
lead-in that this chosen evidence does not include. The input document does support
the finding, but the selected evidence alone is incomplete for checking it. Token
alignment cannot restore an unselected component. This demonstrates why accepted
judgment count alone is insufficient. Other Q2 quotations locate the relevant
statements; many rely on the surrounding source for broader document context.

Both Q runs flag C0016's possible classification; both P runs accept it. Retain the
masked review's uncertainty about this modality distinction. The different counts
of partial units (Q: four; P: three) do not establish better extraction coverage.
All runs flag the same uncertain expected-to-act cases C0004/C0010, and all detect
the known C0014 summary/scope defect. No arm explicitly recognizes the qualifications
that survive in C0014.logic_text, although none explicitly claims total loss either.
P2's rationale loosely attributes an unusual-circumstances phrase to F003; the phrase
is actually in F004, also selected in its evidence range. This is imprecise narrative
attribution, not an unresolved source reference or missing cited component.

## Decision against the saved gate

H1 has bounded support for evidence reliability and component preservation on this
source; all fresh judgments retain relevant support, and IDs avoid the copied-quote
failure in Q1 and incomplete selected lead-in in Q2. Yet the strict adoption gate
is not met: Q2 already passes mechanical matching, the retained-logic recognition
criterion fails in every run, and classification quality remains uncertain. Do not
claim two-repetition mechanical superiority or semantic superiority over Q-token.

H2 shows that a known passage selection can disambiguate separate paragraphs and
produce a smaller quotation. It fails the broader ambiguity/layout/component gate:
repeats within a passage and table/list joins still align, and narrowing can discard
a separately selected qualification. A model-facing IDs-plus-quote hybrid was not
tested. Keep narrowing experimental.

No production change is adopted. If pursuing a separate, narrower reliability
change, passage-only comparison using existing CUE references is the simpler
candidate; preserve full selected evidence and keep semantic review findings
separate. Such a decision would explicitly narrow the original gate, not mean it
passed. There is no demonstrated need for a fuzzy matcher or another model pass.
Stop this experiment at the authorized four calls rather than tune these fixtures.
