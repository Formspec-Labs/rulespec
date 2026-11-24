//! Consumer-selection helper.
//!
//! Several behavior contracts (stale transition, reducer step 5, PIT anchor
//! check, and bridge validation) read capabilities from a
//! `rkaf:BridgeConsumerRegistration` node.

use serde_json::Value;

use crate::{errors::RuntimeError, graph::Graph};

/// Select the registration whose capabilities apply to the request.
///
/// If omitted, use the sole registration or return `None` for an unregistered graph.
///
/// # Errors
///
/// Returns `MalformedTestCase` if an explicit registration does not resolve or
/// the request omits the registration ID when multiple registrations exist.
pub fn select_consumer<'a>(
    test_case: &Value,
    graph: &'a Graph<'a>,
) -> Result<Option<&'a Value>, RuntimeError> {
    let mut registrations = graph.nodes_by_type("rkaf:BridgeConsumerRegistration");
    if let Some(explicit) = test_case.get("rkaf:evaluationConsumer") {
        let target_id = explicit
            .as_str()
            .filter(|id| !id.trim().is_empty())
            .ok_or_else(|| {
                RuntimeError::MalformedTestCase(
                    "rkaf:evaluationConsumer must be a nonempty registration ID".into(),
                )
            })?;
        return registrations
            .find(|registration| registration["@id"].as_str() == Some(target_id))
            .map(Some)
            .ok_or_else(|| {
                RuntimeError::MalformedTestCase(format!(
                    "rkaf:evaluationConsumer={target_id} does not resolve to a BCR in the graph"
                ))
            });
    }

    match (registrations.next(), registrations.next()) {
        (first, None) => Ok(first),
        (_, Some(_)) => Err(RuntimeError::MalformedTestCase(format!(
            "graph carries {} BridgeConsumerRegistration nodes; the BehaviorTestCase MUST set rkaf:evaluationConsumer to the @id of the BCR to use",
            registrations.count() + 2
        ))),
    }
}
