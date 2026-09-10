# Prior research against the current extractor

**The best next investment is completing and simplifying the existing evidence
and relationship paths. More explanation fields or a mandatory extra audit are
not supported by the saved results.** The strongest measured efficiency candidate
is the shared evidence catalog; the strongest unresolved meaning problem is
finding every rule governed by a qualification.

This is a read-only research/code assessment of local HEAD `bc337a0d` plus the
existing uncommitted exemption-link changes. “Current” means callable local code,
not a released service. The main task is separately implementing passage-reference
challenge evidence; that change was pending during this review. No production
files, saved captures or earlier conclusions were edited, and no provider calls
or test suites were run. The test-hypotheses skill informed the distinction between
observed results and proposed follow-ups.

**Completion note from the implementation task:** passage-reference challenges
are now integrated locally. The [integration check](../experiments/2026-09-10-challenge-source-refs/README.md)
records 433 passing tests and one live challenge applying all five saved railroad
links. References to the pending change below describe the review's starting
snapshot. The follow-up compression comparison and target-discovery experiments
remain unimplemented.

## What is already available

| Capability | Current implementation | Consequence for follow-up work |
| --- | --- | --- |
| Meaning-first extraction, source IDs, low thinking | `extraction.py`: `extract_run`, `passage_catalog`, `resolve_passage`; canonical `schema_data/document-understanding.cue` | Reuse these selectors and the generated schemas. Do not invent another evidence format or schema compiler. |
| Audit source references and medium thinking | `audit.py`: `SOURCE_REFS`, `_judgments`, `DEFAULT_THINKING_LEVEL`; current audit version 5 | The older “quotation copying blocks audit” diagnosis is addressed in comparison. The separate refinement challenge was still quote-based when this review started. |
| Actors, defined terms and explicit uses | CUE term registry; `terms.py`: `resolve_components`, `term_identity`, `add_term_graph`; `core.py`: `evidence_expectations` | Concepts, aliases, evidence and uses already have a working path. Remaining gaps concern finding uses and disambiguating evidence, not absence of a concept schema. |
| Stable identities, revisions and retained findings | `terms.py`: `term_lookup`; `review.py`; `refinement.py`: `_action`, `refine_run` | Proposed repairs should flow through existing review edits and retain refused/older observations. |
| Exemptions can acquire outgoing qualification links | Local `core.py`: `_claim`, `resolve_links`; `refinement.py`: `_decode_proposals`; `test_exemption_links.py` | The old refusal of every exemption edit is obsolete. Link edits preserve exemption kind, not-required force and all other meaning/evidence. |
| Source-preserving discovery and applicability | `discovery.py`: `records`, `export_discovery`; `core.py`: `_scope_record`, graph compilation | The platform already retains source passages, complete logic and existing Core `ApplicabilityScope`, `RelationshipAssertion` and `EvidenceBinding` records. Missing links are an inference problem. |
| Compact aliases and less proposal repetition | `refinement.py`: `_model_packet`, `_challenge_prompt` | Those reductions already exist. Do not count them as new savings. Shared quotation cataloging is still experimental. |

Paths in the table are under
`packages/rulespec-extrapolator/src/rulespec_extrapolator/`, except the test under
`packages/rulespec-extrapolator/tests/`. Native schemas are built by
`tools/build_extraction_schemas.py`.

## Prioritized follow-ups

### 1. Re-test shared evidence after the challenge-reference change

**Measured benefit, not yet safe to adopt.** The
[catalog experiment](../experiments/2026-09-10-evidence-catalog/README.md) reduced
input tokens 31.66% and total tokens 22.75%. Both arms proposed nine correct primary
links; repeated text applied nine and catalog text applied eight. The missing
application came from the challenge changing a thin space while copying a quote.
Catalog output also had two extra unresolved actor-evidence components. These
are retained failures, not grounds to declare a retrospective pass.

Once the independently implemented challenge references are verified, compare
current uncompressed versus catalog inputs with **both arms using the same new
reference output**. Reuse `catalog.py`'s exact reconstruction check, current
refinement helpers and saved counterexamples. Include a fresh source and wrong
targets; a reference that resolves may still support the wrong judgment. Measure
final applied links, component warnings and all token categories. One previous
quote error does not establish that compression caused it or that references
will remove all regressions.

This is the leading cost follow-up because it preserves information and has a
live savings signal. It does not require new persistent Core fields.

### 2. Test target discovery separately from auditing or rewriting statements

**Unresolved semantic problem.** Both catalog arms missed the refrigerant
C0001 → C0004 edge even though the affected local service rule was in the packet.
The older [explicit-contrast audit](../experiments/2026-09-10-explicit-audit-contrast/README.md)
accepted local duties while separately accepting remote exemptions. More elaborate
rationales found no additional defects. The
[relationship-audit experiment](../experiments/2026-09-10-relationship-audit/README.md)
also omitted the section-wide seatbelt exclusion's targets.

A useful different task is: **for each qualification, assess its candidate target
rules**, including “no supported link,” rather than ask for general corrections.
Start with the existing claim aliases, `references`, `reference_links` and source
section locations. `core.resolve_links` currently resolves section labels by exact
normalized label/ID equality; it is not a complete relative-citation resolver.
Explicit paragraph references can nominate candidates; neither a citation nor
proximity establishes applicability. Keep the target set bounded and include
nearby duties that remain binding and qualifications governing several rules.

The smallest experiment uses current source-backed exemption edits and challenges,
changing only target enumeration. Do not add a general graph schema or a new
mandatory audit. Evaluate whether the final links add useful meaning relationships,
not whether an audit's changing self-generated inventory reports 100% coverage.

### 3. Reduce copying in tiny edits and component evidence

**Plausible reliability improvement; limited direct cost ceiling.** Current
exemption edits must reproduce every existing field except the relationship and
targets. A model-facing link edit could name the existing claim and selected
targets; deterministic code would populate unchanged fields before the ordinary
preview/challenge/review path. Existing equality protection must remain. This is
a smaller application view, not another Core operation.

The [cost accounting](../experiments/2026-09-10-refinement-cost-accounting/README.md)
found only 4,695 answer tokens across the two relationship proposals, under 2% of
the full workflow. Do not market this as the leading whole-workflow cost fix.
Its stronger hypothesis is avoiding copy-induced rejection and accidental edits.

Similarly, `core._evidence` already searches within the parent quote before the
whole document, but repeated `driver` or `Staff` inside that parent remains
ambiguous. The [manual review](2026-09-10-manual-data-closeout.md) and
[end-to-end run](../experiments/2026-09-10-exemption-end-to-end/README.md) preserve
actual failures. Revisit selecting an existing passage for component support,
retaining the complete source passage when the short label is ambiguous. Actor
labels and supporting evidence need not be identical strings. Test repeated
actors with different duties and actor-versus-approver counterexamples. Do not
resolve ambiguity by accepting the first substring match.

## Useful later, with a narrower product decision

- **A link-enrichment-only route.** `refine_run` always obtains an initial audit,
  runs recovery and relationships, and obtains a final audit. The two fresh
  [full workflows](../experiments/2026-09-10-exemption-end-to-end/README.md) improved
  seven links but no original statements; both recovery calls were empty, and
  the complete path cost 20.2 times initial extraction. A cheaper source-backed
  discovery enrichment mode is worth comparing when links are the requested
  output. Removing stages changes available information; 20.2 times is not an
  achievable savings claim. Keep completeness review optional and explicit.
- **Omit prior audit rationales from relationship input.** They occupied 32.9% of
  the two saved packet character counts. Test after lossless compression, because
  removing judgments is information removal. Preserve them in history and decide
  explicitly which unresolved findings the relationship task still needs.
- **Cross-window definition reuse.** `terms.resolve_components` resolves a term
  against exactly one accepted defining unit in the current window. `term_lookup`
  preserves current/historical identities but does not discover missing uses or
  reconcile meanings across documents. The medical-treatment/first-aid missed
  term use is a saved diagnostic. Revisit only against an actual search/graph use
  case; matching aliases alone must not collapse different senses.

## Conclusions to retain or update

| Earlier conclusion | Status today |
| --- | --- |
| “Whitespace compensation is implemented.” | Incorrect for production. The whitespace and known-library fuzzy experiments recovered citations but failed ambiguity/layout controls; neither broad fallback was adopted. Passage references are the existing integration route. |
| “Exemptions cannot be linked without reclassification.” | Superseded by the current local exemption-link implementation and fresh end-to-end evidence. This does not fix omitted targets. |
| “Assess relationships before the audit.” | That tested bundle produced no added detection and used 2.65 times the tokens. Its operation blocker has changed, but its default-workflow adoption gate did not pass. Revisit only a narrower link task or new explicit hypothesis. |
| “The evidence catalog still needs its first live test.” | Stale text in `2026-09-10-refinement-efficiency-hypotheses.md`; the completed catalog report now controls. The failed gate remains failed. |
| “Add logic/modality explanations or another grouping reminder.” | Keep unadopted. Fresh explanation tests found no sufficient net gain; grouping followed the instruction in only one of two same-scope runs. These exact prompt branches do not merit immediate reopening. |
| “Actors/definitions need a new schema.” | Superseded by combined extraction and fixed enrichment. Missing uses, scope fidelity and ambiguous evidence remain. |
| “Green audit/schema/grounding proves complete rules.” | Still false. Preserve `semantic_completeness=not_established` and the known false passes. |

Evidence for rejected alternatives:
[whitespace](../../examples/document_understanding/whitespace-evidence-experiment/README.md),
[configured libraries](../../examples/document_understanding/library-fuzzy-evidence-experiment/README.md),
[fresh explanations](../../examples/document_understanding/fresh-explanation-check/README.md),
[deadline grouping](../../examples/document_understanding/deadline-grouping-experiment/README.md),
[actor/definition integration](../../examples/document_understanding/actor-term-integration/README.md).

The recommended sequence is to finish the current reference implementation, then
choose one bounded cost or target-discovery comparison. Avoid combining those
changes: one addresses avoidable copying and packet size; the other addresses
which rules the source actually governs. Saved results use selected sources,
small samples and revisable agent assessments, not a general accuracy benchmark.
