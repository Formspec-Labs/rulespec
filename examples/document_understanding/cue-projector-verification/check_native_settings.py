#!/usr/bin/env python3
"""Check native CUE settings without changing production source or old captures."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "native-export" / "settings-check"
CASES = [
    ("Concept", "valid", {"z_id": "c1", "a_label": "Applicant"}, True),
    ("Concept", "missing-id", {"a_label": "Applicant"}, False),
    ("Concept", "extra-field", {"z_id": "c1", "a_label": "Applicant", "extra": True}, False),
    ("Composed", "valid", {"z_id": "c1", "a_label": "Applicant", "own": 1}, True),
    ("Composed", "missing-own", {"z_id": "c1", "a_label": "Applicant"}, False),
    ("Composed", "below-minimum", {"z_id": "c1", "a_label": "Applicant", "own": 0}, False),
    ("Composed", "extra-field", {"z_id": "c1", "a_label": "Applicant", "own": 1, "extra": True}, False),
    ("Conditional", "human", {"kind": "human"}, True),
    ("Conditional", "ai-with-lineage", {"kind": "ai", "lineage": "run-1"}, True),
    ("Conditional", "ai-without-lineage", {"kind": "ai"}, False),
    ("Conditional", "empty", {}, False),
    ("Conditional", "wrong-kind", {"kind": "robot"}, False),
    ("Conditional", "wrong-lineage-type", {"kind": "ai", "lineage": 7}, False),
    ("Conditional", "lineage-outside-branch", {"kind": "human", "lineage": "run-1"}, False),
    ("Conditional", "extra-field", {"kind": "ai", "lineage": "run-1", "extra": True}, False),
]


def run(command, *, cwd=None):
    result = subprocess.run([str(x) for x in command], cwd=cwd, capture_output=True, text=True, timeout=40)
    return {"command": [str(x) for x in command], "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cue", type=Path, required=True)
    parser.add_argument("--settings-probe", type=Path, required=True)
    args = parser.parse_args()
    cue, probe = args.cue.resolve(), args.settings_probe.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    original = (HERE / "native-export/probes/ordinary.cue").read_text()
    source_variants = {"original": HERE / "native-export/probes/ordinary.cue"}
    setup = []
    for exp in ["explicitopen", "aliasv2", "all"]:
        source = OUT / ("fix-" + exp) / "ordinary.cue"
        source.parent.mkdir(exist_ok=True)
        source.write_text(original)
        result = run([cue, "fix", "--exp=" + exp, source])
        setup.append(result)
        assert result["returncode"] == 0, result
        source_variants["fix-" + exp] = source
    no_alias = OUT / "no-alias.cue"
    no_alias.write_text(original.replace("#Conditional: record={", "#Conditional: {").replace('record["kind"]', 'kind').replace('"kind":', 'kind:'))
    source_variants["no-alias"] = no_alias
    for language in ["v0.10.0", "v0.17.0"]:
        for exp in [False, True]:
            key = "language-" + language + ("-explicitopen" if exp else "")
            directory = OUT / key
            (directory / "cue.mod").mkdir(parents=True, exist_ok=True)
            (directory / "cue.mod/module.cue").write_text('module: "rulespec.invalid/settings@v0"\nlanguage: version: "' + language + '"\n')
            source = directory / "ordinary.cue"
            source.write_text(original)
            if exp:
                result = run([cue, "fix", "--exp=explicitopen", "ordinary.cue"], cwd=directory)
                setup.append(result)
            source_variants[key] = source
    strict_schema = json.loads((OUT / "conditional-input.json").read_text())
    strict_schema["else"] = {"not": {"required": ["lineage"]}}
    write_json(OUT / "conditional-strict-input.json", strict_schema)
    imported = OUT / "imported-strict-conditional.cue"
    result = run([cue, "import", "jsonschema:", OUT / "conditional-strict-input.json", "-l", "#Conditional:", "-p", "test", "-f", "-o", imported])
    setup.append(result)
    assert result["returncode"] == 0, result
    source_variants["imported-matchIf-strict"] = imported
    union = OUT / "union-conditional.cue"
    union.write_text('package test\n\n#Conditional: {kind: "human"} | {kind: "ai", lineage: string}\n')
    source_variants["union-conditional"] = union
    fixtures = OUT / "fixtures"
    fixtures.mkdir(exist_ok=True)
    for shape, name, payload, _ in CASES:
        write_json(fixtures / (shape + "-" + name + ".json"), payload)

    source_checks = []
    exports = []
    for variant, source in source_variants.items():
        shapes = {shape for shape, _, _, _ in CASES if shape == "Conditional" or variant not in {"imported-matchIf-strict", "union-conditional"}}
        for shape in sorted(shapes):
            result = run([cue, "def", "--out", "jsonschema", "-e", "#" + shape, source.name], cwd=source.parent)
            write_json(OUT / "exports" / (variant + "-" + shape + ".json"), result)
            schema = json.loads(result["stdout"]) if result["returncode"] == 0 else None
            if schema is not None:
                Draft202012Validator.check_schema(schema)
            checks = []
            for case_shape, name, payload, expected in CASES:
                if case_shape != shape:
                    continue
                vet = run([cue, "vet", "-c", "-d", "#" + shape, source.name, fixtures / (shape + "-" + name + ".json")], cwd=source.parent)
                accepts = vet["returncode"] == 0
                errors = list(Draft202012Validator(schema).iter_errors(payload)) if schema is not None else None
                row = {"variant": variant, "shape": shape, "case": name, "expected": expected,
                       "source_accepts": accepts, "source_stderr": vet["stderr"],
                       "schema_accepts": not errors if errors is not None else None,
                       "schema_errors": [e.message for e in errors] if errors is not None else None}
                checks.append(row)
                source_checks.append(row)
            exports.append({"variant": variant, "shape": shape, "returncode": result["returncode"],
                            "source_mismatches": sum(r["source_accepts"] != r["expected"] for r in checks),
                            "schema_mismatches": sum(r["schema_accepts"] != r["expected"] for r in checks)})

    flag_results = []
    settings = [("default", "jsonschema", []), ("strict", "jsonschema+strict", []),
                ("strict-features", "jsonschema+strictFeatures", []),
                ("strict-keywords", "jsonschema+strictKeywords", []),
                ("open-only-when-explicit", "jsonschema+openOnlyWhenExplicit", []),
                ("attributes", "jsonschema", ["-A"]), ("simplify", "jsonschema", ["-s"]),
                ("inline-imports", "jsonschema", ["--inline-imports"])]
    for variant in ["original", "fix-explicitopen", "imported-matchIf-strict"]:
        source = source_variants[variant]
        for shape in (["Conditional"] if variant == "imported-matchIf-strict" else ["Concept", "Composed", "Conditional"]):
            baseline = None
            for setting, tag, flags in settings:
                result = run([cue, "def", "--out", tag, *flags, "-e", "#" + shape, source])
                schema = json.loads(result["stdout"]) if result["returncode"] == 0 else None
                if setting == "default":
                    baseline = schema
                flag_results.append({"variant": variant, "shape": shape, "setting": setting,
                                     "same_schema_as_default": schema == baseline, **result})

    api_results = []
    for variant in ["original", "fix-explicitopen", "imported-matchIf-strict"]:
        source = source_variants[variant]
        for shape in (["Conditional"] if variant == "imported-matchIf-strict" else ["Concept", "Composed", "Conditional"]):
            for flags in [[], ["-explicit-open"], ["-eval"], ["-eval", "-explicit-open"], ["-check-value-error"]]:
                result = run([probe, "-schema", "#" + shape, *flags, source])
                schema = json.loads(result["stdout"]) if result["returncode"] == 0 else None
                checks = []
                for case_shape, name, payload, expected in CASES:
                    if shape == case_shape:
                        accepts = Draft202012Validator(schema).is_valid(payload) if schema is not None else None
                        checks.append({"case": name, "expected": expected, "accepts": accepts})
                api_results.append({"variant": variant, "shape": shape, "flags": flags,
                                    "checks": checks, "mismatches": sum(r["accepts"] != r["expected"] for r in checks), **result})
    openapi_results = []
    for variant in ["original", "fix-explicitopen", "imported-matchIf-strict", "union-conditional"]:
        for flags in [[], ["-expand-references"], ["-strict-features"], ["-expand-references", "-strict-features"], ["-version", "3.1.0", "-strict-features"]]:
            result = run([probe, "-openapi", *flags, source_variants[variant]])
            openapi_results.append({"variant": variant, "flags": flags, **result})
    report = {"cue_version": run([cue, "version"]), "environment": {name: os.environ.get(name) for name in ["CUE_EXPERIMENT", "CUE_EVALUATOR"]},
              "source_hashes": {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in source_variants.items()},
              "setup": setup, "source_exports": exports, "source_checks": source_checks,
              "cli_settings": flag_results, "go_api_settings": api_results, "openapi_settings": openapi_results}
    write_json(OUT / "report.json", report)
    print(json.dumps({"source_exports": exports,
                      "cli_changes": [{k: r[k] for k in ["variant", "shape", "setting", "returncode", "same_schema_as_default", "stderr"]} for r in flag_results if not r["same_schema_as_default"]],
                      "go_api_settings": [{k: r[k] for k in ["variant", "shape", "flags", "mismatches", "returncode"]} for r in api_results],
                      "openapi_settings": [{k: r[k] for k in ["variant", "flags", "returncode", "stderr"]} for r in openapi_results]}, indent=2))


if __name__ == "__main__":
    main()
