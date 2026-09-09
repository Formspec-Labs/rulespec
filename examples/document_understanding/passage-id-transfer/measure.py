"""Verify captures and derive transfer metrics without provider calls."""
import argparse
from datetime import datetime
from pathlib import Path
from rulespec_extrapolator import audit as a, extraction as e
from rulespec_extrapolator.discovery import export_discovery

ROOT = Path(__file__).resolve().parent


def measure():
    output = {}
    for case in ('passport', 'waste'):
        directory = ROOT / case
        book = e._load(directory / 'extraction/rulebook.json')
        report = e._load(directory / 'audit/report.json')
        inventory = e._load(directory / 'audit/inventory.json')
        audit = e._load(directory / 'audit/audit.json')
        assert audit['schema_version'] == a.AUDIT_VERSION
        assert export_discovery(book) == e._load(directory / 'discovery.json')
        calls = []
        for stage in ('extraction', 'audit/inventory', 'audit/comparison'):
            for response in (directory / stage).glob('*.response.json'):
                raw = e._load(response)
                attempt = e._load(response.with_name(response.name.replace('.response.json', '.json')))
                request = e._load(response.with_name(response.name.replace('.response.json', '.request.json')))
                config = request['config']
                expected_thinking = 'low' if stage == 'extraction' else 'medium'
                assert request['model'] == e.DEFAULT_MODEL
                assert config['temperature'] == 0
                assert config['thinking_config'] == {'thinking_level': expected_thinking}
                assert 'max_output_tokens' not in config
                assert raw['candidates'][0]['finish_reason'] == 'STOP'
                calls.append({'stage': stage, 'usage': raw.get('usage_metadata'),
                    'finish_reason': 'STOP', 'seconds': (datetime.fromisoformat(attempt['finished_at']) -
                        datetime.fromisoformat(attempt['started_at'])).total_seconds()})
        assert len(calls) == 3
        judgments = e._load(directory / 'audit/judgments.json')
        for field in ('claim_judgments', 'unit_judgments'):
            for row in judgments[field]:
                for span in row['source_spans']:
                    assert span['quote'] == book['document']['text'][span['start']:span['end']]
        for subdirectory in ('extraction', 'audit'):
            r = directory / subdirectory
            for name, digest in e._load(r / 'manifest.json')['artifacts_sha256'].items():
                assert e._digest((r / name).read_bytes()) == digest, name
        output[case] = {'accepted_claims': len(book['accepted']), 'rejected_claims': len(book['rejected']),
            'extraction_status': book['run']['status'], 'extraction_refusals': len(book['extraction_refusals']),
            'component_evidence_warnings': sum(x['code'] == 'component_evidence_unresolved'
                for c in book['accepted'] for x in c.get('issues', [])),
            'unresolved_citation_records': len(book['unresolved']),
            'inventory_observations': len(inventory['units']), 'substantive_inventory_units': report['counts']['expected_units'],
            'inventory_issues': inventory['issues'], 'comparison_issues': report['audit_issues'],
            'accepted_judgments': sum(len(judgments[f]) for f in ('claim_judgments', 'unit_judgments')),
            'model_audit_status': report['status'], 'review_complete': report['review_complete'],
            'semantic_completeness': report['semantic_completeness'], 'calls': calls,
            'total_reported_tokens': sum(c['usage']['total_token_count'] for c in calls)}
    return output


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=('run', 'replay'))
    args = p.parse_args()
    result = measure()
    if args.mode == 'run':
        assert not (ROOT / 'metrics.json').exists()
        e._save(ROOT / 'metrics.json', result)
    else:
        assert result == e._load(ROOT / 'metrics.json')
    for case, row in result.items():
        print(case, row['accepted_judgments'], 'judgments;', row['total_reported_tokens'], 'tokens')
