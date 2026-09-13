# Local clause navigation

Decision: connect the existing reference scanner and context exporter to the
ordinary local references missed by the saved IEP extraction. This is a
deterministic implementation of the previous trace, not a new model experiment.

RefSpec owns occurrence recognition. Initially support singular `clause (i)`
forms with lowercase Roman labels. Preserve exact spans and refuse attached
pinpoints, lists, ranges and explicit different-container qualifiers. Native
USLM lookup uses the enclosing clause's actual parent and direct clause children;
it never searches another branch for a missing label. Missing or ambiguous
native structure remains unresolved. Notes and quoted content do not establish
the local operative scope.

Rulespec reuses `SourceIndex`, source evidence, reference targets and
`context-export`. Outgoing targets and incoming referring claims become
navigation evidence with an unassessed semantic role. Current statements,
classification, `target_ids`, identifiers and review history remain unchanged.
No model call, prompt change or mandatory processing pass is required.

Acceptance: on the saved IEP book, the writing rule's two occurrences locate
clauses (i)/(ii); contexts for R004/R005 expose R006, while R003/R007 do not.
Keep the previous two external publisher readings and LEA readings unchanged.
Constructed controls cover repeated labels in separate branches, missing and
duplicate targets, unsupported syntax, nonoperative text, overlapping current
claims and context limits. Reproduce outputs without a model and verify source
and book digests. Original trace artifacts stay unchanged.

Implementation should index native structure once, then resolve each occurrence
with a binary search and ancestor traversal. Do not rescan the XML per reference.
Build and install the RefSpec wheel before Rulespec verification; validate the
installed Rulespec wheel outside the checkout. Commit each owner's changes
locally and record their artifact digests. Broader reference grammar, automatic
semantic assignment and independently complete extracted statements remain open.

Completed: [delivery results](../experiments/2026-09-12-local-clause-navigation/README.md)
record the real-case navigation, counterexamples, installed wheels and unchanged
source/review checks. The broader semantic-completeness problem remains open.
