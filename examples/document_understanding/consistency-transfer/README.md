# Finer evidence helps locating text, but does not improve complete meanings reliably

**Decision: retain paragraph references in production.** Sentence references reduced
unresolved component locations but lost governing conditions and antecedents in
fresh first-aid/recording documents. The declared no-regression gate failed.
The sentence splitter remains confined to this experiment; no sentence-specific
prompt patch or new explanation field was adopted.

## Comparison

[PLAN.md](PLAN.md) records the hypotheses, competing explanations, cases, settings
and decision rule before provider results. [REVIEW.md](REVIEW.md) assesses every
raw output against source, with cell/row examples and uncertain labels.
[results.json](results.json) contains the mechanical counts and actual usage.

One call per case/arm: `gemini-3.8-flash`, temperature 0, low thinking, 32768 output
tokens, whole-document focus up to 24000 characters. All ten recorded request
configurations have the same hash; only the passage catalog/prompt text differs.
Sentence spans use installed LangExtract 1.6.0 `SentenceIterator`, with no custom
boundary rules. Every non-whitespace source character remains selectable in order.
Library splits inside citations/abbreviations are retained, not manually corrected.

| Case | Paragraph / sentence claims | Unresolved component locations P / S | Output tokens P / S | Main finding |
|---|---:|---:|---:|---|
| Seatbelts, fresh | 17 / 17 | 7 / 6 | 5,334 / 5,537 | Better structured scope in S; both leave some exclusions outside the default statement |
| First aid, fresh | 13 / 15 | 9 / 0 | 2,889 / 3,273 | S loses explicit antecedents; P omits some background |
| Recording, fresh | 54 / 60 | 27 / 14 | 8,381 / 14,829 | S retains more note content but loses two inherited prerequisites |
| Passport, development | 14 / 14 | 0 / 0 | 3,130 / 3,119 | S repairs the Posts duty but reintroduces “this information” |
| Constructed counterexamples | 15 / 17 | 6 / 2 | 3,182 / 3,432 | Both preserve major role/sense distinctions; S adds a redundant duty without its object |

All ten responses parsed, with no candidate rejection or parser refusal. That does
not mean all components grounded: repeated words such as `you`, `must` and `Staff`
still produce the warnings above. Those remain visible on retained statements.
S also has two ambiguous term-support fragments in the long first-aid definition;
although the main definition is complete, the validated term index withholds that
sense, leaving four term links unavailable. Section citations also remain unresolved
where their targets are absent from the prepared section index; they are retained
without guessed destinations (counts in results.json). A valid passage selection alone does not establish useful semantic support.

Across the five cases, S used 30,190 output tokens versus 22,916 for P (32% more),
and 20,977 input tokens versus 17,186 (22% more). Provider-reported totals were
51,167 versus 40,102. Separate thinking-token counts were not returned; do not call
that zero thinking. These are usage counts, not a priced invoice. The biggest
increase occurred in recording: S emitted 540 null fields versus P's 122, more
structured context and six additional statements. Sparse CUE fields permit omission,
but do not guarantee the model will omit them. Neither arm populated logic fields;
only P's seatbelt label alternatives used a separate choice field.

Mean main-evidence length fell in every case, but this is a size measurement, not
a quality score. For example, S selected only the permission lead-in as main
evidence for the sport-parachuting option, placing the actual action in scope
support. Shorter evidence can still be the wrong main citation.

Three authentic govinfo **2025 snapshots** are preserved as XML, normalized text,
prepared documents, source URLs and normalization receipts under `sources/`.
They are newly selected diagnostic cases, not an independent benchmark or a claim
about current law. The constructed fixture and familiar passport case are labeled.
One sample per cell cannot estimate repeatability or general accuracy. The review
used cell labels before opening the arm mapping, but visible passage granularity
prevents claiming full blinding. Agent judgments remain revisable.

## Production workflow checks

`integration/` uses P's actual first-aid extraction, then makes one enrichment
and two medium-audit calls. Enrichment correctly made no additions. The audit
finished with no processing issues and reported one missing background unit,
so its semantic verdict is `failed`, with `review_complete=true` and
`semantic_completeness=not_established`. It marked all supplied claim dimensions
correct; our manual review still found an imprecise optional scope field. A
recorded agent correction resolved that field. Core validation, source recovery,
review reload, discovery reload, extraction replay, enrichment replay and audit
replay passed. A failed semantic verdict is preserved, not rewritten as success.
The saved audit becomes stale after correction; it does not assess the edited draft.

`partial-enrichment/` adds one actual provider call after the invalid-existing-
definition edge-case fix. It starts from a real captured constructed-source
extraction and records two deliberate fixture edits: remove one of two term uses,
and clear an actor. The model restored the missing reference in the nonempty list.
It proposed Staff, but the repeated source word could not be uniquely located, so
the actor was withheld. An observation and Core Finding preserve the suggestion,
reason, actual request/model provenance and affected revision. A later recorded
agent edit used the unique complete source sentence to resolve the actor. This is
integration evidence, not an independent extraction-quality result.

That smoke's initial `statements_unchanged` measurement incorrectly compared list
order: editing moves revisions in the current view. The original measurement is
retained in `checks-original-order-sensitive.json`; `checks.json` compares by
stable `rule_id` and confirms unchanged statement text. No response was changed
or retried to obtain that result. Enrichment replay and workspace reload passed.

The first pre-call setup attempt found no key in RefSpec and sent no request.
Its failure and original runner/design remain under `setup-failure/`; Spicy Regs
provided the already-authorized credential. Ten comparison calls plus four
integration calls were made; the setup failure is not a provider call. No credentials
are part of these artifacts. Copies and replay files do not represent extra calls.

## Reproduction and stopping point

The post-trial robustness fix changes runtime fingerprints. Strict replay should
refuse silently mixing that code with older captures. To verify the original trial
with its saved application and matching installed dependencies:

```sh
.tools/document-poc-venv/bin/python examples/document_understanding/consistency-transfer/replay.py \
  --output .tools/new-consistency-replay
```

The later partial-enrichment capture replays with current production code:

```sh
rulespec-understand enrich-replay examples/document_understanding/consistency-transfer/partial-enrichment/capture \
  --output .tools/new-partial-enrichment-replay
```

Original inputs, provider captures, manifests, runtime versions and failures remain
available. `experiment.py` refuses overwriting/resuming existing cells; new provider
trials require a new directory and preregistered decision, not rerunning until green.

This closes the planned comparison with a **tradeoff / no adoption** decision.
Remaining quality problems are standalone qualifications/antecedents, incomplete
term uses, ambiguous short component quotes, source-dependent modality and omitted
contextual content. Favor a separate experiment that preserves already-selected
component coordinates or challenges complete statement meaning; do not indiscriminately
split more sentences or add optional fields. These findings do not establish
production semantic completeness or a general accuracy rate.
