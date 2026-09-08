"""Prompt-only follow-up: reuse the prior schema, catalog, adapter and provider path."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import importlib.util
from pathlib import Path
import shutil

from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / "attached-qualifications-experiment"
spec = importlib.util.spec_from_file_location("attached_trial", PREVIOUS / "experiment.py")
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)
trial.ROOT = ROOT
trial.PROMPT = (ROOT / "prompt.txt").read_text()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("run", "replay"))
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if args.mode == "replay":
        design = e._load(ROOT / "design.json")
        for name, digest in design["files_sha256"].items():
            assert e._digest((ROOT / name).read_bytes()) == digest, name
        assert e._digest((PREVIOUS / "experiment.py").read_bytes()) == design["adapter_sha256"]
        sources = e._runtime_sources()
        for name, digest in design["runtime"]["sources_sha256"].items():
            assert e._digest(sources[name].read_bytes()) == digest, name
        for sample in ("names", "photos"):
            directory = ROOT / "runs" / sample
            request = e._load(directory / "attempt-0000.request.json")
            assert request["config"]["response_json_schema"] == e._load(ROOT / "provider.schema.json")
            assert request["config"]["temperature"] == 0
            payload = trial.decode(e._load(directory / "attempt-0000.response.json"))
            book = e._load(directory / "rulebook.json")
            rebuilt, mapping = trial.compile_output(payload, e._load(ROOT / f"{sample}.json"), book["run"])
            assert payload == e._load(directory / "output.json")
            assert rebuilt == book and mapping == e._load(directory / "mapping.json")
            assert e._check_graph(rebuilt["graph"])["status"] == "passed"
        e._save(ROOT / "replay.json", {"status": "identical", "provider_calls": 0})
        print("Both raw responses, mappings and valid Core graphs reproduce identically.")
        return

    if (ROOT / "design.json").exists():
        raise FileExistsError("Preserve the completed or partial experiment")
    copied = ["provider.schema.json", "native-export.json", "experiment.cue",
              "names.json", "photos.json", "names-catalog.json", "photos-catalog.json"]
    for name in copied:
        shutil.copyfile(PREVIOUS / name, ROOT / name)
    schema = e._load(ROOT / "provider.schema.json")
    runtime = e._freeze(ROOT, [], schema)
    runtime["prompt_sha256"] = e._digest(trial.PROMPT)
    shutil.copyfile(PREVIOUS / "experiment.py", ROOT / "frozen/adapter.py")
    for name in ("experiment.py", "experiment.cue", "prompt.txt"):
        shutil.copyfile(ROOT / name, ROOT / "frozen" / name)
    e._save(ROOT / "design.json", {
        "created_at": e._now(), "request_budget": 2, "model": e.DEFAULT_MODEL, "temperature": 0,
        "runtime": runtime, "adapter_sha256": e._digest((PREVIOUS / "experiment.py").read_bytes()),
        "files_sha256": {name: e._digest((ROOT / name).read_bytes())
                         for name in [*copied, "experiment.py", "prompt.txt"]},
        "controls": "../attached-qualifications-experiment (corrected-conversion and raw runs)",
        "changed": ["prompt instructions and invented examples only"],
        "held_fixed": ["provider schema including descriptions and field order", "source documents and passage catalogs",
                       "corrected adapter", "model", "temperature", "output token budget", "no retries or repair calls"],
        "checks": ["previous-name exception retains its target and limits", "emergency permission inherits all three case limits",
                   "recent-change exemption and conditional documentation duty are separate",
                   "explanations and cautions remain visible without false conditions",
                   "photo likeness allowance does not waive recency", "all six alternatives survive conversion",
                   "modality preserved", "all generated qualifications reviewed against source", "graph validation and exact replay"],
        "limits": "Two familiar excerpts; one new response each and saved controls. Failure-informed guidance is not held-out evaluation."
    })
    key = e._credential(args.env_file)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for stats in pool.map(lambda sample: trial.call(sample, key), ("names", "photos")):
            print(e._canonical(stats), flush=True)
    e._write_manifest(ROOT)


if __name__ == "__main__":
    main()
