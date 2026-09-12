"""Summarize pre-reveal manual labels; no provider or model judging calls."""
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import mean
from rulespec_extrapolator import extraction as e

HERE = Path(__file__).resolve().parent
load = lambda name: e._load(HERE / name)
for name, expected in load('blind-review-pin.json').items():
    assert sha256((HERE / name).read_bytes()).hexdigest() == expected
labels = load('blind-labels.json')
key = load('review-key.json')
scored, cells = [], []
for name, arm in key.items():
    decoded = load(f'decoded/{name}.json')
    rows = decoded['canonical_response']['extractions']
    assert len(rows) == len(decoded['book']['accepted']) == len(labels[name])
    # Verify row identity through parsing and Core without fuzzy matching.
    for row, candidate, accepted in zip(rows, decoded['parsed']['candidates'],
                                        decoded['book']['accepted'], strict=True):
        assert row['unit_attributes']['statement'] == candidate['summary'] == accepted['summary']
    for item in decoded['confidence']:
        index = item['row_index']
        scored.append({'cell': name, 'row_index': index, 'label': labels[name][index]['label'],
                       'score': item['confidence']['rkaf:score']})
    usage = e.recorded_usage(HERE / 'captures' / name)
    cells.append({'cell': name, 'arm': arm, 'records': len(rows),
        'labels': dict(Counter(r['label'] for r in labels[name])),
        'tokens': usage['tokens'], 'seconds': load(f'captures/{name}/timing.json')['seconds']})


def budget(rows):
    limit = math.ceil(len(rows) * 0.2)
    threshold = sorted(r['score'] for r in rows)[limit - 1]
    below = [r for r in rows if r['score'] < threshold]
    tied = [r for r in rows if r['score'] == threshold]
    detected = sum(r['label'] == 'flawed' for r in below)
    detected += (limit - len(below)) * sum(r['label'] == 'flawed' for r in tied) / len(tied)
    defects = sum(r['label'] == 'flawed' for r in rows)
    random_expected = limit * defects / len(rows)
    return {'records': len(rows), 'budget': limit, 'boundary_score': threshold,
        'boundary_tied_records': len(tied), 'known_flaws_detected_tie_expected': detected,
        'known_flaw_recall': detected / defects, 'random_expected_known_flaws': random_expected,
        'lift_vs_random': detected / random_expected}


faithful = [r['score'] for r in scored if r['label'] == 'faithful']
flawed = [r['score'] for r in scored if r['label'] == 'flawed']
auc = mean(1 if bad < good else 0.5 if bad == good else 0 for bad in flawed for good in faithful)
primary_budget = budget(scored)
assert len(scored) == 31 and len(flawed) == 4 and len(faithful) == 24
assert auc == 0.4375
summary = {'cells': cells, 'scored': scored, 'ranking_auc_uncertain_excluded': auc,
    'budget_all_scored_including_uncertain': primary_budget,
    'budget_uncertain_excluded_sensitivity': budget([r for r in scored if r['label'] != 'uncertain']),
    'distributions': {label: {'n': len(values), 'min': min(values), 'max': max(values),
        'mean': mean(values), 'counts': dict(Counter(values))}
        for label, values in [('faithful', faithful), ('flawed', flawed)]},
    'known_flaws_scoring_at_least_090': sum(v >= 0.90 for v in flawed),
    'arms': {}, 'decision': 'No adoption; ranking and review-budget gates fail; CSBG content regression.',
    'limits': 'Selected development sources; one draw per arm; manual revisable labels; no general calibration claim.'}
for arm in ('A', 'B'):
    values = [c for c in cells if c['arm'] == arm]
    token_names = set().union(*(c['tokens'] for c in values))
    summary['arms'][arm] = {'records': sum(c['records'] for c in values),
        'tokens': {k: sum(c['tokens'].get(k, 0) for c in values) for k in token_names},
        'seconds': sum(c['seconds'] for c in values)}
with (HERE / 'assessment.json').open('x') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2, allow_nan=False)
    f.write('\n')
print(json.dumps({k: v for k, v in summary.items() if k not in ('scored', 'cells')}, indent=2))
