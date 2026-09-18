# Extraction efficiency investigation

Decision: identify the smallest changes that reduce model requests or token use
while preserving or improving faithful, independently usable requirements. The
user explicitly authorized parallel agents and bounded experiments. Findings do
not authorize automatic production adoption.

Baseline: installed production at commit 765f8b8 and the complete pinned CSBG
retest. Section extraction used 27 requests, 202,158 recorded tokens, 282 accepted
records, and captured all thirteen State-plan content topics with eleven passing
the detail review. Its two plan gaps, lost board scope, opaque references, and
evidence duplication remain test targets. Broad extraction used six requests and
129,185 tokens but lost the list's meanings and truncated one window.

Three independent agents own disjoint experiment subdirectories:

1. `output/`: unnecessary optional fields, repeated output and schema-guided omission.
2. `windows/`: repeated request overhead, bounded grouping, call count and latency.
3. `process/`: source assembly or another simpler alternative to prose rewriting.

Each agent must write a pre-call plan and use current schemas/capture facilities,
retaining exact requests, responses, refusals and source-based review. Each may
make at most four fresh Gemini calls with a 16,384 generation-token cap and a
15-minute capture bound. Combined maximum: twelve generation calls. No automatic
retries, production file changes, commits, mandatory extra passes or corpus-wide
run are authorized within this investigation. The root agent measures the saved
request/storage profile and reconciles recommendations, avoiding duplicate live
tests. Existing research is checked before spending on a repeated idea.

Report actual model-call count, input/answer/thinking/total tokens where available,
elapsed time and costs separately from serialized byte sizes. Missing provider
usage stays unknown. Local evidence copies are not model output. Offline size
estimates are not measured provider-token or billing savings. Test a complete
meaning against raw source; model claims and schema validity are not approval.

Decision rule: prefer an experimentally supported cost or fidelity gain that
reuses existing code, schemas and source identity. Report regressions and tradeoffs
even when counts improve. A few development/other-source cases support bounded
findings only. Stop after the planned comparisons; save an ordered integration
recommendation instead of accumulating more prompt variants.

After the twelve calls, a fourth agent reviewed complete source and anonymized
separate-section/task-grouped outputs. It received no experiment conclusions and
made no provider calls. Its review was saved and hashed before the root opened
the assignment key. This checks the meaning judgments; it adds no model samples.
See [results](RESULTS.md) and the [verification receipt](verification.json).
