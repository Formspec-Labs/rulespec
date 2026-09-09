"""Replay audits, verify unchanged drafts and account for both audit stages."""
from datetime import datetime
from pathlib import Path
import sys

from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent


def main():
    output = Path(sys.argv[1])
    output.mkdir(parents=True, exist_ok=False)
    design = e._load(ROOT / 'design.json')
    low = e._load(ROOT.parent / 'low-thinking-experiment/results.json')['runs']
    results = []
    for cell, spec in design['runs'].items():
        directory = ROOT / 'runs' / cell
        original = ROOT.parent / spec['source_run'] / 'rulebook.json'
        assert e._digest(original.read_bytes()) == spec['source_rulebook_sha256']
        assert (ROOT / spec['input']).read_bytes() == original.read_bytes()
        assert e._load(directory / 'rulebook.json') == e._load(original)
        report = a.replay_audit(directory, output / cell)
        run = e._load(directory / 'audit.json')
        stages = []
        for stage in ('inventory', 'comparison'):
            for attempt in run[stage + '_attempts']:
                record = {'stage': stage, 'error_code': attempt.get('error_code')}
                if attempt.get('request_file'):
                    request = e._load(directory / stage / attempt['request_file'])
                    assert request['config']['thinking_config'] == {'thinking_level': 'high'}
                    assert 'max_output_tokens' not in request['config']
                    assert ('Draft and inventory:' in request['contents']) == (stage == 'comparison')
                if attempt.get('response_file'):
                    response = e._load(directory / stage / attempt['response_file'])
                    record.update(usage=response.get('usage_metadata'),
                                  finish_reason=response['candidates'][0].get('finish_reason'))
                record['seconds'] = round((datetime.fromisoformat(attempt['finished_at'])
                                          - datetime.fromisoformat(attempt['started_at'])).total_seconds(), 2)
                stages.append(record)
        input_run = next(item for item in low if item['cell'] == cell)
        tokens = sum((stage.get('usage') or {}).get('total_token_count', 0) for stage in stages)
        results.append({'cell': cell, 'replayed_identically': True, 'draft_unchanged': True,
                        'processing_status': run['status'], 'assessment_status': report['status'],
                        'review_complete': report.get('review_complete'),
                        'coverage': report.get('coverage'), 'audit_issues': report.get('audit_issues'),
                        'issues': report.get('issues'), 'stages': stages,
                        'audit_reported_tokens': tokens,
                        'low_plus_audit_reported_tokens': tokens + input_run['reported_tokens']})
    calls = sum(len(row['stages']) for row in results)
    assert calls == design['provider_calls']
    e._save(ROOT / 'verification.json', {'provider_calls': calls, 'replay_provider_calls': 0,
                                        'audits': results})
    print(e._canonical({'replayed': len(results), 'audit_calls': calls,
                        'audit_tokens': sum(row['audit_reported_tokens'] for row in results)}))


if __name__ == '__main__':
    main()
