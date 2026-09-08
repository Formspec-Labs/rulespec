#!/usr/bin/env python3
"""Compare native CUE schema export with the saved compiler and its fixtures.

This is a diagnostic: it writes separate outputs and never replaces generated
schemas. Select fixture nodes using the original schema so a missing native
class discriminator cannot silently turn a fixture into an empty test.
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import constraints_parity as parity
from jsonschema import Draft202012Validator, FormatChecker


def verdict(schema: dict, nodes: list[dict], *, extensions: bool = False) -> dict:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    messages = []
    for node in nodes:
        messages.extend(error.message for error in validator.iter_errors(node))
        if extensions:
            for order in schema.get("x-rkaf-order", []):
                if parity.violates_order(node.get(order["lower"]), node.get(order["upper"])):
                    messages.append("Rulespec ordered-field constraint failed")
            for relation in schema.get("x-rkaf-not-equal", []):
                if parity.violates_not_equal(node.get(relation["left"]), node.get(relation["right"])):
                    messages.append("Rulespec field-inequality constraint failed")
    return {"verdict": "FAIL" if messages else "PASS", "errors": messages[:5]}


def source_spelling(value: object, schema: dict, definitions: dict) -> object:
    """Remove JSON-LD resource IDs and expand admitted scalar list shorthand.

    This adapts fixture data only. It does not repair an exported schema, remove
    domain properties, or relax any CUE constraints.
    """
    if "$ref" in schema:
        schema = definitions[schema["$ref"].removeprefix("#/$defs/")]
    array = next((choice for choice in schema.get("anyOf", []) if choice.get("type") == "array"), None)
    if array is not None:
        schema = array
        if not isinstance(value, list):
            value = [value]
    if isinstance(value, list):
        return [source_spelling(item, schema.get("items", {}), definitions) for item in value]
    if isinstance(value, dict):
        properties = schema.get("properties", {})
        return {key: source_spelling(item, properties.get(key, {}), definitions)
                for key, item in value.items() if key not in {"@context", "@id"}}
    return value


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cue", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, default=ROOT / "constraints", help="isolated constraint copy to export and validate")
    ap.add_argument("--out", type=Path, default=HERE / "native-export" / "comparison", help="separate diagnostic output directory")
    args = ap.parse_args()
    cue = args.cue.resolve()
    baseline = json.loads((HERE / "baseline.json").read_text())
    changed = [path for path, digest in baseline["sources"].items()
               if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest]
    if changed:
        raise SystemExit(f"Sources changed since the saved baseline; capture a new baseline first: {changed}")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sources = sorted(
        p for p in args.source_root.resolve().rglob("*.cue")
        if p.parent.name != "semantics" and p.parent.name != "platform"
    )
    source_args = [str(p) for p in sources]
    pairs = sorted(set((c, s) for c, s, _, _ in parity.FIXTURE_BINDINGS))

    def export(pair: tuple[str, str]) -> tuple[tuple[str, str], dict]:
        constraint, shape = pair
        command = [str(cue), "def", "--out", "jsonschema", "-e", "#" + shape, *source_args]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        (out / f"{shape}.stdout.json").write_text(result.stdout)
        (out / f"{shape}.stderr.txt").write_text(result.stderr)
        record = {"returncode": result.returncode, "stderr": result.stderr}
        if result.returncode == 0:
            record["schema"] = json.loads(result.stdout)
            Draft202012Validator.check_schema(record["schema"])
        return pair, record

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        exports = dict(pool.map(export, pairs))
    print(f"Exported {len(exports)} fixture shapes", flush=True)

    def check(binding: tuple[str, str, str, str]) -> dict:
        constraint, shape, fixture, expected = binding
        rel = Path(parity.CONSTRAINTS[constraint]) / f"{constraint}.json"
        original_doc = json.loads((HERE / "before" / rel).read_text())
        original = {**original_doc["$defs"][shape], "$defs": original_doc["$defs"]}
        payload = json.loads((ROOT / fixture).read_text())
        target_type = original.get("properties", {}).get("@type", {}).get("const")
        if "@graph" in payload:
            nodes = [n for n in payload["@graph"] if n.get("@type") == target_type]
        else:
            nodes = [payload]
        nodes = [{k: v for k, v in node.items() if k != "@context"} for node in nodes]
        record = {"constraint": constraint, "shape": shape, "fixture": fixture,
                  "expected": expected, "node_count": len(nodes),
                  "adversarial": constraint in parity.ADVERSARIAL_CONSTRAINTS}
        if not nodes:
            return {**record, "setup_error": "No matching fixture node"}
        record["original"] = verdict(original, nodes, extensions=True)
        native = exports[(constraint, shape)]
        record["native"] = verdict(native["schema"], nodes) if "schema" in native else {
            "verdict": "EXPORT_ERROR", "errors": [native["stderr"]]}
        normalized = [source_spelling(node, original, original_doc["$defs"]) for node in nodes]
        record["native_source_spelling"] = verdict(native["schema"], normalized) if "schema" in native else record["native"]
        with tempfile.TemporaryDirectory(prefix="rulespec-native-fixture-") as temporary:
            files = []
            for index, node in enumerate(normalized):
                path = Path(temporary) / f"node-{index}.json"
                path.write_text(json.dumps(node))
                files.append(str(path))
            result = subprocess.run(
                [str(cue), "vet", "-c", "-d", "#" + shape, *source_args, *files],
                capture_output=True, text=True, timeout=30,
            )
        record["cue_source_spelling"] = {"verdict": "PASS" if result.returncode == 0 else "FAIL",
                                         "errors": result.stderr.splitlines()[:8]}
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(check, parity.FIXTURE_BINDINGS))
    comparable = [row for row in rows if "setup_error" not in row]
    summary = {
        "fixture_pairs": len(rows), "setup_errors": len(rows) - len(comparable),
        "shapes": len(exports),
        "exported_shapes": sum("schema" in item for item in exports.values()),
        "original_expected_mismatches": sum(row["original"]["verdict"] != row["expected"] for row in comparable),
        "native_expected_mismatches": sum(row["native"]["verdict"] != row["expected"] for row in comparable),
        "source_spelling_native_vs_cue_mismatches": sum(row["native_source_spelling"]["verdict"] != row["cue_source_spelling"]["verdict"] for row in comparable),
        "source_spelling_native_accepts_cue_rejects": sum(row["native_source_spelling"]["verdict"] == "PASS" and row["cue_source_spelling"]["verdict"] == "FAIL" for row in comparable),
        "source_spelling_native_rejects_cue_accepts": sum(row["native_source_spelling"]["verdict"] == "FAIL" and row["cue_source_spelling"]["verdict"] == "PASS" for row in comparable),
        "native_verdicts": dict(collections.Counter(row["native"]["verdict"] for row in comparable)),
    }
    report = {
        "cue_version": subprocess.check_output([str(cue), "version"], text=True),
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "fixture_sha256": {fixture: hashlib.sha256((ROOT / fixture).read_bytes()).hexdigest() for _, _, fixture, _ in parity.FIXTURE_BINDINGS},
        "interpretation": "Raw fixture results test compatibility with Rulespec conventions. Source-spelling results remove JSON-LD IDs and expand scalar list shorthand before testing identical data with CUE and native JSON Schema; other source/carrier differences remain visible.",
        "export_errors": {s: e["stderr"] for (_, s), e in exports.items() if "schema" not in e},
        "summary": summary, "fixtures": rows,
    }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
