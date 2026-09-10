"""Freeze extracted claims; compare existing discovery views without model calls."""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import subprocess

from rulespec_extrapolator import discovery, documents, core

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CAPTURES = REPO / 'examples/document_understanding/consistency-transfer/cells'
CASES = [
    ('passport', 'cell-01', '930b0aaa5e194ff7776dc0f6bfcef69841870403d30e71caf80d82d826984daf'),
    ('seatbelts', 'cell-00', 'd1fe2614c6635c052be429d75e5618a7f5f23f0800167385ac00e595564acf98'),
    ('recording-experimental', 'cell-05', '4ef71c8b7984751d29547656c1dc90c21cafde5fffe05cc309a3c1c20cef33b7'),
    ('first-aid-uncertainty', 'cell-04', 'bada4dbde97d35922ad47848e71b66edf88fe9e527b0339080951da7e24dd7e2'),
    ('separate-exemptions-constructed', 'cell-03', 'd6c9f2692903d4fc89b93e0bef563e05b0b60c68473cf438a5474b71ca51fbfb'),
    ('and-duty-constructed', 'cell-03', '71bc2f7cee0a2d3545bc07ce3e72e1265e87d6d4fd28b184078be83ce7bfc2fe'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate():
    results = []
    inputs = {HERE / 'PLAN.md', Path(__file__)}
    for name, cell, suffix in CASES:
        path = CAPTURES / cell / 'rulebook.json'
        inputs.update([path, CAPTURES / cell / 'raw-model-text.txt'])
        book = json.loads(path.read_text())
        claim, = [c for c in book['accepted'] if c['id'].endswith(suffix)]
        summary, = [r for r in discovery.records(book, book['document']['id'], 'summaries')
                    if r['id'] == claim['id']]
        packets = [r for r in discovery.records(book, book['document']['id'], 'packets')
                   if claim['id'] in r['claim_ids']]
        alternatives = {'A': [], 'B': summary['evidence'],
                        'C': [e for r in packets for e in r['evidence']]}
        arms = {}
        for arm, evidence in alternatives.items():
            spans = {}
            for e in evidence:
                assert book['document']['text'][e['start']:e['end']] == e['quote']
                item = spans.setdefault((e['start'], e['end']),
                                        {'start': e['start'], 'end': e['end'],
                                         'quote': e['quote'], 'roles': []})
                if e['field'] not in item['roles']:
                    item['roles'].append(e['field'])
            selected = [spans[key] for key in sorted(spans)]
            shown = '\n\n'.join([claim['summary'], *[s['quote'] for s in selected]])
            arms[arm] = {'statement': claim['summary'], 'spans': selected,
                         'characters': len(shown), 'text': shown}
        results.append({'case': name, 'capture': cell, 'claim_id': claim['id'],
                        'packet_ids': [r['id'] for r in packets], 'arms': arms})
    modules = [discovery, documents, core]
    return {'provider_calls': 0, 'new_provider_cost': 0,
            'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
            'inputs': {str(p.relative_to(REPO)): sha(p) for p in sorted(inputs)},
            'runtime': {str(Path(inspect.getfile(m)).relative_to(REPO)): sha(Path(inspect.getfile(m)))
                        for m in modules},
            'cases': results}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = evaluate()
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    lines = ['# Displayed retrieval material', '', 'A: statement. B: main evidence. C: existing packets.', '']
    for case in result['cases']:
        lines += [f"## {case['case']}", '', f"Capture: {case['capture']}; claim: {case['claim_id']}", '']
        for name, arm in case['arms'].items():
            lines += [f"### {name} ({arm['characters']} characters)", '', arm['text'], '']
    (args.output / 'display.md').write_text('\n'.join(lines))
    print(json.dumps({c['case']: {a: v['characters'] for a, v in c['arms'].items()}
                      for c in result['cases']}, indent=2))
