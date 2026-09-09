# Explicit defaults verified through the live workflow

CLI and library calls now default to **low extraction / medium audit**. Each stage
owns one default used by both entry points. Explicit low/medium/high overrides
remain available; Python `thinking_level=None` still omits the thinking setting.
Output caps, window sizes, schemas and extraction instructions are unchanged.
Reprocessing compares captures against the new defaults while preserving the
original requests and recorded settings.

This implements the [propagation plan](../../../thoughts/plans/2026-09-09-production-propagation.md).
It promotes the operating recommendation, not a demonstrated semantic improvement
against the provider's implicit thinking default. Research and the maintained
[evaluation case index](../evaluation-cases.md) were committed separately in
`beb3fbf`. No deployment or release is included.

## Verification

All **371 package and schema-generator tests passed**; native CUE drift checking
passed. Tests cover CLI omitted options and overrides, public API omitted values
and explicit low/medium/high/None, recorded requests, replay, reprocessing and
changed-metadata refusal. Existing dependency deprecation warnings remain.

Before changing runtime files, all 26 calls across the four preceding experiments
replayed identically without provider calls. Their immutable manifests and raw
captures remain unchanged. For historical replay, use checkout `beb3fbf` with the
recorded dependencies; current-runtime hash drift refusal remains intentional.

The bounded live check reused the 2,536-character passport introduction and omitted
thinking, temperature, window and output-limit flags. All three SDK requests sent
the expected settings and returned STOP, with no retries or numeric thinking budget.

| Stage | Actual thinking | Output cap | Reported total tokens |
|---|---|---:|---:|
| Extraction | low | 16,384 | 5,100 |
| Source inventory | medium | 32,768 | 3,716 |
| Comparison | medium | 32,768 | 24,209 |
| Total | | | 33,025 |

Both stages used one full-source window: extraction's default limit remained
24,000 characters and audit's remained 3,000. This is one reused development
source, not a long-document check, relative-cost comparison or accuracy benchmark.
Provider token counts are not a billed-dollar estimate; unavailable thinking-token
breakdowns are preserved as null in the original responses.

The extraction and audit replay identically with provider creation explicitly
blocked. Discovery export also reproduces exactly, retains all nine source passages
and preserves each statement's `logic_text`. All 81 retained extraction/comparison
evidence spans match their source slices. The graph passes Core and SHACL validation.
See the [verification receipt](verification.json), [preregistered bounds](PLAN.md),
[raw extraction](extraction/attempt-0000.response.json),
[raw inventory](audit/inventory/attempt-0000.response.json) and
[raw comparison](audit/comparison/attempt-0000.response.json).

## Raw source review and remaining failures

The extractor retained 16 statements and rejected no complete statements. It kept
agency approval authorities and exceptions, adjudication sequence, and the two
IN exemptions: no applicant response and no personalization. Posts' authority to
adapt correspondence remains a separate statement with its local-use conditions.
These are agent-reviewed observations on the saved source, not legal approval.

Two qualifications prevent calling this a clean extraction:

- C0012 supplied the non-verbatim modality quote
  `no changes or alterations ... may be made`. The converter correctly withheld
  that component and kept the raw suggestion. The run is **partial**, with one
  component refusal and three unresolved reference records. Two reference records
  are the organizational abbreviation `CA/PPT/S/A`; the third is `8 FAM`. They remain
  source text, not resolved graph targets.
- C0005 says “Posts must use the cleared language in the IRLs.” Its short statement
  omits the local-adaptation qualification, while C0006 retains the corresponding
  authority. Neither has populated `logic_text`, but both retain source evidence.
  The collection preserves the two meanings; standalone consumption can overstate
  the duty. The auditor accepts both without naming that risk.

The audit returned `passed`, with 16 claim and 15 inventory judgments and complete
review accounting. Its rationales generally restate that the claims are accurate;
the cleared-language rationale does not discuss the adjacent authorization. This
is consistent with the previously observed miss, not evidence of its repair.
`semantic_completeness` remains `not_established` and no review approval or repair
was applied. Discovery flags the partial window as needing attention; its zero
fully processed passages does not mean no source was attempted.

Configuration, validation and replay checks passed. A stronger criterion requiring
an entirely complete extraction remains unmet. The bounded check ended after three
calls; these retained issues do not justify another prompt or schema patch here.

## Reproduce offline

From the repository root at this runtime, use new output directories:

```sh
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python -m rulespec_extrapolator.cli replay \
  examples/document_understanding/production-defaults-check/extraction --output /tmp/rulespec-defaults-extraction-replay
PYTHONDONTWRITEBYTECODE=1 .tools/document-poc-venv/bin/python -m rulespec_extrapolator.cli audit-replay \
  examples/document_understanding/production-defaults-check/audit --output /tmp/rulespec-defaults-audit-replay
```

The live commands used `extract source.json` and then `audit extraction/rulebook.json`
with only the required new output path and the authorized local `--env-file`.
Actual model requests, runtime sources, source hash and failures are saved; credentials
are excluded. Do not rerun live calls over these saved directories.
