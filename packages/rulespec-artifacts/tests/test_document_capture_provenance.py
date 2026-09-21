"""Installed-wheel checks for the dependency-free capture provenance API."""

import hashlib
import unittest

from rulespec_artifacts import resources
from rulespec_artifacts.document_capture_provenance import (
    check_provenance,
    check_retained_evidence,
    converter_digest,
    full_timestamp,
)


class CaptureProvenancePackageTest(unittest.TestCase):
    def test_versioned_resources_and_legacy_bytes(self):
        self.assertEqual(
            resources.document_capture_schema()["title"], "DocumentCapture v1"
        )
        self.assertEqual(
            hashlib.sha256(resources.document_capture_schema_bytes()).hexdigest(),
            "a090fbc8baf6ae55c80a29ad70fc9d411b495ede26443dd0c4f125dd4184689e",
        )
        self.assertEqual(
            resources.document_capture_schema(2)["title"], "DocumentCapture v2"
        )
        self.assertEqual(
            resources.document_capture_profile_schema(2)["title"],
            "DocumentCapture v2 family profile",
        )
        self.assertIn("RS1", resources.document_capture_spec())

    def test_provenance_requires_explicit_v2(self):
        self.assertEqual(
            check_provenance({"captureVersion": 1}, profile_bytes=b"{}"),
            [{"code": "unsupported-provenance-version", "path": "/captureVersion"}],
        )
        self.assertTrue(full_timestamp("2026-09-21T12:13:14.123456Z"))
        self.assertFalse(full_timestamp("2026-09-21"))
        self.assertEqual(
            converter_digest({"version": "1", "id": "urn:converter:test"}),
            converter_digest({"id": "urn:converter:test", "version": "1"}),
        )

    def test_retained_bytes_are_checked_without_implicit_io(self):
        data = b"retained source\n"
        capture = {
            "artifact": {
                "sha256": hashlib.sha256(data).hexdigest(),
                "byteSize": len(data),
            }
        }
        self.assertEqual(
            check_retained_evidence(
                capture, read_bytes=lambda _: data, observations={}
            ),
            [],
        )
        self.assertEqual(
            check_retained_evidence(
                capture, read_bytes=lambda _: b"changed", observations={}
            ),
            [{"code": "retained-bytes-mismatch", "path": "/artifact"}],
        )
