"""Four-call, isolated comparison. Core conversion reuses the current extractor."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import re
import shutil

from jsonschema import Draft202012Validator, ValidationError
from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import core, extraction as e

ROOT = Path(__file__).resolve().parent
VARIANTS = ("current", "indexed")


def instructions():
    text = e.PROMPT.replace("summary", "statement").replace("summaries", "statements")
    text = text.replace("section labels in references", "section labels in the citation index and refer to their IDs in citation_refs")
    text = text.replace("JSON object with an extractions list; [] means no supported units were found.",
                        "JSON object with roles, citations, concepts, and statements in that order. Empty lists retain uncertainty.")
    return text + "\nUse the schema's shared indexes and lexical-signal guidance. Index only supplied text; IDs do not establish identity or correctness. Write direct source-faithful statements, with no reporting preamble.\n"


def decode(raw, schema):
    answers = raw.get("candidates") or []
    if len(answers) != 1 or answers[0].get("finish_reason") != "STOP":
        raise ValueError("Provider response did not finish as one complete answer")
    text = "".join(p.get("text", "") for p in answers[0]["content"]["parts"] if not p.get("thought"))
    payload = json.loads(text, object_pairs_hook=e._pairs_without_duplicates)
    Draft202012Validator(schema).validate(payload)
    return payload


def normalize(payload, document, window):
    """Resolve local IDs; keep indexes/mapping separate from existing Core fields."""
    indices, issues = {}, []
    for field in ("roles", "citations", "concepts"):
        index = {}
        for row in payload[field]:
            if not row["id"] or row["id"] in index:
                raise ValueError(f"Empty or duplicate {field} ID")
            index[row["id"]] = row
            quote = row["topic"]["quote"] if field == "concepts" else row["quote"]
            if not quote or quote not in document["text"]:
                issues.append({"index": field, "id": row["id"], "code": "index_evidence_unresolved"})
            if field == "roles":
                if row["title"] and row["title"] not in quote:
                    issues.append({"index": field, "id": row["id"], "code": "unsupported_role_title"})
                if row["scope_quote"] and row["scope_quote"] not in document["text"]:
                    issues.append({"index": field, "id": row["id"], "code": "role_scope_quote_absent"})
        indices[field] = index
    normalized, mapping, refused = [], [], []
    for i, row in enumerate(payload["statements"]):
        attrs = deepcopy(row["unit_attributes"])
        role_id = attrs.pop("role_ref")
        concept_ids, citation_ids = attrs.pop("concept_refs"), attrs.pop("citation_refs")
        unknown = ([role_id] if role_id and role_id not in indices["roles"] else [])
        unknown += [k for k in concept_ids if k not in indices["concepts"]]
        unknown += [k for k in citation_ids if k not in indices["citations"]]
        if unknown:
            refused.append({"row_index": i, "code": "missing_index_reference", "ids": unknown})
            continue
        if role_id:
            role = indices["roles"][role_id]
            labels = {s.casefold() for s in [role["label"], *role["aliases"]]}
            if attrs["actor"].casefold() not in labels:
                issues.append({"row_index": i, "code": "actor_role_disagreement"})
        attrs["summary"] = attrs.pop("statement")
        attrs["concepts"] = [deepcopy(indices["concepts"][k]["topic"]) for k in concept_ids]
        attrs["references"] = [indices["citations"][k]["label"] for k in citation_ids]
        normalized.append({"unit": row["unit"], "unit_attributes": attrs})
        mapping.append({"row_index": i, "role_ref": role_id, "concept_refs": concept_ids, "citation_refs": citation_ids})
    parsed = e.parse_response_text(json.dumps({"extractions": normalized}), document, window)
    parsed["refusals"] += refused
    occurrences = [{"id": c["id"], "label": c["label"], "spans": [
        {"start": m.start(), "end": m.end()} for m in re.finditer(re.escape(c["label"]), document["text"])]}
        for c in payload["citations"] if c["label"]]
    return parsed, {"issues": issues, "units": mapping, "citation_occurrences": occurrences}


def call(sample, variant, key):
    directory = ROOT / "runs" / f"{sample}-{variant}"
    directory.mkdir(parents=True, exist_ok=False)
    document = e._load(ROOT / f"{sample}.json")
    window, = e.plan_windows(document)
    schema = e._load(ROOT / ("provider.schema.json" if variant == "indexed" else "current.schema.json"))
    prompt = e._window_prompt(e._prompt_generator(e.invented_examples(), instructions() if variant == "indexed" else None), document, window)
    (directory / "prompt.txt").write_text(prompt)
    model = e._create_model(e.DEFAULT_MODEL, key, GeminiSchema.from_schema_dict(schema))
    attempt = e._record_window(model, prompt, directory, window, key, temperature=0)
    stats = {"sample": sample, "variant": variant, "attempt": attempt, "temperature": 0,
             "schema_sha256": e._digest(schema), "prompt_sha256": e._digest(prompt)}
    if attempt["response_file"]:
        raw = e._load(directory / attempt["response_file"])
        stats["usage"] = raw.get("usage_metadata")
        try:
            payload = decode(raw, schema)
            e._save_provider_json(directory / "output.json", payload, key)
            if variant == "indexed":
                parsed, mapping = normalize(payload, document, window)
            else:
                parsed, mapping = e.parse_raw_response(raw, document, window), {}
            run = {"id": "urn:rulespec:indexed-trial:" + e._digest([sample, variant, prompt]),
                   "model": e.DEFAULT_MODEL, "temperature": 0, "model_version": raw.get("model_version"),
                   "prompt_sha256": e._digest(prompt)}
            book = core.compile_candidates(document, parsed["candidates"], run)
            for name, value in (("candidates", parsed["candidates"]), ("refusals", parsed["refusals"]),
                                ("mapping", mapping), ("rulebook", book), ("validation", e._check_graph(book["graph"]))):
                e._save(directory / f"{name}.json", value)
            stats.update(schema_valid=True, accepted=len(book["accepted"]), refused=len(parsed["refusals"]),
                         rejected=len(book["rejected"]), explicit_links=sum(len(c["target_ids"]) for c in book["accepted"]),
                         issues=dict(Counter(i["code"] for c in book["accepted"] for i in c["issues"])),
                         output_order=list(payload))
        except (ValueError, KeyError, TypeError, ValidationError) as error:
            stats.update(processing_error=type(error).__name__)
    e._save(directory / "stats.json", stats)
    return {"run": directory.name, **{k: stats.get(k) for k in ("accepted", "refused", "explicit_links", "processing_error")}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--env-file", type=Path, required=True)
    args = ap.parse_args()
    key = e._credential(args.env_file)
    if (ROOT / "design.json").exists():
        raise FileExistsError("This experiment is already initialized; preserve the original captures")
    old = ROOT.parent / "extraction-polish"
    for sample, original in (("names", "final-names-2"), ("photos", "final-photos-1")):
        shutil.copyfile(old / original / "document.json", ROOT / f"{sample}.json")
    schema = e.provider_schema().to_provider_config()["response_json_schema"]
    e._save(ROOT / "current.schema.json", schema)
    fingerprints = e._freeze(ROOT, e.invented_examples(), schema)
    shutil.copyfile(Path(__file__), ROOT / "frozen/experiment.py")
    shutil.copyfile(ROOT / "experiment.cue", ROOT / "frozen/experiment.cue")
    e._save(ROOT / "design.json", {"created_at": e._now(), "model": e.DEFAULT_MODEL,
        "temperature": 0, "request_budget": 4, "retries": 0, "samples": ["names", "photos"],
        "variants": list(VARIANTS), "runtime": fingerprints, "schema_sha256": e._digest(e._load(ROOT / "provider.schema.json")),
        "runner_sha256": e._digest(Path(__file__).read_bytes()), "checks": [
            "no invented actor titles in statements or roles", "citation labels complete, IDs resolve, external content not invented",
            "topics distinct from actors and references", "direct readable statements without reporting preambles",
            "previous-name exception retains meaning and an explicit correct target",
            "emergency and recent-change conditions retained", "all six name-document alternatives retained",
            "generally-needed explanation and certificate timing caution retained", "photo should stays should"],
        "limits": "One repeat per variant/document; bundled interventions cannot isolate individual effects; familiar development sources, no general accuracy claim."})
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(lambda pair: call(*pair, key), [("names", "current"), ("photos", "indexed"), ("photos", "current"), ("names", "indexed")]):
            print(json.dumps(result), flush=True)
    e._write_manifest(ROOT)


if __name__ == "__main__":
    main()
