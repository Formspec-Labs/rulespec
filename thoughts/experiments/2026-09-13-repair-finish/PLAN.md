# Finish the repair-format iteration

Decision: adopt one small, evidence-backed repair-format improvement, or explicitly
defer it and close this iteration. No follow-on prompt tuning inside this task.
The user authorized working toward a finishing point, including integration and
a local commit when the evidence supports it. Initial extraction stays simple;
there is no new default model pass or standalone checker command.

Hypothesis: retaining unchanged fields deterministically reduces copying failures,
unnecessary field changes and output cost while preserving complete repairs.
Alternatives: generating missing governing meaning is the main problem, so fewer
fields do not help; or full replacement usefully encourages consistency, so sparse
edits leave stale components and regress. This tests response shape, not a claim
about the model's hidden reasoning.

Arms: A returns full replacement fields using the existing CUE-derived proposal
schema. B returns only changed fields, deriving their types/descriptions from
that same schema and merging with the selected current record before the existing
decoder and review path. Omitted fields, quote and qualification targets retain
their current values; explicit empty values clear them. All additions remain full
records. Reject unknown fields, invalid types, unknown targets and out-of-scope
edits; unchanged evidence must not be silently cleared. The small representation
instruction differs as necessary; semantic task and other inputs stay identical.

Use the previously tested positive complete-reading task in both arms, with
explicit selected statements and current review status. This is a scoped generation
experiment, not an exact reproduction of the current full `refine` command.
The checker uses the same positive task and actual generated candidates plus
unchanged candidates, in randomized order. It is advisory. Manual source judgments
are the primary quality evidence; a model verdict is neither a label nor approval.

Cases selected before extraction: four new archived US Code excerpts, release
119-102: 5 USC 552(a)(6)(A), 5 USC 555(e), 29 USC 1025(a), and 42 USC
12112(b)(5). They cover nested timing/notice/tolling, denial reasons and exceptions,
pension-statement duties and exceptions, and accommodation/discrimination meanings.
Use their ordinary production extraction once, with no retries, source replacement
or planted omissions. Select at most four readings per excerpt by source relevance
and freeze exact aliases, criteria and uncertainty after reading the initial
outputs but before any repair calls. If the native drafts have no repair
opportunities, report that limitation; do not manufacture natural failures.

Also retain the exact saved pension carryover C0001 failure from the September 12
fresh-focused-repair capture. Add one explicitly constructed actor-component error
to a copy of a fresh benefits reading; preserve its default meaning and source
evidence. This is a counterexample to blanket rejection of component edits, not
another fresh document. Unselected records and selected complete readings are
preservation controls. Definitions must not become invented duties.

Held constant: source, reviewed starting record, selected aliases, complete-reading
task, reference navigation, model (`gemini-3.8-flash`), medium repair/check thinking,
32,768 output limit, no sampling overrides or thinking budget. Extraction uses
production low-thinking defaults. Two repetitions per source/arm, shuffled: 24
generation calls, at most 24 advisory checks, and four initial extraction calls.
Save requests, schema, labels, code/version hashes and source receipts before the
relevant calls. Retain refusals and unexpected no-proposal outcomes. No retries.
Stop before launching another call at 52 calls, 650,000 reported tokens or 2,400
summed call seconds. Stop on two consecutive systemic provider/schema failures.

Decision rule: adoption requires no substantive source/actor/modality/condition/
target regression, no loss on selected complete controls or the component-error
control, and no evidence/history corruption. In addition, require either:

- at least two additional valid, complete repair outcomes across at least two
  fresh sources, without a paired quality loss; or
- equal quality, at least two source-validated fresh repair outcomes in each arm,
  and at least 15% fewer total generation-plus-check tokens for B.

Known pension gains alone do not establish fresh-source value. Repetitions measure
variability, not source coverage. Report complete default meaning, populated-field
fidelity, necessary corrections, evidence/preview validity, checker agreement,
combined application/export, token use and time separately. Record uncertainty
and reasonable alternative labels before scoring. Read anonymized raw outputs
before aggregate scoring; shape can reveal the arm, so this is not independent
human blinding.

If a gate passes, implement the smallest supported change using current schemas
and review/capture APIs, then test the actual integrated request and saved response
path, relevant regression tests, replay, and installed packaging where changed.
Because generation is scoped here, any broader recovery or relationship behavior
requires its own verification; do not silently generalize the result. If the gate
fails or evidence is insufficient, preserve the experiment and close the iteration
with production unchanged. In either case, consolidate current operating guidance
and active tasks, retain old failures, make a local commit and stop. Do not launch
another comparison merely because the result is disappointing.
