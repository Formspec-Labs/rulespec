"""Qualify the v2 tool against its former encoder and the owner corpus."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from collections import UserDict
from pathlib import Path
from types import MappingProxyType
from unittest.mock import patch

from rulespec_artifacts import ArtifactVerificationError, canonical_json_bytes

from tools import extrapolation_canonical_oracle as old
from tools import extrapolation_release_v2 as current
from tools.build_extrapolation_release_v2_fixtures import (
    FIXTURE_ROOT,
    UPSTREAM_DOCUMENT_RELEASE,
    _tree_digest,
)
from tools.build_rulespec_release_fixtures import open_fixture_atlas

ROOT = Path(__file__).resolve().parents[1]
CORPUS = json.loads(
    (ROOT / "platform-fixtures/canonical-json/corpus.json").read_bytes()
)
# Reuse the owner's test-only value materializer; no production import overlay.
_RUNNER_PATH = ROOT / "packages/rulespec-artifacts/tests/canonical_corpus_runner.py"
_SPEC = importlib.util.spec_from_file_location(
    "canonical_corpus_test_runner", _RUNNER_PATH
)
assert _SPEC is not None and _SPEC.loader is not None
_RUNNER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_RUNNER)


class CanonicalOwnerTests(unittest.TestCase):
    def test_accepted_golden_bytes_and_unqualified_digest_match_old_encoder(
        self,
    ) -> None:
        self.assertIs(current.canonical_json_bytes, canonical_json_bytes)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "root.json"
            for case in CORPUS["encodeAccepted"]:
                with self.subTest(case=case["name"]):
                    expected = bytes.fromhex(case["canonicalHex"])
                    self.assertEqual(old.canonical_json_bytes(case["value"]), expected)
                    self.assertEqual(
                        current.canonical_json_bytes(case["value"]), expected
                    )
                    self.assertEqual(
                        current.canonical_sha256(case["value"]),
                        hashlib.sha256(expected).hexdigest(),
                    )
                    path.write_bytes(expected)
                    self.assertEqual(
                        current.load_strict_canonical_json(path),
                        old.load_strict_canonical_json(path),
                    )

    def test_rejected_golden_values_remain_refused(self) -> None:
        for case in CORPUS["encodeRejected"]:
            value = _RUNNER._materialize_input(case["input"])
            with self.subTest(case=case["name"]):
                with self.assertRaises(ValueError):
                    old.canonical_json_bytes(value)
                with self.assertRaises(ArtifactVerificationError):
                    current.canonical_json_bytes(value)

    def test_rejected_golden_bytes_keep_release_issue_code_and_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            path = bundle / "release.json"
            for case in CORPUS["parseRejected"]:
                with self.subTest(case=case["name"]):
                    path.write_bytes(bytes.fromhex(case["utf8Hex"]))
                    with self.assertRaises(ValueError):
                        old.load_strict_canonical_json(path)
                    with self.assertRaises(ArtifactVerificationError) as raised:
                        current.load_strict_canonical_json(path)
                    self.assertEqual(raised.exception.issue.code, "invalid.root-syntax")
                    self.assertEqual(raised.exception.issue.path, "$")
                    issues = []
                    self.assertIsNone(current._read_v2_root(bundle, issues))
                    self.assertEqual(
                        [(item.code, item.path) for item in issues],
                        [("invalid.root-syntax", "release.json")],
                    )
                    self.assertEqual(issues[0].message, str(raised.exception))

    def test_owner_mapping_and_tuple_domain_is_an_explicit_expansion(self) -> None:
        for value in [
            UserDict({"a": (1, True)}),
            MappingProxyType({"a": [1, True]}),
            {"a": (1, True)},
        ]:
            with self.subTest(type=type(value).__name__):
                with self.assertRaises(ValueError):
                    old.canonical_json_bytes(value)
                self.assertEqual(current.canonical_json_bytes(value), b'{"a":[1,true]}')

    def test_owner_error_retains_nested_value_location(self) -> None:
        with self.assertRaises(ArtifactVerificationError) as raised:
            current.canonical_json_bytes({"a": [1.5]})
        self.assertEqual(raised.exception.issue.path, "$/a/0")
        self.assertIsInstance(raised.exception, ValueError)

    def test_embedded_v1_keeps_its_finite_float_profile(self) -> None:
        self.assertEqual(
            current._strict_v1_record_json('{"score":0.25}'), {"score": 0.25}
        )
        for raw in ['{"score":NaN}', '{"score":1,"score":2}']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                current._strict_v1_record_json(raw)
        with self.assertRaises(ArtifactVerificationError):
            current.canonical_json_bytes({"score": 0.25})

    def test_all_pinned_bundle_trees_and_full_verdicts_match_old_helpers(self) -> None:
        document_release = current.load_document_release_view(UPSTREAM_DOCUMENT_RELEASE)
        atlas = open_fixture_atlas()
        corpus = json.loads((FIXTURE_ROOT / "corpus.json").read_bytes())
        self.assertEqual(len(corpus["cases"]), 15)
        for case in corpus["cases"]:
            with self.subTest(case=case["name"]):
                bundle = FIXTURE_ROOT / case["bundle"]
                self.assertEqual(_tree_digest(bundle), case["treeSha256"])
                actual = current.verify_extrapolation_release_v2(
                    bundle, document_release=document_release, atlas=atlas
                )
                with (
                    patch.object(
                        current, "canonical_json_bytes", old.canonical_json_bytes
                    ),
                    patch.object(
                        current,
                        "load_strict_canonical_json",
                        old.load_strict_canonical_json,
                    ),
                ):
                    expected = current.verify_extrapolation_release_v2(
                        bundle, document_release=document_release, atlas=atlas
                    )
                self.assertEqual(actual, expected)
                self.assertEqual(actual.code, case["expectedCode"])


if __name__ == "__main__":
    unittest.main()
