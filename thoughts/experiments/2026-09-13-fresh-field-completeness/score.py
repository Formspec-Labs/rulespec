"""Apply frozen labels and comparative gates only after raw review."""
import run as exp
from rulespec_extrapolator import extraction as e, refinement as r


def count(rows):
    return dict(correct=sum(v['correct'] for v in rows), total=len(rows),
        false_accepts=sum(v['actual'] == 'supported' and v['expected'] != 'supported' for v in rows),
        abstentions=sum(v['actual'] in {'unknown', 'unassessed'} for v in rows))


def main():
    assert (exp.HERE / 'RAW-REVIEW.md').exists()
    exp.x.pins()
    exp.x.pins('check-pins.json')
    key = e._load(exp.HERE / 'arm-key.json')
    labels = e._load(exp.HERE / 'labels.json')
    instructions = e._load(exp.HERE / 'instructions.json')
    rows, costs = [], {}
    calls = {c['name']:c for c in e._load(exp.HERE / 'calls.json')}
    for cell, info in key.items():
        data = e._load(exp.HERE / f'inputs/{cell}.json')
        path = exp.HERE / f'decoded/{cell}.json'
        decoded = e._load(path) if path.exists() else dict(judgments={})
        for p in data['candidates']:
            label = labels[info['source'] + '/' + p['id']]
            actual = decoded['judgments'].get(p['id'], {}).get('verdict', 'unassessed')
            rows.append(dict(cell=cell, **info, candidate=p['id'], category=label['category'],
                operation=p['proposal']['operation'], expected=label['expected'], actual=actual, correct=actual==label['expected']))
        if info['arm'] == 'A':
            paired, = [c for c,v in key.items() if v == dict(info, arm='B')]
            other = e._load(exp.HERE / f'inputs/{paired}.json')
            assert all(data[k] == other[k] for k in ('document', 'window', 'packet'))
            assert data['candidates'] == [p for p in other['candidates'] if p['proposal']['operation'] != 'no_change']
        # Verify the intended complete prefix and unchanged production data formatter.
        assert data['prompt'].startswith(instructions[info['arm']] + r._challenge_prompt(data['packet'], data['candidates'], data['document'])[len(r.CHECK):])
        group = ('fresh/' if info['fresh'] else 'diagnostic/') + info['arm']
        cost = costs.setdefault(group, dict(calls=0, tokens={}, provider_seconds=0))
        usage = e.recorded_usage(exp.HERE / 'captures' / cell)
        cost['calls'] += usage['recorded_requests']
        cost['provider_seconds'] += calls.get(cell, {}).get('seconds', 0)
        for k, value in usage['tokens'].items(): cost['tokens'][k] = cost['tokens'].get(k, 0) + value
    def select(arm, category=None, source=None, operation=None, fresh=True):
        return [v for v in rows if v['arm']==arm and v['fresh']==fresh
                and (category is None or v['category']==category)
                and (source is None or v['source']==source)
                and (operation is None or v['operation']==operation)]
    categories = sorted({v['category'] for v in rows if v['fresh']})
    totals = {arm: dict(edits=count(select(arm, operation='edit')), noops=count(select(arm, operation='no_change')),
        by_category={c:count(select(arm, category=c)) for c in categories},
        by_source_edits={s:count(select(arm, source=s, operation='edit')) for s in exp.x.NAMES}) for arm in ('A','B')}
    def rate(value): return value['correct'] / value['total'] if value['total'] else 0
    def value(arm, category): return totals[arm]['by_category'][category]
    improved = [s for s in exp.x.NAMES if totals['B']['by_source_edits'][s]['correct'] > totals['A']['by_source_edits'][s]['correct']]
    regressed = [s for s in exp.x.NAMES if totals['B']['by_source_edits'][s]['correct'] < totals['A']['by_source_edits'][s]['correct']]
    needed_contexts = {v['source'] for v in select('B', category='complete_repair')}
    complete_contexts = {v['source'] for v in select('B', category='complete_noop')}
    incomplete_contexts = {v['source'] for v in select('B', category='incomplete_noop')}
    diag = {arm:count(select(arm, fresh=False)) for arm in ('A','B')}
    gate = dict(edit_accuracy_at_least_85_percent=rate(totals['B']['edits'])>=.85,
        edit_gain_at_least_10_points=rate(totals['B']['edits'])-rate(totals['A']['edits'])>=.10,
        improves_three_sources=len(improved)>=3,
        needed_repairs_at_least_80_percent=rate(value('B','complete_repair'))>=.80,
        no_loss_needed_repairs=value('B','complete_repair')['correct']>=value('A','complete_repair')['correct'],
        at_least_two_natural_meaning_gaps=len(needed_contexts)>=2,
        noop_accuracy_at_least_85_percent=rate(totals['B']['noops'])>=.85,
        noop_case_coverage=len(complete_contexts)>=2 and len(incomplete_contexts)>=2,
        all_wrong_edits_rejected=value('B','wrong_meaning')['correct']==value('B','wrong_meaning')['total'],
        plain_redundancy_at_least_90_percent=rate(value('B','unnecessary_enrichment'))>=.90,
        cosmetic_redundancy_at_least_90_percent=rate(value('B','cosmetic_enrichment'))>=.90,
        redundant_case_coverage=len({v['source'] for v in select('B', category='unnecessary_enrichment')})>=3,
        all_four_useful_diagnostic_corrections_accepted=sum(v['correct'] for v in select('B', fresh=False) if v['expected']=='supported')==4,
        all_diagnostic_wrong_controls_rejected=all(v['correct'] for v in select('B', fresh=False) if v['expected']=='unsupported'))
    excluded = {'debt', 'jury_fee', 'religious'}
    sensitivity = {arm:dict(edits=count([v for v in select(arm, operation='edit') if v['source'] not in excluded]),
        noops=count([v for v in select(arm, operation='no_change') if v['source'] not in excluded])) for arm in ('A','B')}
    result = dict(totals=totals, diagnostic=diag, improved_sources=improved, regressed_sources=regressed,
        gate=gate, advance=all(gate.values()), sensitivity_excluding_debt_jury_fee_religious=sensitivity,
        production_unassessed_noop_targets=len(select('B', operation='no_change')), costs=costs, rows=rows)
    e._save(exp.HERE / 'scores.json', result)
    print(e._canonical({k:v for k,v in result.items() if k not in {'rows','costs'}}))
    print(e._canonical(costs))
    print(e._canonical(e._load(exp.HERE / 'usage.json')))


if __name__ == '__main__': main()
