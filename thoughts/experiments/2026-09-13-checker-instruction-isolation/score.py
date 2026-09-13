"""Apply the preregistered rules after manual review, retaining every judgment."""
from pathlib import Path
from rulespec_extrapolator import extraction as e

HERE = Path(__file__).resolve().parent


def count(rows):
    return dict(correct=sum(r['correct'] for r in rows), total=len(rows),
                false_accepts=sum(r['actual'] == 'supported' and r['expected'] != 'supported' for r in rows),
                abstentions=sum(r['actual'] in {'unknown', 'unassessed'} for r in rows))


def main():
    assert (HERE / 'RAW-REVIEW.md').exists(), 'Read raw results before unmasking scores'
    key = e._load(HERE / 'arm-key.json')
    labels = e._load(HERE / 'labels.json')
    instructions = e._load(HERE / 'instructions.json')
    rows = []
    for cell, info in key.items():
        data = e._load(HERE / f'inputs/{cell}.json')
        path = HERE / f'decoded/{cell}.json'
        decoded = e._load(path) if path.exists() else dict(judgments={})
        for p in data['candidates']:
            label = labels[info['experiment'] + '/' + info['source']][p['id']]
            actual = decoded['judgments'].get(p['id'], {}).get('verdict', 'unassessed')
            rows.append(dict(cell=cell, **info, candidate=p['id'], category=label['category'],
                             expected=label['expected'], actual=actual, correct=actual == label['expected']))
        if info['arm'] == 'A':
            other, = [name for name, value in key.items() if value == dict(info, arm='B')]
            paired = e._load(HERE / f'inputs/{other}.json')
            prompt_a = data.pop('prompt')
            prompt_b = paired.pop('prompt')
            assert data == paired
            assert prompt_a[len(instructions[info['experiment']]['A']):] == prompt_b[len(instructions[info['experiment']]['B']):]
    totals, gates = {}, {}
    for experiment in ('M4a', 'M4b'):
        selected = [r for r in rows if r['experiment'] == experiment]
        def choose(arm, category=None, source=None):
            return [r for r in selected if r['arm'] == arm and (category is None or r['category'] == category)
                    and (source is None or r['source'] == source)]
        totals[experiment] = {arm: dict(all=count(choose(arm)),
            by_category={c: count(choose(arm, c)) for c in sorted({r['category'] for r in selected})},
            by_source={s: count(choose(arm, source=s)) for s in sorted({r['source'] for r in selected})})
            for arm in ('A', 'B')}
        def correct(arm, category): return count(choose(arm, category))['correct']
        if experiment == 'M4a':
            gates[experiment] = dict(
                rejects_all_six_unnecessary_edits=correct('B', 'unnecessary_enrichment') == 6,
                improves_unnecessary_edit_rejection=correct('B', 'unnecessary_enrichment') > correct('A', 'unnecessary_enrichment'),
                accepts_both_medical_repairs=correct('B', 'complete_repair') == 2,
                accepts_all_four_component_and_link_fixes=correct('B', 'component_fix') + correct('B', 'qualification_link') == 4,
                no_increase_wrong_edit_acceptance=count(choose('B', 'wrong_meaning'))['false_accepts'] <= count(choose('A', 'wrong_meaning'))['false_accepts'])
        else:
            gains = {s: count(choose('B', source=s))['correct'] - count(choose('A', source=s))['correct']
                     for s in ('privacy', 'medical', 'notice')}
            losses = []
            for row in choose('A'):
                if row['category'] not in {'wrong_meaning', 'complete_noop'} or not row['correct']: continue
                match, = [r for r in choose('B') if all(r[k] == row[k] for k in ('source', 'candidate', 'repeat'))]
                if not match['correct']: losses.append(match)
            gates[experiment] = dict(at_least_three_net_correct_judgments=sum(gains.values()) >= 3,
                improves_at_least_two_target_contexts=sum(v > 0 for v in gains.values()) >= 2,
                no_lost_wrong_edit_or_complete_noop_control=not losses)
    result = dict(totals=totals, gates=gates, advance={x: all(g.values()) for x, g in gates.items()}, rows=rows)
    e._save(HERE / 'scores.json', result)
    print(e._canonical({k: v for k, v in result.items() if k != 'rows'}))
    print(e._canonical(e._load(HERE / 'usage.json')))
    print('Provider seconds:', sum(c['seconds'] for c in e._load(HERE / 'calls.json')))


if __name__ == '__main__': main()
