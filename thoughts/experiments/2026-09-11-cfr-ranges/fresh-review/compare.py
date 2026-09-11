"""Run one source-frozen CFR comparison; refuse to overwrite observations."""
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
LIVE = Path('/Users/mikewolfd/Work/RefSpec/src/refspec/registry/citation_grammar.py')
BASELINE = HERE.parent.parent / '2026-09-11-cfr-whole-tokens/baseline.py'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def assess(case, rows):
    focus_rows = [r for r in rows if r['start'] < case['focus_end'] and r['end'] > case['focus_start']]
    grounded = all(case['text'][r['start']:r['end']] == r['text'] for r in rows)
    if len(focus_rows) != 1:
        return {'verdict': 'fail', 'reason': 'expected_one_complete_occurrence', 'focus_rows': len(focus_rows), 'grounded': grounded}
    row = focus_rows[0]
    covers = row['start'] <= case['focus_start'] and row['end'] >= case['focus_end']
    refused = bool(row.get('refusal') or row.get('qualifier_status'))
    expected, citation = case['expected'], row['citation']
    mode = expected['mode']
    if refused and covers:
        verdict = 'pass_refusal' if mode in {'single_or_explicit_refusal', 'explicit_refusal'} else 'unresolved'
        reason = 'full_source_retained_with_refusal'
    elif mode == 'range':
        start, end = citation.get('start', {}), citation.get('end', {})
        correct = start.get('cfr_title') == end.get('cfr_title') == expected['title'] and [start.get('cfr_part'), start.get('cfr_section')] == expected['start'] and [end.get('cfr_part'), end.get('cfr_section')] == expected['end']
        verdict, reason = ('pass', 'both_written_endpoints') if covers and correct and not refused else ('fail', 'range_incomplete_or_changed')
    elif mode == 'explicit_refusal':
        verdict, reason = 'fail', 'uncertain_historical_address_accepted'
    else:
        correct = citation.get('cfr_title') == expected['title'] and citation.get('cfr_part') == expected['part'] and citation.get('cfr_section') == expected['section']
        verdict, reason = ('pass', 'complete_single_reference') if covers and correct and not refused else ('fail', 'single_reference_split_or_truncated')
    return {'verdict': verdict, 'reason': reason, 'covers_focus': covers, 'grounded': grounded}


def main():
    frozen = HERE / 'source-cases.json'
    source_hash = sha(frozen.read_bytes())
    assert source_hash == '4bf0ced4eac341852515fb9e3fd2454053a9b50bcfd96797044083131970f98f'
    live_raw = LIVE.read_bytes()
    snapshot = HERE / 'grammar-snapshot.py'
    with snapshot.open('xb') as stream:
        stream.write(live_raw)
    current = load('fresh_cfr_current', snapshot)
    baseline = load('fresh_cfr_baseline', BASELINE)
    assert hasattr(current, 'CfrCitationRange')
    print(json.dumps({'current_module': current.__file__, 'baseline_module': baseline.__file__}))
    cases = json.loads(frozen.read_text())['cases']
    observations = []
    for case in cases:
        row = {'id': case['id'], 'expected': case['expected'], 'label_certainty': case['label_certainty']}
        for name, module in [('baseline', baseline), ('current', current)]:
            rows = [asdict(value) for value in module.find_cfr_citations(case['text'])]
            row[name] = rows
            row[name + '_assessment'] = assess(case, rows)
        observations.append(row)
    result = {
        'schema': 'independent-cfr-range-observations/1',
        'source_cases_sha256': source_hash, 'current_source_path': str(LIVE),
        'current_snapshot_path': str(snapshot), 'current_sha256': sha(live_raw),
        'baseline_path': str(BASELINE), 'baseline_sha256': sha(BASELINE.read_bytes()),
        'live_file_unchanged_across_run': sha(LIVE.read_bytes()) == sha(live_raw),
        'model_calls': 0, 'network_calls': 0, 'observations': observations,
    }
    with (HERE / 'observations.json').open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps([{ 'id': row['id'], 'baseline': row['baseline_assessment'], 'current': row['current_assessment']} for row in observations], indent=2))


if __name__ == '__main__':
    main()
