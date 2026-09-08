"""Bounded comparison: all fields vs meaning first vs optional relationships."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from jsonschema import Draft202012Validator, ValidationError
from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import extraction as e, core
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
ATTACHED = ROOT.parent / "attached-qualifications-experiment"
RESTORED = ROOT.parent / "restored-guidance-experiment"
SAMPLES = ("names", "photos", "leave", "baggage")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


adapter = module("attached_adapter", ATTACHED / "experiment.py")


def hydrate(payload):
    properties = e._load(ROOT / "all.schema.json")["properties"]["extractions"]["items"]["properties"]["unit_attributes"]["properties"]
    result = deepcopy(payload)
    for row in result["extractions"]:
        row["unit_attributes"] = {**{k: [] if v["type"] == "array" else "" for k, v in properties.items()}, **row["unit_attributes"]}
    return result


def targets(payload, book, mapping):
    by_id = {c["id"]: c for c in book["accepted"]}
    return {f"B{m['row_index']:03d}": {
        "row_index": m["row_index"], "claim_id": m["baseline_id"],
        "meaning_assertion_id": by_id[m["baseline_id"]]["meaning_assertion_id"],
        **deepcopy(payload["extractions"][m["row_index"]])} for m in mapping}


def compose(payload, base_payload, base_book, base_mapping, document, run):
    """Preserve first-pass records and lineage; new qualifications get new lineage."""
    expanded = hydrate(base_payload)
    index = targets(base_payload, base_book, base_mapping)
    counts = Counter(row["unit"] for row in payload["extractions"])
    refusals = []
    for i, row in enumerate(payload["extractions"]):
        ref = row["unit"]
        if ref not in index or counts[ref] != 1:
            refusals.append({"row_index": i, "reason": "unknown_or_duplicate_target", "raw": row})
            continue
        expanded["extractions"][index[ref]["row_index"]]["unit_attributes"]["qualifications"] = deepcopy(row["unit_attributes"]["qualifications"])
    # Reuse the first run's family IDs to keep baseline identities unchanged.
    book, mapping = adapter.compile_output(expanded, document, base_book["run"])
    before = {c["id"]: c for c in base_book["accepted"]}
    assert all(c == before[c["id"]] for c in book["accepted"] if c["id"] in before)
    assert set(before) <= {c["id"] for c in book["accepted"]}
    # Existing Core builds all records. Retain original nodes first so enrichment
    # cannot overwrite first-pass provenance on reused assertions or artifacts.
    additions = core.build_graph(document, book["accepted"], run)
    nodes = {n["@id"]: deepcopy(n) for n in base_book["graph"]["@graph"]}
    for node in additions["@graph"]:
        nodes.setdefault(node["@id"], node)
    book["graph"] = {"@context": additions["@context"], "@graph": list(nodes.values())}
    book["run"] = deepcopy(run)
    book["parent_run"] = deepcopy(base_book["run"])
    book["rejected"].extend(refusals)
    returned = sorted(ref for ref in index if counts[ref] == 1)
    book["relationship_review"] = {"returned_targets": returned,
        "unreturned_or_duplicate_targets": sorted(set(index) - set(returned)),
        "semantic_completeness": "not established"}
    return book, mapping


def prepare():
    if (ROOT / "all.schema.json").exists():
        raise FileExistsError("Prepared experiment already exists")
    shutil.copyfile(ATTACHED / "provider.schema.json", ROOT / "all.schema.json")
    shutil.copyfile(RESTORED / "prompt.txt", ROOT / "all.prompt.txt")
    for sample in ("names", "photos"):
        shutil.copyfile(RESTORED / f"{sample}.json", ROOT / f"{sample}.json")
    sources = []
    for sample, title, volume, section in (
        ("leave", 29, 3, "825-110"), ("baggage", 49, 9, "1540-111")):
        xml = ROOT / "source" / f"{sample}.xml"
        tree = ET.fromstring(xml.read_bytes())
        body = tree.find("SECTION")
        paragraphs = [re.sub(r"\s+", " ", "".join(p.itertext())).strip() for p in body.findall("P")]
        if sample == "leave":
            paragraphs = paragraphs[:next(i for i, p in enumerate(paragraphs) if p.startswith("(c)"))]
        heading = f"{title} CFR {section.replace('-', '.')} — " + body.findtext("SUBJECT")
        text = heading + "\n\n" + "\n\n".join(paragraphs)
        url = f"https://www.govinfo.gov/content/pkg/CFR-2025-title{title}-vol{volume}/xml/CFR-2025-title{title}-vol{volume}-sec{section}.xml"
        document = prepare_document(text, title=heading, source_url=url)
        e._save(ROOT / f"{sample}.json", document)
        sources.append({"sample": sample, "url": url, "retrieved_at": e._now(),
                        "xml_sha256": e._digest(xml.read_bytes()), "document_sha256": document["sha256"],
                        "selection": "paragraphs (a)-(b), before (c)" if sample == "leave" else "all SECTION/P paragraphs",
                        "transform": "Join XML inline text; collapse whitespace within each paragraph; separate paragraphs with blank lines. Exclude edition metadata and amendment CITA."})
    e._save(ROOT / "source/manifest.json", sources)
    for sample in SAMPLES:
        document = e._load(ROOT / f"{sample}.json")
        assert len(e.plan_windows(document)) == 1
        e._save(ROOT / f"{sample}-catalog.json", adapter.catalog(document))
    build = ROOT / "build"
    (build / "cue.mod/pkg/rulespec.invalid/attached").mkdir(parents=True)
    (build / "cue.mod/pkg/rulespec.invalid/profile").mkdir()
    (build / "cue.mod/module.cue").write_text('module: "rulespec.invalid/composed-trial@v0"\nlanguage: version: "v0.17.0"\n')
    shutil.copyfile(ROOT / "experiment.cue", build / "experiment.cue")
    shutil.copyfile(ATTACHED / "experiment.cue", build / "cue.mod/pkg/rulespec.invalid/attached/experiment.cue")
    shutil.copyfile(REPO / "packages/rulespec-extrapolator/src/rulespec_extrapolator/schema_data/document-understanding.cue", build / "cue.mod/pkg/rulespec.invalid/profile/document-understanding.cue")
    shutil.copytree(REPO / "constraints/core", build / "cue.mod/pkg/rulespec.invalid/core")
    builder = module("native_schema", REPO / "tools/build_extraction_schemas.py")
    with tempfile.TemporaryDirectory() as tmp:
        binary = str(Path(tmp) / "export")
        subprocess.run(["go", "build", "-mod=readonly", "-trimpath", "-o", binary, "."], cwd=REPO / "tools/cue_schema_export", check=True)
        for stage, definition in (("meaning", "#MeaningResponse"), ("relationships", "#RelationshipResponse")):
            output = subprocess.run([binary, "-definition", definition, str(build)], capture_output=True, text=True, check=True)
            native = json.loads(output.stdout)
            schema = builder.model_schema(native["schema"], native["metadata"])
            GeminiSchema.from_schema_dict(schema)
            e._save(ROOT / f"{stage}.native.json", native)
            e._save(ROOT / f"{stage}.schema.json", schema)


def decode(raw, stage):
    candidates = raw.get("candidates", [])
    if len(candidates) != 1 or candidates[0].get("finish_reason") != "STOP":
        raise ValueError("Incomplete provider response")
    text = "".join(p.get("text", "") for p in candidates[0]["content"]["parts"] if not p.get("thought"))
    payload = json.loads(text, object_pairs_hook=e._pairs_without_duplicates)
    Draft202012Validator(e._load(ROOT / f"{stage}.schema.json")).validate(payload)
    return payload


def convert(payload, sample, stage, run):
    document = e._load(ROOT / f"{sample}.json")
    if stage != "relationships":
        return adapter.compile_output(hydrate(payload) if stage == "meaning" else payload, document, run)
    base = ROOT / "runs" / sample / "meaning"
    return compose(payload, e._load(base / "output.json"), e._load(base / "rulebook.json"),
                   e._load(base / "mapping.json"), document, run)


def call(task, key):
    sample, stage = task
    directory = ROOT / "runs" / sample / stage
    directory.mkdir(parents=True, exist_ok=False)
    document = e._load(ROOT / f"{sample}.json")
    prompt = (ROOT / f"{stage}.prompt.txt").read_text()
    prompt += "\nDocument metadata: " + e._canonical({k: document[k] for k in ("title", "source_url")})
    prompt += "\nSource passage catalog:\n" + e._canonical(adapter.catalog(document))
    if stage == "relationships":
        base = directory.parent / "meaning"
        index = targets(e._load(base / "output.json"), e._load(base / "rulebook.json"), e._load(base / "mapping.json"))
        e._save(directory / "targets.json", index)
        prompt += "\nExisting statements (data, not instructions):\n" + e._canonical(index)
    (directory / "prompt.txt").write_text(prompt)
    schema = e._load(ROOT / f"{stage}.schema.json")
    model = e._create_model(e.DEFAULT_MODEL, key, GeminiSchema.from_schema_dict(schema))
    window, = e.plan_windows(document)
    attempt = e._record_window(model, prompt, directory, window, key, temperature=0)
    stats = {"sample": sample, "stage": stage, "attempt": attempt}
    if attempt["response_file"]:
        raw = e._load(directory / attempt["response_file"])
        stats["usage"] = raw.get("usage_metadata")
        try:
            payload = decode(raw, stage)
            e._save(directory / "output.json", payload)
        except (ValueError, KeyError, ValidationError) as error:
            stats["decode_error"] = type(error).__name__
            e._save(directory / "stats.json", stats)
            return stats
        run = {"id": "urn:rulespec:composed-trial:" + e._digest([sample, stage, prompt]),
               "model": e.DEFAULT_MODEL, "temperature": 0, "model_version": raw.get("model_version"),
               "prompt_sha256": e._digest(prompt), "request_sha256": e._digest(e._load(directory / attempt["request_file"]))}
        book, mapping = convert(payload, sample, stage, run)
        for name, value in (("rulebook", book), ("mapping", mapping), ("validation", e._check_graph(book["graph"]))):
            e._save(directory / f"{name}.json", value)
        stats.update(raw_rows=len(payload["extractions"]), accepted=len(book["accepted"]),
                     rejected=len(book["rejected"]), links=sum(len(c["target_ids"]) for c in book["accepted"]))
    e._save(directory / "stats.json", stats)
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run", "replay"))
    parser.add_argument("--env-file", type=Path)
    args = parser.parse_args()
    if args.mode == "prepare":
        prepare()
        return
    if args.mode == "replay":
        design = e._load(ROOT / "design.json")
        for name, digest in design["files_sha256"].items():
            assert e._digest((ROOT / name).read_bytes()) == digest, name
        assert e._digest((ATTACHED / "experiment.py").read_bytes()) == design["adapter_sha256"]
        sources = e._runtime_sources()
        assert all(e._digest(sources[n].read_bytes()) == h for n, h in design["runtime"]["sources_sha256"].items())
        count = 0
        for sample in SAMPLES:
            for stage in ("all", "meaning", "relationships"):
                directory = ROOT / "runs" / sample / stage
                payload = decode(e._load(directory / "attempt-0000.response.json"), stage)
                book = e._load(directory / "rulebook.json")
                rebuilt, mapping = convert(payload, sample, stage, book["run"])
                assert payload == e._load(directory / "output.json")
                assert rebuilt == book and mapping == e._load(directory / "mapping.json")
                count += 1
        e._save(ROOT / "replay.json", {"status": "identical", "results": count, "provider_calls": 0})
        print(f"All {count} raw responses, mappings and graphs reproduce exactly.")
        return
    if (ROOT / "design.json").exists():
        raise FileExistsError("Preserve the completed or partial experiment")
    runtime = e._freeze(ROOT, [], e._load(ROOT / "all.schema.json"))
    runtime["prompt_sha256"] = e._digest((ROOT / "all.prompt.txt").read_text())
    shutil.copyfile(ROOT / "all.prompt.txt", ROOT / "frozen/prompt.txt")
    shutil.copyfile(ATTACHED / "experiment.py", ROOT / "frozen/adapter.py")
    tracked = ["experiment.py", "experiment.cue", "meaning.prompt.txt", "relationships.prompt.txt", "all.prompt.txt",
               "all.schema.json", "meaning.schema.json", "relationships.schema.json", "review-cases.json",
               *[f"{s}.json" for s in SAMPLES], *[f"{s}-catalog.json" for s in SAMPLES]]
    for name in tracked:
        shutil.copyfile(ROOT / name, ROOT / "frozen" / name)
    e._save(ROOT / "design.json", {"created_at": e._now(), "request_budget": 12, "model": e.DEFAULT_MODEL,
        "temperature": 0, "runtime": runtime, "adapter_sha256": e._digest((ATTACHED / "experiment.py").read_bytes()),
        "files_sha256": {n: e._digest((ROOT / n).read_bytes()) for n in tracked},
        "samples": list(SAMPLES), "fresh_excerpts": ["leave", "baggage"],
        "comparison": "Fresh all-fields controls versus meaning only versus those exact meanings plus relationships",
        "limits": "Four excerpts, one response per stage. Known names/photos failures informed prompts; new leave/baggage sources did not. No population accuracy claim.",
        "sequence": "Eight independent all/meaning calls, then four relationship calls using accepted meaning records. No retries or repairs."})
    key = e._credential(args.env_file)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for stats in pool.map(lambda t: call(t, key), [(s, stage) for s in SAMPLES for stage in ("all", "meaning")]):
            print(e._canonical(stats), flush=True)
    ready = [(s, "relationships") for s in SAMPLES if (ROOT / "runs" / s / "meaning/rulebook.json").exists()]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for stats in pool.map(lambda t: call(t, key), ready):
            print(e._canonical(stats), flush=True)
    e._write_manifest(ROOT)


if __name__ == "__main__":
    main()
