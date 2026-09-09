"""Replay captures and verify that property order was the only request change."""
from pathlib import Path
from copy import deepcopy
import json
import subprocess
import sys
from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent

def attribute_order(schema):
    return list(schema['properties']['extractions']['items']['properties']['unit_attributes']['properties'])


def main():
    replay_root = Path(sys.argv[1]).resolve()
    replay_root.mkdir(parents=True, exist_ok=False)
    design = e._load(ROOT / 'design.json')
    rows = []
    for sample, variant, repeat in design['calls']:
        run = ROOT / 'runs' / sample / variant / str(repeat)
        p = subprocess.run([sys.executable, str(ROOT/'experiment.py'), 'replay', sample, variant,
            str(repeat), '--output', str(replay_root/sample/variant/str(repeat))], capture_output=True, text=True)
        if p.returncode:
            raise RuntimeError('Replay failed: ' + str(run))
        request = e._load(run/'attempt-0000.request.json')
        control = e._load(ROOT/'runs'/sample/'control/1/attempt-0000.request.json')
        # Dictionary equality ignores order, so check the intended order separately.
        assert request == control, 'Request meaning/configuration changed'
        schema = request['config']['response_json_schema']
        expected_order = design['control_attribute_order' if variant == 'control' else 'treatment_attribute_order']
        assert attribute_order(schema) == expected_order
        restored = deepcopy(request)
        attrs = restored['config']['response_json_schema']['properties']['extractions']['items']['properties']['unit_attributes']
        attrs['properties'] = {k: attrs['properties'][k] for k in design['control_attribute_order']}
        assert json.dumps(restored) == json.dumps(control), 'Another request order changed'
        assert attribute_order(e._load(run/'frozen/provider-schema.json')) == expected_order
        response = e._load(run/'attempt-0000.response.json')
        raw = json.loads(''.join(p['text'] for p in response['candidates'][0]['content']['parts']
            if p.get('text') and not p.get('thought')))
        book = e._load(run/'rulebook.json')
        raw_rows = raw['extractions']
        preserved = len(raw_rows) == len(book['accepted']) and all(
            all(row['unit_attributes'][a] == claim[b] for a,b in [('statement','summary'),
                ('scope_text','scope_text'),('kind','kind'),('modality','modality')])
            for row,claim in zip(raw_rows,book['accepted']))
        usage = response['usage_metadata']
        rows.append({'sample':sample,'variant':variant,'repeat':repeat,
            'replay_identical':True,'only_property_order_changed':True,
            'response_rows_follow_order':sum(list(r['unit_attributes']) == expected_order for r in raw_rows),
            'raw_rows':len(raw_rows),'raw_meaning_preserved':preserved,
            'accepted':len(book['accepted']),'refusals':len(book['extraction_refusals']),
            'rejected':len(book['rejected']),'status':book['run']['status'],
            'finish_reason':response['candidates'][0].get('finish_reason'),
            'tokens':usage['total_token_count'],'prompt_tokens':usage['prompt_token_count'],
            'output_tokens':usage['candidates_token_count'],'thought_tokens':usage.get('thoughts_token_count',0),
            'validation':e._load(run/'validation.json'),
            'request_sha256':e._digest((run/'attempt-0000.request.json').read_bytes()),
            'response_sha256':e._digest((run/'attempt-0000.response.json').read_bytes())})
    e._save(ROOT/'verification.json',{'provider_calls':len(rows),'replay_provider_calls':0,
        'total_reported_tokens':sum(r['tokens'] for r in rows),'results':rows})
    print(e._canonical({'replayed':len(rows),'reported_tokens':sum(r['tokens'] for r in rows)}))

if __name__ == '__main__':
    main()
