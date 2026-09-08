#!/usr/bin/env python3
"""Save small source-versus-export checks, independently of JSON-LD fixtures."""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cue", type=Path, required=True)
    ap.add_argument("--source-probe", type=Path, required=True)
    args = ap.parse_args()
    cue = args.cue.resolve()
    source_probe = args.source_probe.resolve()
    out = HERE / "native-export" / "probes"
    ordinary = out / "ordinary.cue"
    cases = [
        ("Concept", {"z_id": "c1", "a_label": "Applicant"}, True),
        ("Concept", {"a_label": "Applicant"}, False),
        ("Composed", {"z_id": "c1", "a_label": "Applicant", "own": 1}, True),
        ("Conditional", {"kind": "human"}, True),
        ("Conditional", {"kind": "ai", "lineage": "run-1"}, True),
        ("Conditional", {"kind": "ai"}, False),
        ("Conditional", {}, False),
    ]
    checks = []
    schemas = {}
    for shape in sorted({shape for shape, _, _ in cases}):
        result = subprocess.run(
            [str(cue), "def", "--out", "jsonschema", "-e", "#" + shape, str(ordinary)],
            capture_output=True, text=True, timeout=20, check=True,
        )
        (out / f"ordinary-{shape}.json").write_text(result.stdout)
        schemas[shape] = json.loads(result.stdout)
    with tempfile.TemporaryDirectory(prefix="rulespec-cue-probes-") as temporary:
        for index, (shape, payload, expected) in enumerate(cases):
            fixture = Path(temporary) / f"case-{index}.json"
            fixture.write_text(json.dumps(payload))
            result = subprocess.run(
                [str(cue), "vet", "-c", "-d", "#" + shape, str(ordinary), str(fixture)],
                capture_output=True, text=True, timeout=20,
            )
            source_accepts = result.returncode == 0
            assert source_accepts == expected, result.stderr
            schema = schemas[shape]
            errors = list(Draft202012Validator(schema).iter_errors(payload))
            checks.append({"shape": shape, "payload": payload, "expected_accepts": expected,
                           "cue_accepts": source_accepts, "export_accepts": not errors,
                           "export_errors": [error.message for error in errors]})
    result = subprocess.run([str(source_probe), str(ordinary)], capture_output=True, text=True, check=True)
    parsed = json.loads(result.stdout)
    (out / "native-source.json").write_text(json.dumps(parsed, indent=2) + "\n")
    fields = {tuple(field["path"]): field for field in parsed["fields"]}
    assert fields[("#Rich",)]["annotations"] == {"title": "Rich record", "description": "Explicit shape description"}
    assert fields[("#Rich", "text")]["annotations"] == {"title": "Text", "description": "Exact source text"}
    assert ("#Conditional", "kind") in fields and ("#Conditional", "lineage") in fields
    assert parsed["conditions"] == ['record["kind"] == "ai"']
    source_order = [field["path"][1] for field in parsed["fields"] if len(field["path"]) == 2 and field["path"][0] == "#Concept"]
    assert source_order == ["z_id", "a_label"]
    schema = schemas["Concept"]
    report = {"validation_checks": checks, "validation_mismatches": sum(row["cue_accepts"] != row["export_accepts"] for row in checks),
              "source_property_order": source_order, "export_property_order": list(schema["properties"]),
              "native_parser_preserves_annotations_order_and_conditional_fields": True}
    (out / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
