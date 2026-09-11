"""Compare an existing baseline with a family-filtered append-only intervention."""
import hashlib
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import sys

from spicysearch import identifiers

root=Path(__file__).resolve().parent
baseline_path=root.parent/'2026-09-10-reference-tool-reuse/scan.py'
spec=importlib.util.spec_from_file_location('baseline_scan',baseline_path)
baseline=importlib.util.module_from_spec(spec);spec.loader.exec_module(baseline)
ALLOWED=frozenset({'public_law','statutes_at_large','executive_order','docket','rin'})


def run_case(case):
    document={'id':case['id'],'text':case['raw'],'sha256':case['text_sha256']}
    a=baseline.scan(document)
    b=baseline.scan(document)
    raw=[c.as_dict() for c in identifiers.detect_identifiers(document['text'])]
    b['additional_reference_candidates']=[c for c in raw if c['kind'] in ALLOWED]
    return {'case':case,'baseline':a,'treatment':b,'unfiltered_detector_output':raw}


def key(kind,value,span):
    return (kind,value,tuple(span))


def assess(row):
    case=row['case'];b=dict(row['treatment']);additions=b.pop('additional_reference_candidates')
    unchanged=b==row['baseline']
    expected=Counter(key(c['kind'],c['value'],c['span']) for c in case['expected_additions'])
    actual=Counter(key(c['kind'],c['value'],c['span']) for c in additions)
    correct=expected & actual
    unexpected=actual-expected
    missed=expected-actual
    spans=[]
    for c in additions:
        start,end=c['span']
        valid=isinstance(start,int) and isinstance(end,int) and 0<=start<end<=len(case['raw'])
        spans.append({'candidate':c,'valid_bounds':valid,'source_quote':case['raw'][start:end] if valid else None})
    return {'id':case['id'],'name':case['name'],'group':case['group'],'baseline_equal':unchanged,
            'expected_additions':sum(expected.values()),'correct_additions':sum(correct.values()),
            'correct_kinds':sorted({k[0] for k in correct}),
            'unexpected':[{'kind':k[0],'value':k[1],'span':list(k[2]),'count':n} for k,n in unexpected.items()],
            'missed':[{'kind':k[0],'value':k[1],'span':list(k[2]),'count':n} for k,n in missed.items()],
            'span_checks':spans}


cases=json.loads(root.joinpath('cases.json').read_text())
for c in cases:
    assert hashlib.sha256(c['raw'].encode()).hexdigest()==c['text_sha256']
    for expected in c['expected_additions']:
        a,b=expected['span'];assert c['raw'][a:b]==expected['quote']
metadata={'started':datetime.now(timezone.utc).isoformat(),'python':sys.executable,
          'baseline_path':str(baseline_path),'baseline_sha256':hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
          'detector_path':identifiers.__file__,'detector_sha256':hashlib.sha256(Path(identifiers.__file__).read_bytes()).hexdigest(),
          'cases_sha256':hashlib.sha256(root.joinpath('cases.json').read_bytes()).hexdigest(),
          'design_sha256':hashlib.sha256(root.joinpath('design.md').read_bytes()).hexdigest(),
          'allowed_kinds':sorted(ALLOWED),'provider_calls':0,'temperature':None,'model':None}
print(json.dumps({'baseline':metadata['baseline_path'],'detector':metadata['detector_path']}),flush=True)
rows=[run_case(c) for c in cases]
with root.joinpath('raw.json').open('x') as f:json.dump(rows,f,ensure_ascii=False,indent=2)
replay=[run_case(c) for c in cases]
with root.joinpath('replay.json').open('x') as f:json.dump(replay,f,ensure_ascii=False,indent=2)
metadata['replay_equal']=rows==replay
judgments=[assess(r) for r in rows]
assert [j['id'] for j in judgments]==[c['id'] for c in cases]
summary={'groups':{},'gate_passed':True}
for group in ('real-positive','historical-noise-control'):
    selected=[j for j in judgments if j['group']==group]
    summary['groups'][group]={'cases':len(selected),'expected_additions':sum(j['expected_additions'] for j in selected),
        'correct_additions':sum(j['correct_additions'] for j in selected),
        'unexpected_additions':sum(c['count'] for j in selected for c in j['unexpected']),
        'missed_additions':sum(c['count'] for j in selected for c in j['missed']),
        'baseline_changes':sum(not j['baseline_equal'] for j in selected),
        'invalid_spans':sum(not c['valid_bounds'] for j in selected for c in j['span_checks']),
        'correct_kinds':sorted({kind for j in selected for kind in j['correct_kinds']})}
summary['gate_passed']=(len(summary['groups']['real-positive']['correct_kinds'])==5
    and all(not any(g[k] for k in ('unexpected_additions','missed_additions','baseline_changes','invalid_spans'))
            for g in summary['groups'].values()))
metadata['finished']=datetime.now(timezone.utc).isoformat()
with root.joinpath('assessment.json').open('x') as f:json.dump(judgments,f,indent=2)
with root.joinpath('summary.json').open('x') as f:json.dump(summary,f,indent=2)
with root.joinpath('run.json').open('x') as f:json.dump(metadata,f,indent=2)
review=[]
for row,j in zip(rows,judgments,strict=True):
    review.append(f"{j['id']} {j['name']} [{j['group']}]")
    review.append('Input: '+row['case']['raw'])
    review.append('Expected additions: '+json.dumps(row['case']['expected_additions'],ensure_ascii=False))
    review.append('Actual additions: '+json.dumps(j['span_checks'],ensure_ascii=False))
    review.append('Unfiltered detector: '+json.dumps(row['unfiltered_detector_output'],ensure_ascii=False))
    review.append('Baseline unchanged: '+str(j['baseline_equal'])+'\n')
root.joinpath('review.txt').write_text('\n'.join(review)+'\n')
print(json.dumps(summary,indent=2))
