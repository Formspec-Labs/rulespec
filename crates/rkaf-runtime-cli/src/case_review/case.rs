//! Project one saved case into the same review record for people and tools.
// Rust guideline compliant 2026-02-21

use anyhow::{bail, ensure, Context, Result};
use serde::{Deserialize, Serialize};

use crate::evidence::{case_passage, contains_id, valid_case_passage};
use crate::policy::{sha256, Passage};
use crate::report::{CaseRow, Comparison, Report, REPORT_VERSION};

pub const CASE_VIEW: &str = include_str!("case_view.html");
const KIND: &str = "rulespec-case-report-excerpt";
const RECEIPT_PREFIX: &str = "urn:rulespec:filing-receipt:";

#[derive(Debug, Default, Deserialize, Serialize)]
pub struct CaseContext {
    pub filing_event: Option<String>,
    pub time_zone: Option<String>,
}

impl CaseContext {
    pub fn is_empty(&self) -> bool {
        self.filing_event.is_none() && self.time_zone.is_none()
    }
}

#[derive(Debug, Deserialize, Serialize)]
pub struct CaseExcerpt {
    kind: String,
    version: u32,
    case_id: String,
    record_number: usize,
    office: String,
    comparison: String,
    pub explanation: String,
    recorded_rule: Option<String>,
    selected_rule: Option<String>,
    hold_reason: Option<String>,
    next_action: Option<String>,
    filing: Filing,
    policy_sha256: String,
    policy_citations: Vec<Citation>,
    filing_evidence: FilingEvidence,
}

#[derive(Debug, Deserialize, Serialize)]
struct Filing {
    event: String,
    anchor: String,
    reported_local_date: Option<String>,
    verification_status: String,
    time_zone: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
struct Citation {
    role: String,
    source_id: String,
    fragment_id: Option<String>,
    source_sha256: Option<String>,
    excerpt: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct FilingEvidence {
    reference: Option<String>,
    status: EvidenceStatus,
    excerpt: Option<String>,
    excerpt_sha256: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "snake_case")]
enum EvidenceStatus {
    ScopedExcerpt,
    ReferenceOnly,
    NoReference,
}

pub fn select<'a>(
    report: &'a Report,
    case_id: Option<&str>,
    ordinal: Option<usize>,
) -> Result<&'a CaseRow> {
    ensure!(
        report.format_version == REPORT_VERSION,
        "Unsupported saved report format {}",
        report.format_version
    );
    ensure!(
        case_id.is_some() || ordinal.is_some(),
        "Pass --case-id or --record-number"
    );
    let mut matches = report.rows.iter().filter(|row| {
        case_id.is_none_or(|id| row.case.case_id == id)
            && ordinal.is_none_or(|number| row.record_number == number)
    });
    let first = matches.next().context("No matching case record")?;
    if matches.next().is_some() {
        if ordinal.is_some() {
            bail!("The saved report contains a duplicate record number");
        }
        bail!("The case ID is ambiguous. Use --record-number to select one saved row");
    }
    Ok(first)
}

pub fn excerpt(report: &Report, row: &CaseRow) -> CaseExcerpt {
    let case = &row.case;
    let event = report
        .case_context
        .filing_event
        .as_deref()
        .unwrap_or_else(|| match report.baseline.evaluation_anchor.as_str() {
            "rkaf:applicationSubmissionTime" => "application filing",
            _ => report.baseline.evaluation_anchor.as_str(),
        });
    let recorded = optional_field(&case.recorded_rule);
    let selected = row.baseline.expected_id();
    let reference = optional_field(&case.evidence_reference).map(|reference| {
        // Hash an unambiguous tuple. The ordinal distinguishes duplicate cases.
        let key = format!(
            "{}\n{}\n{reference}",
            report.input_sha256, row.record_number
        );
        format!("{RECEIPT_PREFIX}{}", sha256(key.as_bytes()))
    });
    let passage = row.local_evidence.as_ref().and_then(|source| {
        case_passage(
            source,
            &case.evidence_reference,
            &report.evidence_documents,
            &case.case_id,
            report
                .rows
                .iter()
                .map(|other| other.case.case_id.as_str())
                .filter(|id| *id != case.case_id),
        )
    });
    let status = match (&reference, &passage) {
        (_, Some(_)) => EvidenceStatus::ScopedExcerpt,
        (Some(_), None) => EvidenceStatus::ReferenceOnly,
        (None, None) => EvidenceStatus::NoReference,
    };
    let next_action = row.baseline.reason.as_deref().or(match row.comparison {
        Comparison::Agreement => Some("Retain the review with the closed case."),
        Comparison::Difference => Some("Review the recorded rule with the responsible office."),
        Comparison::HistoricalRuleAbsent => Some("Retrieve the rule recorded in the closed case."),
        _ => None,
    });
    let local = optional_field(&case.filing_date);
    let zone = report.case_context.time_zone.as_deref();
    let when = match (local, zone) {
        (Some(date), Some(zone)) => format!(" on {date} in {zone}"),
        (Some(date), None) => format!(" on {date}"),
        (None, _) => String::new(),
    };
    let id = &case.case_id;
    let explanation = match (row.comparison, selected, recorded) {
        (Comparison::Agreement, Some(rule), _) =>
            format!("The verified {event}{when} selects {rule} for {id}, matching the recorded rule."),
        (Comparison::Difference, Some(rule), Some(recorded)) =>
            format!("The verified {event}{when} selects {rule} for {id}, whose recorded rule is {recorded}."),
        (Comparison::HistoricalRuleAbsent, Some(rule), _) =>
            format!("The verified {event}{when} selects {rule} for {id}, and the historical rule is absent."),
        (Comparison::OutsidePolicyScope, _, _) =>
            format!("Refer {id} to {} because its reported office is outside the selected policy's scope.", case.office),
        _ if row.baseline.reason_code.as_deref() == Some("disputed_filing_date") =>
            format!("{id} remains unresolved because records of its {event} conflict."),
        _ if row.baseline.reason_code.as_deref() == Some("missing_verified_filing_evidence") =>
            format!("{id} remains unresolved pending evidence of its {event}."),
        _ => format!("{id} remains unresolved pending review of its {event} and applicable policy."),
    };

    CaseExcerpt {
        kind: KIND.into(),
        version: 1,
        case_id: id.clone(),
        record_number: row.record_number,
        office: case.office.clone(),
        comparison: row.comparison.label().into(),
        explanation,
        recorded_rule: recorded.map(str::to_owned),
        selected_rule: selected.map(str::to_owned),
        hold_reason: row.baseline.reason_code.clone(),
        next_action: next_action.map(str::to_owned),
        filing: Filing {
            event: event.into(),
            anchor: report.baseline.evaluation_anchor.clone(),
            reported_local_date: local.map(str::to_owned),
            verification_status: case.verification_status.clone(),
            time_zone: zone.map(str::to_owned),
        },
        policy_sha256: report.baseline.policy_sha256.clone(),
        policy_citations: citations(report, row),
        filing_evidence: FilingEvidence {
            reference,
            status,
            excerpt_sha256: passage.as_ref().map(|evidence| sha256(evidence.as_bytes())),
            excerpt: passage,
        },
    }
}

fn optional_field(value: &str) -> Option<&str> {
    (!value.trim().is_empty()).then_some(value)
}

fn citations(report: &Report, row: &CaseRow) -> Vec<Citation> {
    fn citation(passage: &Passage, role: &str) -> Citation {
        Citation {
            role: role.into(),
            source_id: passage.artifact.clone(),
            fragment_id: passage.fragment.clone(),
            source_sha256: passage.source_sha256.clone(),
            excerpt: passage
                .exact_quote
                .as_deref()
                .filter(|text| text.len() <= 768)
                .map(str::to_owned),
        }
    }

    if row.baseline.expected_id().is_some() {
        return row
            .baseline
            .passages
            .iter()
            .take(8)
            .map(|p| citation(p, "selected_rule"))
            .collect();
    }
    if matches!(row.comparison, Comparison::OutsidePolicyScope) {
        return report
            .filing_instructions
            .iter()
            .filter(|p| {
                p.exact_quote
                    .as_deref()
                    .is_some_and(|quote| contains_id(quote, &row.case.office))
            })
            .take(8)
            .map(|p| citation(p, "office_scope"))
            .collect();
    }
    if report.baseline.scope.as_deref() == Some(row.case.office.as_str()) {
        return report
            .filing_instructions
            .iter()
            .take(8)
            .map(|p| citation(p, "filing_review_context"))
            .collect();
    }
    Vec::new()
}

pub fn resolve<'a>(record: &'a CaseExcerpt, reference: &str) -> Result<&'a FilingEvidence> {
    ensure!(
        record.kind == KIND && record.version == 1,
        "Use a Rulespec single-case record"
    );
    let evidence = &record.filing_evidence;
    ensure!(
        reference
            .strip_prefix("urn:rulespec:filing-receipt:sha256:")
            .is_some_and(|hex| hex.len() == 64
                && hex
                    .bytes()
                    .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b)))
            && evidence.reference.as_deref() == Some(reference),
        "That receipt reference does not belong to this case record"
    );
    ensure!(
        evidence.excerpt.as_deref().is_none_or(valid_case_passage),
        "Filing evidence exceeds the single-case passage boundary"
    );
    ensure!(
        evidence
            .excerpt
            .as_ref()
            .map(|text| sha256(text.as_bytes()))
            == evidence.excerpt_sha256,
        "Filing evidence excerpt digest differs"
    );
    Ok(evidence)
}

pub fn html_safe(json: &str) -> String {
    json.replace('&', "\\u0026")
        .replace('<', "\\u003c")
        .replace('>', "\\u003e")
}

pub fn html(record: &CaseExcerpt) -> Result<String> {
    Ok(CASE_VIEW.replace(
        "{{CASE_RECORD}}",
        &html_safe(&serde_json::to_string(record)?),
    ))
}
