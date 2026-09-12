"""Assess saved verdicts; preserve the initial decoder's bracket mismatch."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from rulespec_extrapolator import extraction as e

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-09-12-extractor-confidence'
for name, expected in e._load(HERE / 'precall-pins.json').items():
    assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name
key = e._load(HERE / 'key.json')
labels = e._load(BASE / 'blind-labels.json')


def read_line(line):
    # Post-capture display normalization only: preserve optional BALANCED ID
    # brackets copied from narrative inputs. Original strict decoding is retained.
    match = re.fullmatch(r'(?:\[(R\d{3,})\]|(R\d{3,})) (true|false)(?: — (.+))?', line.strip())
    if not match:
        raise ValueError('Uninterpretable verdict line')
    bracketed, bare, verdict, reason = match.groups()
    return bracketed or bare, verdict == 'true', reason


assert read_line('R004 false — omitted condition (F053)') == read_line('[R004] false — omitted condition (F053)')
assert read_line('R000 true') == read_line('[R000] true')
for bad in ('[R000 true', 'R000] true', 'R000 maybe', 'R000 true trailing'):
    try:
        read_line(bad)
    except ValueError:
        continue
    raise AssertionError('Malformed line accepted')

rows, calls = [], []
for cell in e._load(HERE / 'cells.json'):
    identity = cell['id']
    meta = key[identity]
    decoded = e._load(HERE / f'decoded/{identity}.json')
    expected = {r['item_id'] for r in cell['packet']['items']}
    observed = set()
    catalog = e.passage_catalog(e._load(BASE / cell['source']), cell['window'])
    for line in decoded['text'].splitlines():
        if not line.strip():
            continue
        item, verdict, reason = read_line(line)
        assert item in expected and item not in observed
        observed.add(item)
        refs = re.findall(r'\b[FC]\d{3,}\b', reason or '')
        assert verdict or (reason and refs)
        assert all(ref in catalog for ref in refs)
        index = int(item[1:])
        rows.append({'cell': identity, **meta, 'item_id': item, 'row_index': index,
            'label': labels[meta['previous_cell']][index]['label'], 'faithful': verdict, 'reason': reason})
    assert observed == expected
    calls.append({'cell': identity, **meta, 'records': len(observed),
        'initial_decoder_issues': len(decoded['issues']),
        'tokens': e.recorded_usage(HERE / 'captures' / identity)['tokens'],
        'seconds': e._load(HERE / f'captures/{identity}/timing.json')['seconds']})
assert len(rows) == 162


def metrics(values):
    return {'records': len(values), 'labels': dict(Counter(r['label'] for r in values)),
        'clear_defects_detected': sum(r['label'] == 'flawed' and not r['faithful'] for r in values),
        'clear_defects_approved': sum(r['label'] == 'flawed' and r['faithful'] for r in values),
        'false_alarms_on_faithful': sum(r['label'] == 'faithful' and not r['faithful'] for r in values),
        'uncertain_flagged': sum(r['label'] == 'uncertain' and not r['faithful'] for r in values)}


report = {'arms': {}, 'calls': calls, 'rows': rows,
    'format_note': 'Original A decoder accepted 81 bare IDs; original B decoder refused bracketed IDs copied from narrative input. This post-capture reader permits balanced brackets. No response or original issue record changed.',
    'display_reader_checks': {'equivalent_positive_pairs': 2, 'malformed_negatives': 4},
    'semantic_decision': 'Neither arm detects any of the eight clearly flawed records; no production adoption.'}
for arm in ('A', 'B'):
    data = [r for r in rows if r['arm'] == arm]
    selected = [c for c in calls if c['arm'] == arm]
    report['arms'][arm] = {**metrics(data), 'cohorts': {
        cohort: metrics([r for r in data if r['cohort'] == cohort]) for cohort in ('inline', 'ordinary')},
        'tokens': {k: sum(c['tokens'].get(k, 0) for c in selected) for k in
                   ('prompt_token_count', 'candidates_token_count', 'total_token_count')},
        'seconds': sum(c['seconds'] for c in selected)}
report['narrative_input_reduction'] = 1 - report['arms']['B']['tokens']['prompt_token_count'] / report['arms']['A']['tokens']['prompt_token_count']
report['narrative_total_reduction'] = 1 - report['arms']['B']['tokens']['total_token_count'] / report['arms']['A']['tokens']['total_token_count']
report['broader_gate_passed'] = False  # Both arms detect zero clear defects.
with (HERE / 'assessment.json').open('x') as f:
    json.dump(report, f, ensure_ascii=False, indent=2, allow_nan=False)
    f.write('\n')
print(json.dumps({k: v for k, v in report.items() if k not in ('calls', 'rows')}, indent=2))
