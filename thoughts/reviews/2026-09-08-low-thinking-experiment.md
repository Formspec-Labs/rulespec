# Low thinking experiment: completed

User requested flash-8 on low thinking, interpreted as gemini-3.8-flash. Ran four normal extractions: full leave and invented display, twice each, temperature 0, intact 24,000-character windows, no thinking_budget or max_output_tokens. Exact requests differ from saved high/provider-limit controls only in thinking_level. Same runtime verified by hashes. No production code, prompt/schema/default changes, retries, repairs or model audits.

Results: 26,522 tokens versus 149,846 across matched saved high runs, 82.3% fewer. Low requests took 8–12 seconds versus 51–133 seconds for high. All four responses STOP/valid JSON; three complete pipelines and one partial due to kind=statement/modality=not_required for the nonconsecutive-month rule. 69 raw meanings: 68 accepted, one preserved Core rejection. No separate thinking-token usage reported; do not infer zero internal reasoning.

Quality: both display repeats preserved core meanings and avoided duplicated broad baseline; paper-map permission labeling and storm component evidence remain inconsistent. Leave detail varied: first retained teacher and future-headcount example, second omitted those topics from statement/scope and merged more rules; both retained principal thresholds, alternative service/rehire paths and eligibility timing. Split permissions can still lose conditions, as with high. Do not confuse token savings or accepted record counts with measured accuracy.

Evidence: examples/document_understanding/low-thinking-experiment/README.md, source-review.json, results.json, raw-dispositions.json, verification.json, design.json and original captures. Four identical provider-free replays; every raw row accounted for. No new package test run because runtime is unchanged from the prior 327-pass gate. Saved high controls untouched.

Decision: low is promising for inexpensive discovery extraction and for a future low-extraction/high-audit experiment. No global default change and no claim that the audit combination has been tested. Natural stopping point reached; no commit requested.
