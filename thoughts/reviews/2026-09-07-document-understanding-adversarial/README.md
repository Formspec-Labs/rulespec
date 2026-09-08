# Blind adversarial review of document extraction

Status: three independent reviews completed, 2026-09-07. Start with the
[consolidated findings](FINDINGS.md). This pass reviews the implementation
and recorded results at `main` / `eac3ab8`, including the local uncommitted
document-understanding application. It makes no production changes or model calls.

## Protocol

Three fresh agents receive no conversation history or prior review reports.
Their work uses isolated copies of the relevant source, recorded model data,
application code, and tests. The [packet manifest](packet-manifest.json) records
the supplied files and their hashes. Isolation here means a controlled reading
protocol in a shared workspace, not a filesystem access-control boundary.

1. The photograph reviewer inventories the exact input before seeing output.
2. The name-change reviewer independently inventories both overlapping inputs
   before seeing four model outputs and the correction case.
3. The workflow reviewer examines code and tests for concrete failures in
   extraction, review, links, and evaluation. Existing test expectations are
   evidence to challenge; they are not independent semantic labels.

The two source inventories are frozen by hash before output is supplied. Their
authors must distinguish selected model input from additional source context.
The correction case preserves candidate content and evidence but removes prior
review rationales, which would disclose the earlier assessment.

Agents are instructed to record outside-packet access and avoid memories,
previous findings, production evaluation labels, and one another's conclusions.
The workflow packet includes the existing development-label fixture needed to
understand its tests; that reviewer is blind to prior output assessments, not to
the test expectations under review.

The integrator has prior context and is **not blind**. The integrator releases
outputs after inventory sealing, verifies candidate findings, reconciles overlap,
and records limitations. Findings distinguish model errors, application
errors, correction-case errors, test gaps, and explicitly unsupported behavior.

## Saved deliverables

- [Photograph review](photos-review.md), [complete claim/unit audit and 15 proposed
  regressions](photos-coverage-claim-audit.json), [sealed inventory](photos-source-inventory.json),
  and [output-release receipt](photos-output-release.json).
- [Name-change review](names-review.md), [complete claim/unit/correction audit](names-coverage.json),
  [15 proposed regressions](names-adversarial-regressions.json),
  [sealed inventory](names-source-inventory.json), and
  [output-release receipt](names-output-release.json).
- [Workflow review](workflows-review.md), with executable offline probes,
  recovery observations, and output from 91 passing selected existing tests.
- [Integrator review](integrator-review.md), including the separate nested-section
  defect and reruns of the workflow reviewer's two confirmed defects.
- [Packet verification](packet-verification.json) and
  [audit accounting verification](audit-verification.json). The checks cover all
  121 raw candidates, 120 accepted claims and 12 current correction-case claims.

The photograph reviewer disclosed an actor-descriptor mistake after sealing:
two source instructions imply an addressee but do not literally contain `you`.
The [separate erratum](photos-inventory-erratum.json) preserves the original
inventory and records the correction after output access. It is not counted as
an extraction error. The name-change inventory needed no erratum.

The reviewed source copies, released outputs and bulk probe captures remain
under `.tools/blind-review-20260907/`. All reports and concise evidence above
remain in this repository folder. The 30 semantic regression cases are proposed
tests; the probes were executed. No production tests or runtime files were
changed by this review.

All reviewers are AI agents. This pass does not establish expert legal review,
human usability, or a calibrated accuracy estimate.
