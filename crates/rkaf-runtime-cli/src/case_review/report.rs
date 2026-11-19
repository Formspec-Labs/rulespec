//! Reads and reconciles CSV records and writes portable case reports.
// Rust guideline compliant 2026-02-21

use std::collections::BTreeSet;
use std::fs;
use std::path::Path;

use anyhow::{ensure, Context, Result};
use csv::{ByteRecord, ReaderBuilder, StringRecord, Writer};
use serde::{Deserialize, Serialize};

use crate::policy::{sha256, Outcome, Policy, PolicySelection};

const REPORT_VERSION: u32 = 1;

#[derive(Debug, Deserialize, Serialize)]
#[serde(default, deny_unknown_fields)]
struct Columns {
    case_id: String,
    filing_date: String,
    verification_status: String,
    office: String,
    recorded_rule: String,
    evidence_reference: Option<String>,
}

impl Default for Columns {
    fn default() -> Self {
        Self {
            case_id: "case_id".into(),
            filing_date: "filing_date".into(),
            verification_status: "verification_status".into(),
            office: "office".into(),
            recorded_rule: "recorded_rule".into(),
            evidence_reference: Some("evidence_reference".into()),
        }
    }
}

#[derive(Debug)]
struct ColumnIndices {
    case_id: usize,
    filing_date: usize,
    verification_status: usize,
    office: usize,
    recorded_rule: usize,
    evidence_reference: Option<usize>,
}

impl ColumnIndices {
    fn resolve(columns: &Columns, headers: &StringRecord, explicit_map: bool) -> Result<Self> {
        let mut used = BTreeSet::new();
        let mut find = |name: &str| {
            let matching: Vec<_> = headers
                .iter()
                .enumerate()
                .filter_map(|(index, header)| (header == name).then_some(index))
                .collect();
            ensure!(!name.is_empty(), "Use nonempty column names");
            ensure!(matching.len() <= 1, "CSV header {name:?} is ambiguous");
            let index = matching.first().copied();
            ensure!(
                index.is_none_or(|index| used.insert(index)),
                "CSV header {name:?} was mapped to multiple fields"
            );
            Ok(index)
        };
        let mut required = |name: &str| {
            find(name)?.with_context(|| {
                format!("CSV header {name:?} is missing; use --map to name the input columns")
            })
        };
        let mut result = Self {
            case_id: required(&columns.case_id)?,
            filing_date: required(&columns.filing_date)?,
            verification_status: required(&columns.verification_status)?,
            office: required(&columns.office)?,
            recorded_rule: required(&columns.recorded_rule)?,
            evidence_reference: None,
        };
        if let Some(name) = &columns.evidence_reference {
            result.evidence_reference = find(name)?;
            ensure!(
                result.evidence_reference.is_some()
                    || !explicit_map
                    || name == "evidence_reference",
                "CSV evidence header {name:?} is missing; check the mapping"
            );
        }
        Ok(result)
    }
}

#[derive(Debug, Deserialize, Serialize)]
pub struct CaseRecord {
    pub case_id: String,
    pub filing_date: String,
    pub verification_status: String,
    pub office: String,
    pub recorded_rule: String,
    pub evidence_reference: String,
}

impl CaseRecord {
    fn from_csv(row: &ByteRecord, indices: &ColumnIndices) -> Self {
        let value = |index| {
            row.get(index)
                .and_then(|field| std::str::from_utf8(field).ok())
                .unwrap_or_default()
                .trim()
                .to_owned()
        };
        Self {
            case_id: value(indices.case_id),
            filing_date: value(indices.filing_date),
            verification_status: value(indices.verification_status),
            office: value(indices.office),
            recorded_rule: value(indices.recorded_rule),
            evidence_reference: indices.evidence_reference.map(value).unwrap_or_default(),
        }
    }
}

#[derive(Debug, Default, Deserialize, Serialize)]
struct Disposition {
    status: String,
    note: String,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
enum Comparison {
    Agreement,
    Difference,
    Unresolved,
    HistoricalRuleAbsent,
}

impl Comparison {
    fn for_case(case: &CaseRecord, outcome: &Outcome) -> Self {
        match outcome.expected_id() {
            None => Self::Unresolved,
            Some(_) if case.recorded_rule.is_empty() => Self::HistoricalRuleAbsent,
            Some(selected) if selected == case.recorded_rule => Self::Agreement,
            Some(_) => Self::Difference,
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::Agreement => "agreement",
            Self::Difference => "difference",
            Self::Unresolved => "unresolved",
            Self::HistoricalRuleAbsent => "historical_rule_absent",
        }
    }
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
enum SelectionChange {
    Changed,
    Unchanged,
    PreviouslyUnresolved,
    ProposedUnresolved,
    BothUnresolved,
}

impl SelectionChange {
    fn between(baseline: &Outcome, proposed: &Outcome) -> Self {
        match (baseline.expected_id(), proposed.expected_id()) {
            (Some(before), Some(after)) if before == after => Self::Unchanged,
            (Some(_), Some(_)) => Self::Changed,
            (None, Some(_)) => Self::PreviouslyUnresolved,
            (Some(_), None) => Self::ProposedUnresolved,
            (None, None) => Self::BothUnresolved,
        }
    }

    fn label(self) -> &'static str {
        match self {
            Self::Changed => "changed",
            Self::Unchanged => "unchanged",
            Self::PreviouslyUnresolved => "previously_unresolved",
            Self::ProposedUnresolved => "proposed_unresolved",
            Self::BothUnresolved => "both_unresolved",
        }
    }
}

#[derive(Debug, Deserialize, Serialize)]
pub struct CaseRow {
    record_number: usize,
    case: CaseRecord,
    baseline: Outcome,
    comparison: Comparison,
    proposed: Option<Outcome>,
    proposed_comparison: Option<Comparison>,
    selection_change: Option<SelectionChange>,
    disposition: Disposition,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Report {
    format_version: u32,
    evaluator_version: String,
    input_sha256: String,
    column_mapping: Columns,
    baseline: PolicySelection,
    proposed: Option<PolicySelection>,
    pub rows: Vec<CaseRow>,
}

pub fn compare(
    path: &Path,
    mapping: Option<&Path>,
    baseline: &Policy,
    proposed: Option<&Policy>,
) -> Result<Report> {
    let mut columns = mapping
        .map(|p| {
            let bytes =
                fs::read(p).with_context(|| format!("Read column mapping {}", p.display()))?;
            serde_json::from_slice::<Columns>(&bytes)
                .with_context(|| format!("Parse column mapping {}", p.display()))
        })
        .transpose()?
        .unwrap_or_default();
    let bytes = fs::read(path).with_context(|| format!("Read case CSV {}", path.display()))?;
    let mut csv = ReaderBuilder::new()
        .flexible(true)
        .from_reader(bytes.as_slice());
    let headers = csv.headers().context("Read UTF-8 CSV headers")?;
    let indices = ColumnIndices::resolve(&columns, headers, mapping.is_some())?;
    let expected_columns = headers.len();
    if indices.evidence_reference.is_none() {
        columns.evidence_reference = None;
    }
    let graph = baseline.graph()?;
    let proposed_graph = proposed.map(Policy::graph).transpose()?;
    let mut rows = Vec::new();
    for (index, row) in csv.byte_records().enumerate() {
        let row = row.context("Read CSV record")?;
        let case = CaseRecord::from_csv(&row, &indices);
        let issue = if row.len() != expected_columns {
            Some(format!(
                "Record contains {} columns. The header contains {expected_columns}.",
                row.len()
            ))
        } else if row.iter().any(|field| std::str::from_utf8(field).is_err()) {
            Some("Record contains invalid UTF-8. Export the case CSV as UTF-8.".into())
        } else {
            None
        };
        let baseline = baseline.evaluate(&graph, &case, issue.as_deref());
        let proposed = proposed
            .zip(proposed_graph.as_ref())
            .map(|(policy, graph)| policy.evaluate(graph, &case, issue.as_deref()));
        rows.push(CaseRow {
            record_number: index + 1,
            comparison: Comparison::for_case(&case, &baseline),
            proposed_comparison: proposed
                .as_ref()
                .map(|outcome| Comparison::for_case(&case, outcome)),
            selection_change: proposed
                .as_ref()
                .map(|outcome| SelectionChange::between(&baseline, outcome)),
            case,
            baseline,
            proposed,
            disposition: Disposition::default(),
        });
    }
    Ok(Report {
        format_version: REPORT_VERSION,
        evaluator_version: env!("CARGO_PKG_VERSION").into(),
        input_sha256: sha256(&bytes),
        column_mapping: columns,
        baseline: baseline.selection.clone(),
        proposed: proposed.map(|policy| policy.selection.clone()),
        rows,
    })
}

#[derive(Debug, Default, Serialize)]
struct Reconciliation {
    agreement: usize,
    difference: usize,
    unresolved: usize,
    historical_rule_absent: usize,
}

impl Reconciliation {
    fn count(comparisons: impl Iterator<Item = Comparison>) -> Self {
        let mut totals = Self::default();
        for comparison in comparisons {
            match comparison {
                Comparison::Agreement => totals.agreement += 1,
                Comparison::Difference => totals.difference += 1,
                Comparison::Unresolved => totals.unresolved += 1,
                Comparison::HistoricalRuleAbsent => totals.historical_rule_absent += 1,
            }
        }
        totals
    }
}

#[derive(Debug, Default, Serialize)]
struct Changes {
    changed: usize,
    unchanged: usize,
    previously_unresolved: usize,
    proposed_unresolved: usize,
    both_unresolved: usize,
}

impl Changes {
    fn count(rows: &[CaseRow]) -> Self {
        let mut totals = Self::default();
        for change in rows.iter().filter_map(|row| row.selection_change) {
            match change {
                SelectionChange::Changed => totals.changed += 1,
                SelectionChange::Unchanged => totals.unchanged += 1,
                SelectionChange::PreviouslyUnresolved => totals.previously_unresolved += 1,
                SelectionChange::ProposedUnresolved => totals.proposed_unresolved += 1,
                SelectionChange::BothUnresolved => totals.both_unresolved += 1,
            }
        }
        totals
    }
}

#[derive(Debug, Serialize)]
struct Totals {
    rows: usize,
    baseline: Reconciliation,
    proposed: Option<Reconciliation>,
    selection_changes: Option<Changes>,
}

pub fn write_report(report: &Report, out: &Path) -> Result<()> {
    ensure!(
        report.format_version == REPORT_VERSION,
        "Unsupported report format {}",
        report.format_version
    );
    let has_proposal = report.proposed.is_some();
    let totals = Totals {
        rows: report.rows.len(),
        baseline: Reconciliation::count(report.rows.iter().map(|row| row.comparison)),
        proposed: has_proposal.then(|| {
            Reconciliation::count(report.rows.iter().filter_map(|row| row.proposed_comparison))
        }),
        selection_changes: has_proposal.then(|| Changes::count(&report.rows)),
    };
    let json = serde_json::to_string_pretty(report)?;
    // A case ID or analyst note can contain an HTML parser delimiter.
    let html_data = json
        .replace('&', "\\u0026")
        .replace('<', "\\u003c")
        .replace('>', "\\u003e");
    let html = include_str!("report.html")
        .replace("{{TOTALS}}", &serde_json::to_string(&totals)?)
        .replace("{{REPORT}}", &html_data);
    let mut dir = fs::DirBuilder::new();
    #[cfg(unix)]
    {
        use std::os::unix::fs::DirBuilderExt;
        dir.mode(0o700);
    }
    // Exports always go to a new directory so no input or prior report can be overwritten.
    dir.create(out)
        .context("Choose a new report directory with an existing parent")?;
    let result = (|| {
        fs::write(out.join("report.json"), json)?;
        fs::write(out.join("totals.json"), serde_json::to_vec_pretty(&totals)?)?;
        write_csv(report, &out.join("rows.csv"))?;
        fs::write(out.join("index.html"), html)?;
        Ok(())
    })();
    if result.is_err() {
        // The output directory was created by this run. Remove only its own files.
        for name in ["report.json", "totals.json", "rows.csv", "index.html"] {
            let _ = fs::remove_file(out.join(name));
        }
        let _ = fs::remove_dir(out);
    }
    result
}

fn write_csv(report: &Report, path: &Path) -> Result<()> {
    let mut csv = Writer::from_path(path)?;
    csv.write_record([
        "record_number",
        "case_id",
        "filing_date",
        "verification_status",
        "office",
        "recorded_rule",
        "evidence_reference",
        "expected_rule",
        "date_based_candidate",
        "comparison",
        "reason_code",
        "reason",
        "source_passages_json",
        "office_approval_ids_json",
        "proposed_expected_rule",
        "proposed_date_based_candidate",
        "proposed_comparison",
        "proposed_reason_code",
        "proposed_reason",
        "proposed_source_passages_json",
        "proposed_office_approval_ids_json",
        "selection_change",
        "disposition",
        "disposition_note",
    ])?;
    for row in &report.rows {
        let case = &row.case;
        let proposed = row.proposed.as_ref();
        let passages = serde_json::to_string(&row.baseline.passages)?;
        let approvals = serde_json::to_string(&row.baseline.office_approvals)?;
        let proposed_passages = serde_json::to_string(&proposed.map(|outcome| &outcome.passages))?;
        let proposed_approvals =
            serde_json::to_string(&proposed.map(|outcome| &outcome.office_approvals))?;
        csv.write_record(
            [
                row.record_number.to_string().as_str(),
                &case.case_id,
                &case.filing_date,
                &case.verification_status,
                &case.office,
                &case.recorded_rule,
                &case.evidence_reference,
                row.baseline.expected_id().unwrap_or_default(),
                row.baseline
                    .candidate_rule
                    .as_ref()
                    .map(|rule| rule.id())
                    .unwrap_or_default(),
                row.comparison.label(),
                row.baseline.reason_code.as_deref().unwrap_or_default(),
                row.baseline.reason.as_deref().unwrap_or_default(),
                &passages,
                &approvals,
                proposed.and_then(Outcome::expected_id).unwrap_or_default(),
                proposed
                    .and_then(|outcome| outcome.candidate_rule.as_ref())
                    .map(|rule| rule.id())
                    .unwrap_or_default(),
                row.proposed_comparison
                    .map(Comparison::label)
                    .unwrap_or_default(),
                proposed
                    .and_then(|outcome| outcome.reason_code.as_deref())
                    .unwrap_or_default(),
                proposed
                    .and_then(|outcome| outcome.reason.as_deref())
                    .unwrap_or_default(),
                &proposed_passages,
                &proposed_approvals,
                row.selection_change
                    .map(SelectionChange::label)
                    .unwrap_or_default(),
                &row.disposition.status,
                &row.disposition.note,
            ]
            .into_iter()
            .map(spreadsheet_text),
        )?;
    }
    csv.flush()?;
    Ok(())
}

fn spreadsheet_text(value: &str) -> std::borrow::Cow<'_, [u8]> {
    // Spreadsheet imports can interpret case IDs and notes as formulas.
    if value
        .trim_start_matches(' ')
        .starts_with(['=', '+', '-', '@', '\t', '\r', '\n'])
    {
        format!("'{value}").into_bytes().into()
    } else {
        value.as_bytes().into()
    }
}
