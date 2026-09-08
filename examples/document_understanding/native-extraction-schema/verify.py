"""Verify native profile generation against pre-migration schemas and captures."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

from jsonschema import Draft202012Validator
from rulespec_extrapolator import core, extraction as e, refinement

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "packages/rulespec-extrapolator/src/rulespec_extrapolator/schema_data"


def controls(candidate, provider):
    base = {"kind": "requirement", "summary": "Staff must log requests.", "actor": "Staff", "quote": "Staff must log requests."}
    cases = []

    def add(definition, name, payload, expected):
        cases.append({"definition": definition, "name": name, "payload": payload, "expected": expected})

    add("Candidate", "minimal", base, True)
    for field in candidate["required"]:
        add("Candidate", "missing-" + field, {k: v for k, v in base.items() if k != field}, False)
    add("Candidate", "extra-property", {**base, "extra": True}, False)
    for field, schema in candidate["properties"].items():
        add("Candidate", "wrong-type-" + field, {**base, field: {}}, False)
        if "enum" in schema:
            for value in schema["enum"]:
                add("Candidate", field + "-" + value, {**base, field: value}, True)
            add("Candidate", "unknown-" + field, {**base, field: "not-a-profile-value"}, False)
        elif schema.get("type") == "string":
            add("Candidate", "empty-" + field, {**base, field: ""}, not schema.get("minLength"))
            add("Candidate", "unicode-" + field, {**base, field: "é🪪"}, True)
        elif schema.get("type") == "array":
            add("Candidate", "empty-list-" + field, {**base, field: []}, True)
            add("Candidate", "empty-item-" + field, {**base, field: [""]}, False)
            add("Candidate", "repeated-item-" + field, {**base, field: ["exact", "exact"]}, not schema.get("uniqueItems"))
            add("Candidate", "valid-list-" + field, {**base, field: ["exact", "other"]}, True)
    for field in ("start", "end"):
        for value, valid in [(None, True), (0, True), (5, True), (-1, False), (0.5, False), (False, False), ("0", False)]:
            add("Candidate", field + "-" + repr(value), {**base, field: value}, valid)
    add("ExtractionResponse", "empty-results", {"extractions": []}, True)
    add("ExtractionResponse", "missing-results", {}, False)
    add("ExtractionResponse", "extra-property", {"extractions": [], "extra": True}, False)
    attrs_schema = provider["properties"]["extractions"]["items"]["properties"]["unit_attributes"]
    attrs = {name: [] if value.get("type") == "array" else "" for name, value in attrs_schema["properties"].items()}
    attrs.update(kind="statement", modality="not_stated", relation="none")
    row = {"unit": "Source text", "unit_attributes": attrs}
    add("ExtractionResponse", "empty-placeholders", {"extractions": [row]}, True)
    for field in row:
        add("ExtractionResponse", "missing-" + field, {"extractions": [{k: v for k, v in row.items() if k != field}]}, False)
    for field in attrs:
        missing = {k: v for k, v in attrs.items() if k != field}
        add("ExtractionResponse", "missing-" + field, {"extractions": [{**row, "unit_attributes": missing}]}, False)
        add("ExtractionResponse", "wrong-type-" + field, {"extractions": [{**row, "unit_attributes": {**attrs, field: {}}}]}, False)
    add("ExtractionResponse", "unknown-meaning-field", {"extractions": [{**row, "unit_attributes": {**attrs, "extra": True}}]}, False)
    for index, example in enumerate(e.invented_examples()):
        payload = {"extractions": [{"unit": item.extraction_text, "unit_attributes": item.attributes} for item in example.extractions]}
        add("ExtractionResponse", f"invented-example-{index}", payload, True)
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cue", type=Path, required=True)
    parser.add_argument("--generated", type=Path, default=DATA)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--runtime", action="store_true", help="also check installed schemas and saved response normalization")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new verification output")
    old_candidate = e._load(HERE / "before/candidate-schema.json")
    old_provider = e._load(HERE / "before/provider-schema.json")
    new_candidate = e._load(args.generated / "candidate.schema.json")
    new_provider = e._load(args.generated / "provider.schema.json")
    assert json.dumps(new_provider) == json.dumps(old_provider), "Model schema changed, including serialization order"
    schemas = {"Candidate": (old_candidate, new_candidate), "ExtractionResponse": (old_provider, new_provider)}
    for pair in schemas.values():
        for schema in pair:
            Draft202012Validator.check_schema(schema)
    cases = controls(old_candidate, old_provider)
    with tempfile.TemporaryDirectory(prefix="rulespec-native-controls-") as temporary:
        def check(indexed):
            index, case = indexed
            path = Path(temporary) / f"{index}.json"
            path.write_text(json.dumps(case["payload"], ensure_ascii=False))
            old, new = schemas[case["definition"]]
            result = subprocess.run([str(args.cue.resolve()), "vet", "-c", "-d", "#" + case["definition"],
                                     ".", str(path)],
                                    cwd=DATA, capture_output=True, text=True, timeout=30)
            return {**case, "old_accepts": Draft202012Validator(old).is_valid(case["payload"]),
                    "generated_accepts": Draft202012Validator(new).is_valid(case["payload"]),
                    "cue_accepts": result.returncode == 0, "cue_stderr": result.stderr}
        with ThreadPoolExecutor(max_workers=4) as pool:
            checked = list(pool.map(check, enumerate(cases)))
    failures = [case for case in checked if any(case[key] != case["expected"] for key in ("old_accepts", "generated_accepts", "cue_accepts"))]
    report = {"status": "failed" if failures else "passed", "provider_calls": 0,
              "exact_model_schema_including_order": True, "controls": checked, "control_count": len(checked),
              "failed_controls": [c["name"] for c in failures]}
    if args.runtime and not failures:
        assert core.CANDIDATE_SCHEMA == new_candidate
        assert json.dumps(e.provider_schema().schema_dict) == json.dumps(old_provider)
        assert json.dumps(refinement.proposal_schema()) == json.dumps(e._load(HERE / "before/proposal-schema.json"))
        baseline = e._load(HERE / "baseline.json")
        assert e._digest(e.PROMPT) == baseline["prompt_sha256"]
        assert e._digest(e._example_records(e.invented_examples())) == baseline["examples_sha256"]
        trial = HERE.parent / "schema-order-experiment/trial-01"
        spec = importlib.util.spec_from_file_location("saved_schema_experiment", trial.parent / "experiment.py")
        experiment = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(experiment)
        captures = []
        for directory in sorted((trial / "runs").glob("*/*/*")):
            stats = e._load(directory / "stats.json")
            sample, variant = stats["sample"], stats["variant"]
            document = e._load(trial / "sources" / f"{sample}.json")
            saved = e._load(directory / "rulebook.json")
            payload = experiment.decode(e._load(directory / "attempt-0000.response.json"), e._load(trial / "schemas" / f"{variant}.json"))
            book, mapping = experiment.normalize(payload, document, e.plan_windows(document)[0], variant, saved["run"])
            assert book == saved, str(directory)
            assert mapping == e._load(directory / "mapping.json"), str(directory)
            assert e._check_graph(book["graph"])["status"] == "passed", str(directory)
            captures.append(str(directory.relative_to(trial)))
        assert len(captures) == 24
        try:
            e._verify_runtime(trial, e._load(trial / "design.json")["runtime"])
        except e.ReplayDriftError:
            pass
        else:
            raise AssertionError("Historical strict replay must notice changed runtime inputs")
        for name, digest in baseline["protected_files"].items():
            assert e._digest((ROOT / name).read_bytes()) == digest, name
        for name, digest in baseline["core_sources"].items():
            assert e._digest((ROOT / name).read_bytes()) == digest, name
        report.update(runtime_schemas_generated=True, refinement_schema_unchanged=True,
                      prompt_and_examples_unchanged=True, unchanged_captures=captures,
                      historical_strict_replay_detects_drift=True, protected_files_unchanged=len(baseline["protected_files"]),
                      unchanged_core_sources=len(baseline["core_sources"]))
    e._save(args.output, report)
    print(json.dumps({k: v for k, v in report.items() if k not in {"controls", "unchanged_captures"}}))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
