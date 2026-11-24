//! Reads and reconciles CSV records and writes portable case reports.
// Rust guideline compliant 2026-02-21

use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::Path;

use anyhow::{ensure, Context, Result};
use csv::{ByteRecord, ReaderBuilder, StringRecord, Writer};
use serde::{Deserialize, Serialize};

use crate::case::{self, CaseContext};
use crate::evidence::{self, Documents, EvidenceDirectory, LocalEvidence};
use crate::policy::{sha256, Outcome, Passage, Policy, PolicySelection};

pub const REPORT_VERSION: u32 = 1;

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
                index.map_or(true, |index| used.insert(index)),
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
        let raw = |index| {
            row.get(index)
                .and_then(|field| std::str::from_utf8(field).ok())
                .unwrap_or_default()
        };
        let value = |index| raw(index).trim().to_owned();
        Self {
            case_id: value(indices.case_id),
            filing_date: value(indices.filing_date),
            verification_status: raw(indices.verification_status).to_owned(),
            office: value(indices.office),
            recorded_rule: value(indices.recorded_rule),
            evidence_reference: indices
                .evidence_reference
                .map(raw)
                .unwrap_or_default()
                .to_owned(),
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
pub enum Comparison {
    Agreement,
    Difference,
    Unresolved,
    HistoricalRuleAbsent,
    OutsidePolicyScope,
}

impl Comparison {
    fn for_case(case: &CaseRecord, outcome: &Outcome) -> Self {
        if outcome.reason_code.as_deref() == Some("office_outside_policy_scope") {
            return Self::OutsidePolicyScope;
        }
        match outcome.expected_id() {
            None => Self::Unresolved,
            Some(_) if case.recorded_rule.is_empty() => Self::HistoricalRuleAbsent,
            Some(selected) if selected == case.recorded_rule => Self::Agreement,
            Some(_) => Self::Difference,
        }
    }

    pub fn label(self) -> &'static str {
        match self {
            Self::Agreement => "agreement",
            Self::Difference => "difference",
            Self::Unresolved => "unresolved",
            Self::HistoricalRuleAbsent => "historical_rule_absent",
            Self::OutsidePolicyScope => "outside_policy_scope",
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
    pub record_number: usize,
    pub case: CaseRecord,
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub local_evidence: Option<LocalEvidence>,
    pub baseline: Outcome,
    pub comparison: Comparison,
    proposed: Option<Outcome>,
    proposed_comparison: Option<Comparison>,
    selection_change: Option<SelectionChange>,
    disposition: Disposition,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Report {
    pub format_version: u32,
    evaluator_version: String,
    pub input_sha256: String,
    column_mapping: Columns,
    pub baseline: PolicySelection,
    proposed: Option<PolicySelection>,
    pub rows: Vec<CaseRow>,
    #[serde(default, skip_serializing_if = "CaseContext::is_empty")]
    pub case_context: CaseContext,
    #[serde(default, skip_serializing_if = "Vec::is_empty")]
    pub filing_instructions: Vec<Passage>,
    #[serde(default, skip_serializing_if = "Documents::is_empty")]
    pub evidence_documents: Documents,
}

pub fn compare(
    path: &Path,
    mapping: Option<&Path>,
    evidence_dir: Option<&Path>,
    baseline: &Policy,
    proposed: Option<&Policy>,
    case_context: CaseContext,
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
    let mut evidence = evidence_dir.map(EvidenceDirectory::open).transpose()?;
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
        let local_evidence = evidence
            .as_mut()
            .filter(|_| issue.is_none())
            .and_then(|directory| directory.resolve(&case.evidence_reference));
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
            local_evidence,
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
        case_context,
        filing_instructions: baseline.filing_instructions(&graph),
        evidence_documents: evidence
            .map(|directory| directory.documents)
            .unwrap_or_default(),
    })
}

#[derive(Debug, Default, Serialize)]
struct Reconciliation {
    agreement: usize,
    difference: usize,
    unresolved: usize,
    historical_rule_absent: usize,
    outside_policy_scope: usize,
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
                Comparison::OutsidePolicyScope => totals.outside_policy_scope += 1,
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

impl Report {
    pub(super) fn reconcile(&mut self) -> Result<()> {
        ensure!(
            self.format_version == REPORT_VERSION,
            "Unsupported report format {}",
            self.format_version
        );
        evidence::validate(&self.evidence_documents)?;
        let mut sources = BTreeMap::new();
        for row in &mut self.rows {
            let proposed = row.proposed.as_ref();
            ensure!(
                self.proposed.is_some() == proposed.is_some(),
                "Record {} and the report disagree about the presence of a proposed policy",
                row.record_number
            );
            row.comparison = Comparison::for_case(&row.case, &row.baseline);
            row.proposed_comparison =
                proposed.map(|outcome| Comparison::for_case(&row.case, outcome));
            row.selection_change =
                proposed.map(|outcome| SelectionChange::between(&row.baseline, outcome));
            if let Some(source) = &mut row.local_evidence {
                source
                    .restore_passage(&row.case.evidence_reference, &self.evidence_documents)
                    .with_context(|| {
                        format!("Read filing evidence for record {}", row.record_number)
                    })?;
                if let Some(previous) = sources.insert(source.path.as_str(), source.sha256.as_str())
                {
                    ensure!(
                        previous == source.sha256,
                        "Record {} assigns a different digest to the same filing evidence path",
                        row.record_number
                    );
                }
            }
        }
        let cited = sources.into_values().collect::<BTreeSet<_>>();
        ensure!(
            cited.len() == self.evidence_documents.len(),
            "The report contains uncited filing evidence"
        );
        Ok(())
    }
}

pub fn write_report(report: &mut Report, out: &Path) -> Result<()> {
    report.reconcile()?;
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
    let cases = report
        .rows
        .iter()
        .map(|row| case::excerpt(report, row))
        .collect::<Vec<_>>();
    let html = report_html(
        &json,
        &serde_json::to_string(&totals)?,
        &serde_json::to_string(&cases)?,
    )?;
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
        evidence::write_copies(&report.evidence_documents, out)?;
        fs::write(out.join("index.html"), html)?;
        Ok(())
    })();
    if result.is_err() {
        // The output directory was created by this run. Remove only its own files.
        for name in ["report.json", "totals.json", "rows.csv", "index.html"] {
            let _ = fs::remove_file(out.join(name));
        }
        for digest in report.evidence_documents.keys() {
            let _ = fs::remove_file(out.join(evidence::copy_path(digest)));
        }
        let _ = fs::remove_dir(out.join("evidence"));
        let _ = fs::remove_dir(out);
    }
    result
}

fn report_html(report: &str, totals: &str, cases: &str) -> Result<String> {
    let view = serde_json::to_string(case::CASE_VIEW)?;
    let mut template = include_str!("report.html");
    let mut html = String::with_capacity(template.len() + report.len() + cases.len() + view.len());
    // Only the remaining template contains slots. Inserted case text is always literal.
    for (marker, json) in [
        ("{{REPORT}}", report),
        ("{{TOTALS}}", totals),
        ("{{CASE_RECORDS}}", cases),
        ("{{CASE_VIEW}}", view.as_str()),
    ] {
        let (prefix, rest) = template
            .split_once(marker)
            .with_context(|| format!("Missing {marker} in batch report template"))?;
        html.push_str(prefix);
        html.push_str(&case::html_safe(json));
        template = rest;
    }
    html.push_str(template);
    Ok(html)
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
        "filing_evidence_sha256",
        "filing_evidence_copy",
        "filing_evidence_anchor",
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
        let local = row.local_evidence.as_ref();
        let evidence_path = local.map(|evidence| evidence::copy_path(&evidence.sha256));
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
                local
                    .map(|evidence| evidence.sha256.as_str())
                    .unwrap_or_default(),
                evidence_path.as_deref().unwrap_or_default(),
                local
                    .and_then(|evidence| evidence.anchor.as_deref())
                    .unwrap_or_default(),
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

#[cfg(test)]
mod tests {
    use super::*;
    use crate::policy::PolicyOverrides;

    #[test]
    fn embedded_case_text_preserves_literal_template_markers() -> Result<()> {
        let data = r#"["{{REPORT}}", "{{TOTALS}}", "{{CASE_RECORDS}}", "{{CASE_VIEW}}"]"#;
        let page = report_html(data, "{}", data)?;
        for id in ["report-data", "case-records"] {
            let marker = format!("id=\"{id}\">");
            let (_, body) = page.split_once(&marker).unwrap();
            assert_eq!(body.split_once("</script>").unwrap().0, data);
        }
        Ok(())
    }

    fn example_report() -> Result<Report> {
        let repo = Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        let policy = Policy::read(
            &repo.join("fixtures/behavior/point-in-time-filing-date.jsonld"),
            None,
            &PolicyOverrides {
                subject: None,
                anchor: None,
                consumer: None,
                as_of: Some("2026-11-18T12:00:00Z"),
            },
        )?;
        compare(
            &repo.join("examples/case-date/cases.csv"),
            None,
            None,
            &policy,
            Some(&policy),
            CaseContext::default(),
        )
    }

    #[test]
    fn reconciles_saved_findings_from_the_case_and_both_policy_results() -> Result<()> {
        let mut report = example_report()?;
        let row = &mut report.rows[0];
        row.comparison = Comparison::Difference;
        row.proposed_comparison = Some(Comparison::HistoricalRuleAbsent);
        row.selection_change = Some(SelectionChange::Changed);
        row.disposition.status = "reviewed".into();
        row.disposition.note = "Checked the receipt".into();

        // Earlier version-1 reports counted an outside-office case as unresolved.
        report.rows[1].baseline = Outcome::default();
        report.rows[1]
            .baseline
            .unresolved("office_outside_policy_scope", "Other office");
        report.rows[1].comparison = Comparison::Unresolved;
        report.rows[2].comparison = Comparison::Agreement;
        report.reconcile()?;

        let row = &report.rows[0];
        assert_eq!(row.comparison.label(), "agreement");
        assert_eq!(row.proposed_comparison.unwrap().label(), "agreement");
        assert_eq!(row.selection_change.unwrap().label(), "unchanged");
        assert_eq!(row.disposition.status, "reviewed");
        assert_eq!(row.disposition.note, "Checked the receipt");
        assert_eq!(report.rows[1].comparison.label(), "outside_policy_scope");
        assert_eq!(
            report.rows[1].selection_change.unwrap().label(),
            "previously_unresolved"
        );
        assert_eq!(report.rows[2].comparison.label(), "unresolved");
        Ok(())
    }

    #[test]
    fn requires_the_declared_proposal_for_each_row_and_allows_an_empty_batch() -> Result<()> {
        let mut report = example_report()?;
        report.rows[2].proposed = None;
        assert!(report.reconcile().is_err());
        report.rows.clear();
        report.reconcile()?;
        report = example_report()?;
        report.proposed = None;
        assert!(report.reconcile().is_err());
        for row in &mut report.rows {
            row.proposed = None;
        }
        report.reconcile()?;
        assert!(report
            .rows
            .iter()
            .all(|row| row.proposed_comparison.is_none() && row.selection_change.is_none()));
        Ok(())
    }

    #[test]
    fn restores_anchored_evidence_only_from_the_referenced_retained_copy() -> Result<()> {
        let mut report = example_report()?;
        let text = "## Earlier\nOther case\n## Receipt\nSAMPLE-22 filed on March 22.";
        let digest = sha256(text.as_bytes());
        report
            .evidence_documents
            .insert(digest.clone(), text.into());
        let row = &mut report.rows[0];
        row.case.evidence_reference = "filings.md#receipt".into();
        row.local_evidence = Some(LocalEvidence {
            path: "filings.md".into(),
            sha256: digest.clone(),
            anchor: Some("receipt".into()),
            passage: Some("stale text".into()),
        });
        report.reconcile()?;
        assert_eq!(
            report.rows[0]
                .local_evidence
                .as_ref()
                .unwrap()
                .passage
                .as_deref(),
            Some("## Receipt\nSAMPLE-22 filed on March 22.")
        );
        for reference in [
            "filings.md#earlier",
            "other.md#receipt",
            "../filings.md#receipt",
        ] {
            report.rows[0].case.evidence_reference = reference.into();
            assert!(report.reconcile().is_err(), "{reference}");
        }
        report.rows[0].case.evidence_reference = "filings.md".into();
        report.rows[0].local_evidence.as_mut().unwrap().anchor = None;
        report.reconcile()?;
        assert!(report.rows[0]
            .local_evidence
            .as_ref()
            .unwrap()
            .passage
            .is_none());
        report
            .evidence_documents
            .insert(digest, "different bytes".into());
        assert!(report.reconcile().is_err());
        Ok(())
    }
}
