"""Check saved-response replay, unchanged claims/reviews and captured reader bytes."""
from copy import deepcopy
import json
from pathlib import Path
import sys

from rulespec_extrapolator.core import NS, digest

HERE = Path(__file__).resolve().parent
attempt = HERE / ('cli-' + sys.argv[1])
previous = HERE.parent / '2026-09-11-reader-runtime-capture/cli-isolated'


def read(path):
    return json.loads(path.read_text())


def comparison_graph(graph, run):
    graph = deepcopy(graph)
    identity = NS + 'lineage:' + digest(run)
    lineage, = [n for n in graph['@graph'] if n['@id'] == identity]
    assert lineage['@type'] == 'rkaf:AILineage'
    lineage['@id'] = 'urn:comparison:recorded-run-lineage'
    for node in graph['@graph']:
        if node.get('rkaf:hasAILineage') == identity:
            node['rkaf:hasAILineage'] = 'urn:comparison:recorded-run-lineage'
    return graph


for name in ('candidates.json', 'refusals.json'):
    assert (attempt / 'reprocessed' / name).read_bytes() == (previous / 'reprocessed' / name).read_bytes(), name
assert read(attempt / 'reprocessed/rulebook.json') == read(attempt / 'replayed/rulebook.json')
before, after = read(previous / 'export.json'), read(attempt / 'export.json')
assert {k: v for k, v in before.items() if k not in ('run', 'graph')} == {
    k: v for k, v in after.items() if k not in ('run', 'graph')}
expected_graph = comparison_graph(before['graph'], before['run'])
assert comparison_graph(after['graph'], after['run']) == expected_graph
mutation = deepcopy(after['graph'])
next(n for n in mutation['@graph'] if n['@type'] == 'rkaf:AILineage')['rkaf:modelId'] = 'changed model'
assert comparison_graph(mutation, after['run']) != expected_graph
mutation = deepcopy(after['graph'])
fragment = next(n for n in mutation['@graph'] if n['@type'] == 'rkaf:SourceFragment')
next(s for s in fragment['oa:hasSelector'] if 'oa:exact' in s)['oa:exact'] = 'fabricated source'
assert comparison_graph(mutation, after['run']) != expected_graph
run = read(attempt / 'reprocessed/run.json')
assert run['reprocessing']['provider_calls'] == 0
sources = read(HERE / (sys.argv[1] + '-packages.json'))['source_hashes']
assert run['fingerprints']['sources_sha256'] == sources
assert all(c['returncode'] == 0 for c in read(attempt / 'commands.json'))

if len(sys.argv) > 2:
    working = HERE / ('cli-' + sys.argv[2])
    for name in ('references.json', 'discovery-export.json', 'export.json', 'usage.log'):
        assert (attempt / name).read_bytes() == (working / name).read_bytes(), name
    assert all(c['returncode'] == 0 for c in read(working / 'commands.json'))

result = {'status': 'passed', 'attempt': sys.argv[1], 'working': sys.argv[2] if len(sys.argv) > 2 else None,
          'candidates_and_refusals_unchanged': True, 'review_unchanged_except_recorded_run': True,
          'graph_unchanged_except_recorded_lineage_id': True, 'negative_lineage_controls_pass': True,
          'exact_replay': True, 'captured_sources_match_installed': True, 'provider_calls': 0}
path = HERE / ('run-checks-' + '-'.join(sys.argv[1:]) + '.json')
with path.open('x') as stream:
    json.dump(result, stream, indent=2)
    stream.write('\n')
print(json.dumps(result))
