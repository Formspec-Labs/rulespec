"""Verify runtime coverage and unchanged data against the sealed retention result."""
import hashlib
import json
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile

from rulespec_extrapolator import extraction as e

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent / '2026-09-11-extraction-retention'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def comparison_graph(graph, run):
    graph = deepcopy(graph)
    expected = e.core.NS + 'lineage:' + e.core.digest(run)
    lineage = [n for n in graph['@graph'] if n['@id'] == expected]
    assert len(lineage) == 1 and lineage[0]['@type'] == 'rkaf:AILineage'
    lineage[0]['@id'] = 'urn:comparison:recorded-run-lineage'
    for node in graph['@graph']:
        if node.get('rkaf:hasAILineage') == expected:
            node['rkaf:hasAILineage'] = 'urn:comparison:recorded-run-lineage'
    return graph


stage = __import__('sys').argv[1]
assert stage in {'isolated', 'working'}
site_names = ['reference-integration-20260911-capture']
if stage == 'working':
    site_names.append('document-poc-venv')
sites = [next((ROOT / '.tools' / name / 'lib').glob('python*/site-packages')) for name in site_names]
packages, source_files = {}, {}
for wheel in read(HERE / 'wheel-inputs.json'):
    path = Path(wheel['path'])
    assert sha(path) == wheel['sha256'], path
    with ZipFile(path) as archive:
        for name in archive.namelist():
            if name.endswith('/') or '.dist-info/' in name or '.data/' in name:
                continue
            digest = hashlib.sha256(archive.read(name)).hexdigest()
            assert all(sha(site / name) == digest for site in sites), name
            packages[name] = digest
            if name.startswith('rulespec_extrapolator/') and '/_data/' not in name:
                assert sha(ROOT / 'packages/rulespec-extrapolator/src' / name) == digest, name
                source_files[name] = digest

before = read(HERE / 'baseline.json')
now = {name: sha(path) for name, path in e._runtime_sources().items()}
assert set(before['source_hashes']) <= set(now)
assert [name for name, digest in before['source_hashes'].items() if now[name] != digest] == ['application/extraction.py']
added = {name: digest for name, digest in now.items() if name not in before['source_hashes']}
assert len(added) == 11, added
assert e._runtime_versions()['packages'].items() >= before['runtime']['packages'].items()
assert set(e._runtime_versions()['packages']) - set(before['runtime']['packages']) == {'refspec', 'spicysearch'}
current = HERE / 'cli-isolated'
prior = PREVIOUS / 'cli-isolated-retry'
for name in ('candidates.json', 'refusals.json'):
    assert (current / 'reprocessed' / name).read_bytes() == (prior / 'reprocessed' / name).read_bytes(), name
for name in ('references.json', 'discovery-export.json'):
    assert (current / name).read_bytes() == (prior / name).read_bytes(), name
old_review, new_review = read(prior / 'export.json'), read(current / 'export.json')
assert {k: v for k, v in old_review.items() if k not in {'run', 'graph'}} == {k: v for k, v in new_review.items() if k not in {'run', 'graph'}}
old_graph = comparison_graph(old_review['graph'], old_review['run'])
assert old_graph == comparison_graph(new_review['graph'], new_review['run'])
# The comparison may substitute the expected ID only, not mask changed provenance
# content or source evidence. Keep both guards independent of production validation.
mutated = deepcopy(new_review['graph'])
next(n for n in mutated['@graph'] if n['@type'] == 'rkaf:AILineage')['rkaf:modelId'] = 'changed model'
assert old_graph != comparison_graph(mutated, new_review['run'])
mutated = deepcopy(new_review['graph'])
fragment = next(n for n in mutated['@graph'] if n['@type'] == 'rkaf:SourceFragment')
next(s for s in fragment['oa:hasSelector'] if 'oa:exact' in s)['oa:exact'] = 'fabricated source'
assert old_graph != comparison_graph(mutated, new_review['run'])
assert read(current / 'reprocessed/rulebook.json') == read(current / 'replayed/rulebook.json')
run = read(current / 'reprocessed/run.json')
assert run['reprocessing']['provider_calls'] == 0
assert all(run['fingerprints']['sources_sha256'][key] == digest for key, digest in added.items())
for name, digest in read(PREVIOUS / 'manifest.json')['files'].items():
    assert sha(PREVIOUS / name) == digest, name
for mode in (['isolated'] if stage == 'isolated' else ['isolated', 'working']):
    receipt = read(HERE / (mode + '-delivery-command.json'))
    assert receipt['status'] == 'passed' and all(c['returncode'] == 0 for c in receipt['commands'])
if stage == 'working':
    for name in ('references.json', 'discovery-export.json', 'export.json', 'usage.log'):
        assert (current / name).read_bytes() == (HERE / 'cli-working' / name).read_bytes(), name
result = {'status': 'passed', 'stage': stage, 'package_files': packages, 'source_files': source_files,
          'additional_runtime_sources': added, 'runtime': e._runtime_versions(),
          'candidates_refusals_unchanged': True, 'discovery_references_unchanged': True,
          'graph_unchanged_except_recorded_lineage_id': True,
          'lineage_comparison_negative_controls_pass': True,
          'review_unchanged_except_run_and_lineage': True, 'prior_manifest_sha256': sha(PREVIOUS / 'manifest.json')}
(HERE / (stage + '-checks.json')).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': 'passed', 'stage': stage, 'additional_sources': list(added)}))
