"""Provider-free retrieval diagnostic; not a production search service.

Rank summaries or source paragraphs with the same fixed BM25 settings. Evidence
packets keep source ranking unchanged and add verified scope/context quotations.
Scores measure recovery of source support, never semantic correctness of a rule.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re

from rulespec_extrapolator.documents import source_passages
from rulespec_extrapolator.enrichment import supported_components


STOP = set("a an the of to in on for and or is are be been it its this that does do can may must should what when why how who with as from at by if".split())


def tokens(text):
    return [word for word in re.findall(r"[a-z0-9]+", text.casefold()) if word not in STOP]


def overlaps(a, b):
    return a["start"] < b["end"] and b["start"] < a["end"]


def verified(book, evidence):
    """Read exact evidence only; never serialize raw meaning or its suggestions."""
    text = book["document"]["text"]
    return [e for e in evidence if text[e["start"]:e["end"]] == e["quote"]]


def records(book, source, mode):
    doc = book["document"]
    claims = book["accepted"]
    if mode == "summaries":
        return [{"id": c["id"], "source": source, "text": c["summary"],
                 "evidence": verified(book, [e for e in c["evidence"] if e["field"] == "summary"]),
                 "claim_ids": [c["id"]]} for c in claims]
    rows = []
    for passage in source_passages(doc):
        text = doc["text"][passage["start"]:passage["end"]]
        evidence = [{"field": "source", "start": passage["start"], "end": passage["end"], "quote": text}]
        linked = []
        if mode == "packets":
            for claim in claims:
                context = verified(book, [e for e in claim["evidence"]
                                          if e["field"].startswith(("scope_text:", "context:"))])
                if overlaps(passage, claim) or any(overlaps(passage, e) for e in context):
                    linked.append(claim["id"])
                    evidence.extend(verified(book, [e for e in claim["evidence"]
                                                    if e["field"] == "summary" or e in context]))
        unique = {(e["start"], e["end"], e["field"]): e for e in evidence}
        rows.append({"id": passage["id"], "source": source, "text": text,
                     "evidence": list(unique.values()), "claim_ids": linked})
    return rows


def search(rows, query, limit=3):
    bags = [Counter(tokens(row["text"])) for row in rows]
    avg = sum(sum(bag.values()) for bag in bags) / max(1, len(bags))
    frequencies = Counter(word for bag in bags for word in bag)
    scored = []
    for row, bag in zip(rows, bags):
        score = 0.0
        for word in set(tokens(query)):
            count = bag[word]
            if count:
                idf = math.log(1 + (len(rows) - frequencies[word] + 0.5) / (frequencies[word] + 0.5))
                score += idf * count * 2.2 / (count + 1.2 * (0.25 + 0.75 * sum(bag.values()) / avg))
        if score:
            scored.append({**row, "score": round(score, 6)})
    return sorted(scored, key=lambda row: (-row["score"], row["source"], row["id"]))[:limit]


def support_found(hits, source, quote):
    return any(hit["source"] == source and any(quote in e["quote"] for e in hit["evidence"]) for hit in hits)


def run(books, questions):
    result = {}
    for mode in ("summaries", "source", "packets"):
        rows = [row for source, book in books.items() for row in records(book, source, mode)]
        checks = []
        for question in questions:
            hits = search(rows, question["query"])
            found = [support_found(hits, question["source"], q) for q in question["required_quotes"]]
            checks.append({**question, "required_support_found": found,
                           "all_source_support_at_3": all(found) if found else None,
                           "returned_evidence_chars": sum(sum(len(e["quote"]) for e in h["evidence"]) for h in hits),
                           "hits": hits})
        answerable = [c for c in checks if c["required_quotes"]]
        result[mode] = {"supported_at_3": sum(c["all_source_support_at_3"] for c in answerable),
                        "answerable_questions": len(answerable), "questions": checks}
    # Re-check components, including historical books that predate these checks.
    # This gate is separate from retrieval: suggestions never enter the index.
    result["admission"] = {
        source: {field: {"candidates": sum(len(c[field]) for c in book["accepted"]),
                        "admitted": sum(len(list(supported_components(c, field))) for c in book["accepted"])}
                 for field in ("claimants", "typed_values")}
        for source, book in books.items()}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--names", type=Path, required=True, help="Rulebook JSON")
    parser.add_argument("--photos", type=Path, required=True, help="Rulebook JSON")
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inputs = {key: getattr(args, key) for key in ("names", "photos", "questions")}
    books = {key: json.loads(path.read_text()) for key, path in inputs.items() if key != "questions"}
    questions = json.loads(args.questions.read_text())["questions"]
    for q in questions:
        for quote in q["required_quotes"]:
            if quote not in books[q["source"]]["document"]["text"]:
                raise ValueError(f"Expected support absent from source: {q['id']}")
    result = {"provider_calls": 0, "metric": "Exact expected source support retrieved at rank <= 3; not answer or extraction accuracy",
              "inputs": {key: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()} for key, path in inputs.items()},
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              **run(books, questions)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({mode: result[mode]["supported_at_3"] for mode in ("summaries", "source", "packets")}))


if __name__ == "__main__":
    main()
