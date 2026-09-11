"""Capture the real CLI path on pinned sources; no synthetic model output."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

from rulespec_extrapolator.core import build_graph, compile_candidates, validate_graph
from rulespec_extrapolator.uslm import read_uslm

HERE = Path(__file__).resolve().parent
output = Path(sys.argv[1]).resolve()
output.mkdir()
commands, reports = [], []
executable = str(Path(sys.executable).parent / 'rulespec-understand')


def save(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def run(*args):
    argv = [executable, *map(str, args)]
    result = subprocess.run(argv, cwd='/tmp', capture_output=True, text=True)
    commands.append({'argv': argv, 'returncode': result.returncode,
                     'stdout': result.stdout, 'stderr': result.stderr})
    (output / 'commands.json').write_text(json.dumps(commands, indent=2) + '\n')
    result.check_returncode()


for capture in ('title-05-s423.xml', 'title-42-s242c.xml', 'fresh-title-05-pair.xml'):
    source = HERE / capture if capture.startswith('fresh') else HERE.parent / '2026-09-11-uslm-source-links' / capture
    folder = output / source.stem
    folder.mkdir()
    run('prepare', source, '--output', folder / 'document.json')
    doc = json.loads((folder / 'document.json').read_text())
    assert doc['uslm_source']['xml'].encode('utf-8') == source.read_bytes()
    assert doc['text'] == (HERE / 'v2' / (source.stem + '.txt')).read_text()
    # An empty extraction is a declared fixture for source-only discovery.
    # It is not a provider response or evidence of extraction completeness.
    save(folder / 'run.json', {})
    save(folder / 'rulebook.json', compile_candidates(doc, [], {}))
    run('references', source, '--output', folder / 'references.json')
    run('references', folder / 'document.json', '--output', folder / 'prepared-references.json')
    scan = json.loads((folder / 'references.json').read_text())
    assert scan == json.loads((folder / 'prepared-references.json').read_text())
    run('discovery-export', folder, '--references', '--output', folder / 'discovery.json')
    discovery = json.loads((folder / 'discovery.json').read_text())
    nodes = read_uslm(doc)['nodes']
    publisher = [row for row in scan['candidates'] if row['kind'] == 'publisher_reference']
    assert len(publisher) == {'title-05-s423.xml': 30, 'title-42-s242c.xml': 40, 'fresh-title-05-pair.xml': 37}[capture]
    overlaps = []
    for row in scan['candidates'] + scan['rejected']:
        if row['kind'] == 'publisher_reference' or not row.get('evidence'):
            continue
        a = row['evidence'][0]
        for parent in publisher:
            path = scan['xml_fragments'][parent['xml_evidence_refs'][0]]['oa:hasSelector'][0]['rdf:value']
            node = nodes[path]
            if 'start' in node and a['start'] < node['end'] and node['start'] < a['end']:
                overlaps.append({'text': a['quote'], 'text_value': row['value'], 'publisher_value': parent['value'],
                                 'text_span': [a['start'], a['end']], 'publisher_span': [node['start'], node['end']]})
    original = {i for p in doc['source_map'] if p['kind'] == 'source' for i in range(p['start'], p['end'])}
    supported = {i for e in discovery['evidence'].values() for i in range(e['start'], e['end'])}
    assert original == supported
    graph = build_graph(doc, [], {})
    graph['@graph'].extend([scan['publisher_source'], *scan['xml_fragments'].values()])
    validation = validate_graph(graph)
    save(folder / 'xml-graph.json', graph)
    save(folder / 'validation.json', validation)
    assert validation['shacl_conforms']
    reports.append({'capture': capture, 'publisher_links': len(publisher),
        'contexts': dict(Counter(row['reading']['context'] for row in publisher)),
        'resolutions': dict(Counter(row['resolution']['status'] for row in publisher)),
        'shared_targets': len(scan['targets']), 'merged_text_readings': sum(len(row.get('text_readings', [])) for row in publisher),
        'merged_dispositions': dict(Counter(reading['disposition'] for row in publisher for reading in row.get('text_readings', []))),
        'remaining_text_candidates': len(scan['candidates']) - len(publisher), 'remaining_rejected': len(scan['rejected']),
        'residual_overlaps': overlaps, 'all_source_characters_preserved': True, 'shacl_conforms': True})
save(output / 'review.json', reports)
print(json.dumps(reports, indent=2))
