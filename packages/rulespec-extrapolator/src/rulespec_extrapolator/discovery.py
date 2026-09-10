"""Source-backed discovery export; evidence overlap is not semantic completeness."""
from copy import deepcopy
from .core import _evidence, sparse
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
    from .terms import term_lookup
    doc = validate_document(book["document"])
    passages = {p['id']: p for p in source_passages(doc)}
    terms = term_lookup(book)
    evidence = {}

    def references(items):
        grouped = {}
        for item in verified(book, items):
            support = item if item.get('fragment_id') else _evidence(doc, item['quote'], item['field'], item['start'], item['end'])
            identity = support['fragment_id']
            evidence[identity] = {**{k: support[k] for k in ('start', 'end')},
                                  'record_ids': [key for key, p in passages.items() if overlaps(support, p)]}
            roles = grouped.setdefault(identity, [])
            if item['field'] not in roles:
                roles.append(item['field'])
        return [{'id': identity, 'roles': roles} for identity, roles in grouped.items()]

    terms = deepcopy(terms)
    for term in terms.values():
        term['evidence_refs'] = references(term.pop('evidence', []))
    rows = records(book, doc["id"], "packets")
    windows = book.get("run", {}).get("windows", [])
    for row in rows:
        row['evidence_refs'] = references(row.pop('evidence'))
        passage = passages[row["id"]]
        assigned = [w for w in windows if overlaps(passage, w)]
        row.update(start=passage["start"], end=passage["end"],
                   parent_id=passage['parent_id'], kind=passage['kind'], structure_method=passage['structure_method'],
                   window_ids=[w["id"] for w in assigned],
                   processing=("not_recorded" if not assigned else
                               "processed" if all(w["status"] in {"complete", "no_candidates"} for w in assigned)
                               else "needs_attention"))
    statements = []
    for c in book['accepted']:
        statement = {"id": c['id'], 'rule_id': c['rule_id'], 'statement': c['summary'],
            **{k: c.get(k) for k in ('kind', 'actor', 'modality', 'scope_text', 'choice_text', 'logic_text', 'references', 'review_event_id')},
            'defines': [key for key, t in terms.items() if t.get('claim_id') == c['id'] and t['status'] == 'available'],
            'term_refs': c.get('term_refs', []), 'qualification_targets': c.get('target_ids', []),
            'evidence_refs': references(c['evidence']),
            'issues': c.get('issues', []) + c.get('link_issues', []), 'review_status': c.get('review_status', 'pending')}
        for key in ('choice_text', 'logic_text'):
            if statement[key] == statement['statement']:
                statement.pop(key)
        statements.append(sparse(statement))
    return {"schema_version": 'rulespec-discovery/2',
            "document": {k: doc[k] for k in ("id", "title", "source_url", "sha256")},
            "records": rows, "terms": terms,
            'evidence': evidence, 'statements': statements,
            "accounting": {"passage_count": len(rows),
                "processed_passages": sum(r["processing"] == "processed" for r in rows),
                "passages_without_linked_statements": sum(not r["claim_ids"] for r in rows),
                "rejected_statements": len(book.get("rejected", [])),
                "semantic_completeness": "not_established"},
            "extraction_issues": book.get("extraction_refusals", []),
            'enrichment_issues': book.get('enrichment_issues', []),
            "limitation": "Evidence links locate related source passages. A linked passage may still contain omitted or misinterpreted meaning; an unlinked passage is not necessarily an omission."}
