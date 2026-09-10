"""Protect candidate evidence constraints and generated-schema consistency."""
from copy import deepcopy
import shutil

from jsonschema import Draft202012Validator
import pytest

from rulespec_extrapolator import schemas


@pytest.mark.parametrize("change,valid", [
    ({"actor": ""}, True),
    ({"quote": ""}, False),
    ({"summary": ""}, False),
    ({"scope_quotes": []}, True),
    ({"scope_quotes": ["same", "same"]}, False),
    ({"context_quotes": [""]}, False),
    ({"alternative_quotes": ["first", "second"]}, True),
    ({"applies_to": ["same", "same"]}, True),
    ({"start": None}, True),
    ({"start": 0}, True),
    ({"end": -1}, False),
    ({"start": True}, False),
    ({"start": 0.5}, False),
    ({"kind": "invented-class"}, False),
    ({"extra": "unstated"}, False),
])
def test_candidate_retains_evidence_and_offset_constraints(change, valid):
    candidate = {"kind": "requirement", "summary": "Staff must log requests.",
                 "actor": "Staff", "quote": "Staff must log requests.", **change}
    assert Draft202012Validator(schemas.load_schema("candidate")).is_valid(candidate) == valid


def test_provider_allows_omitted_or_null_scope_list():
    from test_extraction import row
    payload = {"terms": [], "extractions": [row()]}
    validator = Draft202012Validator(schemas.load_schema("provider"))
    assert validator.is_valid(payload)
    del payload["extractions"][0]["unit_attributes"]["scope_quotes"]
    assert validator.is_valid(payload)
    payload["extractions"][0]["unit_attributes"]["scope_quotes"] = None
    assert validator.is_valid(payload)


@pytest.mark.parametrize("filename", ["document-understanding.cue", "cue.mod/module.cue",
                                     "candidate.schema.json", "meaning.schema.json", "provider.schema.json", "inventory.schema.json", "enrichment.schema.json"])
def test_inconsistent_source_or_output_refuses_to_load(tmp_path, monkeypatch, filename):
    copied = tmp_path / "schema_data"
    shutil.copytree(schemas.SCHEMA_DATA, copied)
    monkeypatch.setattr(schemas, "SCHEMA_DATA", copied)
    path = copied / filename
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(RuntimeError, match="differs from its build manifest"):
        schemas.load_schema("provider")


def test_loaded_schemas_are_independent_copies():
    first = schemas.load_schema("provider")
    first["properties"].clear()
    assert "extractions" in schemas.load_schema("provider")["properties"]


def test_model_fields_use_shared_core_enums_and_concepts_come_first():
    from rulespec_conformance.contract import resources
    fields = schemas.UNIT_FIELDS
    assert next(iter(fields)) == 'concepts'
    for field, property_, filename, definition in [
        ('concepts', 'role', 'concept-assignment', 'ConceptAssignmentPredicate'),
        ('claimants', 'attribution', 'source-claimant', 'ClaimantAttribution'),
        ('typed_values', 'datatype', 'value-assertion', 'ValueDatatype'),
    ]:
        shared = resources.json_schema(filename)['$defs'][definition]['enum']
        assert set(fields[field]['items']['properties'][property_]['enum']) == set(shared)
