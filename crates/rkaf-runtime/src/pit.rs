//! Case-date evaluation for point-in-time exceptions (spec/rkaf-behavior.md §4).

use chrono::NaiveDate;
use serde_json::{json, Value};

use crate::{consumer::select_consumer, errors::RuntimeError, graph::Graph, verdict::Verdict};

#[derive(Clone, Copy, PartialEq)]
enum Window {
    Before,
    OnOrAfter,
    Review(&'static str),
    UnsupportedAnchor,
}

fn calendar_date(value: &Value, field: &str) -> Result<NaiveDate, RuntimeError> {
    let date = value.as_str().and_then(|raw| {
        let parsed = NaiveDate::parse_from_str(raw, "%Y-%m-%d").ok()?;
        (raw.len() == 10 && parsed.to_string() == raw).then_some(parsed)
    });
    date.ok_or_else(|| {
        RuntimeError::MalformedTestCase(format!("{field} must be a YYYY-MM-DD calendar date"))
    })
}

fn required_string<'a>(node: &'a Value, field: &str) -> Result<&'a str, RuntimeError> {
    node[field]
        .as_str()
        .filter(|id| !id.is_empty())
        .ok_or_else(|| {
            RuntimeError::MalformedTestCase(format!(
                "required string field {field} is missing or invalid"
            ))
        })
}

fn window(
    exception: &Value,
    anchor: &str,
    case: &Value,
    consumer: Option<&Value>,
) -> Result<Window, RuntimeError> {
    let supported = consumer
        .and_then(|reg| reg["rkaf:supportedEvaluationAnchors"].as_array())
        .is_some_and(|anchors| anchors.iter().any(|value| value.as_str() == Some(anchor)));
    if !supported {
        return Ok(Window::UnsupportedAnchor);
    }
    let Some(cutoff) = exception.get("rkaf:anchorDateBefore") else {
        return Ok(Window::Review("reviewExceptionScope"));
    };
    let cutoff = calendar_date(cutoff, "rkaf:anchorDateBefore")?;
    if exception
        .get("rkaf:exceptionScope")
        .is_some_and(|scope| !scope.as_str().is_some_and(|text| text.trim().is_empty()))
    {
        // The prose may impose additional conditions that the engine cannot verify.
        return Ok(Window::Review("reviewExceptionScope"));
    }
    if case["rkaf:evaluationAnchor"].as_str() != Some(anchor)
        || case["rkaf:caseDateVerified"].as_bool() != Some(true)
        || case["rkaf:caseDate"].is_null()
    {
        return Ok(Window::Review("verifyCaseDate"));
    }
    let date = calendar_date(&case["rkaf:caseDate"], "rkaf:caseDate")?;
    Ok(if date < cutoff {
        Window::Before
    } else {
        Window::OnOrAfter
    })
}

/// Check a version's case-date conditions before local approval can broaden its use.
pub(crate) fn allows_use(
    id: &str,
    stale: bool,
    case: &Value,
    consumer: Option<&Value>,
    graph: &Graph,
) -> Result<bool, RuntimeError> {
    let mut retained = false;
    for exception in graph.nodes_by_type("rkaf:PointInTimeException") {
        let prior = exception["rkaf:retainsAssertion"].as_str();
        let successor = exception["rkaf:successorAssertion"].as_str();
        if prior != Some(id) && successor != Some(id) {
            continue;
        }
        // A retention-only exception matters only when the assertion is stale.
        if !stale && exception.get("rkaf:successorAssertion").is_none() {
            continue;
        }
        validate_pair(exception, graph)?;
        let anchor = required_string(exception, "rkaf:evaluationAnchor")?;
        let result = window(exception, anchor, case, consumer)?;
        if successor.is_some() {
            let required = if prior == Some(id) {
                Window::Before
            } else {
                Window::OnOrAfter
            };
            if result != required {
                return Ok(false);
            }
        }
        retained |= prior == Some(id) && result == Window::Before;
    }
    Ok(!stale || retained)
}

fn assertion<'a>(graph: &Graph<'a>, id: &str) -> Result<&'a Value, RuntimeError> {
    let node = graph.require(id)?;
    if crate::graph::has_type(node, "rkaf:Assertion") {
        Ok(node)
    } else {
        Err(RuntimeError::MalformedTestCase(format!(
            "{id} must identify an Assertion"
        )))
    }
}

fn validate_pair(exception: &Value, graph: &Graph) -> Result<(), RuntimeError> {
    if let Some(next) = exception.get("rkaf:successorAssertion") {
        let (Some(prior), Some(next)) =
            (exception["rkaf:retainsAssertion"].as_str(), next.as_str())
        else {
            return Err(RuntimeError::MalformedTestCase(
                "a case-date rule pair requires two assertion IDs".into(),
            ));
        };
        if prior == next {
            return Err(RuntimeError::MalformedTestCase(
                "a case-date rule pair requires distinct assertions".into(),
            ));
        }
        for id in [prior, next] {
            let rule = assertion(graph, id)?;
            let cited = rule["prov:wasDerivedFrom"]
                .as_array()
                .is_some_and(|sources| {
                    !sources.is_empty()
                        && sources
                            .iter()
                            .all(|source| source.as_str().is_some_and(|iri| !iri.trim().is_empty()))
                });
            if !cited {
                return Err(RuntimeError::MalformedTestCase(format!(
                    "case-date rule {id} requires source references in prov:wasDerivedFrom"
                )));
            }
        }
    }
    Ok(())
}

/// Evaluate the named retention and return the case-date evidence a consumer can save.
pub fn evaluate(case: &Value, graph: &Graph) -> Result<Verdict, RuntimeError> {
    let subject = case
        .get("rkaf:subjectAssertion")
        .map(|_| required_string(case, "rkaf:subjectAssertion"))
        .transpose()?;
    let mut candidates = graph
        .nodes_by_type("rkaf:PointInTimeException")
        .filter(|exception| {
            exception["rkaf:retainsAssertion"]
                .as_str()
                .is_some_and(|prior| subject.is_none() || subject == Some(prior))
        });
    let exception = candidates.next().ok_or_else(|| {
        RuntimeError::MalformedTestCase(
            "no PointInTimeException retains the subject assertion".into(),
        )
    })?;
    if candidates.next().is_some() {
        return Err(RuntimeError::MalformedTestCase(
            "evaluate one retention per subject in a PointInTimeException request".into(),
        ));
    }
    let prior = required_string(exception, "rkaf:retainsAssertion")?;
    let exception_id = required_string(exception, "@id")?;
    let anchor = required_string(exception, "rkaf:evaluationAnchor")?;
    let consumer = select_consumer(case, graph)?;
    let node = assertion(graph, prior)?;
    validate_pair(exception, graph)?;
    let result = window(exception, anchor, case, consumer)?;
    let state = node["rkaf:consumerLifecycleState"]
        .as_str()
        .unwrap_or("rkaf:operational");
    let mut decision = json!({
        "exception": exception_id, "anchor": anchor, "cutoff": exception["rkaf:anchorDateBefore"],
    });
    let selected = match result {
        Window::Before => {
            decision["status"] = json!("priorRule");
            Some(node)
        }
        Window::OnOrAfter => {
            let successor = exception["rkaf:successorAssertion"].as_str();
            decision["status"] = json!(if successor.is_some() {
                "successorRule"
            } else {
                "outsideWindow"
            });
            successor.map(|id| assertion(graph, id)).transpose()?
        }
        Window::Review(reason) => {
            decision["status"] = json!("needsReview");
            decision["reason"] = json!(reason);
            None
        }
        Window::UnsupportedAnchor => {
            return Ok(Verdict::new(json!({
                "errorClass": "rkaf:UnsupportedEvaluationAnchor",
                "rationale": format!("Consumer does not support {anchor}"),
            })))
        }
    };
    if matches!(result, Window::Before | Window::OnOrAfter) {
        decision["verifiedCaseDate"] = case["rkaf:caseDate"].clone();
    }
    let mut retained = result == Window::Before;
    if let Some(rule) = selected {
        let id = required_string(rule, "@id")?;
        // A later transition may also constrain this version. A request about one
        // exception must never issue a citation that another known date gate blocks.
        if allows_use(id, false, case, consumer, graph)? {
            decision["selectedAssertion"] = json!(id);
            decision["sourceReferences"] = rule
                .get("prov:wasDerivedFrom")
                .cloned()
                .unwrap_or_else(|| json!([]));
        } else {
            decision["status"] = json!("needsReview");
            decision["reason"] = json!("reviewRuleTransitions");
            retained = false;
        }
    }
    let short = anchor.strip_prefix("rkaf:").unwrap_or(anchor);
    Ok(Verdict::new(json!({
        format!("{prior}.effectiveStateForAnchor:{short}"): if retained { "rkaf:retainedForPointInTime" } else { state },
        format!("{prior}.effectiveStateForCurrentUse"): state,
        "caseDecision": decision,
    })))
}
