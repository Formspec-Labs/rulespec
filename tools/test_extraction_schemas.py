"""Check that model formatting preserves restrictions or rejects unsupported input."""
import pytest

from tools.build_extraction_schemas import inline_references, model_schema


def test_local_reference_keeps_native_restrictions_and_source_order():
    native = {"type": "object", "additionalProperties": False, "required": ["text"],
              "properties": {"text": {"$ref": "#/$defs/Text"}},
              "$defs": {"Text": {"type": "string", "minLength": 2, "maxLength": 8}}}
    metadata = {"order": ["text"], "properties": {"text": {"title": "Exact text"}}}
    result = model_schema(native, metadata)
    assert result["additionalProperties"] is False
    assert result["required"] == ["text"]
    assert result["properties"]["text"] == {"type": "string", "title": "Exact text", "minLength": 2, "maxLength": 8}


@pytest.mark.parametrize("reference,definitions", [
    ({"$ref": "https://example.org/schema"}, {}),
    ({"$ref": "#/$defs/Missing"}, {}),
    ({"$ref": "#/$defs/Cycle"}, {"Cycle": {"$ref": "#/$defs/Cycle"}}),
    ({"$ref": "#/$defs/Text", "maxLength": 2}, {"Text": {"type": "string"}}),
])
def test_unsupported_references_cannot_drop_restrictions(reference, definitions):
    with pytest.raises(ValueError):
        inline_references(reference, definitions)


def test_missing_metadata_cannot_drop_native_fields():
    native = {"type": "object", "properties": {"visible": {"type": "string"}, "lost": {"type": "string"}}}
    with pytest.raises(ValueError, match="fields differ"):
        model_schema(native, {"order": ["visible"], "properties": {"visible": {}}})
