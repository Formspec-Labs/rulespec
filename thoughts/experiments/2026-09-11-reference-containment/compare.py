"""Compare both application policies, preserving native/raw and discovery output."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys

from rulespec_extrapolator import uslm
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import load_document
from rulespec_extrapolator.references import scan_references

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=False)
spec = importlib.util.spec_from_file_location('rulespec_extrapolator._containment_baseline', HERE / 'uslm_before.py')
baseline = importlib.util.module_from_spec(spec); spec.loader.exec_module(baseline)
candidate = uslm.attach_publisher_links


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def normalized(scan):
    """Remove association only: every native reading and its disposition remains."""
    result = deepcopy(scan)
    text = []
    publisher = []
    for group in ('candidates', 'rejected'):
        for row in result.pop(group):
            if row['kind'] == 'publisher_reference':
                text.extend(row.pop('text_readings', []))
                publisher.append(row)
            else:
                text.append({'disposition': group, **row})
    for row in text:
        row.pop('id', None); row.pop('record_ids', None)
    result['publisher'] = publisher
    result['text'] = sorted(text, key=lambda r: json.dumps(r, sort_keys=True))
    return result


cases = json.loads((ROOT / 'packages/rulespec-extrapolator/tests/fixtures/uslm/containment.json').read_text())
prepared = [(case['id'], uslm.prepare_uslm('<uscDoc xmlns="http://xml.house.gov/schemas/uslm/1.0" identifier="/us/usc/t5"><section identifier="/us/usc/t5/s1">' + case['body'] + '</section></uscDoc>'), case) for case in cases]
for path in (HERE.parent / '2026-09-11-uslm-source-links/title-05-s423.xml',
             HERE.parent / '2026-09-11-uslm-source-links/title-42-s242c.xml',
             HERE.parent / '2026-09-11-uslm-readable-text/fresh-title-05-pair.xml'):
    prepared.append((path.stem, load_document(path), None))

reports = []
try:
    for name, doc, expected in prepared:
        results = {}
        for arm, method in (('A', baseline.attach_publisher_links), ('B', candidate)):
            uslm.attach_publisher_links = method
            scan = scan_references(doc)
            discovery = export_discovery({'document': doc, 'accepted': []}, include_references=True)
            save(f'{name}-{arm}-scan.json', scan)
            save(f'{name}-{arm}-discovery.json', discovery)
            results[arm] = (scan, discovery)
        a, b = results['A'][0], results['B'][0]
        publisher = [r for r in b['candidates'] if r['kind'] == 'publisher_reference']
        associated = sum(len(r.get('text_readings', [])) for r in publisher)
        separate = sum(r['kind'] != 'publisher_reference' for r in b['candidates'] + b['rejected'])
        # Independent test-only full scan oracle: XML reference intervals alone
        # determine unique containment, irrespective of normalized identifiers.
        nodes = uslm.read_uslm(doc)['nodes']
        intervals = [nodes[b['xml_fragments'][r['xml_evidence_refs'][0]]['oa:hasSelector'][0]['rdf:value']] for r in publisher]
        oracle_count = 0
        oracle_owners = {}
        for row in normalized(b)['text']:
            if row.get('evidence'):
                support = row['evidence'][0]
                count = sum('start' in n and n['start'] <= support['start'] and support['end'] <= n['end'] for n in intervals)
                oracle_count += count == 1
                oracle_owners[json.dumps(row, sort_keys=True)] = [parent['id'] for parent, node in zip(publisher, intervals, strict=True)
                    if 'start' in node and node['start'] <= support['start'] and support['end'] <= node['end']]
        owners_agree = all(oracle_owners[json.dumps(row, sort_keys=True)] == [parent['id']]
                           for parent in publisher for row in parent.get('text_readings', []))
        report = {'id': name, 'associated_a': sum(len(r.get('text_readings', [])) for r in a['candidates']),
                  'associated_b': associated, 'separate_b': separate,
                  'all_native_readings_preserved': normalized(a) == normalized(b),
                  'shared_discovery_evidence_unchanged': results['A'][1]['evidence'] == results['B'][1]['evidence'],
                  'independent_containment_oracle_agrees': oracle_count == associated and owners_agree,
                  'declared_control_passes': expected is None or (associated, separate) == (expected['associated'], expected['separate'])}
        reports.append(report)
finally:
    uslm.attach_publisher_links = candidate
save('reports.json', reports)
source_reports = [r for r in reports if r['id'] in {'title-05-s423', 'title-42-s242c', 'fresh-title-05-pair'}]
checks = {key: all(r[key] for r in reports) for key in ('all_native_readings_preserved', 'shared_discovery_evidence_unchanged', 'independent_containment_oracle_agrees', 'declared_control_passes')}
checks['four_real_associations_added'] = sum(r['associated_b'] - r['associated_a'] for r in source_reports) == 4
save('checks.json', checks)
print(json.dumps({'checks': checks, 'sources': source_reports}, indent=2))
if not all(checks.values()): raise SystemExit(1)
