"""Source-backed discovery export; evidence overlap is not semantic completeness."""
from bisect import bisect_left, bisect_right
from copy import deepcopy
from .core import _evidence, sparse
from .documents import source_passages, validate_document


def overlaps(a, b):
    return a["start"] < b["end"] and b["start"] < a["end"]


def verified(book, evidence):
    """Read exact evidence only; never serialize raw meaning or its suggestions."""
    doc = book["document"]
    return [{**e, **support} for e in evidence
            if doc['text'][e['start']:e['end']] == e['quote']
            and (support := _evidence(doc, e['quote'], e['field'], e['start'], e['end'])) is not None]


def records(book, source, mode):
    if mode not in {"summaries", "source", "packets"}:
        raise ValueError("Unknown discovery record mode")
    doc = book["document"]
    claims = book["accepted"]
    if mode == "summaries":
        return [{"id": c["id"], "source": source, "text": c["summary"],
                 "evidence": verified(book, [e for e in c["evidence"] if e["field"] == "summary"]),
                 "claim_ids": [c["id"]]} for c in claims]
    # Source-map slices bound evidence; prepared passage text and IDs stay intact.
    parts = [p for p in doc.get('source_map', [{'kind': 'source', 'start': 0, 'end': len(doc['text'])}])
             if p['kind'] == 'source']
    starts, ends = [p['start'] for p in parts], [p['end'] for p in parts]
    rows = []
    for passage in source_passages(doc):
        text = doc["text"][passage["start"]:passage["end"]]
        evidence = []
        for part in parts[bisect_right(ends, passage['start']):bisect_left(starts, passage['end'])]:
            start, end = max(part['start'], passage['start']), min(part['end'], passage['end'])
            evidence.append({'field': 'source', 'start': start, 'end': end, 'quote': doc['text'][start:end]})
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



def export_discovery(book, *, include_references=False, act_index=None, source_credit_index=None):
    """Keep every source passage, including passages with no extracted statement."""
    from .terms import term_lookup
    doc = validate_document(book["document"])
    passages = {p['id']: p for p in source_passages(doc)}
    terms = term_lookup(book)
    evidence = {}

    def references(items):
        grouped = {}
        for support in verified(book, items):
            identity = support['fragment_id']
            evidence[identity] = {**{k: support[k] for k in ('start', 'end')},
                                  'record_ids': [key for key, p in passages.items() if overlaps(support, p)]}
            roles = grouped.setdefault(identity, [])
            if support['field'] not in roles:
                roles.append(support['field'])
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
    result = {"schema_version": 'rulespec-discovery/2',
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
    if include_references or act_index is not None or source_credit_index is not None:
        from .references import scan_references
        scan = scan_references(doc, act_index=act_index, source_credit_index=source_credit_index)
        scan.pop('document')  # The export already pins this exact document.
        for candidate in scan['candidates'] + scan['rejected'] + list(scan.get('targets', {}).values()):
            for reading in [candidate] + candidate.get('text_readings', []):
                if 'evidence' in reading:
                    reading['evidence_refs'] = references(reading.pop('evidence'))
        result['reference_scan'] = scan
    return result
