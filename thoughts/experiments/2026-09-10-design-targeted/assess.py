"""Mechanical accounting and recommendation simulation, not deployment evidence."""
from pathlib import Path
from rulespec_extrapolator import extraction as e, refinement as r

ROOT=Path(__file__).resolve().parent
expected=e._load(ROOT/'expected.json')
rows=[]
for i,cell in enumerate(e._load(ROOT/'design.json')['cells']):
    path=ROOT/'cells'/f'cell-{i:02d}'
    result=e._load(path/'result.json');data=e._load(ROOT/'inputs'/f"{cell['case']}.json")
    attempt=e._load(path/'attempt-0000.json');request=e._load(path/attempt['request_file'])
    response=e._load(path/attempt['response_file']);usage=response.get('usage_metadata') or {}
    assert request['model']==e.DEFAULT_MODEL
    config={k:v for k,v in request['config'].items() if k!='response_json_schema'}
    assert config==dict(temperature=0,max_output_tokens=32768,candidate_count=1,response_mime_type='application/json')
    judgments=[];narrowed=[]
    for pid,labels in expected[cell['case']].items():
        proposal=next(p for p in data['proposals'] if p['id']==pid)
        meaning=result['checks'].get(pid if cell['arm']=='A' else pid+':meaning',{}).get('verdict','missing')
        supported=[]
        for target in proposal['proposal']['qualifies']:
            check=result['checks'].get(pid if cell['arm']=='A' else pid+':'+target,{})
            verdict=check.get('verdict','missing')
            eligible=meaning=='supported' and verdict=='supported'
            if eligible:supported.append(target)
            label=next(k for k in ['positive','negative','uncertain'] if target in labels[k])
            judgments.append(dict(proposal=pid,target=target,label=label,verdict=verdict,
                meaning_verdict=meaning,recommended=eligible,
                rationale=check.get('rationale'),source_spans=check.get('source_spans',[])))
        if supported and proposal['proposal']['operation']=='edit' and proposal['fields']['kind']=='exemption':
            raw=dict(operation='link',target=proposal['proposal']['target'],qualifies=supported,rationale='Experimental selection of independently supported candidate targets; no graph application.')
            window,=e.plan_windows(data['book']['document'],24000)
            decoded,issues=r._decode_proposals(dict(proposals=[raw],observations=[]),[],data['book']['document'],window,data['packet'],'relationships')
            assert len(decoded)==1 and not issues
            narrowed.append(dict(proposal=pid,targets=supported,current_link_decoder_valid=True,applied=False))
    rows.append(dict(**cell,cell=f'cell-{i:02d}',judgments=judgments,narrowed_existing_links=narrowed,
        decoding_issues=result['issues'],usage={k:usage.get(v) for k,v in dict(input='prompt_token_count',answer='candidates_token_count',thinking='thoughts_token_count',total='total_token_count').items()}))
totals={}
for arm in ['A','B']:
    cells=[row for row in rows if row['arm']==arm]
    decisions=[j for c in cells for j in c['judgments']]
    totals[arm]=dict(calls=len(cells),known_positive_recommended=sum(j['recommended'] and j['label']=='positive' for j in decisions),
        known_negative_recommended=sum(j['recommended'] and j['label']=='negative' for j in decisions),
        uncertain_recommended=sum(j['recommended'] and j['label']=='uncertain' for j in decisions),
        **{k:sum(c['usage'][k] for c in cells if c['usage'][k] is not None) for k in ['input','answer','thinking','total']},
        missing_usage={k:sum(c['usage'][k] is None for c in cells) for k in ['input','answer','thinking','total']})
assessment=dict(cells=rows,totals=totals,expected_positive=5,expected_negative=3,uncertain_pairs=1,
    applied_graph_changes=0,partial_additions_are='recommendations only',
    total_token_ratio_B_A=totals['B']['total']/totals['A']['total'])
e._save(ROOT/'assessment.json',assessment)
print(e._canonical({k:v for k,v in assessment.items() if k!='cells'}))
