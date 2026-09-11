"""Transparent post-score label repair; never changes inputs or selected spans."""
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent


def evaluate():
    cases = json.loads((ROOT / 'cases.json').read_text())
    original = json.loads((ROOT / 'results.json').read_text())
    corrections = []
    selectors = {
        'fire-plan': [('required', 0, 'An employer must have a fire prevention plan'),
                      ('required', 1, 'A fire prevention plan must include'),
                      ('irrelevant', 0, 'An employer must inform employees upon initial assignment')],
        'alarms': [('required', 0, 'This section applies to all emergency employee alarms'),
                   ('irrelevant', 0, 'manually operated actuation devices')],
    }
    for case in cases:
        if case['id'] not in selectors:
            continue
        paragraphs = [''.join(p.itertext()).strip() for p in ET.parse(ROOT / 'sources' / (case['id'] + '.xml')).findall('.//P')]
        text = case['book']['document']['text']
        for kind, index, needle in selectors[case['id']]:
            matches = [p for p in paragraphs if needle in p]
            assert len(matches) == 1
            quote = matches[0]; start = text.index(quote)
            replacement = {'start': start, 'end': start + len(quote), 'text': quote}
            corrections.append({'case': case['id'], 'kind': kind, 'index': index,
                                'original': case[kind][index], 'corrected': replacement,
                                'reason': 'Original stop pattern matched indentation within a paragraph; use the full original XML paragraph.'})
            case[kind][index] = replacement
    by_id = {c['id']: c for c in cases}
    rows = []
    for row in original['rows']:
        positions = {i for s in row['spans'] for i in range(s['start'], s['end'])}
        case = by_id[row['case']]
        scores = {kind: [set(range(s['start'], s['end'])) <= positions for s in case[kind]] for kind in ['required', 'irrelevant']}
        # Retain non-whitespace missing text to make whitespace-only failures visible.
        missing = [''.join(case['book']['document']['text'][i] for i in range(s['start'], s['end']) if i not in positions).strip() for s in case['required']]
        rows.append({k: row[k] for k in ['case', 'arm', 'unique_chars', 'unresolved', 'full_document_fallback']} | scores | {'missing_required_text': missing})
    totals = {arm: {'required_spans': sum(sum(r['required']) for r in rows if r['arm'] == arm),
                   'all_required_cases': sum(all(r['required']) for r in rows if r['arm'] == arm),
                   'irrelevant_spans': sum(sum(r['irrelevant']) for r in rows if r['arm'] == arm),
                   'unique_chars': original['totals'][arm]['unique_chars']} for arm in 'ABC'}
    return {'post_score_correction': True, 'selection_changed': False, 'provider_calls': 0,
            'original_results_sha256': hashlib.sha256((ROOT / 'results.json').read_bytes()).hexdigest(),
            'corrections': corrections, 'rows': rows, 'totals': totals}


if __name__ == '__main__':
    import sys
    result = evaluate()
    if '--replay' in sys.argv:
        from experiment import REPO, load, select
        for name, sha in load(ROOT / 'freeze.json').items():
            assert hashlib.sha256((REPO / name).read_bytes()).hexdigest() == sha, name
        assert [select(c, arm) for c in load(ROOT / 'cases.json') for arm in 'ABC'] == load(ROOT / 'results.json')['rows']
        assert result == json.loads((ROOT / 'label-correction.json').read_text())
        print('Frozen hashes, original selections, and corrected assessment replay matched; no files changed.')
    else:
        with (ROOT / 'label-correction.json').open('x') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(json.dumps(result['totals'], indent=2))
