//! Checks the case evaluator's office approval requirement.
// Rust guideline compliant 2026-02-21

use std::path::Path;

use serde_json::json;

use super::{CaseRecord, Policy, PolicyOverrides};

#[test]
fn a_rule_with_general_official_use_still_needs_a_named_current_office_grant() {
    let fixture = Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../fixtures/behavior/point-in-time-filing-date.jsonld");
    let mut policy = Policy::read(
        &fixture,
        None,
        &PolicyOverrides {
            subject: None,
            anchor: None,
            consumer: None,
            as_of: Some("2026-11-18T12:00:00Z"),
        },
    )
    .unwrap();
    let mut case = CaseRecord {
        case_id: "SAMPLE-22".into(),
        filing_date: "2017-03-22".into(),
        verification_status: "verified".into(),
        office: "urn:rulespec:example:office".into(),
        recorded_rule: "urn:rulespec:example:medical-opinions:prior".into(),
        evidence_reference: String::new(),
    };
    let nodes = policy.payload["@graph"].as_array_mut().unwrap();
    for node in nodes {
        if node["@type"] == "rkaf:Assertion" {
            node["rkaf:usageEligibility"] = json!("rkaf:officialUse");
        }
    }
    let evaluate =
        |policy: &Policy, case: &CaseRecord| policy.evaluate(&policy.graph().unwrap(), case, None);
    let approved = evaluate(&policy, &case);
    assert_eq!(approved.expected_id(), Some(case.recorded_rule.as_str()));
    assert_eq!(
        approved.office_approvals,
        ["urn:rulespec:example:prior-approval"]
    );

    let check_held = |policy: &Policy, case: &CaseRecord| {
        let outcome = evaluate(policy, case);
        assert_eq!(
            outcome.reason_code.as_deref(),
            Some("office_approval_unavailable")
        );
        assert!(outcome.expected_id().is_none());
        assert!(outcome.office_approvals.is_empty());
        assert_eq!(outcome.candidate_rule.unwrap().id, case.recorded_rule);
    };
    case.office = "office-with-no-grant".into();
    check_held(&policy, &case);

    case.office = "urn:rulespec:example:office".into();
    let grant_index = policy.payload["@graph"]
        .as_array()
        .unwrap()
        .iter()
        .position(|node| node["@id"] == "urn:rulespec:example:prior-approval")
        .unwrap();
    policy.payload["@graph"][grant_index]["rkaf:validUntil"] = json!("2026-11-18T12:00:00Z");
    check_held(&policy, &case);

    let grant = policy.payload["@graph"][grant_index]
        .as_object_mut()
        .unwrap();
    grant.remove("rkaf:validUntil");
    grant.remove("@id");
    check_held(&policy, &case);
}
