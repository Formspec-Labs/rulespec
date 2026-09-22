//! Umbrella-crate conformance: vocabulary round-trips, validation through the
//! facade, and one projector operation per carrier. Registry/federation ops
//! are skipped until Plan 4.

use std::path::PathBuf;

use rkaf::projectors::Projector;
use serde_json::Value;

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

#[test]
fn vocabulary_literals_round_trip_through_serde() {
    let literal = rkaf::vocabulary::LanguageTaggedString {
        value: "Standards of Performance".to_string(),
        language: "en".to_string(),
    };
    let encoded = serde_json::to_value(&literal).expect("serialize");
    let decoded: rkaf::vocabulary::LanguageTaggedString =
        serde_json::from_value(encoded).expect("deserialize");
    assert_eq!(decoded.value, literal.value);
    assert_eq!(decoded.language, "en");
}

#[test]
fn the_facade_validates_a_reference_corpus_document() {
    let document: Value = serde_json::from_str(include_str!(
        "../../../reference-corpora/us-rulemaking/v0.2/data/epa-oil-and-gas-climate-review.jsonld"
    ))
    .expect("parse corpus document");
    rkaf::parse_and_validate(&document).expect("corpus document validates");
}

#[test]
fn the_facade_reports_every_violation_of_a_wrong_document() {
    let document: Value = serde_json::from_str(
        r#"{"@context": "../../../context/rkaf-context.jsonld",
            "@graph": [{"@type": "rkaf:Artifact"}]}"#,
    )
    .expect("parse");
    let errors = rkaf::parse_and_validate(&document).expect_err("missing identifiers refuse");
    assert!(!errors.is_empty());
}

#[tokio::test]
async fn the_json_schema_projector_attaches_an_overlay() {
    let projector = rkaf::projectors::JsonSchemaProjector::with_repo_root(repo_root());
    let native: Value = serde_json::json!({"dcterms:title": "Example"});
    let overlay: Value = serde_json::json!({"rkaf:assertionOrigin": "rkaf:agent"});
    let merged = projector.attach(native, overlay).await.expect("attach");
    assert_eq!(merged["dcterms:title"], "Example");
    let (extracted_native, extracted_overlay) =
        projector.extract(merged).await.expect("extract");
    assert_eq!(extracted_native["dcterms:title"], "Example");
    assert_eq!(extracted_overlay["rkaf:assertionOrigin"], "rkaf:agent");
}
