"""Derive comparison metrics from preserved captures; no provider access."""
import argparse
from datetime import datetime
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('passage_trial', ROOT / 'experiment.py')
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)
e, a = trial.e, trial.a


def measure():
    results, fixture = e._load(ROOT / 'results.json'), e._load(ROOT / 'fixture.json')
    summary = {}
    for cell, result in results.items():
        directory = ROOT / 'runs' / cell
        attempt = e._load(directory / 'attempts.json')[0]
        payload, errors = a._read_response(directory, attempt)
        assert not errors and result['schema_valid']
        claims = {r['claim_id']: r for r in payload['claim_judgments']}
        units = {r['unit_id']: r for r in payload['unit_judgments']}
        assert set(claims) == {f'C{i:04d}' for i in range(18)}
        assert set(units) == {f'U{i:04d}' for i in range(18)}
        assert all(c in units[u]['claim_ids'] for c,r in claims.items() for u in r['unit_ids'])
        assert all(u in claims[c]['unit_ids'] for u,r in units.items() for c in r['claim_ids'])
        config = e._load(ROOT / 'configuration.json')[cell[0]]
        order_matches = all(list(row) == list(config['schema']['properties'][field]['items']['properties'])
            for field in ('claim_judgments','unit_judgments') for row in payload[field])
        usage = result['usage']
        summary[cell] = {'seconds': (datetime.fromisoformat(attempt['finished_at']) - datetime.fromisoformat(attempt['started_at'])).total_seconds(),
            'prompt_tokens': usage['prompt_token_count'], 'output_tokens': usage['candidates_token_count'],
            'thinking_tokens': usage['thoughts_token_count'], 'total_tokens': usage['total_token_count'],
            'cached_prompt_tokens': usage.get('cached_content_token_count'), 'all_reciprocal_links': True,
            'request_and_output_field_order_match': order_matches,
            'model_evidence_chars': sum(len(s) for field in ('claim_judgments','unit_judgments')
                for row in payload[field] for s in row.get('quotes',row.get('source_refs',[]))),
            'workflows': {k: {'accepted_judgments': sum(len(v['judgments'][f]) for f in ('claim_judgments','unit_judgments')),
                'refused_judgments': len(v['issues']), 'review_complete': v['report']['review_complete'],
                'audit_status': v['report']['status'], 'resolved_evidence_chars': v['source_evidence_chars']}
                for k,v in result['workflows'].items()}}
        if cell[0] == 'Q':
            for field,identity in [('claim_judgments','claim_id'),('unit_judgments','unit_id')]:
                exact = result['workflows']['Q-exact']['judgments'][field]
                token = {r[identity]:r for r in result['workflows']['Q-token']['judgments'][field]}
                assert all(row == token[row[identity]] for row in exact)
    means = {arm: {key: sum(v[key] for c,v in summary.items() if c.startswith(arm))/2
        for key in ('seconds','prompt_tokens','output_tokens','thinking_tokens','total_tokens')}
        for arm in ('P','Q')}
    return {'runs': summary, 'means': means, 'total_reported_tokens': sum(v['total_tokens'] for v in summary.values()),
        'output_token_reduction_fraction': 1-means['P']['output_tokens']/means['Q']['output_tokens'],
        'total_token_reduction_fraction': 1-means['P']['total_tokens']/means['Q']['total_tokens'],
        'quote_accepted_records_preserved_under_token_alignment': True}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('run','replay'))
    args=p.parse_args()
    result=measure()
    if args.mode=='run':
        assert not (ROOT/'metrics.json').exists()
        e._save(ROOT/'metrics.json',result)
    else:
        assert result==e._load(ROOT/'metrics.json')
    print(e._canonical(result))
