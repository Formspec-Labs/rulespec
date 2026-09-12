"""Compare separate-pass scores using unchanged pre-existing manual labels."""
from collections import Counter
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
from statistics import mean
from rulespec_extrapolator import extraction as e

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-09-12-extractor-confidence'
for name, expected in e._load(HERE / 'precall-pins.json').items():
    assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name
labels = e._load(BASE / 'blind-labels.json')
key = e._load(HERE / 'key.json')
prior = e._load(BASE / 'assessment.json')


def metrics(rows):
    good = [r['score'] for r in rows if r['label'] == 'faithful']
    bad = [r['score'] for r in rows if r['label'] == 'flawed']
    auc = mean(1 if b < g else 0.5 if b == g else 0 for b in bad for g in good) if bad and good else None
    budget = math.ceil(len(rows) * 0.2)
    threshold = sorted(r['score'] for r in rows)[budget - 1]
    below = [r for r in rows if r['score'] < threshold]
    tied = [r for r in rows if r['score'] == threshold]
    found = sum(r['label'] == 'flawed' for r in below)
    found += (budget - len(below)) * sum(r['label'] == 'flawed' for r in tied) / len(tied)
    expected = budget * len(bad) / len(rows)
    return {'n': len(rows), 'labels': dict(Counter(r['label'] for r in rows)), 'ranking_auc': auc,
        'review_budget': budget, 'boundary_score': threshold, 'boundary_ties': len(tied),
        'expected_flaws_found': found, 'random_expected_flaws': expected,
        'review_lift': found / expected if expected else None,
        'known_flaws_at_least_090': sum(v >= 0.90 for v in bad),
        'faithful_below_090': sum(v < 0.90 for v in good),
        'uncertain_below_090': sum(r['score'] < 0.90 for r in rows if r['label'] == 'uncertain'),
        'score_distribution': dict(Counter(r['score'] for r in rows))}


rows, calls = [], []
for cell, info in key.items():
    decoded = e._load(HERE / f'decoded/{cell}.json')
    assert not decoded['response_errors'] and not decoded['issues']
    assert decoded['observed'] == decoded['expected']
    previous = info['previous_cell']
    for record in decoded['records']:
        index = int(record['item_id'][1:])
        rows.append({'cell': cell, 'previous_cell': previous, 'cohort': info['cohort'], 'row_index': index,
            'label': labels[previous][index]['label'], 'score': record['confidence']['rkaf:score']})
    usage = e.recorded_usage(HERE / 'captures' / cell)
    calls.append({'cell': cell, **info, 'tokens': usage['tokens'],
                  'seconds': e._load(HERE / f'captures/{cell}/timing.json')['seconds']})
assert len(rows) == 81
report = {'historical_inline': metrics(prior['scored']), 'cohorts': {}, 'per_saved_output': {},
          'scores': rows, 'calls': calls, 'label_source': '../2026-09-12-extractor-confidence/blind-labels.json'}
for cohort in ('inline', 'ordinary'):
    scored = [r for r in rows if r['cohort'] == cohort]
    result = metrics(scored)
    result['gate_passed'] = result['ranking_auc'] >= 0.70 and result['review_lift'] >= 2
    report['cohorts'][cohort] = result
    # Post-hoc sensitivity only: original uncertain labels remain unchanged.
    unsure = [r for r in scored if r['label'] == 'uncertain']
    fixed = [r for r in scored if r['label'] != 'uncertain']
    sensitivity = [metrics(fixed + [dict(r, label=l) for r, l in zip(unsure, outcomes)])['ranking_auc']
        for outcomes in itertools.product(('faithful', 'flawed'), repeat=len(unsure))]
    result['posthoc_uncertain_label_auc_range'] = [min(sensitivity), max(sensitivity)]
for name in labels:
    report['per_saved_output'][name] = metrics([r for r in rows if r['previous_cell'] == name])
report['broader_gate_passed'] = all(r['gate_passed'] for r in report['cohorts'].values())
report['decision'] = 'Primary cohort improves; ordinary cohort fails; no production adoption.'
with (HERE / 'assessment.json').open('x') as f:
    json.dump(report, f, ensure_ascii=False, indent=2, allow_nan=False)
    f.write('\n')
print(json.dumps({k: v for k, v in report.items() if k not in ('scores', 'calls')}, indent=2))
