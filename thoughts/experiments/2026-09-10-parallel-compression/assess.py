"""Saved-call accounting and final-record checks, separate from manual semantics."""
from datetime import datetime
from pathlib import Path

from rulespec_extrapolator import extraction as e, refinement as r
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.review_store import ReviewStore

ROOT=Path(__file__).resolve().parent
rows=[]
for cell in e._load(ROOT/'cells-design.json')['cells']:
    path=ROOT/'cells'/cell['id'];result=e._load(path/'result.json')
    before=e._load(ROOT/'inputs'/cell['case']/'book.json');after=e._load(path/'after.json')
    assert ReviewStore(path/'workspace').snapshot()==after
    assert export_discovery(after)==e._load(path/'discovery.json')
    originals={c['rule_id']:c for c in before['accepted']}
    current={c['rule_id']:c for c in after['accepted']}
    properties=r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
    for rule_id,prior in originals.items():
        revised=current[rule_id]
        assert all(prior[k]==revised[k] for k in properties if k!='relation')
        assert prior['quote']==revised['quote'] and prior['evidence']==revised['evidence']
    assert after['history']==[o['event'] for o in result['outcomes'] if o['status']=='applied']
    names={c['id']:f'C{i:04d}' for i,c in enumerate(before['accepted'])}
    links=[dict(kind=c['kind'],statement=c['summary'],targets=[names.get(t,t) for t in c['target_ids']])
           for c in after['accepted'] if c['target_ids']]
    stages={}
    for stage in ['proposal','challenge']:
        if not (path/stage/'attempt-0000.json').exists(): continue
        attempt=e._load(path/stage/'attempt-0000.json')
        request=e._load(path/stage/attempt['request_file']);response=e._load(path/stage/attempt['response_file'])
        expected_schema=r.proposal_schema() if stage=='proposal' else r.CHECK_SCHEMA
        assert request['model']==e.DEFAULT_MODEL
        assert request['config']=={'temperature':0,'max_output_tokens':32768,'candidate_count':1,
            'response_mime_type':'application/json','response_json_schema':expected_schema}
        usage=response.get('usage_metadata') or {}
        stages[stage]=dict(input=usage.get('prompt_token_count'),answer=usage.get('candidates_token_count'),
            thinking=usage.get('thoughts_token_count'),total=usage.get('total_token_count'),
            seconds=(datetime.fromisoformat(attempt['finished_at'])-datetime.fromisoformat(attempt['started_at'])).total_seconds(),
            request_sha256=e._digest(request),response_sha256=e._digest(response))
    rows.append(dict(**cell,stages=stages,links=links,original_meaning_and_evidence_preserved=True,
        component_issues_before=[dict(rule_id=c['rule_id'],issue=i) for c in before['accepted'] for i in c['issues']],
        component_issues_after=[dict(rule_id=c['rule_id'],issue=i) for c in after['accepted'] for i in c['issues']],
        applied=sum(o['status']=='applied' for o in result['outcomes']),issues=result['issues']))
totals={}
for arm in ['A','B']:
    data=[stage for row in rows if row['arm']==arm for stage in row['stages'].values()]
    totals[arm]=dict(calls=len(data),**{k:sum(d[k] for d in data if d[k] is not None) for k in ['input','answer','thinking','total','seconds']},
        missing_usage={k:sum(d[k] is None for d in data) for k in ['input','answer','thinking','total']})
result=dict(cells=rows,totals=totals,shared_extraction=e.recorded_usage(ROOT/'fresh-extraction'),
    input_reduction=1-totals['B']['input']/totals['A']['input'],
    total_reduction=1-totals['B']['total']/totals['A']['total'])
e._save(ROOT/'assessment.json',result)
print(e._canonical({k:v for k,v in result.items() if k!='cells'}))
