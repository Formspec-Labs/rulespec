# R6 delivery: preserve the native USC result through existing exports

Decision: connect RefSpec `find_usc_citations` from commit `c5c0a27d` to Rulespec's
existing optional reference adapter, then deliver verified wheels.

Hypothesis: the shared record/evidence path can expose the native USC occurrences
without changing extracted claims or other reference families. Complete native
qualifications, original source spans, inherited context and explicit refusals
must survive both `references` and `discovery-export --references`.

Comparison: current installed reader/adapter versus direct source imports, then
the rebuilt isolated and working installations. Freeze baseline outputs before
editing. Use the same 29 R5 cases plus the two real authority notes, the current
full application suite, the saved fresh-extraction run, and publisher USLM source
fixtures. Add controls for inserted text, mismatched parser quotations, repeated
mentions, inheritance and refused qualifications.

Reuse: native `AuthorityCitation` and occurrence fields, Core source evidence,
existing passage association, existing sparse serialization, discovery evidence
sharing, publisher containment and captured reader identities. Do not add model
or CUE fields or a second parser. For USC, `value` is the source quotation; the
native `reading` and context identify its normalized target. This avoids making
another formatter reinterpret abbreviated endpoints or rejected qualifiers.
Existing families keep their current display values.

Held constant: saved source/model outputs, model settings, dependency versions
apart from the two rebuilt local packages, existing review state and source
captures. No model calls, browser work, target crawling or production publication.
This is correctness work owned by Rulespec, not a SpicySearch performance run.
Use fresh exclusive output directories; preserve every failed attempt.

Gate: direct and installed outputs preserve all native USC information needed for
target meaning and refusals, with exact evidence and deterministic replay. Existing
family candidates/refusals remain unchanged except for the additional USC
observations and parser metadata. Publisher association must retain separate text
readings, not claim target agreement. Default discovery and accepted claims remain
unchanged. Verify source-to-wheel and installed files, run the full application
suite from outside the checkout, and run normal reprocess/replay/reference/discovery
commands against a saved response. Stop this delivery if those checks fail;
do not quietly narrow the gate. Broader R1–R26 work remains separate and open.
