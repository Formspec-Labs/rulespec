// Rust guideline compliant 2026-02-21

use rkaf_runtime::Runtime;
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
    use rkaf_runtime::{pit::rule_family, Graph};

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
