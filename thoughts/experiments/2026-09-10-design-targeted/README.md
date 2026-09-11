# Per-target source challenge: useful separation, adoption gate failed

Independent target decisions retained **4 of 5** expected useful links, compared with **2 of 5** for the current whole-proposal challenge. Neither accepted any of the **3 known wrong links**. Total tokens increased **4.0%**. The proposed bundle did not pass its gate: it lost a previously supported applicability link and generated an overbroad explanatory sentence. Nothing changed in production or any review graph.

| Measure | A: current whole-proposal challenge | B: per-target plus affected-action descriptions |
|---|---:|---:|
| Known positive links recommended | 2/5 | 4/5 |
| Known negative links recommended | 0/3 | 0/3 |
| Uncertain carrier edge recommended | 0/1 | 0/1 |
| Grounded responses with decoding errors | 0/3 | 0/3 |
| Input tokens | 38,216 | 38,246 |
| Answer tokens | 782 | 2,082 |
| Thinking tokens | 8,263 | 8,820 |
| Total tokens | 47,261 | 49,148 |

All six fresh requests used Gemini 3.8 Flash, temperature 0, provider-default thinking, 32,768 output-token limit and one candidate. Usage fields were present for every response. Six calls consumed **96,409 total reported tokens**; no retries, extraction calls or full audits. These numbers compare challenge stages only; they do not establish savings over the entire refinement pipeline.

## What the comparison isolates

A and B received the same source catalog, draft, audit data and frozen proposals. A used the current production challenge unchanged. B changed the task and response schema to separately decide substantive meaning and every proposed target, with an affected-action description. The task used the existing source-reference schema and production grounding resolver. This is a deliberate bundle; the experiment does not isolate the descriptions' contribution from target granularity.

The actual phone failure was preserved: a proposed companion exception links the driver prohibition and disputed carrier prohibition. Refrigerant and railroad link bundles were constructed from saved original claims, using the current compact-link decoder, to include positive and negative targets. No original captures were changed. Candidate pairs were supplied to both arms. **This is a target-selection test, not a missing-target discovery test.**

## Practical result

| Case | A | B |
|---|---|---|
| Phone emergency use | Rejects bundle, loses clear driver edge | Separates driver support from carrier rejection |
| Listed refrigerant substitutes | Supports venting and service edges | Supports venting; rejects service as already outside baseline scope |
| De-minimis refrigerant releases | Rejects bundle, loses venting edge | Retains venting; rejects post-recovery and independent-service edges |
| Railroad stop exemption | Rejects bundle, loses stopping edge | Retains stopping; rejects gear-change edge |

A's rationales already recognize the driver, de-minimis venting and railroad stopping distinctions. B makes those distinctions explicit in separate fields. This is a bounded improvement in review output, not evidence of better underlying understanding.

B fails the frozen five-positive/no-negative gate because it rejects the exempt-substitute→service relationship. Its rationale says service obligations already exclude exempt substitutes, so a further exception does not alter them. A treats that relationship as useful explicit applicability information. Both describe compatible substantive applicability; they disagree about what the edge records. This suggests clarifying existing relationship semantics before another prompt change. The original expected label remains unchanged; its modeling assumption is now an explicit uncertainty.

The carrier question remains unresolved. Both give an unsupported verdict categorically, despite its preregistered uncertainty; neither should be treated as a legal conclusion. B also adds the sentence “All other releases remain prohibited,” which overstates the de-minimis exception's surviving baseline and ignores the separate listed-substitute exemption. Generated affected-action text needs its own evaluation and must not silently become executable meaning.

## Application and verification boundary

These are **recommendation simulations**, not applied changes. Supported B targets count only when the separate meaning verdict is also supported. Existing exemption selections were validated through the current compact-link decoder. No review action, export, or final graph was mutated. The partial phone addition was not rewritten or applied. The affected-action field exists only in the experiment and has no operational Core interpretation.

All six responses complied with their response schemas and grounded through the current resolver. Zero-provider-call replay reproduced the request/schema checks and grounded decoding; it is not a new behavioral replicate or a full graph-application replay. Frozen runtime, input, source, prompt and harness hashes matched.

The experiment used one observation per arm on three selected historical documents, with same-agent manual review. It cannot establish general accuracy, semantic completeness or provider repeatability. Hypotheses and expected labels were frozen before calls. No tuning followed results.

## Decision

**Investigate a smaller change; do not adopt this bundle.** Independent decisions can prevent one questionable target from hiding useful links. A future comparison should separate target decisions from generated descriptions, clarify whether an edge records already-expressed applicability as well as scope-changing exceptions, and retain disputed interpretations explicitly. That is a new experiment, not permission to bypass this failed gate.

- [Preregistered plan](PLAN.md), [frozen expectations](expected.json), [design and hashes](design.json).
- [Complete manual raw review](RAW-REVIEW.md), [machine accounting and recommendation simulation](assessment.json).
- [Replay receipt](replay.json), [raw calls](cells/), [harness](experiment.py).
