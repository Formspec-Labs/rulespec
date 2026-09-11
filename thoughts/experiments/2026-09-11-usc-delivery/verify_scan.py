"""Compare the existing adapter and native fields; no provider calls or labels inferred."""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

from refspec.registry import citation_grammar as grammar
from rulespec_extrapolator.core import sparse
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.extraction import _runtime_sources, _runtime_versions
from rulespec_extrapolator.references import scan_references

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / sys.argv[1]
OUTPUT.mkdir(exist_ok=False)


def write(name, value):
    with (OUTPUT / name).open('x') as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write('\n')


baseline = json.loads((HERE / 'baseline.json').read_text())
scans, totals = [], {'accepted': 0, 'rejected': 0}
for case in baseline:
    doc = case['document']
    book = {'document': doc, 'accepted': []}
    original = deepcopy(book)
    scan = scan_references(doc)
    exported = export_discovery(book, include_references=True)
    assert scan_references(doc) == scan
    assert export_discovery(book) == case['default_discovery']
    assert book == original
    for group in ('candidates', 'rejected'):
        assert [r for r in scan[group] if r['kind'] != 'usc'] == case['scan'][group]
    rows = sorted([r for group in ('candidates', 'rejected') for r in scan[group] if r['kind'] == 'usc'],
                  key=lambda r: (r['evidence'][0]['start'], r['evidence'][0]['end']))
    native = grammar.find_usc_citations(doc['text'])
    assert len(rows) == len(native)
    for row, match in zip(rows, native, strict=True):
        expected = sparse(asdict(match.citation))
        for field in ('pinpoint', 'range_end_pinpoint', 'subchapter', 'subchapter_end'):
            value = getattr(match, field)
            if value:
                expected[field] = list(value) if isinstance(value, tuple) else value
        assert row['reading'] == expected
        assert row['value'] == match.text
        primary = row['evidence'][0]
        assert (primary['start'], primary['end'], primary['quote']) == (match.start, match.end, match.text)
        assert doc['text'][primary['start']:primary['end']] == primary['quote']
        assert row.get('code') == match.refusal
        if match.context_start is not None:
            context = row['evidence'][1]
            assert (context['start'], context['end']) == (match.context_start, match.context_end)
            assert context['quote'] == doc['text'][match.context_start:match.context_end]
        else:
            assert len(row['evidence']) == 1
        group = 'rejected' if match.refusal else 'candidates'
        saved, = [r for r in exported['reference_scan'][group] if r['kind'] == 'usc'
                  and exported['evidence'][r['evidence_refs'][0]['id']]['start'] == match.start]
        assert saved['reading'] == row['reading'] and saved.get('code') == match.refusal
        totals['rejected' if match.refusal else 'accepted'] += 1
    scans.append({'id': case['id'], 'scan': scan, 'discovery': exported})
write('scans.json', scans)

publisher = json.loads((HERE / 'baseline-uslm.json').read_text())
scan = scan_references(publisher['document'])
# Full native USC observations may be associated with existing publisher links.
# Removing ONLY the new kind must recover all previous candidate/rejection data.
def previous_readings(rows):
    result = []
    for original in rows:
        if original['kind'] == 'usc':
            continue
        row = deepcopy(original)
        if 'text_readings' in row:
            row['text_readings'] = [r for r in row['text_readings'] if r['kind'] != 'usc']
            if not row['text_readings']:
                row.pop('text_readings')
        result.append(row)
    return result

for group in ('candidates', 'rejected'):
    assert previous_readings(scan[group]) == publisher['scan'][group]
for key in ('targets', 'xml_fragments', 'publisher_source'):
    assert scan[key] == publisher['scan'][key]
write('publisher.json', scan)
write('checks.json', {'status': 'passed', 'cases': len(baseline), 'usc_occurrences': totals,
      'native_fields_and_refusals_retained': True, 'other_families_unchanged': True,
      'default_discovery_unchanged': True, 'publisher_targets_unchanged': True,
      'exact_replay': True, 'runtime': _runtime_versions(),
      'source_hashes': {name: hashlib.sha256(path.read_bytes()).hexdigest()
                        for name, path in _runtime_sources().items()}})
print(json.dumps({'status': 'passed', 'cases': len(baseline), 'usc_occurrences': totals}))
