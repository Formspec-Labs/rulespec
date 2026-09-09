# Test comparison passage IDs before adopting the combined approach

## Decision

Should comparison judgments select source passage IDs, and is token alignment
within a selected passage worth adding? These are separate decisions. Design the
experiment now; no provider calls or production adoption are part of this update.

## Evidence and competing explanations

Verified: comparison still requests copied quotations. In the saved 825.303 audit,
three claim/unit pairs fail because their quotations change source whitespace.
LangExtract token-exact alignment recovers all six even with fuzzy matching off.
The library alone still selects a match from repeated text and joins layout-sensitive
text in constructed cases. Extraction and inventory already use passage IDs.

Hypothesis H1: model-selected passage IDs reduce unusable comparison evidence
without weakening the audit's ability to detect overbroad or incomplete meaning.
Fewer mechanical refusals accompanied by less relevant evidence or missed scope
errors would weaken H1 rather than count as success.

Hypothesis H2: restricting token alignment to an explicitly selected passage
reduces ambiguity from repeated wording elsewhere and provides smaller citations
without dropping the evidence needed for the judgment. Repeats inside the chosen
passage, wrong passage selection and layout boundaries may defeat this benefit.

Alternative explanation: existing token-exact alignment already solves the relevant
formatting problem; passage IDs add no measurable value on this source. Another
alternative is that IDs merely make evidence easier to accept while broad passages
hide weaker interpretation. Measure relevance and meaning separately from validity.

## Stage 1: bounded post-processing comparison, no model calls

Reuse the saved source, windows and quotations, existing CUE source-reference
definitions, `passage_catalog`, `resolve_passage`, source-map guard and LangExtract
`Resolver.align(enable_fuzzy_alignment=False, accept_match_lesser=False)`.

Compare whole-window token alignment against alignment restricted to a selected
passage/range. Manually reviewed IDs are constructed inputs in this stage, not
evidence that a model can select the correct IDs. Retain original text and offsets,
model quotation, selected IDs, alignment method and all refused selections.

Use the three real failed quotation pairs and these explicit counterexamples:

- Identical wording in two different passages: a selected ID should locate the
  intended occurrence; whole-window ambiguity must remain visible.
- Two occurrences inside the same selected passage: selection does not establish
  uniqueness; do not count the library's single best result as proof of uniqueness.
- A valid but unrelated ID: mechanical validity is expected, semantic evidence
  relevance is not. Flag this in source review rather than inventing a parser check.
- Invalid/out-of-request IDs, ranges crossing unseen text and inserted separators:
  refuse through the existing source-reference and source-map checks.
- Table cells or list entries inside one passage: ID selection must not be credited
  with solving the previously observed layout relationship problem.
- Missing/inserted negation, changed number, changed AND/OR, and omitted intervening
  words: carry over the existing counterexamples and their recorded source context.
- A qualification in another passage: preserve both components; a shorter quotation
  is not an improvement if it hides the governing condition.

Record actual selected offsets, ambiguity, source relevance, support for all
components of the judgment and citation length. Shorter evidence is a measured
size change, not proof of faster human review. Do not build a new matcher or
general table parser to make this stage pass. Stop a proposed narrowing behavior
if the existing machinery cannot establish its required preconditions.

## Stage 2: fresh comparison calls, source and draft held fixed

Use the saved full 4,360-character 825.303 document, all 18 extracted claims,
inventory, source window and current comparison instructions. This is development
data, not an untouched evaluation source. Freeze exact fixtures and expected
checks before calling the provider.

Two model-facing arms, two repetitions each: **four comparison calls maximum**.

| Arm | Model output | Local processing |
|---|---|---|
| Q | Current quotation fields | Current exact matcher; additionally evaluate the same response with recorded token-exact alignment offline |
| P | Passage references replacing quotation fields | Existing passage resolver returning original source spans |

This yields three evaluated workflows from four calls: Q-exact, Q-token and P-ID.
Q-exact versus Q-token isolates processing on identical responses. Q versus P is
a model-facing evidence-format change, so it requires fresh calls and compares
that schema/instruction change as a bundle. Do not credit ID syntax alone with a
causal effect. Keep judgment field order, claim/unit aliases and all semantic
instructions unchanged. Reuse CUE source-reference definitions; do not introduce
a competing production schema just for the experiment.

Use `gemini-3.8-flash`, medium thinking, temperature zero, provider output allowance,
no numeric thinking budget, no automatic retries, and the existing five-minute
per-request timeout. Alternate arm order between repetitions. No extraction,
inventory regeneration, repair calls or prompt tuning. All attempts count.

If Stage 1 exposes a limitation in token alignment, retain it in Q-token's results;
do not silently add an untested guard or compare a hypothetical fixed version.
P-ID does not request an extra quotation in this stage. Stage 1's scoped alignment
therefore cannot establish the quality or cost of a future model-facing hybrid
that emits both IDs and quotations. That would require a separate decision.

## Assessment and decision rule

Review raw outputs with arm labels and evidence syntax hidden for the initial
meaning assessment, then inspect their full evidence. Keep both assessments.
Agent labels are revisable; uncertain modality classifications are not gold.

Primary checks:

1. Accepted judgment count and exact original source offsets; correct C/U aliases
   and reciprocal links; every refusal remains recorded.
2. Source relevance for each proposed judgment, including valid but unrelated IDs.
3. Detection of C0014's overbroad standalone permission, with explicit recognition
   that its complete source paragraph remains in `logic_text`.
4. No new scope/meaning errors or false alarms on source-reviewed correct claims,
   especially notice alternatives, first/subsequent requests and emergency timing.
5. Preserve uncertainty over the existing expected-to-act modality findings.
6. Actual tokens, request time and evidence volume. Repeated full input evidence
   is held constant; do not claim request deduplication or other untested savings.

Recommend P-ID for a narrowly scoped adoption only if both repetitions improve
evidence reliability relative to Q-exact, retain relevant support and detect the
known scope defect without new material regressions. Compare with Q-token as well:
if it matches P-ID on these measures, report parity and choose based on demonstrated
ambiguity behavior and implementation effort. If Q-exact already passes, report
that a benefit was not reproduced rather than declaring P-ID superior.

If P-ID provides adequate evidence and token narrowing supplies no demonstrated
additional value, stop at IDs. If narrowing provides useful precision but fails
ambiguity or component-evidence checks, keep it experimental. Do not infer that
ID selection solves table semantics or guarantees complete rule meaning.

Preserve requests, raw responses, runtime/schema fingerprints, all verdicts,
rejections, IDs, original offsets and review notes. Replay processing separately
from fresh behavior. A passed accounting check is not a clean semantic audit.
Do not adopt any runtime change solely because this experiment was authorized.

## Existing evidence and implementation pointers

- `examples/document_understanding/minor-audit-improvements/fresh/`
- `examples/document_understanding/whitespace-evidence-experiment/`
- `examples/document_understanding/library-fuzzy-evidence-experiment/`
- `packages/rulespec-extrapolator/src/rulespec_extrapolator/audit.py`
- `packages/rulespec-extrapolator/src/rulespec_extrapolator/extraction.py`
- `packages/rulespec-extrapolator/src/rulespec_extrapolator/schema_data/document-understanding.cue`
