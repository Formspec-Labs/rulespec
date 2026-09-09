"""Replay checker captures and compare their findings and usage with saved controls."""
from pathlib import Path
import json

from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent


def replay(cell, design):
    """Verify comparison-only captures; the extraction manifest has other requirements."""
    run = ROOT / 'runs' / cell
    old = ROOT.parent / 'low-extract-high-audit/runs' / cell
    manifest = e._load(run / 'manifest.json')
    assert manifest['version'] == 1
    artifacts = manifest['artifacts_sha256']
    required = {'configuration.json', 'attempts.json', 'judgments.json', 'report.json'}
    required.update('frozen/' + name for name in design['runtime_sources_sha256'])
    assert required <= artifacts.keys()
    for name, digest in artifacts.items():
        assert e._digest(e._contained(run, name).read_bytes()) == digest, name
    for name, digest in design['runtime_sources_sha256'].items():
        assert artifacts['frozen/' + name] == digest, name
    saved = a.load_audit(old)
    book, labels, windows = saved['book'], saved['labels'], saved['run']['windows']
    assert e._load(run / 'configuration.json') == {
        'prompt': a.comparison_prompt(), 'schema': a.COMPARISON_SCHEMA,
        'source_audit': str(old),
        'source_manifest_sha256': e._digest((old / 'manifest.json').read_bytes()),
    }
    attempts = e._load(run / 'attempts.json')
    assert len(attempts) == len(windows)
    generator = e._prompt_generator([], a.comparison_prompt())
    for attempt, window in zip(attempts, windows):
        assert attempt['window_id'] == window['id']
        record = 'comparison/' + attempt['id'] + '.json'
        assert record in artifacts and attempt == e._load(e._contained(run, record))
        for field in ('request_file', 'response_file'):
            assert 'comparison/' + attempt[field] in artifacts
        prompt = e._window_prompt(generator, book['document'], window)
        prompt += '\nDraft and inventory: ' + e._canonical(
            a._model_input(a._comparison_input(book, labels, window)[0]))
        request = e._load(run / 'comparison' / attempt['request_file'])
        control = e._load(old / 'comparison' / attempt['request_file'])
        assert request == {**control, 'contents': prompt}
    judgments, issues = a._judgments(run / 'comparison', book, labels, windows, attempts, e.DEFAULT_MODEL)
    assert judgments == e._load(run / 'judgments.json')
    assert a._assessment(book, labels, judgments, issues) == e._load(run / 'report.json')


def main():
    design = e._load(ROOT / 'design.json')
    for name, digest in design['inputs_sha256'].items():
        assert e._digest(e._contained(ROOT.parent, name).read_bytes()) == digest, name
    assert {name: e._digest(path.read_bytes()) for name, path in e._runtime_sources().items()} == design['runtime_sources_sha256']
    results = []
    for cell in design['runs']:
        replay(cell, design)
        comparisons = {}
        for label, root in (('control', ROOT.parent / 'low-extract-high-audit'), ('treatment', ROOT)):
            run = root / 'runs' / cell
            response = e._load(run / 'comparison/attempt-0000.response.json')
            report = e._load(run / 'report.json')
            try:
                raw = json.loads(''.join(part.get('text', '') for part in response['candidates'][0]['content']['parts']
                                         if not part.get('thought')))
            except ValueError:
                raw = {}
            comparisons[label] = {
                'usage': response['usage_metadata'], 'finish_reason': response['candidates'][0]['finish_reason'],
                'assessment': report['status'], 'review_complete': report['review_complete'],
                'audit_issues': report['audit_issues'], 'issues': report['issues'],
                'coverage': {key: report['coverage'][key] for key in ('covered', 'partial', 'missing', 'unknown')},
                'flagged_claims': [row for row in raw.get('claim_judgments', [])
                                   if any(value in ('error', 'unknown') for value in row['dimensions'].values())],
                'uncovered_units': [row for row in raw.get('unit_judgments', []) if row['status'] != 'covered'],
            }
        results.append({'cell': cell, 'replay_identical': True, **comparisons})
    e._save(ROOT / 'verification.json', {'new_provider_calls': len(results), 'replay_provider_calls': 0,
                                        'results': results})
    print(e._canonical({'replayed': len(results), 'new_comparison_tokens': sum(
        row['treatment']['usage']['total_token_count'] for row in results)}))


if __name__ == '__main__':
    main()
