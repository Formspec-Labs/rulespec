"""Score the frozen two-factor comparison after raw review."""
import run as exp
from rulespec_extrapolator import extraction as e


def count(rows):
    return dict(correct=sum(r['correct'] for r in rows),total=len(rows),
        unassessed=sum(r['actual']=='unassessed' for r in rows))


def main():
    assert (exp.HERE/'RAW-REVIEW.md').exists()
    exp.x.pins()
    rows,costs=[],{}
    calls={r['name']:r for r in e._load(exp.HERE/'calls.json')}
    for cell,info in e._load(exp.HERE/'arm-key.json').items():
        data=e._load(exp.HERE/f'inputs/{cell}.json')
        decoded=e._load(exp.HERE/f'decoded/{cell}.json')
        for p in data['candidates']:
            label=data['labels'][p['id']]
            actual=decoded['judgments'].get(p['id'],{}).get('verdict','unassessed')
            rows.append(dict(cell=cell,**info,candidate=p['id'],category=label['category'],
                expected=label['expected'],actual=actual,correct=actual==label['expected']))
        usage=e.recorded_usage(exp.HERE/'captures'/cell)
        cost=costs.setdefault(info['arm'],dict(calls=0,tokens={},seconds=0))
        cost['calls']+=usage['recorded_requests']
        cost['seconds']+=calls[cell]['seconds']
        for k,v in usage['tokens'].items(): cost['tokens'][k]=cost['tokens'].get(k,0)+v
    def selected(source=None,arm=None,noop=None):
        return [r for r in rows if (source is None or r['source']==source) and (arm is None or r['arm']==arm)
            and (noop is None or (r['candidate']=='N0000')==noop)]
    matrix={s:{arm:count(selected(s,arm,True)) for arm in exp.FACTORS} for s in exp.CASES}
    hazard_intact=all(matrix['hazard'][arm]['correct']==2 for arm in exp.FACTORS)
    contrasts={}
    for factor,pairs in {'extra_link_status':[('A','B'),('C','D')],
                         'remove_competing_candidates':[('A','C'),('B','D')]}.items():
        contrasts[factor]=[dict(source=s,baseline=lo,changed=hi,
            baseline_correct=matrix[s][lo]['correct'],changed_correct=matrix[s][hi]['correct'],
            repeated_failure_lead=matrix[s][lo]['correct']==2 and matrix[s][hi]['correct']==0 and hazard_intact)
            for s in exp.CASES for lo,hi in pairs]
    interaction=hazard_intact and matrix['leave']['D']['correct']==0 and all(matrix['leave'][arm]['correct']==2 for arm in ('B','C'))
    result=dict(nochange=matrix,totals=dict(nochange=count(selected(noop=True)),edited_controls=count(selected(noop=False))),
        contrasts=contrasts,interaction_lead=interaction,hazard_control_intact=hazard_intact,
        mechanistic_lead=interaction or any(c['repeated_failure_lead'] for values in contrasts.values() for c in values),
        costs=costs,usage=e.recorded_usage(exp.HERE),rows=rows)
    e._save(exp.HERE/'scores.json',result)
    print(e._canonical({k:v for k,v in result.items() if k not in {'rows','costs'}}))
    print(e._canonical(costs))


if __name__=='__main__':main()
