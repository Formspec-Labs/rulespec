"""Assess fixed source labels without rerunning or editing the source captures."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path

import rulespec_extrapolator.documents as documents
from candidate import baseline_paths,source_passages

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output',required=True)
args = parser.parse_args()
cases = json.loads((HERE/'cases.json').read_text())
labels = {x['id']:x['targets'] for x in json.loads((HERE/'labels.json').read_text())}
baseline = {x['id']:x['passages'] for x in json.loads((HERE/'baseline.json').read_text())}
original_reader = documents.source_passages
result = {'cases':[], 'method':'manual source labels; deterministic structural guesses, no model calls'}
for case in cases:
    document = case['document']
    text = document['text']
    before = baseline_paths(baseline[case['id']],text)
    after = source_passages(document)
    def assess(passages):
        counts,rows = Counter(),[]
        by_start = {p['start']+len(text[p['start']:p['end']])-len(text[p['start']:p['end']].lstrip()):p
                    for p in passages if text[p['start']:p['end']].strip()}
        addresses = defaultdict(list)
        for p in passages:
            if p['path']:
                addresses[(p['section_id'],tuple(p['path']))].append(p['id'])
        for target in labels[case['id']]:
            found = by_start.get(target['start'])
            actual = found['path'] if found else None
            expected = target['path']
            status = ('false_unique' if actual else 'abstained') if expected is None else (
                'correct' if actual == expected else 'wrong' if actual else 'missing')
            counts[status] += 1
            rows.append({**target,'actual_path':actual,'status':status,
                         'passage_id':found['id'] if found else None})
        duplicates = [{'section_id':k[0],'path':list(k[1]),'passage_ids':v}
                      for k,v in addresses.items() if len(v)>1]
        return {'counts':dict(counts),'targets':rows,'duplicate_addresses':duplicates}
    old_spans = {(p['start'],p['end']):p for p in before}
    new_spans = {(p['start'],p['end']):p for p in after}
    shared = old_spans.keys() & new_spans.keys()
    assert all(old_spans[k]['id'] == new_spans[k]['id'] for k in shared)
    assert ''.join(text[p['start']:p['end']] for p in after) == text
    assert all(a['end'] == b['start'] for a,b in zip(after,after[1:]))
    contexts = []
    try:
        for target in labels[case['id']]:
            window = {'start':target['start'],'end':min(target['start']+120,len(text))}
            documents.source_passages = original_reader
            old_context = documents.with_context(document,window)
            documents.source_passages = source_passages
            new_context = documents.with_context(document,window)
            if old_context != new_context:
                contexts.append({'window':window,'before':old_context,'after':new_context})
    finally:
        documents.source_passages = original_reader
    result['cases'].append({'id':case['id'],'origin':case['origin'],
        'before':assess(before),'after':assess(after), 'candidate_passages':after,
        'unchanged_ids':len(shared),'removed_boundaries':len(old_spans.keys()-new_spans.keys()),
        'added_boundaries':len(new_spans.keys()-old_spans.keys()),
        'changed_parents':sum(old_spans[k]['parent_id'] != new_spans[k]['parent_id'] for k in shared),
        'context_changes':contexts})
result['totals'] = {}
for arm in ('before','after'):
    totals = Counter()
    for case in result['cases']:
        totals.update(case[arm]['counts'])
    result['totals'][arm] = dict(totals)
result['inputs'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in
    [HERE/'cases.json',HERE/'labels.json',HERE/'baseline.json',HERE/'candidate.py']}
with Path(args.output).open('x') as stream:
    json.dump(result,stream,ensure_ascii=False,indent=2)
    stream.write('\n')
print(json.dumps(result['totals']))
for case in result['cases']:
    print(case['id'],case['before']['counts'],'->',case['after']['counts'],
          'context changes',len(case['context_changes']))
