//! Case-date evaluation for point-in-time exceptions (spec/rkaf-behavior.md §4).

use std::collections::{BTreeSet, HashMap, HashSet};

use chrono::NaiveDate;
use serde_json::{json, Value};

use crate::{
    consumer::select_consumer,
    errors::RuntimeError,
    graph::{has_type, Graph},
    verdict::Verdict,
};

const EXCEPTION_TYPE: &str = "rkaf:PointInTimeException";
const PRIOR: &str = "rkaf:retainsAssertion";
const SUCCESSOR: &str = "rkaf:successorAssertion";
const ANCHOR: &str = "rkaf:evaluationAnchor";
const CUTOFF: &str = "rkaf:anchorDateBefore";
const REVIEW_TRANSITIONS: &str = "reviewRuleTransitions";

enum Window {
    Dated { cutoff: NaiveDate, date: NaiveDate },
    Review(&'static str),
}

enum Selection<'a> {
    Rule {
        id: &'a str,
        retained: bool,
        sources: Vec<&'a str>,
    },
    OutsideWindow,
    Review(&'static str),
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
        .filter(|value| !value.trim().is_empty())
        .ok_or_else(|| {
            RuntimeError::MalformedTestCase(format!(
                "required string field {field} is missing or invalid"
            ))
        })
}

pub(crate) fn supports_anchor(consumer: Option<&Value>, anchor: &str) -> bool {
    consumer
        .and_then(|reg| reg["rkaf:supportedEvaluationAnchors"].as_array())
        .is_some_and(|anchors| anchors.iter().any(|value| value.as_str() == Some(anchor)))
}

fn unsupported_anchor<'a>(
    links: &[&'a Value],
    consumer: Option<&Value>,
) -> Result<Option<&'a str>, RuntimeError> {
    let mut unsupported = None;
    for link in links {
        let anchor = required_string(link, ANCHOR)?;
        if !supports_anchor(consumer, anchor) {
            unsupported = Some(unsupported.map_or(anchor, |previous: &str| previous.min(anchor)));
        }
    }
    Ok(unsupported)
}

fn window(exception: &Value, case: &Value) -> Result<Window, RuntimeError> {
    let anchor = required_string(exception, ANCHOR)?;
    let Some(cutoff) = exception.get(CUTOFF) else {
        return Ok(Window::Review("reviewExceptionScope"));
    };
    let cutoff = calendar_date(cutoff, CUTOFF)?;
    if exception
        .get("rkaf:exceptionScope")
        .is_some_and(|scope| !scope.as_str().is_some_and(|text| text.trim().is_empty()))
    {
        // The prose may impose additional conditions that the engine cannot verify.
        return Ok(Window::Review("reviewExceptionScope"));
    }
    if case[ANCHOR].as_str() != Some(anchor)
        || case["rkaf:caseDateVerified"].as_bool() != Some(true)
        || case["rkaf:caseDate"].is_null()
    {
        return Ok(Window::Review("verifyCaseDate"));
    }
    let date = calendar_date(&case["rkaf:caseDate"], "rkaf:caseDate")?;
    Ok(Window::Dated { cutoff, date })
}

pub(crate) fn assertion<'a>(graph: &Graph<'a>, id: &str) -> Result<&'a Value, RuntimeError> {
    let node = graph.require(id)?;
    // Use the assertion family defined in Core §4.3. Runtime input does not
    // include the subclass triples that SHACL uses to recognize these types.
    if [
        "rkaf:Assertion",
        "rkaf:ValueAssertion",
        "rkaf:RelationshipAssertion",
        "rkaf:ConceptAssignment",
        "rkaf:ConceptMapping",
        "rkaf:ClosureClaim",
        "rkaf:RelationChangeEvent",
    ]
    .iter()
    .any(|kind| has_type(node, kind))
    {
        Ok(node)
    } else {
        Err(RuntimeError::MalformedTestCase(format!(
            "{id} must identify an Assertion"
        )))
    }
}

fn evidence_bindings<'a, 'graph>(
    id: &'graph str,
    graph: &'graph Graph<'a>,
) -> impl Iterator<Item = &'a Value> + use<'a, 'graph> {
    graph
        .nodes_by_type("rkaf:EvidenceBinding")
        .filter(move |binding| binding["rkaf:bindsAssertion"].as_str() == Some(id))
}

fn source_references<'a>(id: &str, rule: &'a Value, graph: &Graph<'a>) -> Vec<&'a str> {
    let mut bindings = evidence_bindings(id, graph).peekable();
    if bindings.peek().is_none() {
        // Behavior-only callers may still cite sources through direct PROV
        // derivation. Canonical bindings take precedence when present.
        return rule["prov:wasDerivedFrom"]
            .as_array()
            .and_then(|references| {
                references
                    .iter()
                    .map(|reference| reference.as_str().filter(|iri| !iri.trim().is_empty()))
                    .collect()
            })
            .unwrap_or_default();
    }
    bound_source_references(bindings, graph, false)
}

/// List supporting Artifact IDs with pinned source fragments.
///
/// Each fragment needs the SHA-256 digest of its source bytes (Core §4.2).
/// The digest must agree with the Artifact digest when the graph supplies one.
/// The returned IDs are distinct and sorted.
pub fn pinned_source_references<'a>(subject: &str, graph: &Graph<'a>) -> Vec<&'a str> {
    bound_source_references(evidence_bindings(subject, graph), graph, true)
}

fn has_source_pin(fragment: &Value, artifact: &Value) -> bool {
    let Some(digest) = fragment["rkaf:sourceArtifactDigest"].as_str() else {
        return false;
    };
    let Some(hex) = digest.strip_prefix("sha256:") else {
        return false;
    };
    hex.len() == 64
        && hex
            .bytes()
            .all(|digit| matches!(digit, b'0'..=b'9' | b'a'..=b'f'))
        && artifact
            .get("rkaf:hasContentDigest")
            .is_none_or(|value| value.as_str() == Some(digest))
}

fn bound_source_references<'a>(
    bindings: impl Iterator<Item = &'a Value>,
    graph: &Graph<'a>,
    require_digest: bool,
) -> Vec<&'a str> {
    // Only affirmative evidence that can express the rule contributes a
    // citation. The role and function are independent in Core §4.3.
    let sources: BTreeSet<_> = bindings
        .filter(|binding| {
            binding.get("rkaf:noEvidenceReason").is_none()
                && binding["rkaf:evidentiaryFunction"] == "rkaf:supports"
                && matches!(
                    binding["rkaf:evidenceRole"].as_str(),
                    Some(
                        "rkaf:textualEvidence"
                            | "rkaf:structuralEvidence"
                            | "rkaf:authorityCitation"
                            | "rkaf:officialSourceMetadata"
                    )
                )
        })
        .filter_map(|binding| binding["rkaf:bindsSourceFragment"].as_array())
        .flatten()
        .filter_map(|fragment| graph.find(fragment.as_str()?))
        .filter(|fragment| has_type(fragment, "rkaf:SourceFragment"))
        .filter_map(|fragment| {
            let source = fragment["oa:hasSource"].as_str()?;
            let artifact = graph.find(source)?;
            (has_type(artifact, "rkaf:Artifact")
                && (!require_digest || has_source_pin(fragment, artifact)))
            .then_some(source)
        })
        .collect();
    sources.into_iter().collect()
}

fn connected_exceptions<'a>(id: &str, graph: &Graph<'a>) -> Vec<&'a Value> {
    let exceptions: Vec<_> = graph.nodes_by_type(EXCEPTION_TYPE).collect();
    let mut by_assertion = HashMap::<&str, Vec<usize>>::new();
    for (index, link) in exceptions.iter().enumerate() {
        for field in [PRIOR, SUCCESSOR] {
            if let Some(assertion) = link[field].as_str() {
                by_assertion.entry(assertion).or_default().push(index);
            }
        }
    }
    let mut pending = vec![id];
    let mut seen = HashSet::new();
    let mut connected = Vec::new();
    while let Some(assertion) = pending.pop() {
        for &index in by_assertion.remove(assertion).iter().flatten() {
            if seen.insert(index) {
                let link = exceptions[index];
                connected.push(link);
                pending.extend(
                    [PRIOR, SUCCESSOR]
                        .iter()
                        .filter_map(|field| link[field].as_str()),
                );
            }
        }
    }
    connected
}

fn ordered_exceptions<'a>(links: &[&'a Value]) -> Result<Option<Vec<&'a Value>>, RuntimeError> {
    let mut by_prior = HashMap::new();
    let mut successors = HashSet::new();
    for &link in links {
        let prior = required_string(link, PRIOR)?;
        if by_prior.insert(prior, link).is_some() {
            return Ok(None);
        }
        if link.get(SUCCESSOR).is_some() && !successors.insert(required_string(link, SUCCESSOR)?) {
            return Ok(None);
        }
    }
    let Some(root) = by_prior
        .keys()
        .find(|prior| !successors.contains(*prior))
        .copied()
    else {
        return Ok(None);
    };
    let mut ordered = Vec::with_capacity(links.len());
    let mut current = root;
    // A connected history can have only one linear ordering. Removing visited
    // links keeps the walk bounded even if policy data contains a cycle.
    while let Some(link) = by_prior.remove(current) {
        ordered.push(link);
        let Some(next) = link[SUCCESSOR].as_str() else {
            break;
        };
        current = next;
    }
    Ok(by_prior.is_empty().then_some(ordered))
}

fn resolve_chain<'a>(
    first: &'a Value,
    links: &[&'a Value],
    case: &Value,
    graph: &Graph<'a>,
) -> Result<Selection<'a>, RuntimeError> {
    let mut selected = Some(required_string(first, PRIOR)?);
    let mut previous_cutoff = None;

    for link in links {
        let (cutoff, date) = match window(link, case)? {
            Window::Dated { cutoff, date } => (cutoff, date),
            Window::Review(reason) => return Ok(Selection::Review(reason)),
        };
        if previous_cutoff.is_some_and(|previous| cutoff <= previous) {
            return Ok(Selection::Review(REVIEW_TRANSITIONS));
        }
        previous_cutoff = Some(cutoff);
        if date >= cutoff {
            selected = link[SUCCESSOR].as_str();
        }
    }

    let Some(selected) = selected else {
        return Ok(Selection::OutsideWindow);
    };
    let standalone = links.len() == 1 && first.get(SUCCESSOR).is_none();
    let mut sources = Vec::new();
    let mut retained = false;
    for id in rule_ids(links) {
        let id = id?;
        let references = source_references(id, assertion(graph, id)?, graph);
        if !standalone && references.is_empty() {
            return Ok(Selection::Review("reviewRuleSources"));
        }
        if id == selected {
            sources = references;
            retained = links.iter().any(|link| link[PRIOR].as_str() == Some(id));
        }
    }
    Ok(Selection::Rule {
        id: selected,
        retained,
        sources,
    })
}

fn rule_ids<'a, 'links>(
    links: &'links [&'a Value],
) -> impl Iterator<Item = Result<&'a str, RuntimeError>> + use<'a, 'links> {
    let terminal = links.last().and_then(|link| link[SUCCESSOR].as_str());
    links
        .iter()
        .map(|link| required_string(link, PRIOR))
        .chain(terminal.map(Ok))
}

/// Return the IDs of versions linked to an assertion, from oldest to newest.
///
/// An assertion without linked versions returns only its own ID. This looks up
/// the versions for callers that need to distinguish a mistimed citation from
/// one about a different rule.
///
/// # Errors
///
/// Returns an error if the links are ambiguous or do not identify assertions.
pub fn rule_family(subject: &str, graph: &Graph<'_>) -> Result<Vec<String>, RuntimeError> {
    let connected = connected_exceptions(subject, graph);
    if connected.is_empty() {
        assertion(graph, subject)?;
        return Ok(vec![subject.to_owned()]);
    }
    let links = ordered_exceptions(&connected)?.ok_or_else(|| {
        RuntimeError::MalformedTestCase(format!("ambiguous rule succession for {subject}"))
    })?;
    rule_ids(&links)
        .map(|id| {
            let id = id?;
            assertion(graph, id)?;
            Ok(id.to_owned())
        })
        .collect()
}

/// Check a version's case-date conditions before local approval can broaden use.
pub(crate) fn allows_use(
    id: &str,
    stale: bool,
    case: &Value,
    consumer: Option<&Value>,
    graph: &Graph,
) -> Result<bool, RuntimeError> {
    let connected = connected_exceptions(id, graph);
    if connected.is_empty() {
        return Ok(!stale);
    }
    // Standalone retentions preserve existing eligibility for a current rule.
    if !stale && connected.iter().all(|link| link.get(SUCCESSOR).is_none()) {
        return Ok(true);
    }
    if unsupported_anchor(&connected, consumer)?.is_some() {
        return Ok(false);
    }
    let Some(links) = ordered_exceptions(&connected)? else {
        return Ok(false);
    };
    Ok(matches!(
        resolve_chain(links[0], &links, case, graph)?,
        Selection::Rule { id: selected, retained, .. } if selected == id && (!stale || retained)
    ))
}

fn decision_record(
    prior: &str,
    node: &Value,
    anchor: &str,
    decision: Value,
    retained: bool,
) -> Verdict {
    let state = node["rkaf:consumerLifecycleState"]
        .as_str()
        .unwrap_or("rkaf:operational");
    let short = anchor.strip_prefix("rkaf:").unwrap_or(anchor);
    Verdict::new(json!({
        format!("{prior}.effectiveStateForAnchor:{short}"): if retained { "rkaf:retainedForPointInTime" } else { state },
        format!("{prior}.effectiveStateForCurrentUse"): state,
        "caseDecision": decision,
    }))
}

/// Evaluate the named retention and return the case-date evidence a consumer can save.
///
/// # Errors
///
/// Returns an error for a missing rule or malformed request or policy data.
pub fn evaluate(case: &Value, graph: &Graph) -> Result<Verdict, RuntimeError> {
    let subject = case
        .get("rkaf:subjectAssertion")
        .map(|_| required_string(case, "rkaf:subjectAssertion"))
        .transpose()?;
    let mut candidates = graph.nodes_by_type(EXCEPTION_TYPE).filter(|exception| {
        exception[PRIOR]
            .as_str()
            .is_some_and(|prior| subject.is_none() || subject == Some(prior))
    });
    let first = candidates.next().ok_or_else(|| {
        RuntimeError::MalformedTestCase(
            "no PointInTimeException retains the subject assertion".into(),
        )
    })?;
    let competing = candidates.next().is_some();
    if competing && subject.is_none() {
        return Err(RuntimeError::MalformedTestCase(
            "rkaf:subjectAssertion is required when multiple exceptions retain assertions".into(),
        ));
    }

    let prior = required_string(first, PRIOR)?;
    let node = assertion(graph, prior)?;
    let consumer = select_consumer(case, graph)?;
    let connected = connected_exceptions(prior, graph);
    if let Some(anchor) = unsupported_anchor(&connected, consumer)? {
        return Ok(Verdict::new(json!({
            "errorClass": "rkaf:UnsupportedEvaluationAnchor",
            "rationale": format!("Consumer does not support {anchor}"),
        })));
    }
    let anchor = if competing {
        case[ANCHOR].as_str().unwrap_or_default()
    } else {
        required_string(first, ANCHOR)?
    };
    let mut decision = if competing {
        json!({ "exception": null, "anchor": case[ANCHOR], "cutoff": null })
    } else {
        json!({
            "exception": required_string(first, "@id")?,
            "anchor": anchor,
            "cutoff": first[CUTOFF],
        })
    };
    let selection = if let Some(links) = ordered_exceptions(&connected)? {
        if links.len() > 1 {
            decision["transitions"] = json!(links
                .iter()
                .map(|link| json!({ "exception": link["@id"], "cutoff": link[CUTOFF] }))
                .collect::<Vec<_>>());
        }
        match resolve_chain(links[0], &links, case, graph)? {
            // A request naming a later subject cannot cite a version from
            // before that subject became applicable.
            Selection::Rule { id, .. }
                if links
                    .iter()
                    .take_while(|link| link[PRIOR] != prior)
                    .any(|link| link[PRIOR] == id) =>
            {
                Selection::Review(REVIEW_TRANSITIONS)
            }
            selection => selection,
        }
    } else {
        Selection::Review(REVIEW_TRANSITIONS)
    };
    let mut retained = false;
    match selection {
        Selection::Rule { id, sources, .. } => {
            retained = id == prior;
            decision["status"] = json!(if retained {
                "priorRule"
            } else {
                "successorRule"
            });
            decision["verifiedCaseDate"] = case["rkaf:caseDate"].clone();
            decision["selectedAssertion"] = json!(id);
            decision["sourceReferences"] = json!(sources);
        }
        Selection::OutsideWindow => {
            decision["status"] = json!("outsideWindow");
            decision["verifiedCaseDate"] = case["rkaf:caseDate"].clone();
        }
        Selection::Review(reason) => {
            decision["status"] = json!("needsReview");
            decision["reason"] = json!(reason);
        }
    }
    Ok(decision_record(prior, node, anchor, decision, retained))
}
