"""Verify evidence-export parity; this does not repeat the model experiment."""
import json
from pathlib import Path
import sys

from rulespec_extrapolator.context import export_context, resolve_context
from rulespec_extrapolator.core import digest

root = Path(__file__).resolve().parent
design = json.loads((root/'design.json').read_text())
rows = []
for case in json.loads((root/'cases.json').read_text()):
    current = export_context(case['book'], case['focus'], reference_sources=case['reference_sources'])
    cell = next(c for c in design['cells'] if c['case'] == case['id'] and c['arm'] == 'B')
    old = json.loads((root/'inputs'/f"{cell['id']}.json").read_text())
    old_material = old['material']
    for source in old_material['sources'].values():
        # Production keeps source metadata once, in material.source_metadata.
        source.pop('metadata')
    current_material = current['material'].copy()
    assert current_material['source_roles'][0]['role'] == 'focus'
    current_material['source_roles'] = current_material['source_roles'][1:]
    assert current_material == old_material, case['id']
    count = 0
    for alias, source in current['material']['sources'].items():
        for key in source['passages']:
            span = resolve_context({'source': alias, 'passage': key}, current)
            assert span['quote'] == old['catalogs'][alias]['passages'][key]['text']
            count += 1
    rows.append({'case': case['id'], 'export_sha256': digest(current), 'grounded_passages': count,
                 'material_equal_except_focus_role_and_metadata_deduplication': True})
    if len(sys.argv) > 1:
        directory = Path(sys.argv[1]); directory.mkdir(parents=True, exist_ok=True)
        with (directory/(case['id']+'.json')).open('x') as f:
            json.dump(current, f, ensure_ascii=False, indent=2); f.write('\n')
print(json.dumps({'provider_calls': 0, 'cases': rows}, indent=2))
