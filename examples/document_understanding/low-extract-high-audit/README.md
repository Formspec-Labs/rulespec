# Low extraction followed by high audit

The existing audit found useful defects, but this combination is **not yet a clear improvement over high extraction alone**. It consumed about three times as many reported tokens, produced false alarms about grouping and schema fields, and did not correct any records. Keep it optional while improving the checker.

## What was tested

Four saved low-thinking Gemini 3.8 Flash drafts, two each for full leave and invented display. Each received two high-thinking calls: an independent source inventory without the draft, then comparison against the source, inventory and accepted claims. Both stages used the full section in a 24,000-character window, temperature zero, no thinking_budget and no application max_output_tokens. Eight new generation calls, no retries, new extraction calls or refinement/repair calls.

The audit now accepts the same thinking and generation options as extraction. Exact settings are recorded and checked during replay. Existing inventory/comparison schemas, prompts, evaluation code and Core Finding records were reused; no new schema was introduced. Defaults remain unchanged.

```sh
.tools/document-poc-venv/bin/rulespec-understand audit my-low-run/rulebook.json \
  --thinking-level high --max-output-tokens provider --max-chars 24000 \
  --env-file /path/to/credentials.env --output /tmp/new-high-audit
```

## Results

All eight responses ended STOP with valid stage output; all four audits processed completely and replayed identically. Each assessment reported issues in the draft. The final display assessment also had internally inconsistent coverage judgments, so the evaluator marked seven units unknown and review_complete=false. Processing completeness does not establish judgment correctness.

| Draft | Audit tokens | Low extraction + audit tokens | Audit request seconds | Consistent complete review |
|---|---:|---:|---:|---|
| leave-full-low-1 | 113,055 | 121,401 | 167 | yes |
| display-low-1 | 87,157 | 92,842 | 166 | yes |
| leave-full-low-2 | 114,619 | 121,565 | 212 | yes |
| display-low-2 | 101,569 | 107,114 | 279 | no |

The audits used 416,400 reported tokens. Including the four saved low extractions gives **442,922**, versus **149,846** for saved high extraction alone: **2.96 times the token volume**. This is not a dollar-cost ratio; input and generated tokens can have different prices. Combined extraction/audit request time was roughly 3–5 minutes per document. Controls were saved earlier, not contemporaneously rerun.

## Useful findings

- First leave audit correctly found the nonconsecutive-month meaning absent from accepted output after Core rejected its kind/modality pair.
- Second leave audit identified teacher-specific wording and the future-headcount example missing from summaries. Full source remained in logic_text, so these are prose/topic recovery opportunities rather than loss of all supporting representation.
- Scope warnings exposed standalone wording that omitted governing conditions, including accounting exceptions and the after-sunset context of a display statement. Some warnings overstated loss because relevant text survived in logic_text.

## Problems in the audit

- Both display audits demanded a separate all-four-duties baseline even though all four mandatory duties under the same scope were present. Combined coverage across multiple claims should count; a duplicate duty is not required.
- One audit interpreted alternative_quotes as necessarily OR. Existing CUE says these are source options/components, with choice_text representing AND/OR grouping. The storm statement and scope correctly said all conditions were required. This was a schema-interpretation false alarm.
- One audit treated optional explicit relationship records as mandatory, including a separate linked exception for unspecified outside premises rules. Complete caveat prose already existed. Graph enrichment should be distinguished from lost meaning.
- Inventories reproduced classification weaknesses: queue possibility was background; non-prohibition was permission; a descriptive non-FMLA situation became permitted wording. Inventories are fallible observations, not gold.
- The last comparison called claims erroneous while labeling seven linked units covered. The existing evaluator correctly withheld consistent-coverage credit and marked those units unknown.

No repairs were applied. The current evidence supports an optional diagnostic, not automatic correction or a blanket quality score.

## Next small iteration

1. Supply the checker with the relevant existing CUE-generated field descriptions, especially choice/grouping semantics, instead of letting it guess from field names.
2. Credit an inventory meaning covered jointly by several faithful claims; separate graph-enrichment suggestions from missing obligations.
3. Distinguish unclear standalone prose from meaning retained elsewhere in the record, and require consistent coverage judgments.
4. Retest the saved cases before increasing reasoning or adding repair passes. A shorter audit focused on concrete defects may reduce cost, but has not been tested here.

## Verification and evidence

333 package tests passed, including 11 focused audit tests. CLI help exposes both controls. Tests cover both stages receiving the settings, unchanged drafts, provider-free replay and tampered metadata refusal. Eight calls and four identical replays are saved in verification.json; results.json records total usage.

criteria.json and design.json were pinned before calls. inputs/ contains byte-identical copies of the original drafts. runs/ retains all source inventories, requests, raw judgments, original drafts, Core findings, reports and frozen runtime. source-review.json records eight revisable findings with exact draft/judgment evidence and schema references. Raw model judgments remain unchanged. manifest.json binds the artifacts.

```sh
.tools/document-poc-venv/bin/python \
  examples/document_understanding/low-extract-high-audit/verify.py \
  /tmp/new-low-high-audit-replay-directory
```

Work remains local and uncommitted. No UI changes or automatic review approval.
