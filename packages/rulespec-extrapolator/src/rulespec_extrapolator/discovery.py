"""Source-backed discovery export; evidence overlap is not semantic completeness."""
from copy import deepcopy
from .core import NS, _evidence, sparse
from .documents import source_passages, source_slicer, validate_document


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
    source_slices = source_slicer(doc)
    rows = []
    for passage in source_passages(doc):
        text = doc["text"][passage["start"]:passage["end"]]
        evidence = []
        for start, end in source_slices(passage['start'], passage['end']):
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



def export_discovery(book, *, include_references=False, act_index=None, source_credit_index=None, reference_sources=()):
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
    reference_sources = tuple(reference_sources)
    if include_references or act_index is not None or source_credit_index is not None or reference_sources:
        from .references import scan_references
        scan = scan_references(doc, act_index=act_index, source_credit_index=source_credit_index,
                               reference_sources=reference_sources)
        scan.pop('document')  # The export already pins this exact document.
        from .uslm import xml_source
        source_documents = {NS + 'xml:' + xml_source(d)['sha256']: d for d in reference_sources}
        for candidate in scan['candidates'] + scan['rejected'] + list(scan.get('targets', {}).values()):
            for reading in [candidate] + candidate.get('text_readings', []):
                if 'evidence' in reading:
                    items = reading.pop('evidence')
                    if 'source_id' not in reading:
                        reading['evidence_refs'] = references(items)
                        continue
                    # External coordinates belong to their own source/evidence table.
                    source_id = reading['source_id']
                    source = scan['reference_sources'][source_id]
                    supports = verified({'document': source_documents[source_id]}, items)
                    if len(supports) != len(items):
                        raise ValueError('External target evidence does not resolve in its source')
                    table = source.setdefault('evidence', {})
                    reading['evidence_refs'] = []
                    for support in supports:
                        identity = support['fragment_id']
                        table[identity] = {k: support[k] for k in ('start', 'end')}
                        table[identity]['record_ids'] = [reading['record_id']]
                        reading['evidence_refs'].append({'id': identity, 'roles': [support['field']]})
        result['reference_scan'] = scan
    return result
