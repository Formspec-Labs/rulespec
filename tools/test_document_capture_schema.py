"""The DocumentCapture v1 parent schema, its profile meta-schema and its invariant validator.

Run through the repository's tooling runner, never a bare interpreter:

    uv run --no-project --python 3.12 --with-requirements requirements.txt python -m unittest tools.test_document_capture_schema

``--no-project`` is what the Makefile passes for the same reason its
``requirements.txt`` states: building the project force-includes the generated
``compiled/`` tree, so a fresh checkout cannot ``uv run --frozen`` before
``make compile``. The gate here needs only ``jsonschema`` and the
``rulespec-artifacts`` wheel ``requirements.txt`` installs, whose ``_data``
carries the two schemas this file reads back.

The composition rule used to be a hand-written whitelist over ``properties``
keys in this file and a second copy in SpicyDocs. Seven tightenings a profile
must not make -- ``else``, ``required``, ``additionalProperties: false``,
``not``, ``required`` on ``profile``, a ``then`` loosening ``kind`` to any
string, ``minItems`` on ``nodes`` -- all passed both copies, and the copies had
already drifted. The rule is now
``release-records/schemas/document-capture-profile-v1.schema.json``: data,
shipped in the artifacts wheel, validated with the ``jsonschema`` both
repositories already have. The two bindings a schema cannot state (the
``x-parent`` digest, and the profile's own name inside its kind patterns) are
``rulespec_artifacts.document_capture.check_profile_bindings``. Each of the
seven probes is a negative control below.
"""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from rulespec_artifacts import document_capture, resources

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "release-records" / "schemas"
SCHEMA = SCHEMAS / "document-capture-v1.schema.json"
PROFILE_SCHEMA = SCHEMAS / "document-capture-profile-v1.schema.json"
FIXTURES = ROOT / "release-records" / "fixtures" / "document-capture-v1"


def sha256(data: bytes | str) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


class DocumentCaptureSchemaTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema_bytes = SCHEMA.read_bytes()
        cls.schema = json.loads(cls.schema_bytes)
        cls.meta_bytes = PROFILE_SCHEMA.read_bytes()
        cls.meta = json.loads(cls.meta_bytes)
        cls.registry = Registry().with_resource(cls.schema["$id"], Resource.from_contents(cls.schema))
        cls.validator = Draft202012Validator(cls.schema, registry=cls.registry)
        cls.meta_validator = Draft202012Validator(cls.meta)
        cls.valid = json.loads((FIXTURES / "minimal-valid.json").read_text())
        cls.profile = json.loads((FIXTURES / "profile-example.schema.json").read_text())

    # --- the schemas themselves -------------------------------------------------

    def test_schemas_are_valid_draft_2020_12_schemas(self) -> None:
        for schema in (self.schema, self.meta):
            Draft202012Validator.check_schema(schema)
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_root_is_closed_and_every_top_level_field_is_required(self) -> None:
        self.assertFalse(self.schema["additionalProperties"])
        self.assertEqual(sorted(self.schema["properties"]), sorted(self.schema["required"]))

    def test_the_wheel_ships_these_exact_bytes(self) -> None:
        """A consumer pins the wheel's copy, so the wheel's copy is these bytes."""
        self.assertEqual(resources.document_capture_schema_bytes(), self.schema_bytes)
        self.assertEqual(resources.document_capture_profile_schema_bytes(), self.meta_bytes)
        self.assertIn("## 2. Invariants the schema cannot state", resources.document_capture_spec())

    # --- the fixtures -----------------------------------------------------------

    def test_minimal_fixture_validates_and_pins_both_schemas(self) -> None:
        self.assertEqual([], [e.message for e in self.validator.iter_errors(self.valid)])
        self.assertEqual(self.valid["schema"], {"$id": self.schema["$id"], "sha256": sha256(self.schema_bytes)})
        self.assertEqual(
            self.valid["profile"]["schema"],
            {"$id": self.profile["$id"], "sha256": sha256((FIXTURES / "profile-example.schema.json").read_bytes())},
            "the fixture's profile pin is stale; regenerate it",
        )

    def test_minimal_fixture_holds_the_invariants(self) -> None:
        self.assertEqual([], document_capture.check_invariants(self.valid, parent_schema=self.schema))

    def test_negative_controls(self) -> None:
        def broken(mutate):
            doc = copy.deepcopy(self.valid)
            mutate(doc)
            return [e.message for e in self.validator.iter_errors(doc)]

        cases = {
            "node kind outside core and namespace": lambda d: d["nodes"][1].__setitem__("kind", "Section"),
            "unknown node field": lambda d: d["nodes"][1].__setitem__("meaning", "a requirement"),
            "span without exact text": lambda d: d["evidence"][0].pop("exact"),
            "empty span": lambda d: d["evidence"][0].update(exact="", end=0),
            "publisher-looking id origin": lambda d: d["capture"].__setitem__("idOrigin", "publisher"),
            "derivation outside the enum": lambda d: d["nodes"][1].__setitem__("derivation", "inferred"),
            "artifact without digest": lambda d: d["artifact"].pop("sha256"),
            "box outside permille": lambda d: d["nodes"][1].__setitem__("source", {"coordinateSystem": "page-region", "page": 1, "box": [0, 0, 1001, 1]}),
            "unresolved region without an issue": lambda d: d["unresolved"].append({"id": "u0001", "evidence": ["s0001"]}),
            "derived text without its rule": lambda d: d["nodes"][1].__setitem__("derived", {"text": "x", "method": "rule"}),
            "rendition kind that is an extractor output": lambda d: d["rendition"].__setitem__("kind", "evidence-lines"),
            "intermediate without a producer": lambda d: d["rendition"].__setitem__(
                "intermediate", {"iri": "urn:x:1", "sha256": "0" * 64, "mediaType": "application/json"}
            ),
            "page size in an unstated unit": lambda d: d["nodes"][1].__setitem__(
                "pageSize", {"width": 612, "height": 792, "unit": "permille"}
            ),
        }
        for name, mutate in cases.items():
            with self.subTest(name):
                self.assertTrue(broken(mutate), f"{name} was accepted")

    def test_invariant_negative_controls(self) -> None:
        def broken(mutate):
            doc = copy.deepcopy(self.valid)
            mutate(doc)
            return document_capture.check_invariants(doc, parent_schema=self.schema)

        def unown(doc):
            for node in doc["nodes"]:
                node["evidence"] = [s for s in node["evidence"] if s != "s0002"]

        cases = {
            "partition": lambda d: d["evidence"][0].update(start=1),
            "ownership": unown,
            "kind namespace": lambda d: d["nodes"][1].__setitem__("kind", "other:Foo"),
            "leaf text": lambda d: d["nodes"][-1].__setitem__("text", "a different text"),
            "span digest": lambda d: d["evidence"][-1].__setitem__("sha256", "0" * 64),
            "tree": lambda d: d["nodes"][-1].__setitem__("depth", 9),
        }
        for name, mutate in cases.items():
            with self.subTest(name):
                self.assertTrue(broken(mutate), f"{name} was accepted")

    # --- the composition rule ---------------------------------------------------

    def test_example_profile_composes_the_parent(self) -> None:
        self.assertEqual([], [e.message for e in self.meta_validator.iter_errors(self.profile)])
        self.assertEqual(
            [],
            document_capture.check_profile_bindings(
                self.profile, parent_id=self.schema["$id"], parent_digest=sha256(self.schema_bytes)
            ),
        )
        validator = Draft202012Validator(self.profile, registry=self.registry)
        self.assertEqual([], [e.message for e in validator.iter_errors(self.valid)])

    def test_the_seven_tightenings_the_old_checker_admitted_are_refused(self) -> None:
        """Each probe passed the hand-written whitelist and changed what a capture validated as."""

        def refused(mutate) -> bool:
            profile = copy.deepcopy(self.profile)
            mutate(profile)
            return bool(list(self.meta_validator.iter_errors(profile)))

        own = lambda p: p["allOf"][1]  # noqa: E731
        node_clauses = lambda p: own(p)["properties"]["nodes"]["items"]["allOf"]  # noqa: E731
        cases = {
            "else on a node clause": lambda p: node_clauses(p)[0].__setitem__("else", {"properties": {"kind": {"const": "x"}}}),
            "required added to the narrowing": lambda p: own(p).__setitem__("required", ["artifact"]),
            "additionalProperties false on the narrowing": lambda p: own(p).__setitem__("additionalProperties", False),
            "not added to the narrowing": lambda p: own(p).__setitem__("not", {"required": ["unresolved"]}),
            "required on profile": lambda p: own(p)["properties"]["profile"].__setitem__("required", ["ext"]),
            "then loosening kind to any string": lambda p: node_clauses(p)[0]["then"]["properties"].__setitem__(
                "kind", {"type": "string"}
            ),
            "minItems on nodes": lambda p: own(p)["properties"]["nodes"].__setitem__("minItems", 2),
        }
        for name, mutate in cases.items():
            with self.subTest(name):
                self.assertTrue(refused(mutate), f"{name} was accepted")

    def test_a_profile_cannot_reach_a_parent_field(self) -> None:
        for name, mutate in {
            "a second parent property": lambda p: p["allOf"][1]["properties"].__setitem__(
                "artifact", {"properties": {"sha256": {"type": "string"}}}
            ),
            "a fourth node clause": lambda p: p["allOf"][1]["properties"]["nodes"]["items"]["allOf"].append(
                {"properties": {"text": {"maxLength": 10}}}
            ),
            "a node clause touching text": lambda p: p["allOf"][1]["properties"]["nodes"]["items"]["allOf"][
                2
            ]["properties"].__setitem__("text", {"maxLength": 10}),
            "an open extension block": lambda p: p["allOf"][1]["properties"]["profile"]["properties"]["ext"].__setitem__(
                "additionalProperties", True
            ),
            "a third allOf clause": lambda p: p["allOf"].append({"properties": {"issues": {"maxItems": 0}}}),
        }.items():
            with self.subTest(name):
                profile = copy.deepcopy(self.profile)
                mutate(profile)
                self.assertTrue([e.message for e in self.meta_validator.iter_errors(profile)], f"{name} was accepted")

    def test_the_bindings_a_schema_cannot_state_are_checked(self) -> None:
        digest = sha256(self.schema_bytes)
        for name, mutate in {
            "a stale parent pin": lambda p: p["x-parent"].__setitem__("sha256", "0" * 64),
            "a foreign kind in its own enum": lambda p: p["allOf"][1]["properties"]["nodes"]["items"]["allOf"][0][
                "then"
            ]["properties"]["kind"]["enum"].append("other:Foo"),
            "a refusal naming another profile": lambda p: p["allOf"][1]["properties"]["nodes"]["items"]["allOf"][1][
                "properties"
            ]["kind"]["not"].__setitem__("pattern", "^(?!other:)[a-z][a-z0-9-]*:"),
            "a kind test for another namespace": lambda p: p["allOf"][1]["properties"]["nodes"]["items"]["allOf"][0][
                "if"
            ]["properties"]["kind"].__setitem__("pattern", "^other:"),
        }.items():
            with self.subTest(name):
                profile = copy.deepcopy(self.profile)
                mutate(profile)
                self.assertTrue(
                    document_capture.check_profile_bindings(
                        profile, parent_id=self.schema["$id"], parent_digest=digest
                    ),
                    f"{name} was accepted",
                )

    def test_profile_refuses_a_kind_outside_its_namespace(self) -> None:
        validator = Draft202012Validator(self.profile, registry=self.registry)
        for kind in ("example:Unknown", "other:Foo"):
            with self.subTest(kind):
                doc = copy.deepcopy(self.valid)
                doc["nodes"][1]["kind"] = kind
                self.assertTrue([e.message for e in validator.iter_errors(doc)], f"{kind} was accepted")


if __name__ == "__main__":
    unittest.main()
