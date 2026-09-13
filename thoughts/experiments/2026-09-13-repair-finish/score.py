"""Aggregate the saved manual source judgments; no model-based labels."""
import run as exp
from rulespec_extrapolator import extraction as e


def main():
    assert (exp.HERE/'RAW-GENERATION-REVIEW.md').exists()
    labels=e._load(exp.HERE/'manual-judgments.json')
    key=e._load(exp.HERE/'arm-key.json')
    counts, costs, adherence = {}, {}, {}
    for cell,info in key.items():
        arm=info['arm']
        decoded=e._load(exp.HERE/f'decoded/{cell}-generation.json')
        for row in labels[cell]:
            group=counts.setdefault(arm,{}).setdefault(row['category'],dict(total=0,raw_success=0,valid_success=0))
            group['total']+=1
            group['raw_success']+=row['raw_success'] is True
            group['valid_success']+=row['valid_success'] is True
        usage=e.recorded_usage(exp.HERE/f'captures/{cell}/generation')
        cost=costs.setdefault(arm,dict(calls=0,tokens={},seconds=0))
        cost['calls']+=usage['recorded_requests']
        call=next(v for v in e._load(exp.HERE/'calls.json') if v['name']==cell+'/generation')
        cost['seconds']+=call['seconds']
        for k,v in usage['tokens'].items():cost['tokens'][k]=cost['tokens'].get(k,0)+v
        shape=adherence.setdefault(arm,dict(proposals=0,full_field_objects=0,emitted_fields=0,unchanged_emitted_fields=0,prepared=0))
        shape['prepared']+=len(decoded['prepared'])
        data=e._load(exp.HERE/f'inputs/{cell}.json')
        names=exp.r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
        for proposal in decoded['payload']['proposals']:
            fields=proposal['fields'];old=data['packet']['claims'][proposal['target']]
            shape['proposals']+=1
            shape['full_field_objects']+=set(fields)==set(names)
            shape['emitted_fields']+=len(fields)
            shape['unchanged_emitted_fields']+=sum(value==old.get(k) for k,value in fields.items())
    assert counts['A']['fresh_repair']['valid_success']==counts['B']['fresh_repair']['valid_success']==0
    for arm in counts:
        counts[arm]['uncertain'].update(raw_success=None,valid_success=None,excluded_from_decision=True)
    result=dict(counts=counts,generation_costs=costs,output_shape=adherence,
        fresh_quality_gain_gate=False,cost_gate=False,
        decision='Do not adopt; neither arm meets the minimum fresh-repair requirement.',
        cost_gate_reason='No fresh complete repairs; generation-plus-check cost not measured because optional checks were skipped.',
        usage=exp.source.x.usage(),provider_seconds=sum(c['seconds'] for c in e._load(exp.HERE/'calls.json')))
    e._save(exp.HERE/'scores.json',result)
    print(e._canonical(result))


if __name__=='__main__':main()
