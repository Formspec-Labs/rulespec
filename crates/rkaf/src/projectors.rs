//! Layer 4 projectors: the [`Projector`] trait and the three concrete
//! carriers (JSON Schema, JSON-LD, OpenAPI).

pub use rkaf_projector_core::Projector;
pub use rkaf_projector_json_ld::JsonLdProjector;
pub use rkaf_projector_json_schema::JsonSchemaProjector;
pub use rkaf_projector_openapi::OpenApiProjector;
