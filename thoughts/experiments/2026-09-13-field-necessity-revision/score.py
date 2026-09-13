"""Score unchanged labels after anonymous raw review; retain all outcomes."""
import run as x
from rulespec_extrapolator import extraction as e


def count(rows):
    return dict(correct=sum(r['correct'] for r in rows), total=len(rows),
        false_accepts=sum(r['actual'] == 'supported' and r['expected'] != 'supported' for r in rows),
        abstentions=sum(r['actual'] in {'unknown', 'unassessed'} for r in rows))


def main():
    assert (x.HERE / 'RAW-REVIEW.md').exists()
    x.x.pins()
    x.paired_check()
    labels = e._load(x.HERE / 'labels.json')
    key = e._load(x.HERE / 'arm-key.json')
    calls = {r['name']: r for r in e._load(x.HERE / 'calls.json')}
    rows, costs = [], {}
    for cell, info in key.items():
        data = e._load(x.HERE / f'inputs/{cell}.json')
        path = x.HERE / f'decoded/{cell}.json'
        decoded = e._load(path) if path.exists() else dict(judgments={})
        for p in data['candidates']:
            label = labels[info['source']][p['id']]
            actual = decoded['judgments'].get(p['id'], {}).get('verdict', 'unassessed')
            rows.append(dict(cell=cell, **info, candidate=p['id'], category=label['category'],
                expected=label['expected'], actual=actual, correct=actual == label['expected']))
        cost = costs.setdefault(info['arm'], dict(calls=0, tokens={}, provider_seconds=0))
        usage = e.recorded_usage(x.HERE / 'captures' / cell)
        cost['calls'] += usage['recorded_requests']
        cost['provider_seconds'] += calls.get(cell, {}).get('seconds', 0)
        for name, value in usage['tokens'].items(): cost['tokens'][name] = cost['tokens'].get(name, 0) + value
    categories = sorted({r['category'] for r in rows})
    sources = sorted({r['source'] for r in rows})
    def select(arm, category=None, source=None):
        return [r for r in rows if r['arm'] == arm and (category is None or r['category'] == category)
                and (source is None or r['source'] == source)]
    totals = {arm: dict(all=count(select(arm)),
        by_category={c: count(select(arm, c)) for c in categories},
        by_source={s: count(select(arm, source=s)) for s in sources}) for arm in ('A', 'B')}
    def correct(arm, category): return totals[arm]['by_category'][category]['correct']
    gate = dict(medical_repairs_both_accepted=correct('B', 'complete_repair') == 2,
        medical_acceptance_improves=correct('B', 'complete_repair') > correct('A', 'complete_repair'),
        unnecessary_original_edits_all_rejected=correct('B', 'unnecessary_enrichment') == 6,
        unnecessary_cosmetic_edits_all_rejected=correct('B', 'cosmetic_enrichment') == 6,
        real_component_fixes_all_accepted=correct('B', 'component_fix') == 2,
        real_qualification_links_all_accepted=correct('B', 'qualification_link') == 2,
        wrong_meaning_actor_target_all_rejected=correct('B', 'wrong_meaning') == 12)
    result = dict(totals=totals, gate=gate, advance=all(gate.values()), costs=costs, rows=rows)
    e._save(x.HERE / 'scores.json', result)
    print(e._canonical({k: v for k, v in result.items() if k != 'rows'}))


if __name__ == '__main__': main()
