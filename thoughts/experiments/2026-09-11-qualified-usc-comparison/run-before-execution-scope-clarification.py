"""Capture existing reader outputs unchanged; no production adapter or new parser."""
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from refspec.registry import citation_grammar as ref
from spicysearch import cfr_citations as spicy

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[3]
LOCK = WORK / "spicysearch/compositions/measurement.lock"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    with (HERE / name).open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


cases = json.loads((HERE / "cases.json").read_text())
metadata = {"python": sys.executable, "network_calls": 0,
            "design_sha256": sha(HERE / "design.md"),
            "cases_sha256": sha(HERE / "cases.json"), "modules": {}, "repos": {}}
for name, module in tuple(sys.modules.items()):
    if name.startswith(("refspec.", "spicysearch.")) and getattr(module, "__file__", None):
        path = Path(module.__file__).resolve()
        if path.is_file():
            metadata["modules"][name] = {"path": str(path), "sha256": sha(path)}
for name in ("rulespec", "RefSpec", "spicysearch"):
    metadata["repos"][name] = {
        label: subprocess.check_output(["git", "-C", str(WORK / name), *args], text=True)
        for label, args in (("head", ["rev-parse", "HEAD"]), ("status", ["status", "--short"]))
    }
print(json.dumps({name: str(Path(module.__file__).resolve())
                  for name, module in (("refspec", ref), ("spicysearch", spicy))}), flush=True)
deadline = time.monotonic() + 300
while True:
    load = os.getloadavg()
    if load[0] < 4:
        try:
            stream = LOCK.open("x")
        except FileExistsError:
            pass
        else:
            with stream:
                json.dump({"holder": "rulespec-qualified-usc", "pid": os.getpid(),
                           "start": datetime.now(timezone.utc).isoformat(),
                           "purpose": "deterministic USC reader comparison", "start_load": load}, stream)
            break
    if time.monotonic() >= deadline:
        save("not-run.json", {**metadata, "reason": "measurement lock or load threshold", "load": load})
        raise SystemExit("No parser run: measurement lock or load threshold.")
    print(f"Waiting for measurement slot; load={load[0]:.2f}", flush=True)
    time.sleep(10)
try:
    metadata.update(started=datetime.now(timezone.utc).isoformat(), start_load=load)
    arms = {"spicysearch_strict": lambda text: spicy.extract_usc_citations(text, strict=True, keep_rejected=True),
            "refspec_authority": ref.parse_authority_citation}

    def run():
        rows = []
        for case in cases:
            assert hashlib.sha256(case["raw"].encode()).hexdigest() == case["text_sha256"]
            row = {"id": case["id"], "arms": {}}
            for name, reader in arms.items():
                try:
                    row["arms"][name] = {"output": [asdict(item) for item in reader(case["raw"])]}
                except Exception as error:
                    row["arms"][name] = {"error": {"type": type(error).__name__, "message": str(error)}}
            if case["id"] == "historical-cfr":
                row["cfr_control"] = [asdict(item) for item in ref.find_cfr_citations(case["raw"])]
            rows.append(row)
        return rows

    first = run()
    save("raw.json", first)
    second = run()
    save("replay.json", second)
    metadata.update(replay_equal=first == second, end_load=os.getloadavg(),
                    finished=datetime.now(timezone.utc).isoformat())
    metadata["source_hashes_unchanged"] = all(
        sha(Path(item["path"])) == item["sha256"] for item in metadata["modules"].values())
    for name, values in metadata["repos"].items():
        values["head_after"] = subprocess.check_output(["git", "-C", str(WORK / name), "rev-parse", "HEAD"], text=True)
    save("run.json", metadata)
    assert metadata["replay_equal"] and metadata["source_hashes_unchanged"]
    assert all(item["head"] == item["head_after"] for item in metadata["repos"].values())
    print(f"Captured {len(first)} cases and exact replay.")
finally:
    LOCK.unlink()
