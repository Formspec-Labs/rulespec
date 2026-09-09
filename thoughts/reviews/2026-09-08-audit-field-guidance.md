# CUE field guidance in the audit: completed checkpoint

Implemented and tested the next checker iteration. The checker reuses seven existing CUE-generated meaning-field descriptions and adds joint-coverage, optional-link and wording-versus-record guidance. Requests, saved configuration and replay use the same generated prompt. No schema changes, extraction changes, repairs or default thinking changes.

Four live comparison-only calls reused saved low-thinking drafts and high-thinking inventories. Three completed; the second leave response hit MAX_TOKENS and remains unknown. All four captures replay identically. The package passed 333 tests, including 11 focused audit tests. No new extraction/inventory calls, retries or commits.

Results are mixed: parent duties are now credited jointly; the previous storm AND/OR and optional-relationship false alarms disappear in the second display case; the first leave omission remains detected. Both display cases introduce a paragraph-versus-leaf evidence warning even though both alternatives are explicitly represented. The accounting warning still understates meaning preserved in logic_text. Existing inventory errors remain. New comparison token volume is 325,361 versus 322,251 for saved controls, so this is not a cost improvement.

Decision: retain the small CUE integration but keep high-thinking audit optional. Next, clarify upstream CUE evidence granularity: a passage can support multiple explicit alternatives, and passage-ID extraction cannot necessarily select a separate substring per option. Test that narrow case before another full audit. Keep summary quality distinct from complete loss of a condition; a smaller targeted audit remains an untested direction. No further calls were made.

Full evidence, limitations, raw captures, commands and revisable source review: [experiment report](../../examples/document_understanding/audit-field-guidance/README.md).

Replay harness note: the pinned acquisition script's replay branch mistakenly assumes extraction-shaped artifacts. The standalone verify.py checks comparison artifacts and reproduces all judgments/reports without model calls. Original acquisition code, design hashes, captures and runtime remain unchanged.
