"""Check explicitly labeled distinctions and scope edges, not general accuracy."""
import argparse
import json
from pathlib import Path

import poc


def evaluate(result, case):
    claims = result["accepted"]
    checks = []
    matched = {}
    for name, expected in case["statements"].items():
        hits = [c for c in claims if expected["anchor"] in c["quote"] and
                c["kind"] not in ("condition", "exception")]
        ok = len(hits) == 1 and hits[0]["kind"] == expected["kind"]
        checks.append({"check": name + ":kind", "pass": ok,
                       "expected": expected["kind"], "observed": [c["kind"] for c in hits]})
        if len(hits) == 1:
            matched[name] = hits[0]["id"]
    for names in case["distinct"]:
        ids = [matched.get(name) for name in names]
        checks.append({"check": "distinct:" + ",".join(names),
                       "pass": None not in ids and len(set(ids)) == len(ids)})
    for expected in case["qualifications"]:
        hits = [c for c in claims if expected["anchor"] in c["quote"] and
                c["kind"] in ("condition", "exception")]
        relation_ok = len(hits) == 1 and hits[0].get("relation") == expected["relation"]
        checks.append({"check": expected["anchor"] + ":relation", "pass": relation_ok,
                       "expected": expected["relation"], "observed": [c.get("relation", "unspecified-v1") for c in hits]})
        ids = set(hits[0].get("target_ids", [hits[0]["target_id"]] if hits[0].get("target_id") else [])) if len(hits) == 1 else set()
        targets = {matched.get(name) for name in expected["targets"]}
        checks.append({"check": expected["anchor"] + ":complete-target-set",
                       "pass": None not in targets and ids == targets,
                       "expected_targets": expected["targets"], "observed_target_count": len(ids)})
    return {"passed": sum(c["pass"] for c in checks), "total": len(checks), "checks": checks,
            "meaning": "Agreement with these labeled distinctions only; not general semantic accuracy"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--case", choices=("constitution", "shared_scope", "scope_counterexample"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    case = poc.load(poc.HERE / "semantic_expectations.json")[args.case]
    if (args.run / "source.txt").read_text() != (poc.HERE / case["source"]).read_text():
        raise ValueError("Evaluation source does not match labeled source")
    result = evaluate(poc.load(args.run / "rulebook.json"), case)
    result["case_sha256"] = poc.digest(json.dumps(case, sort_keys=True))
    result["source_sha256"] = poc.digest((args.run / "source.txt").read_bytes())
    result["rulebook_sha256"] = poc.digest((args.run / "rulebook.json").read_bytes())
    poc.save(args.output, result)
    print(f'{result["passed"]}/{result["total"]} labeled checks passed')
    for check in result["checks"]:
        if not check["pass"]:
            print("FAIL", check["check"])
    raise SystemExit(0 if result["passed"] == result["total"] else 1)


if __name__ == "__main__":
    main()
