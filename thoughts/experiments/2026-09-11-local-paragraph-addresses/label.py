"""Freeze manually reviewed hierarchy labels before running the candidate."""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
cases = json.loads((HERE / 'cases.json').read_text())
# Source order, reviewed against complete selected paragraphs. Empty paths mean
# the supplied text does not establish an unambiguous absolute address.
paths = {
    'venting': ['a', 'a/1'] + [f'a/1/{v}' for v in ('i','ii','iii','iv','v','vi','vii','viii','ix','x')]
        + ['a/2', 'a/2/i', 'a/2/ii', 'a/3', 'b', 'b/1', 'b/2'],
    'label-scope': ['a', 'a/1', 'a/2', 'a/3', 'a/3/i', 'a/3/ii', 'a/3/iii',
        'a/3/iii/A', 'a/3/iii/B', 'a/3/iii/B/1', 'a/3/iii/B/2',
        'a/3/iii/B/2/i', 'a/3/iii/B/2/ii', 'a/3/iii/B/3',
        'a/3/iii/B/3/ii', 'a/3/iii/B/3/iii', 'a/3/iii/B/3/iv',
        'a/3/iii/B/4', 'a/3/iii/C', 'a/3/iii/C/1', 'a/3/iii/C/2', 'a/3/iii/C/3', 'b'],
    'ecfr-21-1.276': ['a', 'b', 'b/1', 'b/2', 'b/3', 'b/4', 'b/4/ii',
        'b/5', 'b/5/i', 'b/5/i/A', 'b/5/i/B', 'b/5/ii']
        + [f'b/{n}' for n in range(6,17)],
    'ecfr-49-1.25a': ['a', 'a/1/i', 'a/1/ii'] + [f'a/{n}' for n in range(2,9)]
        + ['b', 'b/1/i', 'b/1/ii'] + [f'b/{n}' for n in range(2,7)]
        + ['b/6/i','b/6/ii'] + [f'b/6/ii/{v}' for v in 'ABCDE']
        + [f'b/6/{v}' for v in ('iii','iv','v','vi','vii','viii')]
        + ['b/7','b/8','b/9'],
    'dotted-passport': ['a', 'a/1','a/1/a','a/1/b','b'],
    'combined': ['b','b/4','c/1','c/1/i','c/1/ii','c/2','d'],
    'top-i': ['h','h/1','i','i/1'],
    'duplicate': ['a','a/1','a','a/1'],
    'missing-parent': [None,None],
    'roman-ambiguity': ['g','g/1',None],
    'spaced-path': ['a','a/3','a/3/iii','a/3/iii/B',None],
    'explicit-path': ['a/3/iii/B/4'],
    'section-reset': ['a','a/1','a','a/1'],
    'overlapping-sections': ['a','a/1','a','a/1'],
    'boundary-without-whitespace': [],
}
labels = []
for case in cases:
    text = case['document']['text']
    starts = []
    for m in re.finditer(r'(?m)^[ \t]*(?:\([ \t]*[A-Za-z0-9]+[ \t]*\)|[a-z]\.)', text):
        starts.append(m.start() + len(m[0]) - len(m[0].lstrip()))
    assert len(starts) == len(paths[case['id']]), (case['id'],len(starts),len(paths[case['id']]))
    labels.append({'id': case['id'], 'targets': [
        {'start': start, 'prefix': text[start:start+90],
         'path': path.split('/') if path else None}
        for start,path in zip(starts, paths[case['id']])]})
# An inline subparagraph is a real address even though it shares the parent's P.
case = next(x for x in cases if x['id'] == 'ecfr-21-1.276')
text = case['document']['text']
next(x for x in labels if x['id'] == case['id'])['targets'].append({
    'start': text.index('(i) For an article'), 'prefix': '(i) For an article',
    'path': ['b','4','i'], 'note': 'Inline child after the parent definition lead-in; inspected in XML.'})
with (HERE / 'labels.json').open('x') as stream:
    json.dump(labels, stream, indent=2, ensure_ascii=False)
    stream.write('\n')
print('Frozen', sum(len(x['targets']) for x in labels), 'source-address labels across',len(labels),'cases')
