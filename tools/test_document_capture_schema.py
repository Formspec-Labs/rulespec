"""The DocumentCapture v1 parent schema and its composition rule.

Run through the repository's tooling runner, never a bare interpreter:

    uv run --no-project --python 3.12 --with-requirements requirements.txt python -m unittest tools.test_document_capture_schema

``--no-project`` is what the Makefile passes for the same reason its
``requirements.txt`` states: building the project force-includes the generated
``compiled/`` tree, so a fresh checkout cannot ``uv run --frozen`` before
``make compile``. The gate here needs only ``jsonschema``.
"""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "release-records" / "schemas" / "document-capture-v1.schema.json"
FIXTURES = ROOT / "release-records" / "fixtures" / "document-capture-v1"


def sha256(data: bytes | str) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def check_profile_composition(profile: dict, parent: dict, parent_digest: str) -> list[str]:
    """A profile references the parent by id and digest and narrows only profile.* and node kind/ext.

    This is the rule spec/document-capture.md §4 states. spicy-docs carries the
    same check beside its profiles because it cannot import this repository's
    tools; the two copies are the cost of the ownership split and are kept
    word-for-word so a divergence is a diff, not a debate.
    """
    problems = []
    if profile.get("x-parent") != {"$id": parent["$id"], "sha256": parent_digest}:
        problems.append("x-parent pin differs from the parent")
    clauses = profile.get("allOf", [])
    if len(clauses) != 2 or clauses[0] != {"$ref": parent["$id"]}:
        problems.append("allOf must be exactly [{$ref: parent $id}, own narrowing]")
        return problems
    own = clauses[1]
    if set(own) - {"properties"} or set(own.get("properties", {})) - {"profile", "nodes"}:
        problems.append("a profile may narrow only properties.profile and properties.nodes")
    if set(own.get("properties", {}).get("profile", {}).get("properties", {})) - {"name", "version", "ext"}:
        problems.append("a profile may narrow only profile.name, profile.version and profile.ext")
    node_keys: set[str] = set()
    items = own.get("properties", {}).get("nodes", {}).get("items", {})
    for clause in items.get("allOf", []):
        node_keys |= set(clause.get("properties", {})) | set(clause.get("then", {}).get("properties", {}))
    if set(items) - {"allOf"} or node_keys - {"kind", "ext"}:
        problems.append(f"a profile may narrow only node kind and ext, not {sorted(node_keys - {'kind', 'ext'})}")
    return problems


class DocumentCaptureSchemaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema_bytes = SCHEMA.read_bytes()
        cls.schema = json.loads(cls.schema_bytes)
        cls.registry = Registry().with_resource(cls.schema["$id"], Resource.from_contents(cls.schema))
        cls.validator = Draft202012Validator(cls.schema, registry=cls.registry)
        cls.valid = json.loads((FIXTURES / "minimal-valid.json").read_text())
        cls.profile = json.loads((FIXTURES / "profile-example.schema.json").read_text())

    def test_schema_is_a_valid_draft_2020_12_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        self.assertEqual(self.schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_minimal_fixture_validates_and_pins_this_schema(self) -> None:
        self.assertEqual([], [e.message for e in self.validator.iter_errors(self.valid)])
        self.assertEqual(self.valid["schema"], {"$id": self.schema["$id"], "sha256": sha256(self.schema_bytes)})

    def test_root_is_closed_and_every_top_level_field_is_required(self) -> None:
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(sorted(self.schema["properties"]), sorted(self.schema["required"]))

    def test_negative_controls(self) -> None:
        def broken(mutate):
            doc = copy.deepcopy(self.valid)
            mutate(doc)
            return [e.message for e in self.validator.iter_errors(doc)]

        cases = {
            "node kind outside core and namespace": lambda d: d["nodes"][1].__setitem__("kind", "Section"),
            "unknown node field": lambda d: d["nodes"][1].__setitem__("meaning", "a requirement"),
            "span without content digest": lambda d: d["evidence"][0].pop("sha256"),
            "empty span": lambda d: d["evidence"][0].update(exact="", end=0),
            "publisher-looking id origin": lambda d: d["capture"].__setitem__("idOrigin", "publisher"),
            "derivation outside the enum": lambda d: d["nodes"][1].__setitem__("derivation", "inferred"),
            "artifact without digest": lambda d: d["artifact"].pop("sha256"),
            "box outside permille": lambda d: d["nodes"][1].__setitem__("source", {"coordinateSystem": "page-region", "page": 1, "box": [0, 0, 1001, 1]}),
            "unresolved region without an issue": lambda d: d["unresolved"].append({"id": "u0001", "evidence": ["s0001"]}),
            "derived text without its rule": lambda d: d["nodes"][1].__setitem__("derived", {"text": "x", "method": "rule"}),
        }
        for name, mutate in cases.items():
            with self.subTest(name):
                self.assertTrue(broken(mutate), f"{name} was accepted")

    def test_example_profile_composes_the_parent(self) -> None:
        self.assertEqual([], check_profile_composition(self.profile, self.schema, sha256(self.schema_bytes)))
        validator = Draft202012Validator(self.profile, registry=self.registry)
        self.assertEqual([], [e.message for e in validator.iter_errors(self.valid)])

    def test_profile_cannot_redefine_a_parent_field(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["allOf"][1]["properties"]["artifact"] = {"properties": {"sha256": {"type": "string"}}}
        self.assertTrue(check_profile_composition(profile, self.schema, sha256(self.schema_bytes)))
        profile = copy.deepcopy(self.profile)
        profile["allOf"][1]["properties"]["nodes"]["items"]["allOf"].append({"properties": {"text": {"maxLength": 10}}})
        self.assertTrue(check_profile_composition(profile, self.schema, sha256(self.schema_bytes)))

    def test_profile_kind_namespace_is_enforced(self) -> None:
        validator = Draft202012Validator(self.profile, registry=self.registry)
        doc = copy.deepcopy(self.valid)
        doc["nodes"][1]["kind"] = "example:Unknown"
        self.assertTrue([e.message for e in validator.iter_errors(doc)])


if __name__ == "__main__":
    unittest.main()
