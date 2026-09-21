"""V2 shared provenance over seven retained captures and genuine mutation controls."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from rulespec_artifacts import resources
from rulespec_artifacts.document_capture import check_invariants
from rulespec_artifacts.document_capture_provenance import (
    check_provenance,
    check_retained_evidence,
    converter_digest,
    full_timestamp,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "release-records/fixtures/document-capture-v2/retained"


class CaptureV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = resources.document_capture_schema(2)
        cls.meta = resources.document_capture_profile_schema(2)
        cls.registry = Registry().with_resource(
            cls.schema["$id"], Resource.from_contents(cls.schema)
        )
        cls.validator = Draft202012Validator(cls.schema, registry=cls.registry)
        cls.manifest = json.loads((FIXTURES / "manifest.json").read_text())
        cls.cases = {c["family"]: c for c in cls.manifest["cases"]}

    def load(self, family="federal-register-xml"):
        case = self.cases[family]
        return json.loads((FIXTURES / case["capture"]).read_text()), (
            FIXTURES / case["profile"]
        ).read_bytes()

    def codes(self, capture, profile):
        return {
            item["code"] for item in check_provenance(capture, profile_bytes=profile)
        }

    def test_resources_are_explicit_and_v1_bytes_are_unchanged(self):
        self.assertEqual(
            resources.document_capture_schema()["title"], "DocumentCapture v1"
        )
        self.assertEqual(
            hashlib.sha256(resources.document_capture_schema_bytes()).hexdigest(),
            "a090fbc8baf6ae55c80a29ad70fc9d411b495ede26443dd0c4f125dd4184689e",
        )
        for version in (1, 2):
            for kind, load in [
                ("document-capture", resources.document_capture_schema_bytes),
                (
                    "document-capture-profile",
                    resources.document_capture_profile_schema_bytes,
                ),
            ]:
                self.assertEqual(
                    load(version),
                    (
                        ROOT / f"release-records/schemas/{kind}-v{version}.schema.json"
                    ).read_bytes(),
                )
        for version in (0, 3, True, "2"):
            with self.assertRaises(ValueError):
                resources.document_capture_schema(version)
        for schema in (self.schema, self.meta):
            Draft202012Validator.check_schema(schema)
        self.assertEqual(
            self.schema["$defs"]["ProvenanceRequirement"]["enum"],
            self.meta["properties"]["x-provenance"]["items"]["enum"],
        )

    def test_all_seven_native_migrations_preserve_known_findings(self):
        self.assertEqual(len(self.cases), 7)
        totals = Counter()
        for case in self.manifest["cases"]:
            with self.subTest(family=case["family"]):
                doc, profile_bytes = self.load(case["family"])
                self.assertEqual(
                    hashlib.sha256(
                        (FIXTURES / case["capture"]).read_bytes()
                    ).hexdigest(),
                    case["capture_sha256"],
                )
                self.assertEqual(
                    hashlib.sha256(profile_bytes).hexdigest(), case["profile_sha256"]
                )
                profile = json.loads(profile_bytes)
                self.assertEqual(
                    [], list(Draft202012Validator(self.meta).iter_errors(profile))
                )
                self.assertEqual([], check_invariants(doc, parent_schema=self.schema))
                findings = check_provenance(doc, profile_bytes=profile_bytes)
                self.assertEqual(case["findings"], findings)
                totals.update(f["code"] for f in findings)
                errors = list(self.validator.iter_errors(doc))
                self.assertEqual(len(errors), len(case["schema_errors"]))
                self.assertEqual(
                    doc["rendition"]["textStream"]["sha256"], case["text_stream_sha256"]
                )
                if not errors:
                    self.assertEqual(
                        [],
                        list(
                            Draft202012Validator(
                                profile, registry=self.registry
                            ).iter_errors(doc)
                        ),
                    )
        self.assertEqual(
            totals,
            Counter(
                {
                    "retrieval-timestamp": 2,
                    "mods-record": 3,
                    "coordinate-fields": 6,
                    "archive-member-pending": 1,
                }
            ),
        )

    def test_legacy_capture_is_not_silently_declared_v2(self):
        doc, profile = self.load()
        doc["captureVersion"] = 1
        self.assertEqual(self.codes(doc, profile), {"unsupported-provenance-version"})
        self.assertTrue(list(self.validator.iter_errors(doc)))

    def test_profile_requirement_and_pin_controls(self):
        doc, profile = self.load()
        self.assertEqual(self.codes(doc, profile), set())
        doc["profile"]["schema"]["sha256"] = "0" * 64
        self.assertIn("profile-pin", self.codes(doc, profile))
        doc, profile = self.load()
        forged = json.loads(profile)
        forged["x-provenance"] = ["anything-goes"]
        self.assertTrue(list(Draft202012Validator(self.meta).iter_errors(forged)))
        forged["allOf"][1]["properties"]["artifact"] = {"type": "object"}
        self.assertTrue(list(Draft202012Validator(self.meta).iter_errors(forged)))
        self.assertIn(
            "profile-requirements", self.codes(doc, json.dumps(forged).encode())
        )

    def test_missing_and_mismatched_source_records_are_findings(self):
        mutations = [
            (
                "acquisition-record",
                lambda d: d["provenance"].__setitem__("sourceRecords", []),
            ),
            (
                "source-record-pin",
                lambda d: d["provenance"]["sourceRecords"][0]["artifact"].pop("sha256"),
            ),
            (
                "acquisition-record-mismatch",
                lambda d: d["provenance"]["sourceRecords"][0][
                    "observedArtifact"
                ].__setitem__("sha256", "0" * 64),
            ),
            (
                "acquisition-record-mismatch",
                lambda d: d["provenance"]["sourceRecords"][0]["observedArtifact"][
                    "locator"
                ].__setitem__("url", "https://example.test/other"),
            ),
            ("rendition-reason", lambda d: d["provenance"].pop("renditionReason")),
        ]
        for code, mutate in mutations:
            with self.subTest(code=code):
                doc, profile = self.load()
                mutate(doc)
                self.assertIn(code, self.codes(doc, profile))

    def test_timestamp_precision_and_evidence_association(self):
        for value in (
            "2026-09-21",
            "2026-09-21T12:13Z",
            "2026-09-21T12:13:14",
            "2026-02-30T12:13:14Z",
        ):
            self.assertFalse(full_timestamp(value))
        self.assertTrue(full_timestamp("2026-09-21T12:13:14.123456789-04:00"))
        self.assertTrue(full_timestamp("2026-09-21T12:13:14Z"))
        doc, profile = self.load()
        doc["artifact"]["retrievedAt"] = "2026-09-19"
        doc["provenance"]["sourceRecords"][0]["observedArtifact"]["retrievedAt"] = (
            "2026-09-19"
        )
        self.assertEqual(self.codes(doc, profile), {"retrieval-timestamp"})

    def test_govinfo_pair_and_mods_bindings_are_conditional(self):
        doc, profile = self.load()
        self.assertNotIn("govinfoIdentity", doc["provenance"])
        self.assertFalse(self.codes(doc, profile))
        doc, profile = self.load("senate-expenditures-pdf")
        baseline = self.codes(doc, profile)
        doc["provenance"]["govinfoIdentity"]["granuleId"] = None
        self.assertIn("govinfo-pair", self.codes(doc, profile) - baseline)
        doc, profile = self.load("senate-expenditures-pdf")
        mods = next(
            r for r in doc["provenance"]["sourceRecords"] if r["role"] == "mods"
        )
        mods["govinfoIdentity"]["packageId"] = "wrong-package"
        self.assertIn("mods-identity-binding", self.codes(doc, profile) - baseline)
        doc, profile = self.load("committee-report-html")
        doc["provenance"]["govinfoIdentity"]["scope"] = "granule"
        self.assertTrue(list(self.validator.iter_errors(doc)))
        self.assertIn("govinfo-pair", self.codes(doc, profile))

    def test_generation_timestamp_keeps_separate_precision(self):
        doc, profile = self.load("senate-expenditures-pdf")
        doc["provenance"]["derivedFrom"]["generatedAt"] = "2026-09-21"
        self.assertIn("generation-timestamp", self.codes(doc, profile))
        doc["provenance"]["derivedFrom"]["generatedAt"] = "2026-09-21T12:13:14.123456Z"
        self.assertNotIn("generation-timestamp", self.codes(doc, profile))

    def test_page_dimensions_do_not_silently_overwrite_each_other(self):
        doc, profile = self.load("slip-opinion-pdf")
        page = next(n for n in doc["nodes"] if n["kind"] == "page")
        size = dict(page["pageSize"], page=page["source"]["page"])
        doc["provenance"]["pageSizes"] = [size, copy.deepcopy(size)]
        self.assertIn("duplicate-page-dimensions", self.codes(doc, profile))
        doc["provenance"]["pageSizes"] = [dict(size, width=size["width"] + 1)]
        self.assertIn("conflicting-page-dimensions", self.codes(doc, profile))

    def test_derivative_keeps_its_own_identity_and_page_mapping(self):
        for code, mutate in [
            (
                "derived-original-url",
                lambda d: d["artifact"]["locator"].__setitem__(
                    "url", d["provenance"]["derivedFrom"]["artifact"]["locator"]["url"]
                ),
            ),
            (
                "derived-original-timestamp",
                lambda d: d["artifact"].__setitem__(
                    "retrievedAt",
                    d["provenance"]["derivedFrom"]["artifact"]["retrievedAt"],
                ),
            ),
            (
                "derived-page-map",
                lambda d: d["provenance"]["derivedFrom"].__setitem__("sourcePages", []),
            ),
            (
                "derived-page-map",
                lambda d: d["provenance"]["derivedFrom"]["sourcePages"][0].__setitem__(
                    "derivedPage", 2
                ),
            ),
            (
                "derived-artifact",
                lambda d: d["provenance"]["derivedFrom"].pop("method"),
            ),
        ]:
            with self.subTest(code=code):
                doc, profile = self.load("senate-expenditures-pdf")
                mutate(doc)
                self.assertIn(code, self.codes(doc, profile))

    def test_effective_coordinates_dimensions_and_cell_identity(self):
        doc, profile = self.load("slip-opinion-pdf")
        self.assertFalse(self.codes(doc, profile))
        span = next(
            s
            for s in doc["evidence"]
            if s["source"].get("coordinateSystem") == "page-region"
        )
        doc["rendition"]["spanDefaults"]["coordinateSystem"] = span["source"].pop(
            "coordinateSystem"
        )
        span["source"].pop("box")
        self.assertIn("coordinate-fields", self.codes(doc, profile))
        doc, profile = self.load("slip-opinion-pdf")
        for node in doc["nodes"]:
            node.pop("pageSize", None)
        self.assertIn("page-dimensions", self.codes(doc, profile))
        doc, profile = self.load("senate-expenditures-pdf")
        next(n for n in doc["nodes"] if n["kind"] == "cell")["cell"].pop("column")
        self.assertIn("pdf-cell-identity", self.codes(doc, profile))
        doc, profile = self.load()
        doc["evidence"][0]["source"] = {
            "coordinateSystem": "utf8-byte",
            "start": 10,
            "end": 2,
        }
        self.assertIn("coordinate-fields", self.codes(doc, profile))

    def test_generated_and_native_inferred_nodes_require_decisions(self):
        doc, profile = self.load()
        node = next(n for n in doc["nodes"] if n["derivation"] == "generated")
        node.pop("decision")
        self.assertIn("derived-node-decision", self.codes(doc, profile))
        self.assertTrue(list(self.validator.iter_errors(doc)))
        doc, profile = self.load("uslm-law")
        node = next(
            n
            for n in doc["nodes"]
            if n["derivation"] == "native" and n.get("levelOrigin") == "rule"
        )
        node.pop("decision")
        self.assertIn("derived-node-decision", self.codes(doc, profile))
        node.pop("levelOrigin")
        self.assertIn("field-origin", self.codes(doc, profile))
        self.assertTrue(list(self.validator.iter_errors(doc)))

    def test_rule_version_and_converter_binding_cannot_go_stale(self):
        for mutate in [
            lambda d: d["converter"]["implementation"].__setitem__(
                "fileSha256", "0" * 64
            ),
            lambda d: d["converter"]["dependencies"][0].__setitem__(
                "version", "changed"
            ),
        ]:
            doc, profile = self.load()
            mutate(doc)
            self.assertIn("stale-rule-binding", self.codes(doc, profile))
        doc, profile = self.load()
        next(n for n in doc["nodes"] if "decision" in n)["decision"]["ruleVersion"] = (
            "unknown"
        )
        self.assertIn("decision-rule-binding", self.codes(doc, profile))
        doc, profile = self.load("cfr-reconstruction")
        next(n for n in doc["nodes"] if "derived" in n)["derived"].pop("ruleVersion")
        self.assertIn("derived-text-rule-binding", self.codes(doc, profile))
        self.assertEqual(
            converter_digest({"b": "x", "a": "y"}),
            converter_digest({"a": "y", "b": "x"}),
        )

    def test_retained_bytes_and_url_evidence_are_independent(self):
        raw = b"unchanged original bytes"
        digest = hashlib.sha256(raw).hexdigest()
        timestamp = "2026-09-21T12:13:14.123456Z"
        artifact = {
            "sha256": digest,
            "byteSize": len(raw),
            "mediaType": "text/plain",
            "locator": {"path": "local.txt", "url": "https://example.test/source"},
            "retrievedAt": timestamp,
        }
        doc = {"artifact": artifact}
        observation = {
            k: artifact[k] for k in ("sha256", "byteSize", "mediaType", "retrievedAt")
        }
        read = lambda a: raw
        self.assertEqual(
            [],
            check_retained_evidence(
                doc,
                read_bytes=read,
                observations={artifact["locator"]["url"]: observation},
            ),
        )
        found = check_retained_evidence(doc, read_bytes=read, observations={})
        self.assertEqual(found[0]["code"], "artifact-url-unverified")
        wrong = dict(observation, sha256="0" * 64)
        found = check_retained_evidence(
            doc, read_bytes=read, observations={artifact["locator"]["url"]: wrong}
        )
        self.assertEqual(found[0]["code"], "artifact-url-bytes-mismatch")
        truncated = dict(observation, retrievedAt="2026-09-21T12:13:14Z")
        found = check_retained_evidence(
            doc, read_bytes=read, observations={artifact["locator"]["url"]: truncated}
        )
        self.assertEqual(found[0]["code"], "artifact-acquisition-time-mismatch")
        found = check_retained_evidence(
            doc,
            read_bytes=lambda a: raw + b"corrupt",
            observations={artifact["locator"]["url"]: observation},
        )
        self.assertEqual(found[0]["code"], "retained-bytes-mismatch")


if __name__ == "__main__":
    unittest.main()
