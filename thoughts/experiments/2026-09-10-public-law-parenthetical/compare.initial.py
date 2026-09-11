"""Replay existing harness functions without overwriting previous observations."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
mode = sys.argv[1]
assert mode in ('control', 'source', 'wheel')
if mode == 'source':
    sys.path.insert(0, '/Users/mikewolfd/Work/spicysearch/src')

from spicysearch import cfr_citations, identifiers
from refspec.registry import citation_grammar

out = root / mode
out.mkdir()
metadata = {'mode': mode, 'python': sys.executable, 'modules': {}, 'provider_calls': 0}
for module in (identifiers, cfr_citations, citation_grammar):
    path = Path(module.__file__).resolve()
    metadata['modules'][module.__name__] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
print(json.dumps(metadata), flush=True)
summary = {}
for name in ('additive-reference-families', 'reference-real-positives', 'broader-parser-comparison'):
    previous = root.parent / f'2026-09-10-{name}'
    script = previous / 'run.py'
    source = script.read_text()
    namespace = {'__file__': str(script), '__name__': 'reused_harness'}
    marker = '\nmetadata = ' if name == 'broader-parser-comparison' else '\ncases=json.loads'
    exec(compile(source.split(marker)[0], str(script), 'exec'), namespace)
    labels = json.loads((previous / 'cases.json').read_text())
    if name == 'broader-parser-comparison':
        cases = labels['cases']
        def run(case):
            return {'case': case, 'arms': {key: namespace['capture'](functions, case['raw']) for key, functions in namespace['arms'].items()}}
    else:
        cases = labels
        run = namespace['run_case']
    rows = [run(case) for case in cases]
    replay = [run(case) for case in cases]
    assert rows == replay
    historical = json.loads((previous / 'raw.json').read_text())
    assert [r['case'] for r in rows] == [r['case'] for r in historical]
    differences = [a['case']['id'] for a, b in zip(rows, historical, strict=True) if a != b]
    expected_differences = ['2025-24202-block-28'] if mode != 'control' and name == 'reference-real-positives' else []
    result = {'cases': len(cases), 'changed_vs_historical': differences, 'expected_changed_cases': expected_differences,
              'only_expected_changes': differences == expected_differences, 'replay_equal': rows == replay,
              'input_sha256': hashlib.sha256((previous / 'cases.json').read_bytes()).hexdigest(),
              'harness_sha256': hashlib.sha256(script.read_bytes()).hexdigest()}
    if name != 'broader-parser-comparison':
        assessments = [namespace['assess'](row) for row in rows]
        (out / f'{name}-assessment.json').write_text(json.dumps(assessments, indent=2))
        result.update(expected=sum(a['expected_additions'] for a in assessments),
                      correct=sum(a['correct_additions'] for a in assessments),
                      missed=sum(c['count'] for a in assessments for c in a['missed']),
                      unexpected=sum(c['count'] for a in assessments for c in a['unexpected']),
                      baseline_changes=sum(not a['baseline_equal'] for a in assessments))
    (out / f'{name}-raw.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    summary[name] = result

(out / 'run.json').write_text(json.dumps(metadata, indent=2))
(out / 'summary.json').write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
assert all(s['only_expected_changes'] for s in summary.values())
for name, s in summary.items():
    if 'expected' in s:
        assert s['unexpected'] == 0 and s['baseline_changes'] == 0
        assert s['missed'] == (1 if mode == 'control' and name == 'reference-real-positives' else 0)
if mode == 'wheel':
    for path in out.glob('*-raw.json'):
        assert json.loads(path.read_text()) == json.loads((root / 'source' / path.name).read_text())
    print('Installed wheel outputs equal direct source outputs.')
