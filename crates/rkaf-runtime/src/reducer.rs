//! UsageEligibility reducer — spec/rkaf-behavior.md §1.

use chrono::{DateTime, Duration, FixedOffset};
use serde_json::{json, Value};

use crate::{
    errors::RuntimeError,
    graph::Graph,
    temporal::{effective_attestations_at, local_adoption_effective_at},
    verdict::Verdict,
};

/// The 7-level UsageEligibility lattice, ordered low → high.
const LATTICE: &[&str] = &[
    "rkaf:notEligible",
    "rkaf:searchOnly",
    "rkaf:reviewQueueOnly",
    "rkaf:draftGenerationAllowed",
    "rkaf:localOperationalUse",
    "rkaf:publicationAllowed",
    "rkaf:officialUse",
];

pub(crate) fn rank(level: &str) -> Option<usize> {
    LATTICE.iter().position(|&l| l == level)
}

fn max_on_lattice(a: &str, b: &str) -> String {
    let ra = rank(a).unwrap_or(0);
    let rb = rank(b).unwrap_or(0);
    LATTICE[ra.max(rb)].to_string()
}

fn min_on_lattice(a: &str, b: &str) -> String {
    let ra = rank(a).unwrap_or(LATTICE.len() - 1);
    let rb = rank(b).unwrap_or(LATTICE.len() - 1);
    LATTICE[ra.min(rb)].to_string()
}

pub fn evaluate(test_case: &Value, graph: &Graph) -> Result<Verdict, RuntimeError> {
    let consumer = crate::consumer::select_consumer(test_case, graph)?;
    let evaluation_time = parse_evaluation_time(test_case)?;
    // Locate the Assertion under evaluation. Per spec §1, the fixture MUST
    // declare `rkaf:subjectAssertion` — greenfield contract, no implicit
    // "pick the first Assertion" fallback. Graphs commonly carry multiple
    // Assertions (e.g., justification chain), so silent selection is unsafe.
    let assertion_id = test_case
        .get("rkaf:subjectAssertion")
        .and_then(Value::as_str)
        .ok_or_else(|| {
            RuntimeError::MalformedTestCase(
                "UsageEligibilityReducer fixture MUST declare rkaf:subjectAssertion (no implicit selection)".into(),
            )
        })?;
    let policy = AssertionUse::for_case(assertion_id, test_case, consumer, graph)?;

    // Determine evaluation scopes.
    // Behavior fixtures MAY carry rkaf:evaluationScopes; otherwise derive from
    // LocalAdoptions targeting the assertion.
    let mut scopes: Vec<String> = Vec::new();
    if let Some(arr) = test_case
        .get("rkaf:evaluationScopes")
        .and_then(Value::as_array)
    {
        for v in arr {
            if let Some(s) = v.as_str() {
                scopes.push(s.into());
            }
        }
    } else {
        // Derive scopes from local approvals when the request omits them.
        for la in graph.nodes_by_type("rkaf:LocalAdoption") {
            if la.get("rkaf:targetAssertion").and_then(Value::as_str) == Some(assertion_id) {
                if let Some(s) = la.get("rkaf:adoptionScope").and_then(Value::as_str) {
                    if !scopes.contains(&s.to_string()) {
                        scopes.push(s.to_string());
                    }
                }
            }
        }
        // For multi-scope reasoning the fixture must declare scopes
        // explicitly; we don't synthesize the "other scope" — too magical.
    }

    // No scopes declared → workspace-wide reduction (no LocalAdoption).
    if scopes.is_empty() {
        let ScopeResult {
            level,
            freshness_narrowed,
            level_before_freshness,
        } = policy.reduce(None, consumer, evaluation_time.as_ref(), graph)?;
        let max_days = consumer
            .and_then(|reg| {
                reg.get("rkaf:maxAttestationStalenessDays")
                    .and_then(Value::as_i64)
            })
            .unwrap_or(0);
        let rationale: String = if freshness_narrowed {
            format!(
                "freshness gate narrowed from {level_before_freshness} to {level} (maxAttestationStalenessDays={max_days})"
            )
        } else if !policy.allowed_for_case {
            "Lifecycle or the case-date condition prevents use of this assertion".into()
        } else {
            "baseline applied; no LocalAdoption broadening (workspace-wide reduction)".into()
        };
        return Ok(Verdict::new(json!({
            "effectiveUsageEligibility": level,
            "rationale": rationale,
        })));
    }

    let mut by_scope = serde_json::Map::new();
    for scope in scopes {
        let result = policy.reduce(Some(&scope), consumer, evaluation_time.as_ref(), graph)?;
        by_scope.insert(scope, Value::String(result.level));
    }
    Ok(Verdict::new(json!({ "byScope": Value::Object(by_scope) })))
}

pub(crate) fn parse_evaluation_time(
    case: &Value,
) -> Result<Option<DateTime<FixedOffset>>, RuntimeError> {
    let Some(value) = case.get("rkaf:evaluationTime") else {
        return Ok(None);
    };
    let raw = value.as_str().ok_or_else(|| {
        RuntimeError::MalformedTestCase("rkaf:evaluationTime must be an RFC 3339 timestamp".into())
    })?;
    DateTime::parse_from_rfc3339(raw).map(Some).map_err(|err| {
        RuntimeError::MalformedTestCase(format!(
            "rkaf:evaluationTime value {raw:?} is not valid RFC 3339: {err}"
        ))
    })
}

/// Internal trace of a single-scope reduction. Used by `evaluate` to
/// build a richer rationale when Step 5.5 fires; per-scope `byScope`
/// output discards the trace (the output shape carries only the level).
pub(crate) struct ScopeResult {
    pub(crate) level: String,
    freshness_narrowed: bool,
    level_before_freshness: String,
}

/// Resolve one assertion and its case-date permissions once for all requested offices.
pub(crate) struct AssertionUse<'a> {
    id: &'a str,
    baseline: &'a str,
    applicability: Vec<&'a str>,
    allowed_for_case: bool,
}

impl<'a> AssertionUse<'a> {
    pub(crate) fn for_case(
        id: &'a str,
        case: &Value,
        consumer: Option<&Value>,
        graph: &Graph<'a>,
    ) -> Result<Self, RuntimeError> {
        let assertion = graph.require(id)?;
        let baseline = assertion["rkaf:usageEligibility"]
            .as_str()
            .unwrap_or("rkaf:notEligible");
        let is_stale = assertion["rkaf:consumerLifecycleState"] == "rkaf:staleForCurrentUse";
        let allowed_for_case = crate::pit::allows_use(id, is_stale, case, consumer, graph)?;
        Ok(Self {
            id,
            baseline,
            applicability: applicability(assertion, graph),
            allowed_for_case,
        })
    }

    pub(crate) fn reduce(
        &self,
        scope: Option<&str>,
        consumer: Option<&Value>,
        evaluation_time: Option<&DateTime<FixedOffset>>,
        graph: &Graph,
    ) -> Result<ScopeResult, RuntimeError> {
        reduce_for_scope_traced(
            self.id,
            self.baseline,
            self.allowed_for_case,
            &self.applicability,
            scope,
            consumer,
            evaluation_time,
            graph,
        )
    }
}

fn applicability<'a>(assertion: &'a Value, graph: &Graph<'a>) -> Vec<&'a str> {
    // hasApplicability is a single IRI per CUE; runtime accepts a list too
    // (defensive for graphs where authors used an array). The applicability
    // set is the IRIs pointing at ApplicabilityScope nodes; we resolve each
    // to its `appliesInJurisdiction` list and union them.
    let applicability_iris: Vec<&str> = match assertion.get("rkaf:hasApplicability") {
        Some(Value::String(s)) => vec![s.as_str()],
        Some(Value::Array(arr)) => arr.iter().filter_map(Value::as_str).collect(),
        _ => Vec::new(),
    };
    let mut applicability_set: Vec<&str> = Vec::new();
    for app_iri in &applicability_iris {
        if let Some(app) = graph.find(app_iri) {
            if let Some(arr) = app
                .get("rkaf:appliesInJurisdiction")
                .and_then(Value::as_array)
            {
                for v in arr {
                    if let Some(s) = v.as_str() {
                        applicability_set.push(s);
                    }
                }
            }
            // Fall back: if appliesInJurisdiction missing, the applicability
            // IRI itself is the scope match key (a one-element set).
            if applicability_set.is_empty() {
                applicability_set.push(app_iri);
            }
        }
    }

    applicability_set
}

/// Compute effective UsageEligibility per spec/rkaf-behavior.md §1.2.
/// This entry point has no verified case date. Use [`crate::Runtime::evaluate`]
/// to supply a date for an assertion governed by a point-in-time exception.
///
/// When the consumer declares `rkaf:maxAttestationStalenessDays`, any effective
/// Attestation targeting `assertion_id` with absent or overdue `lastVerifiedAt`
/// narrows the effective level by one step.
///
/// # Errors
/// Returns [`RuntimeError`] for invalid case rules or attestation timestamps,
/// or when freshness could affect the result and `evaluation_time` is absent.
#[allow(clippy::too_many_arguments)]
pub fn reduce_for_scope(
    assertion_id: &str,
    baseline: &str,
    is_stale: bool,
    applicability_set: &[&str],
    scope: Option<&str>,
    consumer: Option<&Value>,
    evaluation_time: Option<&DateTime<FixedOffset>>,
    graph: &Graph,
) -> Result<String, RuntimeError> {
    let allowed = crate::pit::allows_use(assertion_id, is_stale, &Value::Null, consumer, graph)?;
    Ok(reduce_for_scope_traced(
        assertion_id,
        baseline,
        allowed,
        applicability_set,
        scope,
        consumer,
        evaluation_time,
        graph,
    )?
    .level)
}

#[allow(clippy::too_many_arguments)]
fn reduce_for_scope_traced(
    assertion_id: &str,
    baseline: &str,
    allowed_for_case: bool,
    applicability_set: &[&str],
    scope: Option<&str>,
    consumer: Option<&Value>,
    evaluation_time: Option<&DateTime<FixedOffset>>,
    graph: &Graph,
) -> Result<ScopeResult, RuntimeError> {
    if !allowed_for_case
        || scope.is_some_and(|id| !applicability_set.is_empty() && !applicability_set.contains(&id))
    {
        return Ok(ScopeResult {
            level: "rkaf:notEligible".into(),
            freshness_narrowed: false,
            level_before_freshness: "rkaf:notEligible".into(),
        });
    }

    let mut effective = baseline.to_owned();
    // Step 4 — LocalAdoption can broaden only after scope and case-date checks.
    if let Some(scope) = scope {
        for adoption in active_adoptions_for_scope(graph, assertion_id, scope, evaluation_time) {
            if let Some(eligibility) = adoption["rkaf:usageEligibility"].as_str() {
                effective = max_on_lattice(&effective, eligibility);
            }
        }
    }

    // Step 5.5 — freshness gate (Plan 7e.2; spec §1.2 step 5.5). Narrow one
    // lattice step downward if ANY relevant **effective** Attestation's
    // `lastVerifiedAt` is older than `evaluation_time - maxAttestationStalenessDays`.
    // Relevance signal: Attestation.targets contains `assertion_id`.
    // Effectiveness gate (Plan 7e review F1+F4): revoked or out-of-period
    // Attestations are silently excluded — they're not in the active
    // authority chain so they should not narrow freshness either.
    let level_before_freshness = effective.clone();
    let mut freshness_narrowed = false;
    if let Some(max_days) =
        consumer.and_then(|reg| reg["rkaf:maxAttestationStalenessDays"].as_i64())
    {
        let stale = match evaluation_time {
            Some(instant) => narrow_for_freshness(assertion_id, graph, instant, max_days)?,
            None if graph
                .nodes_by_type("rkaf:Attestation")
                .any(|att| targets_assertion(att, assertion_id)) =>
            {
                return Err(RuntimeError::MalformedTestCase(format!(
                    "rkaf:evaluationTime is required to check attestation freshness for {assertion_id}"
                )));
            }
            None => false,
        };
        if stale {
            effective = step_down_lattice(&effective);
            freshness_narrowed = effective != level_before_freshness;
        }
    }

    // Step 5 — consumer capability cap. Reads from the resolved consumer
    // (passed in by the dispatcher, NOT picked via .next()).
    if let Some(reg) = consumer {
        if let Some(cap) = reg.get("rkaf:capabilityCap").and_then(Value::as_str) {
            effective = min_on_lattice(&effective, cap);
        }
    }

    Ok(ScopeResult {
        level: effective,
        freshness_narrowed,
        level_before_freshness,
    })
}

/// Iterate approvals active for an assertion, office, and evaluation instant.
pub fn active_adoptions_for_scope<'a, 'graph>(
    graph: &'graph Graph<'a>,
    subject: &'graph str,
    scope: &'graph str,
    time: Option<&'graph DateTime<FixedOffset>>,
) -> impl Iterator<Item = &'a Value> + 'graph {
    graph
        .nodes_by_type("rkaf:LocalAdoption")
        .filter(move |adoption| {
            adoption["rkaf:targetAssertion"] == subject
                && adoption["rkaf:adoptionScope"] == scope
                && local_adoption_effective_at(adoption, time)
        })
}

fn targets_assertion(attestation: &Value, assertion_id: &str) -> bool {
    attestation["rkaf:targets"]
        .as_array()
        .is_some_and(|targets| targets.iter().any(|id| id.as_str() == Some(assertion_id)))
}

/// Step 5.5 helper — returns true iff a relevant **effective** Attestation
/// is stale per the BCR's `maxAttestationStalenessDays` window.
///
/// Plan 7e review F1+F4: the universe walked is
/// `effective_attestations_at(graph, evaluation_time)`, NOT every targeting
/// Attestation. Revoked or out-of-period Attestations are silently excluded
/// from the freshness narrowing (they're already excluded from the
/// underlying authority chain by `temporal::effective_at`). This is the
/// only production caller of the Plan 7e.1 helper.
///
/// "Relevant" means `Attestation.targets` contains the assertion IRI.
/// Malformed RFC-3339 on `lastVerifiedAt` propagates as `MalformedTestCase`.
/// Malformed timestamps on `revokedAt` / `effectivePeriod{Start,End}` also
/// propagate via `effective_attestations_at` (same strict posture).
fn narrow_for_freshness(
    assertion_id: &str,
    graph: &Graph,
    evaluation_time: &DateTime<FixedOffset>,
    max_days: i64,
) -> Result<bool, RuntimeError> {
    let cutoff = Duration::try_days(max_days)
        .and_then(|window| evaluation_time.checked_sub_signed(window))
        .ok_or_else(|| {
            RuntimeError::MalformedTestCase(format!(
                "rkaf:maxAttestationStalenessDays value {max_days} is out of range for rkaf:evaluationTime"
            ))
        })?;
    let effective = effective_attestations_at(graph, evaluation_time)?;
    for att in effective {
        if !targets_assertion(att, assertion_id) {
            continue;
        }
        let Some(raw) = att.get("rkaf:lastVerifiedAt").and_then(Value::as_str) else {
            // Effective Attestation with no freshness signal → does not
            // satisfy freshness, so it narrows. Author intent: a consumer
            // that declares maxAttestationStalenessDays wants every relevant
            // Attestation to carry lastVerifiedAt.
            return Ok(true);
        };
        let att_id = att
            .get("@id")
            .and_then(Value::as_str)
            .unwrap_or("<unknown>");
        let last = DateTime::parse_from_rfc3339(raw).map_err(|e| {
            RuntimeError::MalformedTestCase(format!(
                "Attestation {att_id} rkaf:lastVerifiedAt value {raw:?} is not valid RFC-3339: {e}"
            ))
        })?;
        if last < cutoff {
            return Ok(true);
        }
    }
    Ok(false)
}

fn step_down_lattice(level: &str) -> String {
    let r = rank(level).unwrap_or(0);
    if r == 0 {
        level.to_string()
    } else {
        LATTICE[r - 1].to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lattice_ordering() {
        assert!(rank("rkaf:officialUse") > rank("rkaf:publicationAllowed"));
        assert!(rank("rkaf:notEligible") < rank("rkaf:searchOnly"));
        assert_eq!(
            max_on_lattice("rkaf:officialUse", "rkaf:searchOnly"),
            "rkaf:officialUse"
        );
        assert_eq!(
            min_on_lattice("rkaf:officialUse", "rkaf:searchOnly"),
            "rkaf:searchOnly"
        );
    }
}
