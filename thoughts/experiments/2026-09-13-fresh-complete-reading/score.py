"""Score frozen labels after raw review; do not replace disputed original labels."""
from collections import defaultdict
from pathlib import Path
import run as x
from rulespec_extrapolator import extraction as e


def main():
    assert (x.HERE/'raw-review-receipt.json').exists()
    labels=e._load(x.HERE/'labels.json'); key=e._load(x.HERE/'arm-key.json'); rows=[]
    regression_labels=e._load(x.OLD/'labels.json')
    for cell,info in key.items():
        data=e._load(x.HERE/f'inputs/{cell}.json'); decoded=e._load(x.HERE/f'decoded/{cell}.json')
        for p in data['candidates']:
            if info['fresh']: label=labels[info['source']+'/'+p['id']]
            else:
                old=regression_labels['notice/'+p['id']]
                label=dict(expected=old['expected'],category=old['label'])
            actual=decoded['judgments'].get(p['id'],{}).get('verdict','unassessed')
            rows.append(dict(cell=cell,**info,candidate=p['id'],operation=p['proposal']['operation'],
                category=label['category'],expected=label['expected'],actual=actual,correct=actual==label['expected']))
    def count(selected):
        return dict(correct=sum(r['correct'] for r in selected),total=len(selected),
            false_accepts=sum(r['actual']=='supported' and r['expected']!='supported' for r in selected),
            abstentions=sum(r['actual'] in ('unknown','unassessed') for r in selected))
    totals={}; sources={}
    for arm in ('A','B'):
        fresh=[r for r in rows if r['fresh'] and r['arm']==arm]
        totals[arm]={group:count([r for r in fresh if predicate(r)]) for group,predicate in {
            'all':lambda r:True,'edits':lambda r:r['operation']=='edit','noops':lambda r:r['operation']=='no_change',
            'needed_repairs':lambda r:r['category']=='complete_repair','wrong_edits':lambda r:r['category']=='wrong_meaning',
            'unnecessary_edits':lambda r:r['category']=='unnecessary_enrichment',
            'complete_noops':lambda r:r['category']=='complete_noop','incomplete_noops':lambda r:r['category']=='incomplete_noop'}.items()}
        sources[arm]={source:count([r for r in fresh if r['source']==source and r['operation']=='edit']) for source in x.NAMES}
    improved=[s for s in x.NAMES if sources['B'][s]['correct']>sources['A'][s]['correct']]
    regressed=[s for s in x.NAMES if sources['B'][s]['correct']<sources['A'][s]['correct']]
    b_rate=totals['B']['edits']['correct']/totals['B']['edits']['total']; a_rate=totals['A']['edits']['correct']/totals['A']['edits']['total']
    gate=dict(edited_accuracy_at_least_85_percent=b_rate>=.85,improvement_at_least_15_points=b_rate-a_rate>=.15,
        improves_at_least_three_sources=len(improved)>=3,
        no_increase_wrong_edit_acceptance=totals['B']['wrong_edits']['false_accepts']<=totals['A']['wrong_edits']['false_accepts'],
        noop_accuracy_at_least_75_percent=totals['B']['noops']['correct']/totals['B']['noops']['total']>=.75)
    # Predeclared recall boundary uncertainty: exclude it, without rewriting labels.
    sensitivity={arm:count([r for r in rows if r['fresh'] and r['arm']==arm and r['source']!='recall' and r['operation']=='edit']) for arm in ('A','B')}
    result=dict(totals=totals,by_source=sources,improved_sources=improved,regressed_sources=regressed,
        gate=gate,all_gate_conditions_met=all(gate.values()),recall_excluded_sensitivity=sensitivity,
        regressions={arm:count([r for r in rows if not r['fresh'] and r['arm']==arm]) for arm in ('A','B')},rows=rows)
    e._save(x.HERE/'scores.json',result)
    print(e._canonical({k:v for k,v in result.items() if k not in {'rows','by_source'}}))
    print(e._canonical(e._load(x.HERE/'usage.json')))
    print('Call seconds',sum(c['seconds'] for c in e._load(x.HERE/'calls.json')))


if __name__=='__main__': main()
