"""Experimental request adapter over delivered source/reference APIs."""
from copy import deepcopy

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.core import NS, evidence_parts
from rulespec_extrapolator.discovery import export_discovery, verified
from rulespec_extrapolator.documents import validate_document, with_context
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator.uslm import xml_source


def union(ranges):
    out = []
    for lo, hi in sorted(ranges):
        if lo >= hi:
            continue
        if out and lo <= out[-1][1]:
            out[-1] = (out[-1][0], max(hi, out[-1][1]))
        else:
            out.append((lo, hi))
    return out


def source_key(doc):
    return NS + 'xml:' + xml_source(doc)['sha256'] if any(k in doc for k in ('uslm_source', 'ecfr_source')) else doc['id']


def build(book, focus, *, integrated=False, reference_sources=(), scan=None, extra_chars=20000):
    """Return model material plus pinned resolver data; no model or mutation."""
    primary = validate_document(book['document'])
    source_id = source_key(primary)
    docs = {source_id: primary}
    for doc in reference_sources:
        validate_document(doc)
        identity = source_key(doc)
        if identity in docs and docs[identity] != doc:
            raise ValueError('Conflicting prepared source for one identity')
        docs[identity] = doc
    window = with_context(primary, {'start': focus['start'], 'end': focus['end']})
    selected = {source_id: [(focus['start'], focus['end'])]}
    roles = []
    decisions = []

    def size():
        return sum(hi - lo for values in selected.values() for lo, hi in union(values))

    def add(sid, lo, hi, role, *, budget=False, **reason):
        doc = docs[sid]
        if not 0 <= lo < hi <= len(doc['text']):
            raise ValueError('Invalid source context coordinates')
        old = selected.get(sid, [])
        ranges = union(old + [(lo, hi)])
        added = sum(b-a for a,b in ranges) - sum(b-a for a,b in union(old))
        status = 'already_supplied' if added == 0 else 'added'
        if budget and size() - baseline_size + added > extra_chars:
            status = 'over_budget'
        decisions.append(dict(source_id=sid, start=lo, end=hi, role=role, status=status, **reason))
        if status != 'over_budget':
            selected[sid] = ranges
            roles.append(dict(source_id=sid, start=lo, end=hi, role=role, **reason))

    for s in window['context_spans']:
        add(source_id, s['start'], s['end'], 'current_context', truncated=s['truncated'])
    for s in verified(book, focus.get('evidence', [])):
        add(source_id, s['start'], s['end'], s['field'])
    baseline_size = size()
    readings, feedback, related = [], [], []
    source_metadata = {}
    if integrated:
        scan = scan or scan_references(primary, reference_sources=reference_sources)
        if any(scan['document'][k] != primary[k] for k in ('id', 'sha256')):
            raise ValueError('Scan differs from primary source')
        enclosing = [s for s in primary['sections'] if s['start'] <= focus['start'] and focus['end'] <= s['end']]
        if enclosing:
            section = min(enclosing, key=lambda s: (s['end']-s['start'], s['id']))
            if section['end'] - section['start'] <= 12000:
                add(source_id, section['start'], section['end'], 'enclosing_section', budget=True, section_id=section['id'])
            else:
                decisions.append({'role': 'enclosing_section', 'status': 'section_over_limit', 'section_id': section['id']})
        claims = book.get('accepted', [])
        linked = [c for c in claims if c['id'] != focus.get('id') and
                  (focus.get('id') in c.get('target_ids', []) or c['id'] in focus.get('target_ids', []))]
        for claim in linked:
            related.append({k: claim.get(k) for k in ('id', 'summary', 'kind', 'modality', 'target_ids')})
            for s in verified(book, claim['evidence']):
                add(source_id, s['start'], s['end'], 'related_claim', budget=True, claim_id=claim['id'], field=s['field'])
        relevant = []
        for group in ('candidates', 'rejected'):
            for row in scan[group]:
                spans = row.get('evidence', [])
                # One-hop expansion from the original focus, not references newly encountered in context.
                if not any(focus['start'] <= x['start'] < x['end'] <= focus['end'] for x in spans):
                    continue
                relevant.append(row)
                brief = {k: row[k] for k in ('id', 'kind', 'value', 'reading', 'resolution', 'code') if k in row}
                if row.get('text_readings'):
                    brief['text_readings'] = [{k: r[k] for k in ('disposition', 'kind', 'value', 'reading', 'resolution', 'code') if k in r} for r in row['text_readings']]
                readings.append({'disposition': group, **brief})
                resolution = row.get('resolution', {})
                targets = resolution.get('target_ids', [])
                if group == 'rejected' or resolution.get('status') != 'located' or len(targets) != 1:
                    decisions.append({'role': 'reference', 'occurrence_id': row.get('id'),
                                      'status': row.get('code') or resolution.get('status', 'target_unavailable')})
                    continue
                if row.get('reading', {}).get('context') in ('note', 'sourceCredit'):
                    decisions.append({'role': 'reference', 'occurrence_id': row.get('id'), 'status': 'nonoperative_reference'})
                    continue
                target = scan['targets'][targets[0]]
                sid = target.get('source_id', source_id)
                if sid not in docs or target.get('text_status') != 'available' or 'start' not in target:
                    decisions.append({'role': 'reference', 'occurrence_id': row.get('id'), 'status': 'target_text_unavailable'})
                    continue
                lo, hi = target['start'], target['end']
                if sid != source_id:
                    source = scan['reference_sources'][sid]
                    record = source['records'][target['record_id']]
                    source_metadata[sid] = {k: source[k] for k in ('publisher_source', 'publication', 'issues') if k in source}
                    containers = [record]
                else:
                    containers = [s for s in primary['sections'] if s['start'] <= lo and hi <= s['end']]
                if containers:
                    container = min(containers, key=lambda s: s['end']-s['start'])
                    if container['end'] - container['start'] <= 6000:
                        lo, hi = container['start'], container['end']
                add(sid, lo, hi, 'reference_target', budget=True, target_id=target['id'], occurrence_id=row.get('id'),
                    edition_match=resolution.get('edition_match', 'same_supplied_source'))
        # Consume observations already retained by the public discovery view.
        # They are reports, not authority to replace scanner readings or approve claims.
        exported = export_discovery(book)
        for observation in exported['enrichment_issues']:
            if observation.get('code') != 'reference_feedback':
                continue
            ref = observation.get('reference', {})
            if any(x.get('id') and x.get('id') == ref.get('id') for x in relevant) or any(
                focus['start'] <= x['start'] < x['end'] <= focus['end'] for x in ref.get('evidence', [])):
                brief = {k: deepcopy(observation[k]) for k in ('code', 'message', 'scan_sha256', 'disposition') if k in observation}
                brief['reference'] = {k: deepcopy(ref[k]) for k in ('id', 'kind', 'value', 'reading', 'resolution', 'code') if k in ref}
                brief['reader_context'] = {k: deepcopy(observation.get('context', {})[k]) for k in ('parsers', 'indexes') if k in observation.get('context', {})}
                feedback.append(brief)
        for sid, source in scan.get('reference_sources', {}).items():
            source_metadata.setdefault(sid, {k: source[k] for k in ('publisher_source', 'publication', 'issues') if k in source})
    catalogs, sources = {}, {}
    for i, sid in enumerate([source_id] + sorted(s for s in selected if s != source_id)):
        doc = docs[sid]
        catalog = {}
        for lo, hi in union(selected[sid]):
            part = e.passage_catalog(doc, {'start': lo, 'end': hi, 'context_spans': []})
            for value in part.values():
                catalog[f'F{len(catalog):03d}'] = value
        alias = f'S{i}'
        catalogs[alias] = {'source_id': sid, 'document': doc, 'passages': catalog}
        sources[alias] = {'source_id': sid, 'document': {k: doc[k] for k in ('id', 'sha256', 'title', 'source_url')},
                          'passages': catalog, 'metadata': source_metadata.get(sid, {})}
    material = {'statement': focus.get('summary') or primary['text'][focus['start']:focus['end']],
                'sources': sources, 'source_roles': roles, 'related_claims': related,
                'reference_readings': readings, 'recorded_feedback': feedback,
                'selection_decisions': decisions, 'source_metadata': source_metadata}
    return {'material': material, 'catalogs': catalogs, 'unique_chars': size(), 'baseline_chars': baseline_size,
            'scan': scan, 'window': window}


def resolve(selection, catalogs):
    source = catalogs[selection['source']]
    span = e.resolve_passage(selection['passage'], source['passages'], source['document'])
    parts = evidence_parts(source['document'], span['quote'], 'context_check', span['start'], span['end'])
    if not parts:
        raise ValueError('Selected passage lacks original source evidence')
    return {'source_id': source['source_id'], 'document_id': source['document']['id'],
            **span, 'evidence': parts}
