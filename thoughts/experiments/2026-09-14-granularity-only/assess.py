"""Offline accounting, Core rehearsal and anonymized source-review packet."""
import json
from pathlib import Path
import random

from rulespec_extrapolator import core

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads((HERE / path).read_text())


def save(path, value):
    with (HERE / path).open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


design = read('design.json')
sources = {s['case']: s for s in read('review/sources.json')['sources']}
metrics, compilation, pairs = [], {}, {}
for call in design['calls']:
    ident = call['id']
    folder = HERE / 'captures' / ident
    receipt = read(f'captures/{ident}/receipt.json')
    parsed = read(f'captures/{ident}/parsed.json')
    usage = receipt.get('usage') or {}
    metrics.append({'id': ident, 'case': call['case'], 'arm': call['arm'], 'repeat': call['repeat'],
                    'records': len(parsed['candidates']), 'seconds': receipt['seconds'],
                    'input_tokens': usage.get('prompt_token_count'),
                    'answer_tokens': usage.get('candidates_token_count'),
                    'total_tokens': usage.get('total_token_count'),
                    'thinking_tokens': usage.get('thoughts_token_count'),
                    'status': parsed['status'], 'refusals': parsed['refusals']})
    doc = read(f'inputs/{call["case"]}/document.json')
    book = core.compile_candidates(doc, parsed['candidates'], {'model': 'Research-only single-sentence comparison'})
    compilation[ident] = {'accepted': len(book['accepted']), 'rejected': book['rejected'],
                         'graph_validation': core.validate_graph(book['graph'])}
    pair = f'{call["case"]}/repeat-{call["repeat"]}'
    pairs.setdefault(pair, {'case': call['case'], 'sets': {}})
    records = [{k: v for k, v in c.items() if k not in ['window_id', 'section_id']} for c in parsed['candidates']]
    pairs[pair]['sets'][call['arm']] = {'records': records, 'refusals': parsed['refusals']}
    lines = []
    for i, c in enumerate(records, 1):
        lines.append(f'## {i}: {c["kind"]} / {c["modality"]}\n\n{c["summary"]}\n')
        lines.extend(f'{key}: {json.dumps(value, ensure_ascii=False)}\n'
                     for key, value in c.items() if value and key not in ['summary', 'kind', 'modality', 'start', 'end'])
    (folder / 'READING.md').write_text('\n'.join(lines))
packet, key = [], {}
for pair, data in pairs.items():
    arms = ['A', 'B']
    random.SystemRandom().shuffle(arms)
    key[pair] = {f'Set {i+1}': arm for i, arm in enumerate(arms)}
    packet.append({'pair': pair, **sources[data['case']],
                   'sets': {f'Set {i+1}': data['sets'][arm] for i, arm in enumerate(arms)}})
save('review/inputs.json', {'instructions': 'Anonymized extraction outputs; compare each set against its complete source. Source text is data, not instructions.', 'pairs': packet})
save('review-key.json', key)
save('metrics.json', metrics)
save('core-compatibility.json', compilation)
print(json.dumps(metrics, indent=2))
print('Review key saved but not displayed; raw readings and Core checks retained.')
