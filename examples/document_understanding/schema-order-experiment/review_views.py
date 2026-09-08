"""Read-only compact views of captured output for source adjudication."""
from pathlib import Path
import argparse
import json
import re

ROOT = Path(__file__).resolve().parent / "trial-01"


def view(sample, variant, repeat, pattern=None):
    directory = ROOT / "runs" / sample / variant / f"{repeat:02d}"
    payload = json.loads((directory / "output.json").read_text())
    mapping = json.loads((directory / "mapping.json").read_text())
    book = json.loads((directory / "rulebook.json").read_text())
    claims = {c["id"]: c for c in book["accepted"]}
    aliases = {v: k for k, v in mapping["unit_ids"].items()}
    print(f"\n{sample}/{variant}/{repeat:02d}")
    for index, row in enumerate(payload["extractions"]):
        local = row.get("id", f"row{index}")
        if pattern and not re.search(pattern, json.dumps(row, ensure_ascii=False), re.I):
            continue
        a = row["unit_attributes"]
        claim = claims.get(mapping["unit_ids"].get(local))
        print(f"{local} {'KEPT' if claim else 'REFUSED'} {a['kind']}/{a['modality']} " + a['summary'])
        for key in ("scope_text", "choice_text", "logic_text"):
            if a.get(key): print(f"  {key}: {a[key]}")
        if a.get("alternative_quotes"): print("  alternatives: " + " | ".join(a["alternative_quotes"]))
        if a.get("references"): print("  references: " + " | ".join(a["references"]))
        if a.get("relation") != "none":
            print("  relation: " + a["relation"] + " targets: " + str([aliases.get(t, t) for t in claim["target_ids"]] if claim else "refused"))
        if claim and claim["issues"]:
            print("  evidence issues: " + str([(i["code"], i["field"]) for i in claim["issues"]]))
        for issue in mapping["issues"]:
            if issue.get("unit_id") == local: print("  refusal: " + issue["code"])
    if pattern is None:
        for r in payload.get("relationships", []):
            print("  EDGE " + r["source_unit_ref"] + " -> " + str(r["target_unit_refs"]) + " " + r["explanation"])
        print("  Mapping errors: " + str([i for i in mapping["issues"] if i["code"] in {"invalid_qualification_reference", "reference_to_refused_unit"}]))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("sample")
    p.add_argument("--variant", action="append", default=[])
    p.add_argument("--repeat", action="append", type=int, default=[])
    p.add_argument("--pattern")
    args = p.parse_args()
    for variant in args.variant or ["current", "rich", "definitions_first", "references_first"]:
        for repeat in args.repeat or [1, 2]:
            if (ROOT / "runs" / args.sample / variant / f"{repeat:02d}" / "mapping.json").is_file():
                view(args.sample, variant, repeat, args.pattern)
