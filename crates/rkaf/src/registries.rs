//! Registry client stub.
//!
//! Real registry operations (resolve, pull, federation) are gated on Plan 4
//! (Layer 3 registries). This module exists so the umbrella crate exposes a
//! stable surface today; every operation returns [`RegistryUnavailable`]
//! until the plan lands and this module stops being a stub.

use std::fmt;

/// Every registry operation fails with this until Plan 4 lands.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct RegistryUnavailable;

impl fmt::Display for RegistryUnavailable {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "registry operations are not implemented: gated on Plan 4")
    }
}

impl std::error::Error for RegistryUnavailable {}

/// Resolve an IRI to its registered artifact. Not implemented: see module docs.
pub fn resolve_artifact(_iri: &str) -> Result<serde_json::Value, RegistryUnavailable> {
    Err(RegistryUnavailable)
}
