// Rust guideline compliant 2026-02-21

use rkaf_runtime::{pit::pinned_source_references, Graph, Runtime};
use serde_json::{json, Value};

const PRIOR: &str = "urn:rulespec:example:medical-opinions:prior";
const CURRENT: &str = "urn:rulespec:example:medical-opinions:current";
const THIRD: &str = "urn:example:third-version";
const FIRST_LINK: &str = "urn:rulespec:example:medical-opinions:filing-cutoff";
const LATER_LINK: &str = "urn:example:later-cutoff";
const ANCHOR: &str = "rkaf:applicationSubmissionTime";
const OFFICE: &str = "urn:rulespec:example:office";
const PRIOR_SOURCE: &str =
    "https://www.govinfo.gov/content/pkg/CFR-2018-title20-vol2/xml/CFR-2018-title20-vol2-sec404-1527.xml";
const CURRENT_SOURCE: &str =
    "https://www.govinfo.gov/content/pkg/CFR-2018-title20-vol2/xml/CFR-2018-title20-vol2-sec404-1520c.xml";
const THIRD_SOURCE: &str = "urn:example:third-version:source";
const PRIOR_BINDING: &str = "urn:rulespec:example:medical-opinions:prior:filing-evidence";
const CURRENT_BINDING: &str = "urn:rulespec:example:medical-opinions:current:filing-evidence";

fn example() -> Value {
    serde_json::from_str(include_str!(
        "../../../fixtures/behavior/point-in-time-filing-date.jsonld"
    ))
    .unwrap()
}

fn nodes(case: &mut Value) -> &mut Vec<Value> {
    case["rkaf:input"]["@graph"].as_array_mut().unwrap()
}

fn node<'a>(case: &'a mut Value, id: &str) -> &'a mut Value {
    nodes(case)
        .iter_mut()
        .find(|node| node["@id"] == id)
        .unwrap()
}

fn decision(case: &Value) -> Value {
    Runtime::evaluate(case).unwrap().output["caseDecision"].clone()
}

fn assert_official_use(case: &Value, rules: &[&str], selected: Option<&str>) {
    for &id in rules {
        let allowed = Some(id) == selected;
        let mut request = case.clone();
        request["rkaf:behaviorContract"] = json!("rkaf:UsageEligibilityReducer");
        request["rkaf:subjectAssertion"] = json!(id);
        request["rkaf:evaluationTime"] = json!("2026-11-18T12:00:00Z");
        request["rkaf:evaluationScopes"] = json!([OFFICE]);
        let reduced = Runtime::evaluate(&request).unwrap().output;
        assert_eq!(
            reduced["byScope"][OFFICE],
            if allowed {
                "rkaf:officialUse"
            } else {
                "rkaf:notEligible"
            },
            "{id}"
        );

        request["rkaf:behaviorContract"] = json!("rkaf:BridgeContractRule");
        request["rkaf:contractRuleNumber"] = json!(2);
        nodes(&mut request).push(json!({
            "@id": "urn:example:use", "@type": "rkaf:ConsumerEffectiveDeclaration",
            "rkaf:forAssertion": id, "rkaf:declaredScope": OFFICE,
            "rkaf:declaredEffective": "rkaf:officialUse"
        }));
        let checked = Runtime::evaluate(&request).unwrap().output;
        assert_eq!(
            checked["bridgeValidationResult"],
            if allowed {
                "rkaf:accepted"
            } else {
                "rkaf:rejected"
            },
            "{id}"
        );
    }
}

#[test]
fn policy_valued_and_relationship_assertions_use_canonical_citations() {
    let mut case = example();
    let prior = node(&mut case, PRIOR);
    prior["@type"] = json!("rkaf:ValueAssertion");
    prior["rkaf:assertsSubject"] = json!("urn:example:filing-policy");
    prior["rkaf:assertsPredicate"] = json!("urn:example:exclusive-cutoff");
    prior["rkaf:assertsValue"] = json!({ "@type": "xsd:date", "@value": "2017-03-27" });
    prior["rkaf:assertionPolarity"] = json!("rkaf:affirmed");

    let current = node(&mut case, CURRENT);
    current["@type"] = json!("rkaf:RelationshipAssertion");
    current["rkaf:assertsSubject"] = json!("urn:example:medical-opinion-evaluation");
    current["rkaf:assertsPredicate"] = json!("urn:example:governed-by");
    current["rkaf:assertsObject"] = json!(CURRENT_SOURCE);
    current["rkaf:assertionPolarity"] = json!("rkaf:affirmed");

    for (date, selected, source) in [
        ("2017-03-26", PRIOR, PRIOR_SOURCE),
        ("2017-03-27", CURRENT, CURRENT_SOURCE),
    ] {
        case["rkaf:caseDate"] = json!(date);
        let result = decision(&case);
        assert_eq!(result["selectedAssertion"], selected);
        assert_eq!(result["sourceReferences"], json!([source]));
        assert_official_use(&case, &[PRIOR, CURRENT], Some(selected));
    }
}

#[test]
fn only_supporting_rule_evidence_is_citable() {
    let mut case = example();
    let mut contextual = node(&mut case, CURRENT_BINDING).clone();
    contextual["@id"] = json!("urn:example:contextual-evidence");
    contextual["rkaf:bindsAssertion"] = json!(PRIOR);
    contextual["rkaf:evidentiaryFunction"] = json!("rkaf:providesContext");
    let mut duplicate = node(&mut case, PRIOR_BINDING).clone();
    duplicate["@id"] = json!("urn:example:duplicate-evidence");
    nodes(&mut case).extend([contextual, duplicate]);
    assert_eq!(decision(&case)["sourceReferences"], json!([PRIOR_SOURCE]));

    let mut anonymous = example();
    node(&mut anonymous, PRIOR_BINDING)
        .as_object_mut()
        .unwrap()
        .remove("@id");
    assert_eq!(
        decision(&anonymous)["sourceReferences"],
        json!([PRIOR_SOURCE])
    );

    case = example();
    node(&mut case, PRIOR)["prov:wasDerivedFrom"] = json!([PRIOR_SOURCE]);
    for (role, function) in [
        ("rkaf:authorityCitation", "rkaf:contradicts"),
        ("rkaf:authorityCitation", "rkaf:qualifies"),
        ("rkaf:retrievalSignal", "rkaf:supports"),
    ] {
        let binding = node(&mut case, PRIOR_BINDING);
        binding["rkaf:evidenceRole"] = json!(role);
        binding["rkaf:evidentiaryFunction"] = json!(function);
        assert_review(&case, "reviewRuleSources", &[PRIOR, CURRENT]);
    }

    let binding = node(&mut case, PRIOR_BINDING);
    let object = binding.as_object_mut().unwrap();
    object.remove("rkaf:bindsSourceFragment");
    object.remove("rkaf:evidenceRole");
    object.remove("rkaf:evidentiaryFunction");
    binding["rkaf:noEvidenceReason"] = json!("rkaf:illustrativeSample");
    node(&mut case, PRIOR)["rkaf:usageEligibility"] = json!("rkaf:draftGenerationAllowed");
    node(&mut case, "urn:rulespec:example:prior-approval")["rkaf:usageEligibility"] =
        json!("rkaf:draftGenerationAllowed");
    assert_review(&case, "reviewRuleSources", &[PRIOR, CURRENT]);

    // The retention source and successor source are both required for a pair.
    case = example();
    nodes(&mut case).retain(|node| node["@id"] != CURRENT_BINDING);
    assert_review(&case, "reviewRuleSources", &[PRIOR, CURRENT]);
}

#[test]
fn operational_citations_require_a_canonical_fragment_and_a_consistent_source_pin() {
    fn pinned(case: &Value) -> Vec<&str> {
        let graph = Graph::from_payload(&case["rkaf:input"]).unwrap();
        pinned_source_references(PRIOR, &graph)
    }

    let mut case = example();
    assert_eq!(pinned(&case), [PRIOR_SOURCE]);
    let binding = node(&mut case, PRIOR_BINDING);
    let fragment_id = binding["rkaf:bindsSourceFragment"][0]
        .as_str()
        .unwrap()
        .to_owned();
    binding.as_object_mut().unwrap().remove("@id");
    assert_eq!(pinned(&case), [PRIOR_SOURCE]);

    let artifact_digest = node(&mut case, PRIOR_SOURCE)["rkaf:hasContentDigest"].clone();
    node(&mut case, PRIOR_SOURCE)
        .as_object_mut()
        .unwrap()
        .remove("rkaf:hasContentDigest");
    assert_eq!(pinned(&case), [PRIOR_SOURCE]);

    node(&mut case, PRIOR_SOURCE)["rkaf:hasContentDigest"] = artifact_digest;
    node(&mut case, &fragment_id)["rkaf:sourceArtifactDigest"] =
        json!("sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
    assert!(pinned(&case).is_empty());

    node(&mut case, &fragment_id)
        .as_object_mut()
        .unwrap()
        .remove("rkaf:sourceArtifactDigest");
    assert!(pinned(&case).is_empty());
    assert_eq!(decision(&case)["sourceReferences"], json!([PRIOR_SOURCE]));

    node(&mut case, PRIOR_SOURCE)
        .as_object_mut()
        .unwrap()
        .remove("rkaf:hasContentDigest");
    node(&mut case, &fragment_id)["rkaf:sourceArtifactDigest"] = json!("sha256:1234");
    assert!(pinned(&case).is_empty());

    nodes(&mut case).retain(|node| node["rkaf:bindsAssertion"] != PRIOR);
    node(&mut case, PRIOR)["prov:wasDerivedFrom"] = json!([PRIOR_SOURCE]);
    assert!(pinned(&case).is_empty());
    assert_eq!(decision(&case)["sourceReferences"], json!([PRIOR_SOURCE]));
}

fn link(id: &str, prior: &str, successor: &str, cutoff: &str) -> Value {
    json!({
        "@id": id, "@type": "rkaf:PointInTimeException",
        "rkaf:retainsAssertion": prior, "rkaf:successorAssertion": successor,
        "rkaf:evaluationAnchor": ANCHOR, "rkaf:anchorDateBefore": cutoff,
    })
}

fn three_versions() -> Value {
    let mut case = example();
    let current = node(&mut case, CURRENT);
    current["rkaf:consumerLifecycleState"] = json!("rkaf:staleForCurrentUse");
    let mut third = current.clone();
    third["@id"] = json!(THIRD);
    third["rkaf:consumerLifecycleState"] = json!("rkaf:operational");
    third["rkaf:supersedesAssertion"] = json!([CURRENT]);
    // Use the direct provenance allowed by the pre-existing behavioral API.
    third["prov:wasDerivedFrom"] = json!([THIRD_SOURCE]);

    let mut approval = node(&mut case, "urn:rulespec:example:current-approval").clone();
    approval["@id"] = json!("urn:example:third-approval");
    approval["rkaf:targetAssertion"] = json!(THIRD);
    nodes(&mut case).extend([
        third,
        approval,
        link(LATER_LINK, CURRENT, THIRD, "2020-01-01"),
    ]);
    case
}

#[test]
fn ordered_cutoffs_select_and_authorize_the_applicable_version() {
    let mut case = three_versions();
    // This separate, unresolved rule creates no conditions for the case rule.
    let mut unrelated = link(
        "urn:example:unrelated",
        "urn:example:other-prior",
        "urn:example:missing-successor",
        "2020-01-01",
    );
    unrelated["rkaf:evaluationAnchor"] = json!("rkaf:eligibilityDeterminationTime");
    nodes(&mut case).push(unrelated);
    nodes(&mut case).reverse();
    for (date, selected, source, status) in [
        ("2017-03-26", PRIOR, PRIOR_SOURCE, "priorRule"),
        ("2017-03-27", CURRENT, CURRENT_SOURCE, "successorRule"),
        ("2019-12-31", CURRENT, CURRENT_SOURCE, "successorRule"),
        ("2020-01-01", THIRD, THIRD_SOURCE, "successorRule"),
        ("2020-01-02", THIRD, THIRD_SOURCE, "successorRule"),
    ] {
        case["rkaf:caseDate"] = json!(date);
        let result = decision(&case);
        assert_eq!(result["status"], status);
        assert_eq!(result["exception"], FIRST_LINK);
        assert_eq!(result["cutoff"], "2017-03-27");
        assert_eq!(result["verifiedCaseDate"], date);
        assert_eq!(result["selectedAssertion"], selected);
        assert_eq!(result["sourceReferences"], json!([source]));
        assert_eq!(
            result["transitions"],
            json!([
                { "exception": FIRST_LINK, "cutoff": "2017-03-27" },
                { "exception": LATER_LINK, "cutoff": "2020-01-01" }
            ])
        );
        assert_official_use(&case, &[PRIOR, CURRENT, THIRD], Some(selected));
    }

    case["rkaf:subjectAssertion"] = json!(CURRENT);
    case["rkaf:caseDate"] = json!("2019-12-31");
    let result = decision(&case);
    assert_eq!(result["status"], "priorRule");
    assert_eq!(result["exception"], LATER_LINK);
    assert_eq!(result["selectedAssertion"], CURRENT);
    case["rkaf:caseDate"] = json!("2017-03-26");
    let result = decision(&case);
    assert_eq!(result["reason"], "reviewRuleTransitions");
    assert!(result.get("selectedAssertion").is_none());
    assert_official_use(&case, &[PRIOR, CURRENT, THIRD], Some(PRIOR));
}

fn assert_review(case: &Value, reason: &str, rules: &[&str]) {
    let result = decision(case);
    assert_eq!(result["status"], "needsReview");
    assert_eq!(result["reason"], reason);
    assert!(result.get("selectedAssertion").is_none());
    assert!(result.get("sourceReferences").is_none());
    assert_official_use(case, rules, None);
}

#[test]
fn conflicting_or_unresolved_transitions_cannot_authorize_any_version() {
    let mut base = three_versions();
    base["rkaf:caseDate"] = json!("2020-01-01");
    let rules = &[PRIOR, CURRENT, THIRD];
    for (prior, successor) in [
        (PRIOR, PRIOR),
        (PRIOR, THIRD),
        (CURRENT, "urn:example:fourth"),
        ("urn:example:other", THIRD),
        (THIRD, PRIOR),
    ] {
        let mut case = base.clone();
        nodes(&mut case).push(link("urn:example:conflict", prior, successor, "2021-01-01"));
        assert_review(&case, "reviewRuleTransitions", rules);
    }

    let mut case = base.clone();
    node(&mut case, LATER_LINK)["rkaf:anchorDateBefore"] = json!("2017-03-27");
    assert_review(&case, "reviewRuleTransitions", rules);
    node(&mut case, LATER_LINK)["rkaf:anchorDateBefore"] = json!("2017-03-26");
    assert_review(&case, "reviewRuleTransitions", rules);
    node(&mut case, LATER_LINK)
        .as_object_mut()
        .unwrap()
        .remove("rkaf:anchorDateBefore");
    assert_review(&case, "reviewExceptionScope", rules);

    let mut case = base.clone();
    node(&mut case, LATER_LINK)["rkaf:exceptionScope"] = json!("Applies only to renewals");
    assert_review(&case, "reviewExceptionScope", rules);

    let mut case = base.clone();
    case["rkaf:caseDateVerified"] = json!(false);
    assert_review(&case, "verifyCaseDate", rules);

    let other_anchor = "rkaf:eligibilityDeterminationTime";
    node(&mut base, LATER_LINK)["rkaf:evaluationAnchor"] = json!(other_anchor);
    let output = Runtime::evaluate(&base).unwrap().output;
    assert_eq!(output["errorClass"], "rkaf:UnsupportedEvaluationAnchor");
    assert_official_use(&base, rules, None);
    node(&mut base, "reg1")["rkaf:supportedEvaluationAnchors"] = json!([ANCHOR, other_anchor]);
    assert_review(&base, "verifyCaseDate", rules);
}

#[test]
fn unsupported_anchor_is_refused_even_in_ambiguous_succession() {
    let other_anchor = "rkaf:eligibilityDeterminationTime";
    for prior in [PRIOR, CURRENT] {
        let mut case = three_versions();
        let mut competing = link(
            "urn:example:unsupported-branch",
            prior,
            "urn:example:alternate",
            "2020-01-01",
        );
        competing["rkaf:evaluationAnchor"] = json!(other_anchor);
        nodes(&mut case).push(competing);
        let output = Runtime::evaluate(&case).unwrap().output;
        assert_eq!(output["errorClass"], "rkaf:UnsupportedEvaluationAnchor");
        assert!(output.get("caseDecision").is_none());
        assert_official_use(&case, &[PRIOR, CURRENT, THIRD], None);

        node(&mut case, "reg1")["rkaf:supportedEvaluationAnchors"] = json!([ANCHOR, other_anchor]);
        assert_review(&case, "reviewRuleTransitions", &[PRIOR, CURRENT, THIRD]);
    }
}

#[test]
fn terminal_retention_window_ends_selection_and_eligibility_for_every_subject() {
    let mut case = example();
    let mut end = link(LATER_LINK, CURRENT, THIRD, "2020-01-01");
    end.as_object_mut()
        .unwrap()
        .remove("rkaf:successorAssertion");
    nodes(&mut case).push(end);
    for lifecycle_state in ["rkaf:operational", "rkaf:staleForCurrentUse"] {
        node(&mut case, CURRENT)["rkaf:consumerLifecycleState"] = json!(lifecycle_state);
        for subject in [PRIOR, CURRENT] {
            case["rkaf:subjectAssertion"] = json!(subject);
            case["rkaf:caseDate"] = json!("2019-12-31");
            let result = decision(&case);
            assert_eq!(result["selectedAssertion"], CURRENT);
            assert_eq!(result["sourceReferences"], json!([CURRENT_SOURCE]));
            assert_official_use(&case, &[PRIOR, CURRENT], Some(CURRENT));

            for date in ["2020-01-01", "2020-01-02"] {
                case["rkaf:caseDate"] = json!(date);
                let result = decision(&case);
                assert_eq!(result["status"], "outsideWindow");
                assert_eq!(result["verifiedCaseDate"], date);
                assert!(result.get("selectedAssertion").is_none());
                assert!(result.get("sourceReferences").is_none());
                assert_official_use(&case, &[PRIOR, CURRENT], None);
            }
        }
    }
}

#[test]
fn rule_family_is_shared_across_versions_and_refuses_ambiguous_links() {
    use rkaf_runtime::pit::rule_family;

    let mut case = three_versions();
    let graph = Graph::from_payload(&case["rkaf:input"]).unwrap();
    for subject in [PRIOR, CURRENT, THIRD] {
        assert_eq!(
            rule_family(subject, &graph).unwrap(),
            [PRIOR, CURRENT, THIRD]
        );
    }
    nodes(&mut case).push(link("urn:example:cycle", THIRD, PRIOR, "2021-01-01"));
    let graph = Graph::from_payload(&case["rkaf:input"]).unwrap();
    assert!(rule_family(PRIOR, &graph).is_err());

    let mut case = example();
    node(&mut case, FIRST_LINK)
        .as_object_mut()
        .unwrap()
        .remove("rkaf:successorAssertion");
    let graph = Graph::from_payload(&case["rkaf:input"]).unwrap();
    assert_eq!(rule_family(PRIOR, &graph).unwrap(), [PRIOR]);
    assert_eq!(rule_family(CURRENT, &graph).unwrap(), [CURRENT]);
}

#[test]
fn earliest_filing_date_bounds_the_entire_history() {
    const START: &str = "rkaf:anchorDateOnOrAfter";
    let mut case = three_versions();
    node(&mut case, FIRST_LINK)[START] = json!("2017-03-22");
    let rules = &[PRIOR, CURRENT, THIRD];
    for (date, selected) in [
        ("2017-03-21", None),
        ("2017-03-22", Some(PRIOR)),
        ("2017-03-27", Some(CURRENT)),
        ("2020-01-01", Some(THIRD)),
    ] {
        case["rkaf:caseDate"] = json!(date);
        let result = decision(&case);
        assert_eq!(result["earliestCaseDate"], "2017-03-22");
        assert_eq!(result["selectedAssertion"].as_str(), selected);
        assert_official_use(&case, rules, selected);
        if selected.is_none() {
            assert_eq!(result["status"], "outsideWindow");
            assert_eq!(result["reason"], "beforeRuleHistoryStart");
            assert!(result.get("sourceReferences").is_none());
        }
    }

    // Later assertions cannot introduce undisclosed gaps into an existing history.
    node(&mut case, LATER_LINK)[START] = json!("2017-03-27");
    assert_review(&case, "reviewRuleTransitions", rules);
    node(&mut case, LATER_LINK)
        .as_object_mut()
        .unwrap()
        .remove(START);
    for invalid in ["2017-03-27", "2017-03-28"] {
        node(&mut case, FIRST_LINK)[START] = json!(invalid);
        assert_review(&case, "reviewRuleTransitions", rules);
    }
    node(&mut case, FIRST_LINK)[START] = json!("2017-02-30");
    assert!(Runtime::evaluate(&case).is_err());
}

#[test]
fn bounded_standalone_exception_gates_a_current_assertion() {
    let mut case = example();
    let exception = node(&mut case, FIRST_LINK);
    exception
        .as_object_mut()
        .unwrap()
        .remove("rkaf:successorAssertion");
    exception["rkaf:anchorDateOnOrAfter"] = json!("2017-03-22");
    node(&mut case, PRIOR)["rkaf:consumerLifecycleState"] = json!("rkaf:operational");
    for (date, selected) in [
        ("2017-03-21", None),
        ("2017-03-22", Some(PRIOR)),
        ("2017-03-27", None),
    ] {
        case["rkaf:caseDate"] = json!(date);
        assert_official_use(&case, &[PRIOR], selected);
    }
}

#[test]
fn office_approval_uses_an_inclusive_start_and_exclusive_expiry() {
    use rkaf_runtime::reducer::active_adoptions_for_scope;

    const APPROVAL: &str = "urn:rulespec:example:prior-approval";
    const START: &str = "2026-04-15T00:00:00Z";
    const END: &str = "2026-05-01T00:00:00Z";
    let mut case = example();
    case["rkaf:behaviorContract"] = json!("rkaf:UsageEligibilityReducer");
    case["rkaf:evaluationScopes"] = json!([OFFICE]);
    node(&mut case, APPROVAL)["rkaf:validUntil"] = json!(END);

    for (instant, allowed) in [
        (None, false),
        (Some("2026-04-14T23:59:59Z"), false),
        (Some(START), true),
        (Some("2026-04-30T23:59:59Z"), true),
        (Some("2026-04-30T20:00:00-04:00"), false),
        (Some(END), false),
        (Some("2026-05-01T00:00:01Z"), false),
    ] {
        if let Some(instant) = instant {
            case["rkaf:evaluationTime"] = json!(instant);
        }
        let level = Runtime::evaluate(&case).unwrap().output;
        assert_eq!(level["byScope"][OFFICE] == "rkaf:officialUse", allowed);
        let time = instant.map(|time| chrono::DateTime::parse_from_rfc3339(time).unwrap());
        let graph = Graph::from_payload(&case["rkaf:input"]).unwrap();
        let ids: Vec<_> = active_adoptions_for_scope(&graph, PRIOR, OFFICE, time.as_ref())
            .map(|node| node["@id"].as_str().unwrap())
            .collect();
        assert_eq!(ids, if allowed { vec![APPROVAL] } else { vec![] });
    }

    case["rkaf:evaluationTime"] = json!("invalid");
    assert!(Runtime::evaluate(&case).is_err());
    case["rkaf:evaluationTime"] = json!(START);
    let mut bad = node(&mut case, APPROVAL).clone();
    bad["@id"] = json!("urn:example:malformed-approval");
    bad["rkaf:validUntil"] = json!("invalid");
    nodes(&mut case).push(bad);
    let mut future = node(&mut case, APPROVAL).clone();
    future["@id"] = json!("urn:example:future-approval");
    future["rkaf:adoptedAt"] = json!(END);
    future["rkaf:validUntil"] = json!("2026-06-01T00:00:00Z");
    nodes(&mut case).push(future);
    let mut bridge = case.clone();
    bridge["rkaf:behaviorContract"] = json!("rkaf:BridgeContractRule");
    bridge["rkaf:contractRuleNumber"] = json!(2);
    nodes(&mut bridge).push(json!({
        "@id": "urn:example:use", "@type": "rkaf:ConsumerEffectiveDeclaration",
        "rkaf:forAssertion": PRIOR, "rkaf:declaredScope": OFFICE,
        "rkaf:declaredEffective": "rkaf:officialUse"
    }));
    for (valid_until, expected) in [(END, "rkaf:accepted"), ("invalid", "rkaf:rejected")] {
        node(&mut bridge, APPROVAL)["rkaf:validUntil"] = json!(valid_until);
        assert_eq!(
            Runtime::evaluate(&bridge).unwrap().output["bridgeValidationResult"],
            expected
        );
    }

    // An old unbounded policy can still be reduced without a review timestamp.
    node(&mut case, APPROVAL)
        .as_object_mut()
        .unwrap()
        .remove("rkaf:validUntil");
    case.as_object_mut().unwrap().remove("rkaf:evaluationTime");
    assert_eq!(
        Runtime::evaluate(&case).unwrap().output["byScope"][OFFICE],
        "rkaf:officialUse"
    );
    case["rkaf:evaluationTime"] = json!("2026-04-14T23:59:59Z");
    assert_eq!(
        Runtime::evaluate(&case).unwrap().output["byScope"][OFFICE],
        "rkaf:publicationAllowed"
    );
}
