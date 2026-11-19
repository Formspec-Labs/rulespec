# Rulespec case evaluator

Compare the rule version recorded in a closed case with the version Rulespec selects from its verified filing date. The report covers rule-version selection. A program reviewer makes the benefit decision.

## Run the three example cases

Download the versioned archive for your operating system and CPU architecture. The bundle runs offline. You need a terminal, `tar`, and a browser with JavaScript enabled for the interactive report. On Linux, run the archive on a system compatible with the build host's GNU C library. The archive contains the native Rulespec evaluator and runs without Rust, Python, a service account, or a case system.

Extract the archive in a directory you can write to. Use the actual versioned filename for your platform.

```sh
tar -xzf rulespec-case-evaluator-VERSION-PLATFORM-gREVISION.tar.gz
cd rulespec-case-evaluator-VERSION-PLATFORM-gREVISION
bin/rulespec-case-review compare \
  --policy fixtures/behavior/point-in-time-filing-date.jsonld \
  --as-of 2026-11-18T12:00:00Z \
  --cases examples/case-date/cases.csv \
  --out example-report
```

Open `example-report/index.html` in your browser. Expand a case, then select **Open cited passage** to read the excerpt offline or follow the publisher link. The office approval, filing receipts, case IDs, and recorded rules in this example are illustrative. The cited federal regulation is real.

| Sample filing | Rulespec selection | Comparison |
| --- | --- | --- |
| March 22, 2017 | 20 CFR § 404.1527 | Agreement |
| March 27, 2017 | 20 CFR § 404.1520c | Difference |
| Disputed date | Resolve the filing date against the original evidence | Unresolved |

The exact archived source files ship in `examples/case-date/sources/`. Use `shasum -a 256 -c SHA256SUMS` on macOS or `sha256sum -c SHA256SUMS` on Linux from that directory to verify them. The original versions and cited excerpts are also available from the publishers. [Archived § 404.1527 (GovInfo)](https://www.govinfo.gov/content/pkg/CFR-2018-title20-vol2/xml/CFR-2018-title20-vol2-sec404-1527.xml) · [Archived § 404.1520c (GovInfo)](https://www.govinfo.gov/content/pkg/CFR-2018-title20-vol2/xml/CFR-2018-title20-vol2-sec404-1520c.xml) · [§ 404.1527 (SSA)](https://www.ssa.gov/OP_Home/cfr20/404/404-1527.htm) · [§ 404.1520c (SSA)](https://www.ssa.gov/OP_Home/cfr20/404/404-1520c.htm)

## Compare a local CSV

Start with the exact Rulespec policy graph and selection JSON approved by the policy owner.

Include supporting source fragments and SHA-256 artifact pins in the policy graph. The comparison reads the graph citations and displays excerpts when the graph includes exact quoted text. The comparison takes the graph and selection file as policy inputs. Retain the original source files with the approved policy package and verify their bytes against the graph's pins separately.

```sh
bin/rulespec-case-review compare \
  --policy /path/to/policy.jsonld --selection /path/to/selection.json \
  --cases /path/to/cases.csv --out my-report
```

The selection file contains `subjectAssertion`, `evaluationAnchor`, `evaluationConsumer` (consumer registration ID), `scope` (office ID), `evaluatedAt` (RFC 3339 timestamp), and `policySha256` (SHA-256 of the exact policy file). An explicit comparison can supply `--subject`, `--anchor`, `--consumer`, and `--as-of`. Explicit options take precedence over corresponding selection settings. Rulespec checks the office from each record against its approved use for the selected rule. A selection file with an office scope limits comparison to that office. A policy can declare its earliest covered filing date. A bounded office approval applies from adoption up to its expiry, which the evaluator checks at the supplied review time.

Use these CSV headers or supply `--map column-map.json`.

| Field | Value |
| --- | --- |
| `case_id` | De-identified case identifier |
| `filing_date` | Calendar date in `YYYY-MM-DD` format |
| `verification_status` | `verified`, `disputed`, `conflicting`, `missing`, or `unverified` |
| `office` | Office ID used in the policy graph |
| `recorded_rule` | Exact assertion ID for the recorded rule. Leave blank when the historical rule is unavailable. |
| `evidence_reference` | Optional receipt or filing-record reference |

A mapping file uses the known field names as keys and exact CSV header names as values. For example, `{"case_id":"Case Number","filing_date":"Filing Date","evidence_reference":"Receipt ID"}` maps those three fields and keeps the default headers for the others. Use `null` for an unused evidence reference.

Rulespec uses the CSV's verification status as the program's report of whether the date was verified. Retain the original records separately and obtain a missing filing evidence reference before confirming a finding. A disputed, conflicting, or unverified filing date, invalid record, or unavailable office approval remains unresolved. Cases from another office count separately when the policy selection names an office. Blank separators in a CSV are skipped. Each parsed record has its own record number, including records that share a case ID.

Add `--evidence-dir /path/to/curated-evidence` to review local evidence offline. A reference such as `receipts/filing-records.md#fr-09` uses a path relative to that directory. Path and anchor components use letters, numbers, periods, underscores, or hyphens. The report accepts UTF-8 Markdown and text files. It finds a passage using an explicit anchor on its own line or a Markdown heading with spaces converted to hyphens. Other references display as text.

The report copies only referenced files, stores one exact copy per SHA-256 hash, and displays excerpts as plain text. The downloadable report JSON includes the source copies. Export verifies their hashes and writes the copies with the new report directory.

To assess a proposed version, add `--proposed candidate.jsonld --proposed-selection candidate-selection.json`. The report retains the baseline selection, proposed selection, and recorded rule for each case. A change to either version of the policy requires a new report directory.

## Save dispositions and export

Open a case in `index.html`, choose an analyst disposition, and add a note. Select **Download report JSON** to save your edits. Generate the detailed CSV, updated interactive report, and reconciled totals in a new directory.

```sh
bin/rulespec-case-review export --report /path/to/rulespec-report.json --out reviewed-report
```

The CSV protects formula-like text for spreadsheet viewing. Use `report.json` for exact field values, policy hashes, source references, and the review settings. Keep report files local and use de-identified data.
