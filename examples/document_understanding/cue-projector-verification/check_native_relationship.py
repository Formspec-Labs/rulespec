#!/usr/bin/env python3
"""Test an explicit matchIf rewrite on copied Rulespec assertions."""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import constraints_parity as parity
from compare_native import source_spelling, verdict

OUT = HERE / "native-export/settings-check/relationship"
FILES = ["assertion.cue", "relationship-assertion.cue", "usage-eligibility.cue",
         "trust-and-safety.cue", "generated-work-product.cue"]


def run(command):
    result = subprocess.run([str(x) for x in command], capture_output=True, text=True, timeout=30)
    return {"command": [str(x) for x in command], "returncode": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr}


def replace_once(source, before, after):
    assert source.count(before) == 1, before
    return source.replace(before, after)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cue", type=Path, required=True)
    args = ap.parse_args()
    cue = args.cue.resolve()
    sources = {}
    for variant in ["original", "explicitopen", "matchIf"]:
        directory = OUT / variant
        directory.mkdir(parents=True, exist_ok=True)
        sources[variant] = [directory / name for name in FILES]
        for name in FILES:
            source_root = ROOT / "constraints/core" if variant == "original" else OUT.parent / "migrated-constraints/core"
            (directory / name).write_bytes((source_root / name).read_bytes())
    assertion = sources["matchIf"][0]
    text = assertion.read_text().replace("#AssertionEnvelope: envelope={", "#AssertionEnvelope: {")
    text = replace_once(text, '''	if envelope["rkaf:assertionOrigin"] == "rkaf:aiSuggested" {
		"rkaf:hasAILineage":     string
		"rkaf:usageEligibility": #ProvisionalAIUsageEligibility
	}''', '''	"rkaf:hasAILineage"?: string
	matchIf({"rkaf:assertionOrigin"!: "rkaf:aiSuggested", ...}, {
		"rkaf:hasAILineage"!:     string
		"rkaf:usageEligibility"!: #ProvisionalAIUsageEligibility
		...
	}, {"rkaf:hasAILineage"?: _|_, ...})''')
    text = replace_once(text, '''	if envelope["rkaf:assertionOrigin"] == "rkaf:deterministicExtraction" {
		"rkaf:hasExtractionProvenance": string
	}''', '''	matchIf({"rkaf:assertionOrigin"!: "rkaf:deterministicExtraction", ...}, {
		"rkaf:hasExtractionProvenance"!: string
		...
	}, _)''')
    assertion.write_text(text)
    relationship = sources["matchIf"][1]
    text = relationship.read_text().replace("#RelationshipAssertion: assertion={", "#RelationshipAssertion: {")
    text = replace_once(text, '''	if assertion["rkaf:assertionOrigin"] == "rkaf:aiSuggested" {
		"rkaf:hasAILineage": string & =~"^[A-Za-z][A-Za-z0-9+.-]*:[^\\\\s]+$"
	}''', '''	matchIf({"rkaf:assertionOrigin"!: "rkaf:aiSuggested", ...}, {
		"rkaf:hasAILineage"!: string & =~"^[A-Za-z][A-Za-z0-9+.-]*:[^\\\\s]+$"
		...
	}, _)''')
    text = replace_once(text, '''	if assertion["rkaf:assertionOrigin"] == "rkaf:deterministicExtraction" {
		"rkaf:hasExtractionProvenance": string & =~"^[A-Za-z][A-Za-z0-9+.-]*:[^\\\\s]+$"
	}''', '''	matchIf({"rkaf:assertionOrigin"!: "rkaf:deterministicExtraction", ...}, {
		"rkaf:hasExtractionProvenance"!: string & =~"^[A-Za-z][A-Za-z0-9+.-]*:[^\\\\s]+$"
		...
	}, _)''')
    relationship.write_text(text)
    format_result = run([cue, "fmt", *sources["matchIf"]])
    assert format_result["returncode"] == 0, format_result
    schema_doc = json.loads((HERE / "before/core/relationship-assertion.json").read_text())
    schema = {**schema_doc["$defs"]["RelationshipAssertion"], "$defs": schema_doc["$defs"]}
    cases = []
    for _, shape, fixture, expected in parity.FIXTURE_BINDINGS:
        if shape != "RelationshipAssertion":
            continue
        payload = json.loads((ROOT / fixture).read_text())
        nodes = [node for node in payload.get("@graph", [payload]) if node.get("@type") == "rkaf:RelationshipAssertion"]
        assert nodes
        nodes = [{k: v for k, v in node.items() if k != "@context"} for node in nodes]
        cases.append({"name": fixture, "kind": "saved-fixture", "expected": expected, "nodes": nodes})
    human = copy.deepcopy(next(c for c in cases if c["name"] == "fixtures/relationshipassertion-affirmed-positive.jsonld")["nodes"][0])
    ai = {**human, "rkaf:assertionOrigin": "rkaf:aiSuggested", "rkaf:hasAILineage": "urn:run:1", "rkaf:usageEligibility": "rkaf:searchOnly"}
    deterministic = {**human, "rkaf:assertionOrigin": "rkaf:deterministicExtraction", "rkaf:hasExtractionProvenance": "urn:run:2"}
    controls = [("valid-ai", ai, "PASS"), ("valid-deterministic", deterministic, "PASS")]
    for name, key in [("ai-missing-lineage-only", "rkaf:hasAILineage"), ("ai-missing-eligibility-only", "rkaf:usageEligibility")]:
        controls.append((name, {k: v for k, v in ai.items() if k != key}, "FAIL"))
    controls.extend([
        ("ai-operational-eligibility", {**ai, "rkaf:usageEligibility": "rkaf:localOperationalUse"}, "FAIL"),
        ("ai-lineage-not-iri", {**ai, "rkaf:hasAILineage": "not-an-iri"}, "FAIL"),
        ("deterministic-missing-provenance-only", {k: v for k, v in deterministic.items() if k != "rkaf:hasExtractionProvenance"}, "FAIL"),
        ("deterministic-provenance-not-iri", {**deterministic, "rkaf:hasExtractionProvenance": "not-an-iri"}, "FAIL"),
        ("human-with-lineage", {**human, "rkaf:hasAILineage": "urn:run:1"}, "FAIL"),
        ("ai-with-extra-field", {**ai, "extra": True}, "FAIL"),
    ])
    cases.extend({"name": name, "kind": "focused-source-control", "expected": expected, "nodes": [node]} for name, node, expected in controls)
    exports = {}
    for variant, source_files in sources.items():
        result = run([cue, "def", "--out", "jsonschema", "-e", "#RelationshipAssertion", *source_files])
        assert result["returncode"] == 0, result
        exports[variant] = result
        (OUT / (variant + ".schema.json")).write_text(result["stdout"])
    checks = []
    for index, case in enumerate(cases):
        nodes = [source_spelling(node, schema, schema_doc["$defs"]) for node in case["nodes"]]
        paths = []
        for node_index, node in enumerate(nodes):
            path = OUT / "fixtures" / (str(index) + "-" + str(node_index) + ".json")
            path.parent.mkdir(exist_ok=True)
            path.write_text(json.dumps(node, indent=2) + "\n")
            paths.append(path)
        row = {**case, "source_spelling_nodes": nodes, "original_compiler_raw": verdict(schema, case["nodes"], extensions=True), "variants": {}}
        for variant, source_files in sources.items():
            vet = run([cue, "vet", "-c", "-d", "#RelationshipAssertion", *source_files, *paths])
            output_schema = json.loads(exports[variant]["stdout"])
            row["variants"][variant] = {"cue": "PASS" if vet["returncode"] == 0 else "FAIL", "cue_stderr": vet["stderr"],
                                        "native_source_spelling": verdict(output_schema, nodes), "native_raw": verdict(output_schema, case["nodes"])}
        checks.append(row)
    summary = {}
    for variant in sources:
        summary[variant] = {"cases": len(checks),
                            "source_expected_mismatches": sum(c["variants"][variant]["cue"] != c["expected"] for c in checks),
                            "export_expected_mismatches": sum(c["variants"][variant]["native_source_spelling"]["verdict"] != c["expected"] for c in checks),
                            "source_behavior_changes": sum(c["variants"][variant]["cue"] != c["variants"]["original"]["cue"] for c in checks),
                            "raw_saved_fixture_mismatches": sum(c["variants"][variant]["native_raw"]["verdict"] != c["expected"] for c in checks if c["kind"] == "saved-fixture")}
    report = {"summary": summary, "format": format_result, "exports": exports, "checks": checks,
              "source_hashes": {variant: {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths} for variant, paths in sources.items()},
              "limitations": "This is a focused source rewrite, not a production converter or proof of equivalence for every extending definition. Raw JSON-LD conventions remain separate. Focused controls expect CUE closure; the existing compiler intentionally accepts resource extensions."}
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
