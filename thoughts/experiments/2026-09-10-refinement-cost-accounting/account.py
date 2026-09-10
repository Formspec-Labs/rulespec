"""Read existing captures; attribute usage without estimating hypothetical bills."""
from collections import Counter
from pathlib import Path

from rulespec_extrapolator import extraction as e, refinement as r

ROOT=Path(__file__).resolve().parent
RUN=ROOT.parent/'2026-09-10-exemption-end-to-end'
rows=[]; packets=[]
for case in ['alcohol','rail-crossings']:
    directory=RUN/'cases'/case
    for area in ['extraction','refinement']:
        for request_path in sorted((directory/area).rglob('attempt-*.request.json')):
            if set(request_path.relative_to(directory).parts)&{'base-run','frozen','previous'}:
                continue
            request=e._load(request_path)
            response=e._load(request_path.with_name(request_path.name.replace('.request.','.response.')))
            relative=str(request_path.relative_to(directory))
            if area=='extraction': stage='extraction'
            elif '/initial-audit/' in relative: stage='initial-audit/'+request_path.parent.name
            elif '/final-audit/' in relative: stage='final-audit/'+request_path.parent.name
            else: stage=request_path.relative_to(directory).parts[1]+'/'+request_path.parent.name
            usage=response.get('usage_metadata') or {}
            rows.append(dict(case=case,stage=stage,request=str(request_path.relative_to(RUN)),
                request_sha256=e._digest(request_path.read_bytes()),response_sha256=e._digest(request_path.with_name(request_path.name.replace('.request.','.response.')).read_bytes()),
                input=usage.get('prompt_token_count'),answer=usage.get('candidates_token_count'),
                thinking=usage.get('thoughts_token_count'),total=usage.get('total_token_count'),
                request_characters=len(request['contents'])))
    for stage in ['recovery','relationships']:
        path=directory/'refinement'/stage/'window-0000'
        packet=e._load(path/'packet.json');view=r._model_packet(packet)
        request=e._load(path/'proposal/attempt-0000.request.json')
        description=r.RECOVERY if stage=='recovery' else r.RELATIONSHIPS
        assert request['contents']==r._proposal_prompt(description,packet)
        top={key:len(e._canonical(value)) for key,value in view.items()}
        claim_fields=Counter()
        for claim in view['claims'].values():
            for key,value in claim.items(): claim_fields[key]+=len(e._canonical(value))
        packets.append(dict(case=case,stage=stage,total_packet_characters=len(e._canonical(view)),
            top_level_value_characters=top,claim_field_value_characters=dict(claim_fields.most_common())))
totals={}
for stage in sorted({row['stage'] for row in rows}):
    group=[row for row in rows if row['stage']==stage]
    totals[stage]=dict(calls=len(group),**{key:dict(reported_sum=sum(row[key] for row in group if isinstance(row[key],int)),
        missing=sum(row[key] is None for row in group)) for key in ['input','answer','thinking','total']})
assert len(rows)==16
assert sum(row['total'] for row in rows)==245683
e._save(ROOT/'results.json',dict(calls=rows,stage_totals=totals,packets=packets,
    limitation='Reported stage costs and serialized value sizes only. No stage removal, provider-token saving, semantic gain or causal attribution is simulated.'))
for stage,values in totals.items():
    print(stage,{key:value for key,value in values.items() if key!='thinking'})
for packet in packets:
    print('PACKET',packet['case'],packet['stage'],'total',packet['total_packet_characters'],
          'parts',packet['top_level_value_characters'],'largest claim fields',list(packet['claim_field_value_characters'].items())[:7])
