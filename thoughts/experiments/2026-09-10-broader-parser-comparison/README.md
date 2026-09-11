# Broader parsers: useful coverage, not a drop-in replacement

**Decision: bounded recognition improvement, failed broader integration gate.**
Keep the current CFR occurrence reader. Test selected additional identifier
families next; do not replace the scan with one of the broader bundles yet.
No production code or schemas changed in this experiment.

## What was tested

The [preregistered design](design.md) compared four bundles on the same
[32 cases](cases.json): three exact saved source passages and 29 constructed
mechanism/counterexample cases. There are 33 manually labeled expected references,
including nine local references that none of these readers supports. Eight
cases are negative controls. These are selected diagnostic examples, not a
representative legal corpus or independent generalization benchmark.

RefSpec and SpicySearch ran from their installed wheels. Rulespec's projection
reader ran by direct local import, as declared before execution. Every actual
module path/hash, checkout state and input hash is in [run.json](run.json).
There were no provider calls or parser exceptions. The single replay matched
all saved outputs exactly; that verifies replay, not additional coverage.

## Results

Counts below come from [summary.json](summary.json), which counts the saved
[manual case assessments](blind-assessment.json), not a new parser or inferred
agreement score. Native spans must be supplied by the tool, be within the
original input, and agree with returned quotes where a quote is provided.
Full-input provenance was retained for every arm; it is not an occurrence span.

| Bundle | Correct expected references | Correct with native occurrence spans | Misleading readings | Negative cases with issues | Baseline successes lost |
|---|---:|---:|---:|---:|---:|
| Current: RefSpec CFR occurrences + SpicySearch strict CFR/USC | 7 | 7 | 1 | 0 | 0 |
| RefSpec: authority + identifier + FR page + compilation + named-act readers | 23 | 2 | 2 | 2 | 1 |
| SpicySearch query identifier detector | 10 | 10 | 3 | 2 | 2 |
| Existing Rulespec projection readers | 10 | 0 | 5 | 2 | 2 |

“Misleading” includes lost qualifiers and lost specificity, not only invented
numbers. A query-shaped candidate is not necessarily a parser defect: the
negative-control concern is promoting it to an unqualified document identity.
The baseline's misleading reading is itself worth retaining: `42 U.S.C. 1983
note` becomes section 1983, losing the distinction between a statutory note
and the section body. Strict token boundaries do not solve that semantic loss.

The RefSpec bundle produced correct additions across many namespaces: public
laws, executive orders, proclamations, constitutional references, treaty and
case citations, reorganization plans, FR pages, chapter/appendix/note-qualified
USC references, known named acts, dockets, RINs and EO compilation locators.
The bundle receives the credit; this design does not isolate causal gains of
its individual helpers. Recognition does not prove target existence.

## Raw examples that determine the decision

- **Additional meaning:** `5 U.S.C. App. 3` becomes an appendix-qualified USC
  reference in RefSpec; the other arms miss it. `42 U.S.C. 1983 note` keeps its
  note flag only in RefSpec. Those distinctions affect the target, not wording.
- **A good partial:** `The agency acts under 5 U.S.C. 552, as discussed below.`
  gives RefSpec's correct section 552 with `parse_status=partial`. A blanket
  rejection of partial status would discard valid citations inside prose.
- **A risky partial:** `42 USC 1983affirmed` gives RefSpec section `1983` with
  partial status, while Rulespec's existing parser gives `1983a`. The strict
  baseline declines it. Whole-value status alone does not distinguish a
  complete embedded citation from a shortened damaged token.
- **Context required:** `5401-5405` becomes a Federal Register document
  candidate in both broad identifier detectors. The shape may be valid in a
  query or a declared metadata field; this deliberately bare-range control
  does not supply enough context to promote that interpretation.
- **Replacing the baseline loses detail:** `40 CFR §§ 82.155(a), 82.156(b)`
  yields both sections, pinpoints and source spans in the current CFR reader.
  RefSpec's broad authority API and SpicySearch's query detector return only
  the first section. Rulespec's old reader also emits an extra part-only 82.
- **Existing duplication is not equivalent:** Rulespec's projection parser
  reads `7 CFR 15a` as part 15. It also shortens `17 CFR 15c3-3` to part 15.
  Reusing that copy unchanged would restore known errors.
- **Still unsolved:** every arm misses the local references in the saved
  seatbelt and refrigerant passages. More external citation families do not
  supply document-local scope or inherited titles.

All native output fields, including nulls and explicit false verdicts, remain
in [raw.json](raw.json). The compact [blinded review](blind-review.txt) hides
arm/function labels and shuffles their order but omits empty fields for reading.
The reviewer checked invalid-title verdicts against the full output. Field
shapes can still reveal the arm, so this is partial masking, not independent
blind adjudication. The manual labels remain revisable.

## Hypotheses and next decision

- **H1 supported on selected cases:** broader readers add correct reference
  types. This is discovery value, not demonstrated downstream LLM accuracy.
- **H2 supported:** query/field conventions and absent occurrence spans prevent
  treating every result as an evidenced document link.
- **H3 weakened:** Rulespec's existing copy does not match RefSpec's broader
  coverage or its handling of several counterexamples. Consolidation needs
  explicit parity decisions; shared function names do not establish parity.

The next small experiment should **append only selected span-bearing families**
from SpicySearch to the existing scan: public laws, Statutes at Large, executive
orders, dockets and RINs. Keep existing CFR/USC reading and exclude generic bare
FR-document inference from that proposal. This is a post-result narrower
proposal, not a passed arm or production adoption.

For the richer RefSpec authority families, the useful upstream work is an
occurrence API that retains matcher offsets and separates token completeness
from surrounding prose. Reuse its matching implementation rather than adding
another citation grammar or guessing offsets by searching normalized strings.
Named-act resolution and section-existence oracles still require the appropriate
reference indexes and edition context; they were not exercised here.

No parser was tuned to these examples. The run stopped after the fixed comparison
and replay. The initial overbroad host-load refusal and an empty-assessment writer
bug are recorded in the design; invalid derived files were preserved and the
assessment coverage check was strengthened before publishing these counts.
