//! The Rulespec SDK umbrella crate.
//!
//! One dependency (`cargo add rkaf`) pulls in the vocabulary ([`vocabulary`]),
//! the compiled constraint validator ([`constraints`]), the Layer 4
//! projectors ([`projectors`]) and the runtime behind a single facade. Registry
//! operations ([`registries`]) are stubs until Plan 4 (Layer 3 registries)
//! lands.

pub mod constraints;
pub mod projectors;
pub mod registries;
pub mod vocabulary;

pub use constraints::{Validator, ValidationError, ValidatorError};

/// Parse a Rulespec JSON document and validate it against the compiled schema
/// set, returning every violation rather than the first.
///
/// A validator-construction failure (embedded schemas should never fail) is
/// reported as a single [`ValidationError`] with ``type_iri``
/// ``"rkaf:Validator"``, keeping the error surface to one type.
pub fn parse_and_validate(document: &serde_json::Value) -> Result<(), Vec<ValidationError>> {
    let validator = Validator::try_new().map_err(|error| {
        vec![ValidationError {
            type_iri: "rkaf:Validator".to_string(),
            pointer: String::new(),
            message: error.to_string(),
        }]
    })?;
    validator.validate_document(document)
}
