"""Experimental display union over frozen evidence; original spans stay intact."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from rulespec_extrapolator.documents import validate_document

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def compact(text, spans):
    blocks = []
    for index, span in sorted(enumerate(spans), key=lambda pair: (pair[1]['start'], pair[1]['end'])):
        start, end = span['start'], span['end']
        if not 0 <= start < end <= len(text) or text[start:end] != span['quote']:
            raise ValueError('Invalid source span')
        if blocks and start < blocks[-1]['end']:
            blocks[-1]['end'] = max(end, blocks[-1]['end'])
            blocks[-1]['members'].append(index)
        else:
            blocks.append({'start': start, 'end': end, 'members': [index]})
    return [{**b, 'quote': text[b['start']:b['end']]} for b in blocks]


def positions(spans):
    return {i for span in spans for i in range(span['start'], span['end'])}


def check(text, spans):
    original = deepcopy(spans)
    blocks = compact(text, spans)
    assert spans == original
    assert positions(blocks) == positions(spans)
    assert sorted(i for block in blocks for i in block['members']) == list(range(len(spans)))
    assert all(text[b['start']:b['end']] == b['quote'] for b in blocks)
    return blocks


def counterexamples():
    cases = [
        ('nested', 'abcdef', [(0, 6), (1, 3)], [(0, 6)]),
        ('partial-overlap', 'abcdef', [(0, 4), (2, 6)], [(0, 6)]),
        ('gap', 'abXXcd', [(0, 2), (4, 6)], [(0, 2), (4, 6)]),
        ('adjacent', 'abcd', [(0, 2), (2, 4)], [(0, 2), (2, 4)]),
        ('repeated-words', 'Staff / Staff', [(0, 5), (8, 13)], [(0, 5), (8, 13)]),
        ('unicode', 'é🙂 must', [(0, 2), (1, 7)], [(0, 7)]),
    ]
    for name, text, ranges, expected in cases:
        spans = [{'start': s, 'end': e, 'quote': text[s:e], 'roles': [name]} for s, e in ranges]
        result = check(text, spans)
        assert [(b['start'], b['end']) for b in result] == expected
    for text in ('must', 'must not'):
        assert check(text, [{'start': 0, 'end': len(text), 'quote': text}])[0]['quote'] == text
    try:
        compact('must not', [{'start': 0, 'end': 8, 'quote': 'must'}])
    except ValueError:
        pass
    else:
        raise AssertionError('Invalid quote accepted')
    return [c[0] for c in cases] + ['separate-documents', 'invalid-quote-refused']


def run():
    baseline_path = HERE / 'run-02/results.json'
    baseline = json.loads(baseline_path.read_text())
    output = {'counterexamples': counterexamples(), 'provider_calls': 0, 'cases': []}
    for case in baseline['cases']:
        path = REPO / 'examples/document_understanding/consistency-transfer/cells' / case['capture'] / 'rulebook.json'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == baseline['inputs'][str(path.relative_to(REPO))]
        document = validate_document(json.loads(path.read_text())['document'])
        before = case['arms']['C']
        blocks = check(document['text'], before['spans'])
        shown = '\n\n'.join([before['statement'], *[b['quote'] for b in blocks]])
        assert len(shown) <= before['characters']
        output['cases'].append({'case': case['case'], 'claim_id': case['claim_id'],
            'statement': before['statement'], 'original_spans': before['spans'],
            'display_blocks': blocks, 'before_characters': before['characters'],
            'after_characters': len(shown), 'text': shown})
    assert any(c['after_characters'] < c['before_characters'] for c in output['cases'])
    output['inputs'] = {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (baseline_path, Path(__file__), HERE / 'COMPACTION-PLAN.md')}
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.mkdir(exist_ok=False)
    (args.output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.output / 'display.md').write_text('\n\n'.join(
        f"## {c['case']} ({c['before_characters']} → {c['after_characters']} characters)\n\n{c['text']}"
        for c in result['cases']))
    print(json.dumps({c['case']: [c['before_characters'], c['after_characters']] for c in result['cases']}))
