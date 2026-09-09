# Audit grounding experiment: completed, not adopted

Executed the proposed six paired inventory calls at medium thinking. The prototype
reuses CUE source-reference definitions, the existing passage catalog/resolver and
audit source-span records. It adds a generated inventory request view; comparison
instructions and downstream record shape remain unchanged. The prototype passes
347 package/generator tests, native CUE generation and all six replay checks.

All six calls completed with zero evidence refusals. Controls accepted 13 units,
treatments 14; total tokens 20,519 (11,004 control, 9,515 treatment). Different
splitting and one sample per cell prohibit accuracy or causal claims.

The predeclared quality gate fails: treatment's separate teacher rule omits the
inaccurate-record governing condition present in the control/source, and its
counting exemption is classified as permission despite retaining need not in
meaning. Both service alternatives and thresholds remain. None of the narrow
controls reproduces the original full-document marker failures.

Decision: no full-document audit and no adoption. Restored all production code,
tests and generated schemas from the clean baseline after preserving the tested
prototype patch and frozen sources. No new model calls, retries, repairs or commit.
The original plan and this experiment's artifacts remain uncommitted.

Next: a deterministic test using the actual four refused inventory rows and
source-reviewed passage selections, keeping meaning text unchanged; separately
evaluate the split teacher condition. Do not merge the location and meaning
questions into a single pass/fail metric.

[Report, raw evidence, prototype patch and frozen replay command](../../examples/document_understanding/audit-grounding-experiment/README.md).
