"""Score frozen bridge labels after raw review, excluding copied input captures."""
import run as exp
from rulespec_extrapolator import extraction as e


def main():
    assert (exp.HERE / 'RAW-REVIEW.md').exists()
    exp.x.pins()
    rows, cost, extra = [], {}, []
    labels = e._load(exp.PRIOR / 'labels.json')
    for cell, info in e._load(exp.HERE / 'arm-key.json').items():
        decoded = e._load(exp.HERE / f'decoded/{cell}.json')
        judgment = decoded['judgments'].get(info['candidate'])
        actual = judgment['verdict'] if judgment else 'unassessed'
        rows.append(dict(cell=cell, **info, actual=actual, correct=actual == info['expected'], issues=decoded['issues']))
        if info['arm'] == 'A':
            for identity, j in decoded['judgments'].items():
                if identity == info['candidate']: continue
                label = labels[info['source'] + '/' + identity]
                extra.append(dict(cell=cell, candidate=identity, category=label['category'],
                    expected=label['expected'], actual=j['verdict'], correct=j['verdict']==label['expected']))
        usage = e.recorded_usage(exp.HERE / 'captures' / cell)
        values = cost.setdefault(info['arm'], dict(calls=0, tokens={}))
        values['calls'] += usage['recorded_requests']
        for k,v in usage['tokens'].items(): values['tokens'][k] = values['tokens'].get(k, 0)+v
    totals = {arm:dict(correct=sum(r['correct'] for r in rows if r['arm']==arm),
        total=sum(r['arm']==arm for r in rows)) for arm in ('A','B')}
    gate = dict(all_integrated_nochange_correct=totals['B']['correct']==8,
        no_loss_against_current_control=totals['B']['correct']>=totals['A']['correct'],
        all_judgments_grounded=all(not r['issues'] for r in rows))
    usage = e.recorded_usage(exp.HERE, exclude=('base-run','previous','frozen','workspaces','verification-output'))
    result = dict(totals=totals, gate=gate, quality_gate_passed=all(gate.values()), rows=rows,
        control_extra_judgments=extra, costs=cost, usage=usage,
        summed_call_seconds=sum(c['seconds'] for c in e._load(exp.HERE / 'calls.json')),
        usage_note='The raw collection usage.json also counts copied extraction workspaces. This accounting excludes them; launch limits were conservative.')
    e._save(exp.HERE / 'scores.json', result)
    print(e._canonical({k:v for k,v in result.items() if k not in {'rows','control_extra_judgments'}}))


if __name__ == '__main__': main()
