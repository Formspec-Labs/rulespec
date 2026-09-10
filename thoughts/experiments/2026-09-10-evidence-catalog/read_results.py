"""Create shuffled reading copies without exposing treatment labels."""
from pathlib import Path
from secrets import SystemRandom

from rulespec_extrapolator import audit as a, extraction as e

ROOT=Path(__file__).resolve().parent
cells=e._load(ROOT/'cells-design.json')['cells'];SystemRandom().shuffle(cells)
mapping={};rows=[]
for i,cell in enumerate(cells):
    label=f'output-{i+1}';mapping[label]=cell
    path=ROOT/'cells'/cell['id'];packet=e._load(ROOT/'inputs'/cell['case']/'packet.json')
    payload,errors=a._read_response(path/'proposal',e._load(path/'proposal/attempt-0000.json'))
    for proposal in payload.get('proposals',[]):
        prior=packet['claims'].get(proposal.get('target'),{})
        proposal['unchanged_fields']=[k for k,v in proposal['fields'].items() if k in prior and v==prior[k]]
        proposal['fields']={k:v for k,v in proposal['fields'].items() if k not in proposal['unchanged_fields'] and v not in ('',[],None)}
        if proposal.get('quote')==prior.get('quote'):
            proposal['quote']='[exactly unchanged from original claim]'
    result=e._load(path/'result.json')
    checks=None
    if (path/'challenge/attempt-0000.json').exists():
        checks,errs=a._read_response(path/'challenge',e._load(path/'challenge/attempt-0000.json'))
        errors+=errs
    before=e._load(ROOT/'inputs'/cell['case']/'book.json')
    after=e._load(path/'after.json');original={c['rule_id']:c for c in before['accepted']}
    names={c['id']:f'C{i:04d}' for i,c in enumerate(before['accepted'])}
    changes=[]
    for claim in after['accepted']:
        prior=original.get(claim['rule_id'],{})
        if prior.get('id')!=claim['id']:
            changes.append(dict(kind=claim['kind'],modality=claim['modality'],statement=claim['summary'],
                targets=[names.get(t,t) for t in claim['target_ids']],
                statement_unchanged=prior.get('summary')==claim['summary'],issues=claim['issues']+claim['link_issues']))
    rows.append(dict(label=label,case=cell['case'],payload=payload,parse_errors=errors,
        decoder_issues=result['issues'],challenge=checks,
        outcomes=[{k:v for k,v in o.items() if k!='event'} for o in result['outcomes']],final_changes=changes))
assert not (ROOT/'blind-map.json').exists()
e._save(ROOT/'blind-map.json',mapping)
e._save(ROOT/'blind-results.json',rows)
print('Saved shuffled, label-hidden results; unchanged fields are listed, originals retained.')
