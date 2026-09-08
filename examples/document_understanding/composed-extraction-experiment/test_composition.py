from copy import deepcopy
import importlib.util
from pathlib import Path

from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("composed", ROOT / "experiment.py")
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)


def fixture():
    doc = prepare_document("Visitors must wear badges, except infants. Guides must keep maps.")
    schema = trial.e._load(ROOT / "meaning.schema.json")
    props = schema["properties"]["extractions"]["items"]["properties"]["unit_attributes"]["properties"]
    attrs = {k: [] if v["type"] == "array" else "" for k, v in props.items()}
    attrs.update(kind="requirement", modality="must", modality_quote="must")
    payload = {"extractions": [{"unit": "P000", "unit_attributes": {
        **attrs, "statement": statement}} for statement in (
            "Visitors must wear badges, except infants.", "Guides must keep maps.")]}
    run = {"id": "urn:test:meaning", "prompt_sha256": "first-pass"}
    book, mapping = trial.adapter.compile_output(trial.hydrate(payload), doc, run)
    return doc, payload, book, mapping


def relation(target="B000", evidence="P000"):
    return {"unit": target, "unit_attributes": {"qualifications": [{
        "relation": "exception", "statement": "Infants are exempt from the badge duty.",
        "evidence": [evidence], "references": []}]}}


def test_composition_preserves_baseline_identity_content_and_lineage():
    doc, payload, base, mapping = fixture()
    original = deepcopy(base)
    result, combined = trial.compose({"extractions": [relation()]}, payload, base, mapping, doc,
                                    {"id": "urn:test:relationships", "prompt_sha256": "second-pass"})
    assert base == original
    nodes = {n["@id"]: n for n in result["graph"]["@graph"]}
    assert all(nodes[n["@id"]] == n for n in base["graph"]["@graph"])
    by_id = {c["id"]: c for c in result["accepted"]}
    assert all(by_id[c["id"]] == c for c in base["accepted"])
    child = by_id[combined[0]["qualification_ids"][0]]
    assert child["target_ids"] == [mapping[0]["baseline_id"]]
    assert child["target_ids"] != [mapping[1]["baseline_id"]]
    old_lineage = nodes[base["accepted"][0]["meaning_assertion_id"]]["rkaf:hasAILineage"]
    new_lineage = nodes[child["meaning_assertion_id"]]["rkaf:hasAILineage"]
    assert old_lineage != new_lineage
    assert result["relationship_review"]["unreturned_or_duplicate_targets"] == ["B001"]
    assert trial.core.validate_graph(result["graph"])["shacl_conforms"]


def test_unknown_and_duplicate_targets_cannot_attach_or_replace_records():
    doc, payload, base, mapping = fixture()
    result, _ = trial.compose({"extractions": [relation(), relation(), relation("B999")]},
        payload, base, mapping, doc, {"id": "urn:test:relationships"})
    assert result["accepted"] == base["accepted"]
    assert len(result["rejected"]) == 3
    assert all(not c["target_ids"] for c in result["accepted"])


def test_bad_new_evidence_preserves_first_pass():
    doc, payload, base, mapping = fixture()
    result, _ = trial.compose({"extractions": [relation(evidence="P999")]},
        payload, base, mapping, doc, {"id": "urn:test:relationships"})
    assert result["accepted"] == base["accepted"]
    assert len(result["rejected"]) == 1
