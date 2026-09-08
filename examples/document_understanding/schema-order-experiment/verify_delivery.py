"""Verify this recorded experiment without provider calls or credentials."""
from pathlib import Path
import json

from rulespec_extrapolator import extraction as e
import experiment as x

ROOT = Path(__file__).resolve().parent
TRIAL = ROOT / "trial-01"


def main():
    design = e._load(TRIAL / "design.json")
    e._verify_runtime(TRIAL, design["runtime"])
    assert e._digest((ROOT / "experiment.py").read_bytes()) == design["runner_sha256"]
    assert (ROOT / "experiment.py").read_bytes() == (TRIAL / "experiment.py").read_bytes()
    for name, sha in design["runtime"]["sources_sha256"].items():
        assert e._digest((TRIAL / "frozen/sources" / name).read_bytes()) == sha
    requests = {}
    for directory in sorted((TRIAL / "runs").glob("*/*/*")):
        request = e._load(directory / "attempt-0000.request.json")
        stats = e._load(directory / "stats.json")
        variant, sample, repeat = stats["variant"], stats["sample"], stats["repeat"]
        config = request["config"]
        assert request["model"] == design["model"]
        assert config["temperature"] == 0 and config["max_output_tokens"] == design["max_output_tokens"]
        assert x.ordered_digest(config["response_json_schema"]) == design["variants"][variant]["ordered_schema_sha256"]
        assert stats["finish_reasons"] == ["STOP"] and stats["output_schema_valid"]
        assert stats["output_order_matches_schema"] and stats["graph_validation"] == "passed"
        requests[sample, variant, repeat] = request["contents"]
    assert len(requests) == 24
    for sample in design["samples"]:
        for repeat in (1, 2):
            assert requests[sample, "current", repeat] == requests[sample, "rich", repeat]
            assert requests[sample, "definitions_first", repeat] == requests[sample, "references_first", repeat]
    assert e._load(TRIAL / "schemas/definitions_first.json") == e._load(TRIAL / "schemas/references_first.json")
    results = e._load(TRIAL / "assessment/results.json")
    assert len(results["judgments"]) == 128
    assert results["review_notes_sha256"] == e._digest((ROOT / "REVIEW-NOTES.md").read_bytes())
    for judgment in results["judgments"]:
        directory = TRIAL / judgment["run_path"]
        assert judgment["raw_output_sha256"] == e._digest((directory / "output.json").read_bytes())
        assert judgment["rulebook_sha256"] == e._digest((directory / "rulebook.json").read_bytes())
        ids = {c["id"] for c in e._load(directory / "rulebook.json")["accepted"]}
        assert set(judgment["accepted_ids"].values()) <= ids
    verification = e._load(TRIAL / "verification.json")
    assert len(verification["replays"]) == 24 and all(r["replayed"] for r in verification["replays"])
    originals = e._load(TRIAL / "original-pins.json")
    assert all(e._digest((ROOT.parent / name).read_bytes()) == sha for name, sha in originals.items())
    record = {"provider_calls": 0, "checked_requests": len(requests), "checked_judgments": 128,
        "same_prompt_comparisons_verified": 12, "ordered_schema_hashes_verified": 24,
        "runtime_and_frozen_sources_match": True, "protected_original_files": len(originals),
        "status": "passed"}
    e._save(TRIAL / "delivery-verification.json", record)
    print(json.dumps(record))


if __name__ == "__main__":
    main()
