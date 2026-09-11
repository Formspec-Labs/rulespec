"""Count the saved manual judgments; never reclassify parser output."""
import json
from pathlib import Path

root=Path(__file__).parent
labels=json.loads(root.joinpath('blind-assessment.json').read_text())
key=json.loads(root.joinpath('blind-key.json').read_text())
raw=json.loads(root.joinpath('raw.json').read_text())
replay=json.loads(root.joinpath('replay.json').read_text())
assert raw==replay
assert [r['case_id'] for r in labels] == [r['case']['id'] for r in raw], 'Assessment coverage differs from inputs'
for assessed, observed in zip(labels, raw, strict=True):
 assert assessed['expected'] == observed['case']['expected']
 for record in assessed['arms'].values():
  assert set(record['correct']) <= set(assessed['expected'])
  assert set(record['correct_with_native_span']) <= set(record['correct'])
expected=sum(len(r['expected']) for r in labels)
baseline={(row['case_id'],v) for row in labels for v in row['arms'][key['A-current']]['correct']}
base_families={v.split('|')[0] for _,v in baseline}
summary={'cases':len(labels),'expected_references':expected,
         'actual_source_passages':sum(r['case']['origin']=='actual pinned source paragraph' for r in raw),
         'negative_cases':sum(r['negative'] for r in labels),'arms':{},'replay_equal':True,
         'provider_calls':0,'parser_errors':[], 'span_checks':[]}
for row in raw:
 text=row['case']['raw']
 for arm,functions in row['arms'].items():
  for function,result in functions.items():
   if 'error' in result:summary['parser_errors'].append({'case':row['case']['id'],'arm':arm,'function':function,**result})
   for observation in result.get('output',[]):
    span=observation.get('span')
    if span is None and 'start' in observation and 'end' in observation:
     span=[observation['start'],observation['end']]
    if span is not None:
     a,b=span
     assert 0<=a<b<=len(text),(row['case']['id'],arm,function,span)
     quote=observation.get('text',observation.get('surface'))
     if quote is not None: assert text[a:b]==quote
     summary['span_checks'].append({'case':row['case']['id'],'arm':arm,'function':function,
                                   'span':span,'source_slice':text[a:b],'returned_quote_checked':quote is not None})
for arm,letter in key.items():
 correct={(row['case_id'],v) for row in labels for v in row['arms'][letter]['correct']}
 grounded={(row['case_id'],v) for row in labels for v in row['arms'][letter]['correct_with_native_span']}
 failures=[{'case':r['case_id'],**issue} for r in labels for issue in r['arms'][letter]['misleading']]
 negative=[f for f in failures if next(r for r in labels if r['case_id']==f['case'])['negative']]
 gained=correct-baseline
 families=sorted({v.split('|')[0] for _,v in gained}-base_families)
 lost=sorted(baseline-correct)
 summary['arms'][arm]={'correct_distinct_references':len(correct),'correct_with_native_span':len(grounded),
    'missed_expected':expected-len(correct),'misleading_readings':failures,'negative_case_issues':len(negative),
    'duplicate_correct_observations':sum(r['arms'][letter]['duplicate_correct_observations'] for r in labels),
    'additional_reference_kinds':families,'baseline_successes_lost':lost,
    'broader_gate_passed':len(families)>=3 and not negative and not lost and gained<=grounded}
with root.joinpath('summary.json').open('x') as f:json.dump(summary,f,indent=2)
print(json.dumps({k:v for k,v in summary.items() if k not in ('span_checks','arms')},indent=2))
for arm,info in summary['arms'].items():print(arm,json.dumps(info))
