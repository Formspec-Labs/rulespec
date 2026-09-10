"""Account for every captured relationship and comparison call."""
from pathlib import Path
from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent
design = e._load(ROOT / 'design.json')
cells = [{'id': name, 'case': name, 'arm': 'relationships',
          'path': ROOT / 'relationships' / name} for name in design['cases']]
cells += [{**c, 'path': ROOT / 'cells' / c['id']} for c in design['cells']]
rows = []
for cell in cells:
    path = cell['path']
    attempt, = e._load(path / 'attempts.json')
    response = e._load(path / attempt['response_file']) if attempt.get('response_file') else {}
    usage = response.get('usage_metadata') or {}
    row = {k:cell[k] for k in ('id','case','arm')}
    row.update(status=attempt['status'], error=attempt.get('error_code'),
        model_version=response.get('model_version'),
        input_tokens=usage.get('prompt_token_count'), output_tokens=usage.get('candidates_token_count'),
        thinking_tokens=usage.get('thoughts_token_count'), total_tokens=usage.get('total_token_count'),
        started_at=attempt['started_at'], finished_at=attempt.get('finished_at'))
    if cell['arm'] == 'relationships':
        decoded = e._load(path / 'decoded.json')
        row.update(decoded_proposals=len(decoded['proposals']), issues=decoded['issues'])
    else:
        report = e._load(path / 'report.json')
        row.update(review_complete=report['review_complete'], report_status=report['status'],
                   audit_issues=report['audit_issues'])
    rows.append(row)
groups = {'A':['A'], 'B_audit_only':['B'], 'relationship_stage':['relationships'],
          'B_with_relationships':['relationships','B']}
totals = {}
for group, arms in groups.items():
    selected = [r for r in rows if r['arm'] in arms]
    totals[group] = {key: sum(r[key] for r in selected) if all(r[key] is not None for r in selected) else None
                    for key in ('input_tokens','output_tokens','thinking_tokens','total_tokens')}
e._save(ROOT / 'measurements.json', {'calls': rows, 'totals': totals,
    'paired_request_checks': e._load(ROOT / 'request-checks.json'),
    'limitation': 'Provider-reported tokens; missing values remain unknown, not zero. No monetary estimate.'})
print(e._canonical({'calls': [{k:r[k] for k in ('id','arm','output_tokens','total_tokens')} for r in rows],
                   'totals': totals}))
