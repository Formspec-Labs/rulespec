//! Layer 2/3 constraint validation, re-exported from `rkaf-validate`.
//!
//! [`Validator`] embeds the compiled JSON Schema set; [`ValidatorError`] is
//! the failure mode of construction (e.g. no compiled schemas) and
//! [`ValidationError`] reports every violation of a document.

pub use rkaf_validate::{ValidationError, Validator, ValidatorError};
