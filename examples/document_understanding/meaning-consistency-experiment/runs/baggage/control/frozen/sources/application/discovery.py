"""Source-backed discovery export; evidence overlap is not semantic completeness."""
from .documents import source_passages, validate_document


def overlaps(a, b):
    return a["start"] < b["end"] and b["start"] < a["end"]


def verified(book, evidence):
    """Read exact evidence only; never serialize raw meaning or its suggestions."""
    text = book["document"]["text"]
    return [e for e in evidence if text[e["start"]:e["end"]] == e["quote"]]


def records(book, source, mode):
    if mode not in {"summaries", "source", "packets"}:
        raise ValueError("Unknown discovery record mode")
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



def export_discovery(book):
    """Keep every source passage, including passages with no extracted statement."""
    doc = validate_document(book["document"])
    rows = records(book, doc["id"], "packets")
    windows = book.get("run", {}).get("windows", [])
    passages = {p["id"]: p for p in source_passages(doc)}
    for row in rows:
        passage = passages[row["id"]]
        assigned = [w for w in windows if overlaps(passage, w)]
        row.update(start=passage["start"], end=passage["end"],
                   window_ids=[w["id"] for w in assigned],
                   processing=("not_recorded" if not assigned else
                               "processed" if all(w["status"] in {"complete", "no_candidates"} for w in assigned)
                               else "needs_attention"))
    return {"document": {k: doc[k] for k in ("id", "title", "source_url", "sha256")},
            "records": rows,
            "statements": [{"id": c["id"], "statement": c["summary"], "kind": c["kind"],
                "modality": c["modality"], "scope_text": c["scope_text"], "choice_text": c["choice_text"],
                "references": c["references"], "issues": c.get("issues", []) + c.get("link_issues", []),
                "review_status": c.get("review_status", "pending")} for c in book["accepted"]],
            "accounting": {"passage_count": len(rows),
                "processed_passages": sum(r["processing"] == "processed" for r in rows),
                "passages_without_linked_statements": sum(not r["claim_ids"] for r in rows),
                "rejected_statements": len(book.get("rejected", [])),
                "semantic_completeness": "not_established"},
            "extraction_issues": book.get("extraction_refusals", []),
            "limitation": "Evidence links locate related source passages. A linked passage may still contain omitted or misinterpreted meaning; an unlinked passage is not necessarily an omission."}
