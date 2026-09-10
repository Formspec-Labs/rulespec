"""Derive counts and verify isolated previews from the six saved captures."""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import tempfile

from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.review_store import ReviewStore

ROOT = Path(__file__).resolve().parent
design = e._load(ROOT/'design.json')
expected = e._load(ROOT/'expected.json')
rows, requests = [], {}
for cell in design['cells']:
    path = ROOT/'cells'/cell['id']
    attempt, = e._load(path/'attempts.json')
    payload, errors = a._read_response(path, attempt)
    request = e._load(path/attempt['request_file'])
    assert request['model'] == design['model']
    assert request['config']['temperature'] == 0
    assert request['config']['max_output_tokens'] == 32768
    assert request['config']['candidate_count'] == 1
    assert request['config']['thinking_config'] == {'thinking_level': 'medium'}
    assert request['config']['response_json_schema'] == e._load(ROOT/'inputs'/f'schema-{cell["arm"]}.json')
    requests[cell['case'],cell['arm']] = request
    decoded = e._load(path/'decoded.json')[cell['arm']]
    book = e._load(ROOT/'inputs'/cell['case']/'book.json')
    packet = e._load(ROOT/'inputs'/cell['case']/'packet.json')
    accepted_indices = {int(p['id'][1:]) for p in decoded['proposals']}
    scores = []
    for target in expected[cell['case']]:
        proposals = [(i,p) for i,p in enumerate(payload.get('proposals',[]))
                     if p['operation']=='edit' and p['target']==target['exemption']]
        proposed = {t for _,p in proposals for t in p['qualifies']}
        accepted = {t for i,p in proposals if i in accepted_indices for t in p['qualifies']}
        desired = set(target['targets'])
        scores.append(dict(exemption=target['exemption'], expected=sorted(desired),
            raw_targets=sorted(proposed), accepted_targets=sorted(accepted),
            correct_raw=len(proposed & desired), wrong_raw=sorted(proposed-desired),
            correct_accepted=len(accepted & desired), wrong_accepted=sorted(accepted-desired),
            raw_exact=proposed==desired, accepted_exact=accepted==desired))
    previews=[]
    with tempfile.TemporaryDirectory() as directory:
        workspace=Path(directory)
        for name,value in [('document.json',book['document']),('rulebook.json',book),('run.json',book['run'])]:
            e._save(workspace/name,value)
        store=ReviewStore(workspace)
        before=store.snapshot()
        for p in decoded['proposals']:
            action=r._action(p,before,'saved provider proposal verification')
            preview=store.preview(action)
            assert store.snapshot()==before
            check=dict(proposal=p['id'],operation=p['proposal']['operation'],preview='passed')
            if p['proposal']['operation']=='edit':
                prior=next(c for c in before['accepted'] if c['id']==p['target_id'])
                revised=next(c for c in preview['accepted'] if c['rule_id']==prior['rule_id'])
                assert len(preview['accepted'])==len(before['accepted'])
                assert revised['supersedes']==[prior['id']] and revised['id']!=prior['id']
                assert revised['target_ids']==sorted(p['qualification_ids'])
                assert revised['review_status']=='pending'
                properties=r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
                assert all(revised[k]==prior[k] for k in properties if k!='relation')
                assert revised['quote']==prior['quote']
                check.update(unchanged_meaning_and_evidence=True, same_rule_id=True,
                             new_revision=True, target_count=len(revised['target_ids']))
            previews.append(check)
    raw=e._load(path/attempt['response_file'])
    elapsed=(datetime.fromisoformat(attempt['finished_at'])-datetime.fromisoformat(attempt['started_at'])).total_seconds()
    rows.append(dict(**cell,errors=errors,raw_proposals=len(payload.get('proposals',[])),
        accepted_proposals=len(decoded['proposals']),
        refused_proposals=sum(i['code']=='proposal_refused' for i in decoded['issues']),
        issues=decoded['issues'],exemptions=scores,previews=previews,
        usage=raw['usage_metadata'],seconds=elapsed))
checks={}
for case in expected:
    left,right=[deepcopy(requests[case,arm]) for arm in ['A','B']]
    for request in [left,right]:
        request.pop('contents')
        request['config'].pop('response_json_schema')
    assert left==right
    checks[case]='Only prompt and schema guidance differ in actual requests.'
totals={}
for arm in ['A','B']:
    arm_rows=[row for row in rows if row['arm']==arm]
    scores=[s for row in arm_rows for s in row['exemptions']]
    totals[arm]=dict(correct_raw=sum(s['correct_raw'] for s in scores),
        correct_accepted=sum(s['correct_accepted'] for s in scores),
        wrong_raw=sum(len(s['wrong_raw']) for s in scores),
        wrong_accepted=sum(len(s['wrong_accepted']) for s in scores),
        positive_target_sets_raw=sum(s['raw_exact'] for s in scores if s['expected']),
        positive_target_sets_accepted=sum(s['accepted_exact'] for s in scores if s['expected']),
        empty_target_controls_pass=sum(s['raw_exact'] for s in scores if not s['expected']),
        usage={key:sum(row['usage'][key] for row in arm_rows) for key in
               ['prompt_token_count','candidates_token_count','thoughts_token_count','total_token_count']},
        seconds=sum(row['seconds'] for row in arm_rows))
result=dict(cells=rows,totals=totals,request_checks=checks,
            limitation='Six single samples on fixed constructed drafts; no new extraction, automated challenge, approval or applied user edits.')
e._save(ROOT/'assessment.json',result)
print(e._canonical(totals))
