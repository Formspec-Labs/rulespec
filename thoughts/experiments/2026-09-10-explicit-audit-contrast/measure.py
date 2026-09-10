"""Account for all saved calls and verify paired actual request settings."""
from datetime import datetime
from pathlib import Path
import runpy

from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent
design = e._load(ROOT / 'design.json')
extra = runpy.run_path(str(ROOT / 'experiment.py'))['EXTRA']
rows, requests = [], {}
cells = [{'id': name, 'case': name, 'arm': 'inventory', 'path': ROOT / 'inventories' / name}
         for name in design['cases']]
cells += [{**c, 'path': ROOT / 'cells' / c['id']} for c in design['cells']]
for cell in cells:
    path = cell['path']
    attempts = e._load(path / 'attempts.json')
    assert len(attempts) == 1
    attempt = attempts[0]
    request = e._load(path / attempt['request_file']) if attempt.get('request_file') else None
    response = e._load(path / attempt['response_file']) if attempt.get('response_file') else {}
    if cell['arm'] != 'inventory':
        requests[cell['case'], cell['arm']] = request
    usage = response.get('usage_metadata') or {}
    row = {k: cell[k] for k in ('id', 'case', 'arm')}
    row.update(status=attempt['status'], error=attempt.get('error_code'),
        model_version=response.get('model_version'),
        input_tokens=usage.get('prompt_token_count'), output_tokens=usage.get('candidates_token_count'),
        thinking_tokens=usage.get('thoughts_token_count'), total_tokens=usage.get('total_token_count'),
        started_at=attempt['started_at'], finished_at=attempt.get('finished_at'),
        request_sha256=e._digest(e._canonical(request)))
    if cell['arm'] != 'inventory':
        report = e._load(path / 'report.json')
        row.update(review_complete=report['review_complete'], report_status=report['status'],
                   audit_issues=report['audit_issues'])
    rows.append(row)
checks = {}
for name in design['cases']:
    left, right = requests[name, 'A'], requests[name, 'B']
    assert left and right
    assert {k:v for k,v in left.items() if k != 'contents'} == {k:v for k,v in right.items() if k != 'contents'}
    assert right['contents'].count(extra) == 1
    assert right['contents'].replace(extra, '', 1) == left['contents']
    checks[name] = 'Actual requests differ only by preregistered prompt addition'
totals = {}
for arm in ('inventory', 'A', 'B'):
    selected = [r for r in rows if r['arm'] == arm]
    totals[arm] = {key: sum(r[key] for r in selected) if all(r[key] is not None for r in selected) else None
                   for key in ('input_tokens', 'output_tokens', 'thinking_tokens', 'total_tokens')}
result = {'calls': rows, 'totals': totals, 'paired_request_checks': checks,
          'runtime_source_hashes': {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()},
          'limitation': 'Token counts are provider-reported; no price or invoice estimate is inferred.'}
e._save(ROOT / 'measurements.json', result)
print(e._canonical({'cells': [{k:r[k] for k in ('id','case','arm','output_tokens','thinking_tokens','total_tokens')}
                            for r in rows], 'totals': totals, 'paired_request_checks': checks}))
