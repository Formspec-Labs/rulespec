from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("indexed_trial", ROOT / "experiment.py")
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)


def fixture():
    old = ROOT.parent / "extraction-polish/final-names-2"
    document = json.loads((old / "document.json").read_text())
    c = json.loads((old / "candidates.json").read_text())[0]
    attrs = {k: v for k, v in c.items() if k not in ("quote", "start", "end", "window_id", "section_id")}
    concepts = [{"id": f"K{i}", "topic": v} for i, v in enumerate(attrs.pop("concepts"))]
    citations = [{"id": f"C{i}", "label": v, "quote": v} for i, v in enumerate(attrs.pop("references"))]
    attrs.update(statement=attrs.pop("summary"), role_ref="", concept_refs=[k["id"] for k in concepts],
                 citation_refs=[k["id"] for k in citations])
    return {"roles": [], "citations": citations, "concepts": concepts,
            "extractions": [{"unit": c["quote"], "unit_attributes": attrs}]}, document, c


def test_native_schema_includes_keyword_guidance_and_shared_types():
    schema = json.loads((ROOT / "provider.schema.json").read_text())
    assert list(schema["properties"]) == ["roles", "citations", "concepts", "extractions"]
    assert "unless/except/other than" in schema["description"]
    assert "must/shall/should/may/not required" in schema["description"]
    Draft202012Validator(schema).validate(fixture()[0])


def test_index_adapter_preserves_existing_candidate_meaning():
    payload, document, candidate = fixture()
    parsed, mapping = trial.normalize(payload, document, trial.e.plan_windows(document)[0])
    assert not parsed["refusals"] and not mapping["issues"]
    assert parsed["candidates"] == [candidate]


def test_missing_reference_never_silently_changes_a_statement():
    payload, document, _ = fixture()
    payload["extractions"][0]["unit_attributes"]["concept_refs"].append("unknown")
    parsed, _ = trial.normalize(payload, document, trial.e.plan_windows(document)[0])
    assert not parsed["candidates"]
    assert parsed["refusals"][0]["code"] == "missing_index_reference"
    bad = deepcopy(payload)
    bad["concepts"].append(bad["concepts"][0])
    with pytest.raises(ValueError, match="duplicate"):
        trial.normalize(bad, document, trial.e.plan_windows(document)[0])
