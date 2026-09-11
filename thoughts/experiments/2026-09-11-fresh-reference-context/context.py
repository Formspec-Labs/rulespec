"""Experiment-only source selection; no new parsing or meaning representation."""
from copy import deepcopy

from rulespec_extrapolator.extraction import _digest


def union(ranges):
    out = []
    for start, end in sorted(ranges):
        if start >= end:
            continue
        if out and start <= out[-1][1]:
            out[-1] = (out[-1][0], max(end, out[-1][1]))
        else:
            out.append((start, end))
    return out


def uncovered(start, end, covered):
    out = []
    for left, right in union(covered):
        if right <= start:
            continue
        if left >= end:
            break
        if left > start:
            out.append((start, left))
        start = max(start, right)
    if start < end:
        out.append((start, end))
    return out


def select_context(document, window, scan, *, budget=12000):
    """Apply the preregistered one-hop policy to native source coordinates.

    Source tables are already prepared. For R eligible references, S sections and
    K selected intervals this small comparison is O(R*S + R*K*log(K)); no source
    rescanning, fetching or recursive reference traversal takes place. Optimize
    only if a measured consumer needs it; this is not a corpus-wide resolver.
    """
    selected = deepcopy(window)
    text = document['text']
    focus = (window['start'], window['end'])
    covered = union([focus] + [(s['start'], s['end']) for s in window['context_spans']])
    baseline = sum(end - start for start, end in covered)
    additions, decisions = [], []

    def add(start, end, **reason):
        if not 0 <= start < end <= len(text) or not text[start:end].strip():
            decisions.append({**reason, 'status': 'empty_or_invalid_target'})
            return
        ranges = uncovered(start, end, covered)
        size = sum(hi - lo for lo, hi in ranges)
        used = sum(hi - lo for lo, hi in covered) - baseline
        status = 'already_supplied' if not size else ('over_budget' if used + size > budget else 'added')
        decisions.append({**reason, 'start': start, 'end': end, 'new_chars': size, 'status': status})
        if status == 'added':
            additions.extend(ranges)
            covered[:] = union(covered + ranges)

    rows = []
    for row in scan['candidates']:
        if row['kind'] != 'publisher_reference':
            continue
        evidence = row.get('evidence', [])
        if not evidence:
            decisions.append({'occurrence_id': row['id'], 'status': 'no_text_location'})
            continue
        lo, hi = min(e['start'] for e in evidence), max(e['end'] for e in evidence)
        if focus[0] <= lo < hi <= focus[1]:
            rows.append((lo, row))
    for _, row in sorted(rows, key=lambda pair: pair[0]):
        reason = {'occurrence_id': row['id'], 'value': row['value'], 'role': 'referenced_target'}
        if row['reading']['context'] != 'operative':
            decisions.append({**reason, 'status': 'nonoperative_reference'})
            continue
        resolution = row['resolution']
        ids = resolution.get('target_ids', [])
        if resolution['status'] != 'located' or len(ids) != 1:
            decisions.append({**reason, 'status': resolution['status'], 'target_ids': ids})
            continue
        target = scan['targets'][ids[0]]
        reason['target_id'] = ids[0]
        if 'start' not in target or 'end' not in target:
            decisions.append({**reason, 'status': 'target_text_unavailable'})
            continue
        start, end = target['start'], target['end']
        sections = [s for s in document['sections'] if s['start'] <= start and s['end'] >= end]
        if len(sections) == 1 and sections[0]['end'] - sections[0]['start'] <= 6000:
            start, end = sections[0]['start'], sections[0]['end']
            reason['expanded_section'] = sections[0]['label']
        add(start, end, **reason)
    for section in document['sections']:
        if section['start'] < focus[1] and section['end'] > focus[0]:
            if section['end'] - section['start'] <= 12000:
                add(section['start'], section['end'], role='enclosing_section', value=section['label'])
            else:
                decisions.append({'role': 'enclosing_section', 'value': section['label'], 'status': 'section_over_limit'})
    for start, end in union(additions):
        selected['context_spans'].append({'start': start, 'end': end, 'text_sha256': _digest(text[start:end]),
                                         'truncated': False, 'selection': 'fresh-reference-context/1'})
    selected['context_version'] = 'experiment:fresh-reference-context/1'
    return selected, {'added_chars': sum(end-start for start, end in union(additions)),
                      'added_ranges': union(additions), 'decisions': decisions}


def controls():
    """Constructed independent expected positions, including refusal boundaries."""
    assert union([(0, 2), (1, 4), (4, 5), (8, 9)]) == [(0, 5), (8, 9)]
    assert uncovered(1, 10, [(0, 2), (4, 7), (9, 20)]) == [(2, 4), (7, 9)]
    doc = {'text': 'x'*100, 'sections': []}
    window = {'start': 0, 'end': 10, 'context_spans': [{'start': 10, 'end': 12}]}
    def row(name, target, context='operative', status='located'):
        return {'id': name, 'kind': 'publisher_reference', 'value': target, 'reading': {'context': context},
                'evidence': [{'start': 2, 'end': 4}], 'resolution': {'status': status, 'target_ids': [target]}}
    targets = {'a': {'start': 8, 'end': 18}, 'b': {'start': 16, 'end': 24}, 'empty': {'start': 30, 'end': 30}}
    scan = {'candidates': [row('one','a'),row('two','a'),row('three','b')], 'targets': targets}
    got, receipt = select_context(doc, window, scan, budget=12)
    assert receipt['added_ranges'] == [(12, 24)] and receipt['added_chars'] == 12
    assert got['context_spans'][0] == window['context_spans'][0]
    assert select_context(doc, window, scan, budget=11)[1]['added_ranges'] == [(12, 18)]
    assert select_context(doc, window, scan, budget=0)[1]['added_ranges'] == []
    negatives = [row('note','a','note'), row('credit','a','sourceCredit'),
                 row('absent','a',status='not_in_selected_source'),row('ambiguous','a',status='ambiguous'),row('empty','empty')]
    assert select_context(doc, window, {**scan,'candidates':negatives})[1]['added_ranges'] == []
    remote = row('remote-cycle','b'); remote['evidence'] = [{'start': 13,'end':15}]
    assert select_context(doc, window, {**scan,'candidates':[row('one','a'),remote]})[1]['added_ranges'] == [(12,18)]
    partial = row('cross-focus','a'); partial['evidence'] = [{'start':9,'end':11}]
    assert select_context(doc, window, {**scan,'candidates':[partial]})[1]['added_ranges'] == []
    large = {'text':'x'*14000,'sections':[{'label':'s','start':20,'end':6020}]}
    small_target = {'candidates':[row('one','a')],'targets':{'a':{'start':30,'end':40}}}
    assert select_context(large,window,small_target)[1]['added_ranges'] == [(20,6020)]
    large['sections'][0]['end'] = 6021
    assert select_context(large,window,small_target)[1]['added_ranges'] == [(30,40)]
    large['sections'] = [{'label':'focus','start':0,'end':12000}]
    empty_scan = {'candidates':[],'targets':{}}
    assert select_context(large,window,empty_scan)[1]['added_ranges'] == [(12,12000)]
    large['sections'][0]['end'] = 12001
    assert select_context(large,window,empty_scan)[1]['added_ranges'] == []
    return {'status':'passed', 'scope':'constructed interval, budget, one-hop, source-context and uncertainty controls'}
