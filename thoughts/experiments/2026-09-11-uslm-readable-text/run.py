"""Freeze preparation outputs and check coordinates against source text."""
from collections import Counter
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from refspec.registry.uslm import iter_edges
from rulespec_extrapolator.core import _evidence
from rulespec_extrapolator.discovery import export_discovery
from prepare import prepare

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / '2026-09-11-uslm-source-links'
parser = argparse.ArgumentParser()
parser.add_argument('--label')
args = parser.parse_args()
OUTPUT = HERE / args.label if args.label else HERE
if args.label:
    OUTPUT.mkdir()


def save(name, value):
    with (OUTPUT / name).open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


cases = [(PRIOR / 'title-05-s423.xml', '05'), (PRIOR / 'title-42-s242c.xml', '42'),
         (HERE / 'fresh-title-05-pair.xml', '05')]
baseline = []
for path, title in cases:
    xml = path.read_bytes()
    skipped = Counter()
    baseline.append({'capture': str(path), 'title': title,
                     'text': ''.join(ET.fromstring(xml).itertext()),
                     'references': list(iter_edges(xml, title, skipped, include_source_path=True)),
                     'skipped': dict(skipped)})
save('baseline.json', baseline)
outputs, reports = [], []
for case in baseline:
    result = prepare(Path(case['capture']).read_bytes(), title=Path(case['capture']).stem)
    document, original = result['document'], result['source_text']
    assert original == case['text']
    parts = [p for p in document['source_map'] if p['kind'] == 'source']
    assert ''.join(document['text'][p['start']:p['end']] for p in parts) == original
    assert all(document['text'][p['start']:p['end']] == original[p['source_start']:p['source_end']] for p in parts)
    references = []
    for row in case['references']:
        node = result['nodes'][row['sourceXPath']]
        quote = original[node['source_start']:node['source_end']]
        prepared_quote = document['text'][node['start']:node['end']] if quote else ''
        assert prepared_quote == quote, (case['capture'], row, quote, prepared_quote)
        if quote:
            assert _evidence(document, quote, 'reference', node['start'], node['end'])
        targets = [dict(sourceXPath=path, **n) for path, n in result['nodes'].items()
                   if n.get('identifier') == row['href']]
        references.append({'reading': row, 'location': node, 'targets': targets})
    result['references'] = references
    result['capture'] = case['capture']
    outputs.append(result)
    discovery = export_discovery({'document': document, 'accepted': []})
    supported = {i for e in discovery['evidence'].values() for i in range(e['start'], e['end'])}
    expected = {i for p in parts for i in range(p['start'], p['end'])}
    assert supported == expected
    reports.append({'capture': Path(case['capture']).name,
                    'original_characters': len(original), 'prepared_characters': len(document['text']),
                    'references': len(references), 'reference_text_preserved': True,
                    'locally_located_targets': sum(len(r['targets']) == 1 for r in references),
                    'operative_located_targets': sum(len(r['targets']) == 1 and r['reading']['context'] == 'operative' for r in references),
                    'discovery_preserves_all_original_characters': True,
                    'discovery_includes_inserted_characters_as_evidence': False})
    with (OUTPUT / (Path(case['capture']).stem + '.txt')).open('x') as f:
        f.write(document['text'])
save('prepared.json', outputs)
save('mechanical-results.json', reports)
print(json.dumps(reports, indent=2))
