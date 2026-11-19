//! Loads a policy and evaluates case dates through the Rulespec runtime.
// Rust guideline compliant 2026-02-21

use std::collections::{BTreeMap, BTreeSet};
use std::fs;
use std::path::Path;

use anyhow::{ensure, Context, Result};
use chrono::{DateTime, FixedOffset, NaiveDate};
use rkaf_runtime::{consumer, pit, reducer, Graph};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};

use crate::report::CaseRecord;

const POINT_IN_TIME: &str = "rkaf:PointInTimeException";

#[derive(Debug)]
pub struct PolicyOverrides<'a> {
    pub subject: Option<&'a str>,
    pub anchor: Option<&'a str>,
    pub consumer: Option<&'a str>,
    pub as_of: Option<&'a str>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PolicySelection {
    subject_assertion: String,
    evaluation_anchor: String,
    evaluation_consumer: String,
    scope: Option<String>,
    evaluated_at: String,
    policy_sha256: String,
}

#[derive(Debug)]
pub struct Policy {
    pub selection: PolicySelection,
    payload: Value,
    evaluated_at: DateTime<FixedOffset>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Rule {
    id: String,
    label: Option<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Passage {
    fragment: Option<String>,
    artifact: String,
    source_sha256: Option<String>,
    fragment_sha256: Option<String>,
    exact_quote: Option<String>,
    publisher_url: Option<String>,
}

#[derive(Debug, Default, Deserialize, Serialize)]
pub struct Outcome {
    pub expected_rule: Option<Rule>,
    pub candidate_rule: Option<Rule>,
    pub reason_code: Option<String>,
    pub reason: Option<String>,
    pub passages: Vec<Passage>,
    pub office_approvals: Vec<String>,
    pub runtime_decision: Option<Value>,
}

impl Rule {
    pub fn id(&self) -> &str {
        &self.id
    }
}

impl Outcome {
    pub fn unresolved(&mut self, code: &str, reason: impl Into<String>) {
        self.reason_code = Some(code.to_owned());
        self.reason = Some(reason.into());
    }

    pub fn expected_id(&self) -> Option<&str> {
        self.expected_rule.as_ref().map(Rule::id)
    }
}

pub fn sha256(bytes: &[u8]) -> String {
    format!("sha256:{:x}", Sha256::digest(bytes))
}

fn nonblank(value: &Value) -> Option<&str> {
    value.as_str().filter(|text| !text.trim().is_empty())
}

impl Policy {
    pub fn read(
        path: &Path,
        selection_path: Option<&Path>,
        overrides: &PolicyOverrides,
    ) -> Result<Self> {
        let bytes = fs::read(path).with_context(|| format!("Read policy {}", path.display()))?;
        let digest = sha256(&bytes);
        let mut doc: Value = serde_json::from_slice(&bytes)
            .with_context(|| format!("Parse policy {}", path.display()))?;
        let wrapper = doc["@type"] == "rkaf:BehaviorTestCase";
        let payload = if wrapper {
            ensure!(
                doc["rkaf:behaviorContract"] == POINT_IN_TIME,
                "Use a point-in-time policy fixture"
            );
            &doc["rkaf:input"]
        } else {
            &doc
        };
        let nodes = payload["@graph"]
            .as_array()
            .context("Policy must contain an @graph array")?;
        let mut ids = BTreeSet::new();
        ensure!(!nodes.is_empty(), "Policy graph is empty");
        for node in nodes {
            ensure!(node.is_object(), "Policy graph nodes must be JSON objects");
            if let Some(id) = node.get("@id") {
                let id = nonblank(id).context("Policy node IDs must be nonempty strings")?;
                ensure!(ids.insert(id), "Duplicate policy node ID {id}");
            }
        }
        let graph = Graph::from_payload(payload)?;

        let selection_file = selection_path
            .map(|path| {
                let bytes =
                    fs::read(path).with_context(|| format!("Read selection {}", path.display()))?;
                serde_json::from_slice::<PolicySelection>(&bytes)
                    .with_context(|| format!("Parse selection {}", path.display()))
            })
            .transpose()?;
        if let Some(settings) = &selection_file {
            let expected = settings
                .policy_sha256
                .strip_prefix("sha256:")
                .unwrap_or(&settings.policy_sha256);
            ensure!(
                digest.strip_prefix("sha256:") == Some(expected),
                "Selection policySha256 differs from the policy file"
            );
            ensure!(
                settings
                    .scope
                    .as_ref()
                    .is_none_or(|scope| !scope.trim().is_empty()),
                "Selection scope must be nonempty"
            );
        }

        let subject = overrides
            .subject
            .or(selection_file
                .as_ref()
                .map(|s| s.subject_assertion.as_str()))
            .or_else(|| {
                wrapper
                    .then(|| nonblank(&doc["rkaf:subjectAssertion"]))
                    .flatten()
            })
            .filter(|subject| !subject.trim().is_empty())
            .context("Set --subject or provide a selection file with subjectAssertion")?;
        let anchor = overrides
            .anchor
            .or(selection_file
                .as_ref()
                .map(|s| s.evaluation_anchor.as_str()))
            .or_else(|| {
                wrapper
                    .then(|| nonblank(&doc["rkaf:evaluationAnchor"]))
                    .flatten()
            })
            .filter(|anchor| !anchor.trim().is_empty())
            .context("Set --anchor or provide a selection file with evaluationAnchor")?;
        let selected_consumer = overrides
            .consumer
            .or(selection_file
                .as_ref()
                .map(|s| s.evaluation_consumer.as_str()))
            .or_else(|| {
                wrapper
                    .then(|| nonblank(&doc["rkaf:evaluationConsumer"]))
                    .flatten()
            });
        let request =
            selected_consumer.map_or(Value::Null, |id| json!({"rkaf:evaluationConsumer": id}));
        let registration = consumer::select_consumer(&request, &graph)?
            .context("Add a BridgeConsumerRegistration to the policy graph")?;
        let registration_id =
            nonblank(&registration["@id"]).context("Registration must have an @id")?;
        let reviewed = overrides
            .as_of
            .or(selection_file.as_ref().map(|s| s.evaluated_at.as_str()))
            .or_else(|| {
                wrapper
                    .then(|| nonblank(&doc["rkaf:evaluationTime"]))
                    .flatten()
            })
            .context("Set --as-of or provide a selection file with evaluatedAt")?;
        let evaluated_at =
            DateTime::parse_from_rfc3339(reviewed).context("Use an RFC 3339 review time")?;
        ensure!(
            graph.nodes_by_type(POINT_IN_TIME).any(|link| {
                link["rkaf:retainsAssertion"] == subject && link["rkaf:evaluationAnchor"] == anchor
            }),
            "No policy transition retains {subject} using {anchor}"
        );

        let selection = PolicySelection {
            subject_assertion: subject.to_owned(),
            evaluation_anchor: anchor.to_owned(),
            evaluation_consumer: registration_id.to_owned(),
            evaluated_at: reviewed.to_owned(),
            scope: selection_file.and_then(|s| s.scope),
            policy_sha256: digest,
        };
        let payload = if wrapper {
            doc["rkaf:input"].take()
        } else {
            doc
        };
        Ok(Self {
            payload,
            selection,
            evaluated_at,
        })
    }

    pub fn graph(&self) -> Result<Graph<'_>> {
        Graph::from_payload(&self.payload).context("Index policy graph")
    }

    pub fn evaluate(
        &self,
        graph: &Graph<'_>,
        case: &CaseRecord,
        input_issue: Option<&str>,
    ) -> Outcome {
        let mut outcome = Outcome::default();
        if let Some(issue) = input_issue {
            outcome.unresolved("invalid_csv_row", issue);
            return outcome;
        }
        if case.case_id.is_empty() {
            outcome.unresolved("missing_case_id", "Enter an identifier for the case.");
            return outcome;
        }

        match case.verification_status.to_ascii_lowercase().as_str() {
            "verified" => {}
            "disputed" => {
                outcome.unresolved(
                    "disputed_filing_date",
                    "Resolve the disputed filing date against the original filing evidence.",
                );
                return outcome;
            }
            "" | "missing" | "unverified" => {
                outcome.unresolved(
                    "missing_verified_filing_evidence",
                    "Obtain filing evidence and verify the filing date.",
                );
                return outcome;
            }
            _ => {
                outcome.unresolved(
                    "invalid_verification_status",
                    "Use verified, disputed, missing, or unverified for the verification status.",
                );
                return outcome;
            }
        }
        if !valid_date(&case.filing_date) {
            outcome.unresolved(
                "invalid_filing_date",
                "Enter the verified filing date as a valid YYYY-MM-DD calendar date.",
            );
            return outcome;
        }
        if case.office.is_empty() {
            outcome.unresolved("missing_office", "Enter the office ID used by the policy.");
            return outcome;
        }

        let mut request = json!({
            "rkaf:subjectAssertion": self.selection.subject_assertion,
            "rkaf:evaluationAnchor": self.selection.evaluation_anchor,
            "rkaf:evaluationConsumer": self.selection.evaluation_consumer,
            "rkaf:evaluationTime": self.selection.evaluated_at,
            "rkaf:evaluationScopes": [case.office],
            "rkaf:caseDate": case.filing_date,
            "rkaf:caseDateVerified": true,
        });
        let verdict = match pit::evaluate(&request, graph) {
            Ok(value) => value.output,
            Err(error) => {
                outcome.unresolved("invalid_policy_transition", error.to_string());
                return outcome;
            }
        };
        let decision = &verdict["caseDecision"];
        outcome.runtime_decision = Some(if decision.is_null() {
            verdict.clone()
        } else {
            decision.clone()
        });
        let Some(selected) = nonblank(&decision["selectedAssertion"]) else {
            let reason = decision["reason"]
                .as_str()
                .or_else(|| verdict["errorClass"].as_str());
            let (code, message) = match reason {
                Some("beforeRuleHistoryStart") => (
                    "before_rule_history_start",
                    "Use an approved policy that covers the recorded filing date.",
                ),
                Some("reviewRuleSources") => (
                    "missing_rule_sources",
                    "Add supporting source passages for the policy versions.",
                ),
                Some("reviewRuleTransitions") => (
                    "ambiguous_policy_transitions",
                    "Ask the policy owner to resolve the rule transition dates and order.",
                ),
                Some("reviewExceptionScope") => (
                    "unresolved_policy_scope",
                    "Ask the policy owner to resolve the exception's applicability.",
                ),
                Some("rkaf:UnsupportedEvaluationAnchor") => (
                    "unsupported_evaluation_anchor",
                    "Use a consumer registration that supports this filing-date anchor.",
                ),
                _ => (
                    "no_applicable_rule",
                    "Ask the policy owner to verify the dated rule history for this case.",
                ),
            };
            outcome.unresolved(code, message);
            return outcome;
        };

        let rule = Rule {
            id: selected.to_owned(),
            label: graph
                .find(selected)
                .and_then(|node| nonblank(&node["rdfs:label"]))
                .map(str::to_owned),
        };
        outcome.passages = passages(graph, selected, &decision["sourceReferences"]);
        outcome.candidate_rule = Some(rule.clone());
        if outcome.passages.is_empty() {
            outcome.unresolved(
                "missing_pinned_rule_sources",
                "Add a supporting source fragment with a valid artifact digest.",
            );
            return outcome;
        }
        if self
            .selection
            .scope
            .as_ref()
            .is_some_and(|scope| scope != &case.office)
        {
            outcome.unresolved(
                "office_outside_policy_scope",
                "Use a policy selection approved for the recorded office or verify the office ID.",
            );
            return outcome;
        }
        request["rkaf:subjectAssertion"] = json!(selected);
        match reducer::evaluate(&request, graph) {
            Ok(verdict) if verdict.output["byScope"][&case.office] == "rkaf:officialUse" => {
                outcome.office_approvals = reducer::active_adoptions_for_scope(
                    graph, selected, &case.office, Some(&self.evaluated_at),
                )
                .filter(|node| node["rkaf:usageEligibility"] == "rkaf:officialUse")
                .filter_map(|node| nonblank(&node["@id"]).map(str::to_owned))
                .collect();
                outcome.office_approvals.sort();
                outcome.expected_rule = Some(rule);
            }
            Ok(_) => outcome.unresolved("office_approval_unavailable", "Verify the office ID and obtain official-use approval that is active at the review time."),
            Err(error) => outcome.unresolved("office_approval_unresolved", error.to_string()),
        }
        outcome
    }
}

fn valid_date(value: &str) -> bool {
    value.len() == 10
        && NaiveDate::parse_from_str(value, "%Y-%m-%d").is_ok_and(|date| date.to_string() == value)
}

fn passages(graph: &Graph<'_>, selected: &str, source_references: &Value) -> Vec<Passage> {
    let mut passages = BTreeMap::new();
    for (fragment, artifact) in pit::pinned_source_fragments(selected, graph) {
        if !source_references
            .as_array()
            .is_some_and(|references| references.iter().any(|source| source == artifact))
        {
            continue;
        }
        let fragment_id = nonblank(&fragment["@id"]);
        let fragment_digest = nonblank(&fragment["rkaf:fragmentContentDigest"]);
        let selector = &fragment["oa:hasSelector"];
        let mut quotes = selector
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(|selector| {
                (selector["@type"] == "oa:TextQuoteSelector")
                    .then(|| nonblank(&selector["oa:exact"]))
                    .flatten()
            });
        let quote = quotes.next();
        if quote
            .zip(fragment_digest)
            .is_some_and(|(quote, expected)| sha256(quote.as_bytes()) != expected)
        {
            continue;
        }
        let publisher_url = graph
            .find(artifact)
            .and_then(|node| nonblank(&node["dcterms:relation"]));
        passages.insert(
            (artifact, fragment_id, quote),
            Passage {
                fragment: fragment_id.map(str::to_owned),
                artifact: artifact.to_owned(),
                source_sha256: nonblank(&fragment["rkaf:sourceArtifactDigest"]).map(str::to_owned),
                fragment_sha256: fragment_digest.map(str::to_owned),
                exact_quote: quote.map(str::to_owned),
                publisher_url: publisher_url.map(str::to_owned),
            },
        );
    }
    passages.into_values().collect()
}
