# Independent fresh CFR range review

Decision: determine whether the complete-range reader still loses written endpoints or extends list scope on up to six fresh publisher XML paragraphs.

Hypothesis: preserving two `CfrCitation` endpoints fixes range loss without absorbing unrelated neighboring numbers or dropping following list members. Any accepted first-endpoint-only reading of an explicit complete range weakens the design.

Arms: the parent experiment's frozen pre-change grammar versus the new RefSpec grammar. No parser run occurs until source readings are frozen and the grammar owner declares the API ready.

Cases: at most two selected paragraphs each from manifest-pinned eCFR titles 2, 29, and 47; none from the eight saved whole-token specimens. Search locates candidates; exact surrounding XML supplies the interpretation. Labels are reviewer judgments, with uncertainty retained rather than invented gold.

Held constant: exact original XML bytes, paragraph text formed by XML `itertext`, original context, source file and manifest hashes. One bounded comparison, no network calls, model calls, range enumeration, corpus accuracy estimate, or production edits.

Decision rule: complete explicit ranges retain both written endpoints and endpoint pinpoints; following list members retain their own scope; unsupported or uncertain scope may be refused explicitly with its full source span. Range refusal is retained as unresolved support, not counted as a successful complete reading. An ordinary single reference must remain single.

Stop: six fresh paragraphs and one comparison after API readiness. Report novel defects to the implementation owners; do not tune these inputs or revise expected readings after seeing outputs.
