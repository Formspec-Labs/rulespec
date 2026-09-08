"""Check schema adoption against saved evidence without changing prior captures."""
from copy import deepcopy
import argparse
import ast
import importlib.util
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from rulespec_extrapolator import extraction as e, refinement as r

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
EXPERIMENT = HERE.parent / "schema-order-experiment"
TRIAL = EXPERIMENT / "trial-01"


def ordered(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def without_annotations(value):
    if isinstance(value, dict):
        return {k: without_annotations(v) for k, v in value.items() if k not in {"title", "description"}}
    if isinstance(value, list):
        return [without_annotations(v) for v in value]
    return value


def except_schema_function(path):
    module = ast.parse(path.read_text(encoding="utf-8"))
    module.body = [node for node in module.body
                   if not isinstance(node, ast.FunctionDef) or node.name != "provider_schema"]
    return ast.dump(module, include_attributes=False)


def verify():
    baseline = e._load(HERE / "baseline.json")
    design = e._load(TRIAL / "design.json")
    current = e.provider_schema().to_provider_config()["response_json_schema"]
    old, rich = (e._load(TRIAL / "schemas" / f"{name}.json") for name in ("current", "rich"))
    assert ordered(current) == ordered(rich), "Default differs from the evaluated rich schema"
    assert ordered(without_annotations(current)) == ordered(without_annotations(old))
    assert e._digest(e.PROMPT) == design["runtime"]["prompt_sha256"]
    assert e._digest(e._example_records(e.invented_examples())) == design["runtime"]["examples_sha256"]
    assert e._runtime_versions() == baseline["runtime"]
    Draft202012Validator.check_schema(current)

    changed_sources = [name for name, path in e._runtime_sources().items()
                       if e._digest(path.read_bytes()) != design["runtime"]["sources_sha256"].get(name)]
    assert changed_sources == ["application/extraction.py"], changed_sources
    assert except_schema_function(Path(e.__file__)) == except_schema_function(
        TRIAL / "frozen/sources/application/extraction.py")
    try:
        e._verify_runtime(TRIAL, design["runtime"])
    except e.ReplayDriftError:
        pass
    else:
        raise AssertionError("Historical strict replay should detect the intentional runtime change")

    attributes = deepcopy(current["properties"]["extractions"]["items"]["properties"]["unit_attributes"])
    attributes["properties"].pop("applies_to")
    attributes["required"].remove("applies_to")
    proposals = r.proposal_schema()
    Draft202012Validator.check_schema(proposals)
    assert ordered(proposals["properties"]["proposals"]["items"]["properties"]["fields"]) == ordered(attributes)

    spec = importlib.util.spec_from_file_location("saved_schema_experiment", EXPERIMENT / "experiment.py")
    experiment = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(experiment)
    captures = []
    for directory in sorted((TRIAL / "runs").glob("*/*/*")):
        stats = e._load(directory / "stats.json")
        sample, variant = stats["sample"], stats["variant"]
        document = e._load(TRIAL / "sources" / f"{sample}.json")
        saved = e._load(directory / "rulebook.json")
        payload = experiment.decode(e._load(directory / "attempt-0000.response.json"),
                                    e._load(TRIAL / "schemas" / f"{variant}.json"))
        if variant in {"current", "rich"}:
            Draft202012Validator(current).validate(payload)
        book, mapping = experiment.normalize(payload, document, e.plan_windows(document)[0], variant, saved["run"])
        assert book == saved, str(directory)
        assert mapping == e._load(directory / "mapping.json"), str(directory)
        assert e._check_graph(book["graph"])["status"] == "passed", str(directory)
        captures.append({"run": str(directory.relative_to(TRIAL)), "records_and_graph_unchanged": True})
    assert len(captures) == 24

    for name, sha in baseline["protected_files"].items():
        assert e._digest((REPO / name).read_bytes()) == sha, name
    return {
        "status": "passed", "verified_at": e._now(), "provider_calls": 0,
        "exact_evaluated_schema_including_order": True,
        "schema_constraints_and_field_order_unchanged": True,
        "prompt_and_examples_unchanged": True, "only_runtime_change": changed_sources,
        "only_changed_function": "provider_schema", "historical_strict_replay_detects_drift": True,
        "refinement_reuses_rich_unit_schema": True,
        "ordered_provider_schema_sha256": e._digest(ordered(current)),
        "proposal_schema_sha256": e._digest(ordered(proposals)),
        "captures": captures, "protected_files_unchanged": len(baseline["protected_files"]),
        "boundary": "Offline compatibility checks; the saved 9/16 scores are not a new quality measurement.",
    }


def probe(directory, env_file):
    directory.mkdir(parents=True, exist_ok=False)
    schema = r.proposal_schema()
    key = e._credential(env_file)
    payload, errors, attempt = r._call(directory,
        "There is no source content or existing claim to correct. Return empty proposals and observations arrays.",
        schema, e.DEFAULT_MODEL, key, None)
    e._save(directory / "attempt.json", attempt)
    assert attempt["status"] == "response_received", attempt
    assert not errors, errors
    raw = e._load(directory / attempt["response_file"])
    assert [candidate.get("finish_reason") for candidate in raw["candidates"]] == ["STOP"]
    Draft202012Validator(schema).validate(payload)
    assert payload == {"proposals": [], "observations": []}, payload
    report = {"status": "passed", "provider_calls": 1, "model": raw.get("model_version"),
              "schema_sha256": e._digest(ordered(schema)), "usage": raw.get("usage_metadata"),
              "boundary": "Provider acceptance only; this empty-source probe does not evaluate recovery quality."}
    e._save(directory / "verification.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "verification.json")
    parser.add_argument("--probe", type=Path, help="Make one live request, saved in a new directory")
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if args.probe:
        report = probe(args.probe, args.env_file)
    else:
        if args.output.exists():
            raise FileExistsError("Choose a new verification output path")
        report = verify()
        e._save(args.output, report)
    print(json.dumps({k: v for k, v in report.items() if k != "captures"}))


if __name__ == "__main__":
    main()
