//! Integration test: every fixture in `fixtures/behavior/` runs through
//! `Runtime::evaluate_and_check` and MUST match its declared
//! `rkaf:expectedOutput`. This is the L4 conformance gate.

// Rust guideline compliant 2026-02-21

use rkaf_runtime::{Runtime, RuntimeError};
use serde_json::Value;
use std::fs;
use std::path::PathBuf;

fn behavior_dir() -> PathBuf {
    let mut p = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    p.push("../../fixtures/behavior");
    p
}

fn load(name: &str) -> Value {
    let mut p = behavior_dir();
    p.push(format!("{name}.jsonld"));
    let bytes = fs::read(&p).unwrap_or_else(|e| panic!("read {}: {e}", p.display()));
    serde_json::from_slice(&bytes).expect("parse jsonld")
}

fn load_path(path: &PathBuf) -> Value {
    let bytes = fs::read(path).unwrap_or_else(|e| panic!("read {}: {e}", path.display()));
    serde_json::from_slice(&bytes).unwrap_or_else(|e| panic!("parse {}: {e}", path.display()))
}

fn behavior_fixture_paths() -> Vec<PathBuf> {
    let mut paths: Vec<PathBuf> = fs::read_dir(behavior_dir())
        .expect("read behavior fixture dir")
        .map(|entry| entry.expect("read behavior fixture entry").path())
        .filter(|path| path.extension().and_then(|s| s.to_str()) == Some("jsonld"))
        .collect();
    paths.sort();
    paths
}

fn assert_passes(name: &str) {
    let tc = load(name);
    assert_value_passes(name, &tc);
}

fn assert_path_passes(path: &PathBuf) {
    let tc = load_path(path);
    let name = path
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("<unknown>");
    assert_value_passes(name, &tc);
}

fn assert_value_passes(name: &str, tc: &Value) {
    // Plan 7e.3 — a fixture MAY declare `rkaf:expectedRuntimeError` to assert
    // the runtime raises a specific structural error (e.g. MalformedTestCase
    // on a dangling IRI). When present, evaluate_and_check MUST error with a
    // matching variant; an Ok verdict is a failure.
    let expected_err = tc.get("rkaf:expectedRuntimeError").and_then(Value::as_str);
    match (Runtime::evaluate_and_check(&tc), expected_err) {
        (Ok(_), None) => {}
        (Ok(_), Some(want)) => {
            panic!("fixture {name} expected runtime error {want:?} but got Ok verdict")
        }
        // OutputMismatch precedence is deliberate: a fixture declaring
        // `rkaf:expectedRuntimeError = "rkaf:OutputMismatch"` is therefore
        // unreachable. OutputMismatch is always treated as an unexpected
        // runtime surprise — fixtures use `rkaf:expectedOutput` for the
        // success path; there is no use case for asserting a mismatch.
        (Err(RuntimeError::OutputMismatch { expected, actual }), _) => {
            panic!(
                "fixture {name} OutputMismatch:\n  expected: {}\n  actual:   {}",
                serde_json::to_string_pretty(&expected).unwrap(),
                serde_json::to_string_pretty(&actual).unwrap()
            );
        }
        (Err(other), Some(want)) => {
            let actual_tag = other.iri_tag();
            assert_eq!(
                actual_tag, want,
                "fixture {name} expected runtime error {want:?}, got {actual_tag:?}: {other}"
            );
        }
        (Err(other), None) => panic!("fixture {name} runtime error: {other}"),
    }
}

#[test]
fn all_behavior_fixtures_pass() {
    let paths = behavior_fixture_paths();
    assert!(
        !paths.is_empty(),
        "fixtures/behavior must contain L4 behavior fixtures"
    );
    for path in paths {
        assert_path_passes(&path);
    }
}

// ─── CascadeClosureV1 ───────────────────────────────────────────────────

#[test]
fn cascade_closure_supersession_fanout() {
    assert_passes("cascade-closure-supersession-fanout");
}

#[test]
fn cascade_all_edge_predicates() {
    assert_passes("cascade-closure-all-edge-predicates");
}

// ─── UsageEligibility reducer ──────────────────────────────────────────

#[test]
fn usage_eligibility_reducer_baseline_workspace() {
    assert_passes("usage-eligibility-reducer-baseline-workspace-positive");
}

#[test]
fn usage_eligibility_reducer_stale_narrows() {
    assert_passes("usage-eligibility-reducer-stale-narrows");
}

#[test]
fn usage_eligibility_reducer_local_broadens_in_scope() {
    assert_passes("usage-eligibility-reducer-local-broadens-in-scope");
}

#[test]
fn usage_eligibility_reducer_requires_an_assertion_as_its_subject() {
    let mut request = load("usage-eligibility-reducer-local-broadens-in-scope");
    assert_eq!(
        Runtime::evaluate(&request).unwrap().output,
        request["rkaf:expectedOutput"]
    );
    request["rkaf:subjectAssertion"] = Value::from("la1");
    assert!(matches!(
        Runtime::evaluate(&request),
        Err(RuntimeError::MalformedTestCase(message))
            if message.contains("la1") && message.contains("Assertion")
    ));
}

// ─── PointInTimeException ──────────────────────────────────────────────

#[test]
fn point_in_time_exception_honored() {
    assert_passes("point-in-time-exception-honored");
}

// ─── ConceptResolutionWithConflict ─────────────────────────────────────

#[test]
fn concept_resolution_mapping_conflict() {
    assert_passes("concept-resolution-mapping-conflict");
}

#[test]
fn concept_resolution_resolved() {
    assert_passes("concept-resolution-resolved-positive");
}

#[test]
fn concept_resolution_unresolved() {
    assert_passes("concept-resolution-unresolved-positive");
}

// ─── Bridge contract rules — all 10 ────────────────────────────────────

#[test]
fn bridge_rule_1_positive() {
    assert_passes("bridge-rule-1-legal-with-authority-positive");
}
#[test]
fn bridge_rule_1_negative() {
    assert_passes("bridge-rule-1-legal-without-authority-negative");
}
#[test]
fn bridge_rule_2_positive() {
    assert_passes("bridge-rule-2-declared-equals-reducer-positive");
}
#[test]
fn bridge_rule_2_negative() {
    assert_passes("bridge-rule-2-declared-broadens-without-adoption-negative");
}
#[test]
fn bridge_rule_3_positive() {
    assert_passes("bridge-rule-3-chain-terminus-kind-matches-positive");
}
#[test]
fn bridge_rule_3_negative() {
    assert_passes("bridge-rule-3-chain-terminus-kind-mismatch-negative");
}
#[test]
fn bridge_rule_4_positive() {
    assert_passes("bridge-rule-4-supported-anchor-positive");
}
#[test]
fn bridge_rule_4_negative() {
    assert_passes("bridge-rule-4-unsupported-anchor-negative");
}

#[test]
fn bridge_rule_4_checks_anchor_support_for_the_selected_registration() {
    use serde_json::json;

    let mut request = load("bridge-rule-4-unsupported-anchor-negative");
    let nodes = request["rkaf:input"]["@graph"].as_array_mut().unwrap();
    let mut alternate = nodes[2].clone();
    alternate["@id"] = json!("reg2");
    alternate["rkaf:consumer"] = json!("urn:example:alternate-consumer");
    alternate["rkaf:supportedEvaluationAnchors"] = json!(["rkaf:eligibilityDeterminationTime"]);
    nodes.push(alternate);

    request["rkaf:evaluationConsumer"] = json!("reg1");
    let unsupported = Runtime::evaluate(&request).unwrap().output;
    assert_eq!(unsupported["bridgeValidationResult"], "rkaf:rejected");
    assert_eq!(unsupported["errorClass"], "rkaf:UnsupportedEvaluationAnchor");

    request["rkaf:evaluationConsumer"] = json!("reg2");
    assert_eq!(
        Runtime::evaluate(&request).unwrap().output["bridgeValidationResult"],
        "rkaf:accepted"
    );
}
#[test]
fn bridge_rule_5_positive() {
    assert_passes("bridge-rule-5-stale-transition-set-positive");
}
#[test]
fn bridge_rule_5_safe_automatic_migration_positive() {
    assert_passes("bridge-rule-5-safe-automatic-migration-positive");
}
#[test]
fn bridge_rule_5_negative() {
    assert_passes("bridge-rule-5-stale-not-transitioned-negative");
}
#[test]
fn bridge_rule_6_positive() {
    assert_passes("bridge-rule-6-no-concept-in-authority-positive");
}
#[test]
fn bridge_rule_6_negative() {
    assert_passes("bridge-rule-6-concept-in-authority-negative");
}
#[test]
fn bridge_rule_7_negative() {
    assert_passes("bridge-rule-7-justification-orphan");
}
#[test]
fn bridge_rule_8_positive() {
    assert_passes("bridge-rule-8-issue-with-attestation-positive");
}
#[test]
fn bridge_rule_8_negative() {
    assert_passes("bridge-rule-8-issue-without-attestation-negative");
}
// Plan 7e — effectiveness + targetFinding refinements of rule_8.
#[test]
fn bridge_rule_8_attestation_revoked() {
    assert_passes("bridge-rule-8-attestation-revoked-negative");
}
#[test]
fn bridge_rule_8_attestation_out_of_period() {
    assert_passes("bridge-rule-8-attestation-out-of-period-negative");
}
#[test]
fn bridge_rule_8_targeted_finding() {
    assert_passes("bridge-rule-8-targeted-finding-positive");
}
#[test]
fn bridge_rule_9_positive() {
    assert_passes("bridge-rule-9-version-in-range-positive");
}
#[test]
fn bridge_rule_9_negative() {
    assert_passes("bridge-rule-9-version-out-of-range-negative");
}
#[test]
fn bridge_rule_10_positive() {
    assert_passes("bridge-rule-10-gwp-with-terminating-justification-positive");
}
#[test]
fn bridge_rule_10_negative() {
    assert_passes("bridge-rule-10-gwp-missing-justification-negative");
}

// ─── Phase G regression fixtures (lock in Phase G remediation) ─────────

#[test]
fn bridge_rule_7_terminating_chain_positive() {
    assert_passes("bridge-rule-7-terminating-chain-positive");
}
#[test]
fn reducer_capability_cap_narrows() {
    assert_passes("usage-eligibility-reducer-capability-cap-narrows");
}
#[test]
fn reducer_applicability_gate() {
    assert_passes("usage-eligibility-reducer-applicability-gate");
}
#[test]
fn reducer_stale_with_honored_pit() {
    assert_passes("usage-eligibility-reducer-stale-with-honored-pit");
}
#[test]
fn concept_resolution_informational_severity() {
    assert_passes("concept-resolution-informational-severity");
}
#[test]
fn pit_unsupported_anchor_error() {
    assert_passes("point-in-time-exception-unsupported-anchor");
}

// ─── Plan 7e.3 — Finding-IRI dangling-IRI parity ───────────────────────

#[test]
fn bridge_rule_8_target_finding_dangling_negative() {
    assert_passes("bridge-rule-8-target-finding-dangling-negative");
}

// ─── Plan 7e.2 — freshness gate (§1.2 step 5.5) ─────────────────────────

#[test]
fn reducer_freshness_stale_narrows() {
    assert_passes("usage-eligibility-reducer-freshness-stale-narrows");
}

#[test]
fn reducer_freshness_fresh_passes() {
    assert_passes("usage-eligibility-reducer-freshness-fresh-passes");
}

// Plan 7e review F6 — strict-error parity for Step 5.5 malformed lastVerifiedAt.
#[test]
fn reducer_freshness_malformed_negative() {
    assert_passes("usage-eligibility-reducer-freshness-malformed-negative");
}

#[test]
fn scoped_bridge_and_reducer_apply_the_same_freshness_gate() {
    use serde_json::json;

    let office = "urn:rulespec:example:office";
    let mut request = load("point-in-time-filing-date");
    let assertion = request["rkaf:subjectAssertion"].clone();
    request["rkaf:evaluationScopes"] = json!([office]);
    let nodes = request["rkaf:input"]["@graph"].as_array_mut().unwrap();
    let registration = nodes
        .iter_mut()
        .find(|node| node["@type"] == "rkaf:BridgeConsumerRegistration")
        .unwrap();
    registration["rkaf:maxAttestationStalenessDays"] = json!(30);
    nodes.push(json!({
        "@id": "urn:example:attestation", "@type": "rkaf:Attestation",
        "rkaf:targets": [assertion], "rkaf:lastVerifiedAt": "2026-05-10T00:00:00Z"
    }));
    nodes.push(json!({
        "@id": "urn:example:declaration", "@type": "rkaf:ConsumerEffectiveDeclaration",
        "rkaf:forAssertion": assertion, "rkaf:declaredScope": office,
        "rkaf:declaredEffective": "rkaf:officialUse"
    }));
    request["rkaf:contractRuleNumber"] = json!(2);

    for (instant, level, bridge) in [
        ("2026-05-15T00:00:00Z", "rkaf:officialUse", "rkaf:accepted"),
        ("2026-07-15T00:00:00Z", "rkaf:publicationAllowed", "rkaf:rejected"),
    ] {
        request["rkaf:evaluationTime"] = json!(instant);
        request["rkaf:behaviorContract"] = json!("rkaf:UsageEligibilityReducer");
        let reduced = Runtime::evaluate(&request).unwrap().output;
        assert_eq!(reduced["byScope"][office], level);
        request["rkaf:behaviorContract"] = json!("rkaf:BridgeContractRule");
        let checked = Runtime::evaluate(&request).unwrap().output;
        assert_eq!(checked["bridgeValidationResult"], bridge);
        if bridge == "rkaf:rejected" {
            assert_eq!(checked["errorClass"], "rkaf:UnauthorizedBroadening");
        }
    }

    for contract in ["rkaf:UsageEligibilityReducer", "rkaf:BridgeContractRule"] {
        request["rkaf:behaviorContract"] = json!(contract);
        for invalid in [json!("not an instant"), json!(20260515), Value::Null] {
            request["rkaf:evaluationTime"] = invalid;
            assert!(matches!(
                Runtime::evaluate(&request),
                Err(RuntimeError::MalformedTestCase(message)) if message.contains("rkaf:evaluationTime")
            ));
        }
        request.as_object_mut().unwrap().remove("rkaf:evaluationTime");
        assert!(matches!(
            Runtime::evaluate(&request),
            Err(RuntimeError::MalformedTestCase(message)) if message.contains("rkaf:evaluationTime")
        ));
    }

    let attestation = request["rkaf:input"]["@graph"]
        .as_array_mut()
        .unwrap()
        .iter_mut()
        .find(|node| node["@id"] == "urn:example:attestation")
        .unwrap();
    attestation["rkaf:targets"] = json!(["urn:example:unrelated"]);
    assert_eq!(
        Runtime::evaluate(&request).unwrap().output["bridgeValidationResult"],
        "rkaf:accepted"
    );
    request["rkaf:behaviorContract"] = json!("rkaf:UsageEligibilityReducer");
    assert_eq!(
        Runtime::evaluate(&request).unwrap().output["byScope"][office],
        "rkaf:officialUse"
    );
}

#[test]
fn bridge_rule_2_binds_official_use_to_the_declaring_consumer() {
    use serde_json::json;

    let mut request = load("point-in-time-filing-date");
    request["rkaf:behaviorContract"] = json!("rkaf:BridgeContractRule");
    request["rkaf:contractRuleNumber"] = json!(2);
    request["rkaf:evaluationTime"] = json!("2026-07-15T00:00:00Z");
    request["rkaf:evaluationConsumer"] = json!("urn:example:alternate-registration");
    let assertion = request["rkaf:subjectAssertion"].clone();
    let nodes = request["rkaf:input"]["@graph"].as_array_mut().unwrap();
    let registration = nodes
        .iter_mut()
        .find(|node| node["@type"] == "rkaf:BridgeConsumerRegistration")
        .unwrap();
    registration["rkaf:maxAttestationStalenessDays"] = json!(30);
    let registered_consumer = registration["rkaf:consumer"].clone();
    let registration_id = registration["@id"].clone();
    let mut alternate = registration.clone();
    alternate["@id"] = json!("urn:example:alternate-registration");
    alternate["rkaf:consumer"] = json!("urn:example:alternate-consumer");
    alternate
        .as_object_mut()
        .unwrap()
        .remove("rkaf:maxAttestationStalenessDays");
    nodes.extend([
        alternate,
        json!({
            "@id": "urn:example:attestation", "@type": "rkaf:Attestation",
            "rkaf:targets": [assertion], "rkaf:lastVerifiedAt": "2026-05-10T00:00:00Z"
        }),
        json!({
            "@id": "urn:example:declaration", "@type": "rkaf:ConsumerEffectiveDeclaration",
            "rkaf:consumer": registered_consumer, "rkaf:forAssertion": assertion,
            "rkaf:declaredScope": "urn:rulespec:example:office",
            "rkaf:declaredEffective": "rkaf:officialUse", "rkaf:declaredAt": "2026-07-15T00:00:00Z"
        }),
    ]);

    let mismatched = Runtime::evaluate(&request).unwrap().output;
    assert_eq!(mismatched["bridgeValidationResult"], "rkaf:rejected");
    assert!(mismatched["rationale"]
        .as_str()
        .unwrap()
        .contains("rkaf:consumer"));

    request["rkaf:evaluationConsumer"] = registration_id;
    let stale = Runtime::evaluate(&request).unwrap().output;
    assert_eq!(stale["bridgeValidationResult"], "rkaf:rejected");
    assert!(stale["rationale"]
        .as_str()
        .unwrap()
        .contains("rkaf:publicationAllowed"));

    request["rkaf:evaluationTime"] = json!("2026-05-15T00:00:00Z");
    assert_eq!(
        Runtime::evaluate(&request).unwrap().output["bridgeValidationResult"],
        "rkaf:accepted"
    );

    request["rkaf:input"]["@graph"]
        .as_array_mut()
        .unwrap()
        .last_mut()
        .unwrap()
        .as_object_mut()
        .unwrap()
        .remove("rkaf:consumer");
    let omitted = Runtime::evaluate(&request).unwrap().output;
    assert_eq!(omitted["bridgeValidationResult"], "rkaf:rejected");
    assert!(omitted["rationale"]
        .as_str()
        .unwrap()
        .contains("rkaf:consumer"));
}

#[test]
fn bridge_rule_2_refuses_an_official_declaration_without_a_resolved_subject() {
    use serde_json::json;

    let mut request = load("bridge-rule-2-declared-broadens-without-adoption-negative");
    let declaration = &mut request["rkaf:input"]["@graph"][1];
    declaration["rkaf:forAssertion"] = json!("urn:example:missing-assertion");
    let dangling = Runtime::evaluate(&request).unwrap().output;
    assert_eq!(dangling["bridgeValidationResult"], "rkaf:rejected");
    assert!(dangling["rationale"]
        .as_str()
        .unwrap()
        .contains("rkaf:forAssertion"));

    request["rkaf:input"]["@graph"][1]
        .as_object_mut()
        .unwrap()
        .remove("rkaf:forAssertion");
    let omitted = Runtime::evaluate(&request).unwrap().output;
    assert_eq!(omitted["bridgeValidationResult"], "rkaf:rejected");
    assert!(omitted["rationale"]
        .as_str()
        .unwrap()
        .contains("rkaf:forAssertion"));

    let nodes = request["rkaf:input"]["@graph"].as_array_mut().unwrap();
    nodes[1]["rkaf:forAssertion"] = json!("urn:example:adoption");
    nodes.push(json!({
        "@id": "urn:example:adoption", "@type": "rkaf:LocalAdoption",
        "rkaf:usageEligibility": "rkaf:officialUse"
    }));
    let wrong_type = Runtime::evaluate(&request).unwrap().output;
    assert_eq!(wrong_type["bridgeValidationResult"], "rkaf:rejected");
    assert!(wrong_type["rationale"]
        .as_str()
        .unwrap()
        .contains("rkaf:forAssertion"));
}

#[test]
fn bridge_rule_2_does_not_fall_back_from_an_explicit_consumer() {
    use serde_json::json;

    let mut request = load("bridge-rule-2-declared-equals-reducer-positive");
    request["rkaf:evaluationConsumer"] = json!("urn:example:other-registration");
    let refuses = |request: &Value| {
        assert!(matches!(
            Runtime::evaluate(request),
            Err(RuntimeError::MalformedTestCase(message)) if message.contains("rkaf:evaluationConsumer")
        ));
    };
    refuses(&request);

    request["rkaf:input"]["@graph"]
        .as_array_mut()
        .unwrap()
        .push(json!({
            "@id": "urn:example:registration", "@type": "rkaf:BridgeConsumerRegistration",
            "rkaf:consumer": "urn:rkaf:consumer:test"
        }));
    refuses(&request);

    request["rkaf:evaluationConsumer"] = Value::Null;
    refuses(&request);

    request["rkaf:evaluationConsumer"] = json!("urn:example:registration");
    assert_eq!(
        Runtime::evaluate(&request).unwrap().output["bridgeValidationResult"],
        "rkaf:accepted"
    );
}

// ─── Plan 7c — severity ladder + cascade as_of ─────────────────────────

#[test]
fn concept_resolution_publication_blocking() {
    assert_passes("concept-resolution-publication-blocking");
}
#[test]
fn concept_resolution_authority_critical() {
    assert_passes("concept-resolution-authority-critical");
}
#[test]
fn cascade_as_of_excludes_expired() {
    assert_passes("cascade-closure-as-of-excludes-expired");
}

/// One office has an active approval for both versions. All three interfaces
/// must agree on both versions for each case, including a reopened claim.
#[test]
fn filing_date_controls_rule_citation_and_office_approval() {
    use serde_json::json;
    let example = load("point-in-time-filing-date");
    let prior = example["rkaf:subjectAssertion"].as_str().unwrap();
    let current = "urn:rulespec:example:medical-opinions:current";
    let office = "urn:rulespec:example:office";
    let other_office = "urn:rulespec:example:other-office";
    let prior_source =
        "https://www.govinfo.gov/content/pkg/CFR-2018-title20-vol2/xml/CFR-2018-title20-vol2-sec404-1527.xml";
    let current_source =
        "https://www.govinfo.gov/content/pkg/CFR-2018-title20-vol2/xml/CFR-2018-title20-vol2-sec404-1520c.xml";
    for (date, verified, selected, source) in [
        (Some("2017-03-22"), true, Some(prior), Some(prior_source)),
        (Some("2017-03-26"), true, Some(prior), Some(prior_source)),
        (
            Some("2017-03-27"),
            true,
            Some(current),
            Some(current_source),
        ),
        (
            Some("2017-03-28"),
            true,
            Some(current),
            Some(current_source),
        ),
        (None, true, None, None),
        (Some("2017-03-22"), false, None, None),
    ] {
        let mut case = example.clone();
        if let Some(date) = date {
            case["rkaf:caseDate"] = json!(date);
        } else {
            case.as_object_mut().unwrap().remove("rkaf:caseDate");
        }
        case["rkaf:caseDateVerified"] = json!(verified);
        case["rkaf:evaluationTime"] = json!("2026-11-18T12:00:00Z");
        let verdict = Runtime::evaluate(&case).unwrap().output;
        let decision = &verdict["caseDecision"];
        assert_eq!(decision["selectedAssertion"].as_str(), selected);
        assert_eq!(
            decision["verifiedCaseDate"].as_str(),
            if verified { date } else { None }
        );
        assert_eq!(
            decision["sourceReferences"],
            source.map(|s| json!([s])).unwrap_or(Value::Null)
        );
        if selected.is_none() {
            assert_eq!(decision["status"], "needsReview");
            assert_eq!(decision["reason"], "verifyCaseDate");
        }

        for id in [prior, current] {
            let mut request = case.clone();
            request["rkaf:behaviorContract"] = json!("rkaf:UsageEligibilityReducer");
            request["rkaf:subjectAssertion"] = json!(id);
            request["rkaf:evaluationScopes"] = json!([office, other_office]);
            let allowed = selected == Some(id);
            let verdict = Runtime::evaluate(&request).unwrap().output;
            assert_eq!(
                verdict["byScope"][office],
                if allowed { "rkaf:officialUse" } else { "rkaf:notEligible" }
            );
            assert_eq!(
                verdict["byScope"][other_office],
                if allowed { "rkaf:publicationAllowed" } else { "rkaf:notEligible" }
            );

            for scope in [office, other_office] {
                let mut bridge_request = request.clone();
                bridge_request["rkaf:behaviorContract"] = json!("rkaf:BridgeContractRule");
                bridge_request["rkaf:contractRuleNumber"] = json!(2);
                bridge_request["rkaf:input"]["@graph"].as_array_mut().unwrap().push(json!({
                    "@id": "claim-use", "@type": "rkaf:ConsumerEffectiveDeclaration",
                    "rkaf:forAssertion": id, "rkaf:declaredScope": scope,
                    "rkaf:declaredEffective": "rkaf:officialUse"
                }));
                let verdict = Runtime::evaluate(&bridge_request).unwrap().output;
                assert_eq!(
                    verdict["bridgeValidationResult"],
                    if allowed && scope == office {
                        "rkaf:accepted"
                    } else {
                        "rkaf:rejected"
                    }
                );
            }
        }
    }
}

#[test]
fn only_verified_facts_for_the_declared_anchor_can_match() {
    use serde_json::json;
    let original = load("point-in-time-filing-date");
    let evaluate = |case: &Value| Runtime::evaluate(case).unwrap().output["caseDecision"].clone();
    let mut case = original.clone();
    case["rkaf:evaluationAnchor"] = json!("rkaf:noticeGenerationTime");
    assert_eq!(evaluate(&case)["reason"], "verifyCaseDate");

    case = original.clone();
    let nodes = case["rkaf:input"]["@graph"].as_array_mut().unwrap();
    let exception = nodes
        .iter_mut()
        .find(|n| n["@type"] == "rkaf:PointInTimeException")
        .unwrap();
    exception["rkaf:exceptionScope"] = json!("Only for renewals referred by the local office.");
    assert_eq!(evaluate(&case)["reason"], "reviewExceptionScope");

    case = original.clone();
    let nodes = case["rkaf:input"]["@graph"].as_array_mut().unwrap();
    let exception = nodes
        .iter_mut()
        .find(|n| n["@type"] == "rkaf:PointInTimeException")
        .unwrap();
    exception
        .as_object_mut()
        .unwrap()
        .remove("rkaf:anchorDateBefore");
    assert_eq!(evaluate(&case)["reason"], "reviewExceptionScope");

    for invalid in ["2017-02-29", "2017-3-2", "2017-03-26T23:59:59Z"] {
        let mut case = original.clone();
        case["rkaf:caseDate"] = json!(invalid);
        assert!(matches!(
            Runtime::evaluate(&case),
            Err(RuntimeError::MalformedTestCase(_))
        ));
    }
}
