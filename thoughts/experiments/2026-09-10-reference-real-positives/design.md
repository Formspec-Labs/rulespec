# Real-source positive reference test

Decision: Does the unchanged five-kind additive reader merit a candidate-only integration proposal when tested on real positive source text?

Hypothesis: It recovers explicit public-law, Statutes at Large, executive-order, docket, and RIN occurrences with their original spans while preserving the baseline. Counterhypothesis: real typography, qualifiers, lists, or context expose omissions or misleading identities hidden by constructed fixtures.

Arms: The same baseline and filtered SpicySearch detector as the preceding additive-reference-families experiment. Reuse that runner's functions; no grammar, kind-filter, or normalization changes.

Cases: Download and preserve the official GovInfo text of Federal Register documents 2025-24202 (2026-01-02) and 2024-07412 (2024-04-16), selected by titles and visible reference-bearing source search results before parser execution. If a source is unavailable, retain the failure and report the gap; do not substitute based on parser behavior. For a bounded manual assessment, select the first complete paragraph mentioning each of the five reference families in each document, plus the immediately following paragraph, deduplicating overlapping paragraph selections. Label every occurrence of an allowed family in the selected text before running parsers. Preserve the full downloaded documents and source-relative offsets. Reuse the previous Ohio source as a separately reported historical noise control.

Selection cues (for manual source selection, not a new production parser): Public Law / Pub. L.; Stat.; Executive Order / E.O.; docket identifier in a heading or narrative; RIN. Whitespace-only paragraphs separate source blocks. Include all identifiers in selected blocks, including repeated ones, and identify uncertainty explicitly. GovInfo text is the input; no repair of line wrapping, punctuation, or hyphenation. If heading layout separates an identifier from its label, retain the adjacent block as context.

Held constant: Installed wheels, baseline scan, allowlist of public_law/statutes_at_large/executive_order/docket/rin, one run and one exact replay. No LLM calls; source downloads only. Maximum two new documents, eleven source cases including the historical control, and 20 minutes. No tuning after results.

Decision rule: A bounded improvement requires unchanged baseline output, exact source evidence for additions, no misleading additions, and all manually labeled occurrences recovered across all five families. If any condition fails, report the failing gate and cause; do not shrink the denominator or filter. Missing real positives for a family means unresolved coverage for that family. A passing gate permits recommending integration, not automatic production adoption. This test measures selected passage recognition, not full-document recall, target resolution, or extraction quality.
