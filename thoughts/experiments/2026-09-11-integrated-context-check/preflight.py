"""Mechanical bridge checks, without provider calls."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from context import build, resolve, source_key
from experiment import ROOT, REPO, e
from rulespec_extrapolator.core import canonical, compile_candidates
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore
from rulespec_extrapolator.uslm import prepare_xml

cases = e._load(ROOT/'cases.json')
design = e._load(ROOT/'design.json')
count = 0
for cell in design['cells']:
    data = e._load(ROOT/'inputs'/f"{cell['id']}.json")
    case = next(c for c in cases if c['id'] == cell['case'])
    before = canonical(case)
    assert build(case['book'], case['focus'], integrated=cell['arm'] == 'B',
                 reference_sources=case['reference_sources']) == data
    assert canonical(case) == before
    for alias, catalog in data['catalogs'].items():
        for key in catalog['passages']:
            span = resolve({'source': alias, 'passage': key}, data['catalogs'])
            assert span['quote'] == catalog['document']['text'][span['start']:span['end']]
            count += 1

c = cases[3]
b = build(c['book'], c['focus'], integrated=True, reference_sources=c['reference_sources'])
decisions = [r for r in b['material']['selection_decisions'] if r['role'] == 'reference_target']
assert len(decisions) == 2 and decisions[1]['status'] == 'already_supplied'
assert decisions[0]['occurrence_id'] != decisions[1]['occurrence_id']
zero = build(c['book'], c['focus'], integrated=True, reference_sources=c['reference_sources'], extra_chars=0)
assert len(zero['catalogs']) == 1 and zero['unique_chars'] == zero['baseline_chars']
assert any(r['status'] == 'over_budget' for r in zero['material']['selection_decisions'])
missing = build(c['book'], c['focus'], integrated=True)
assert len(missing['catalogs']) == 1 and len(missing['material']['reference_readings']) == 2
c = cases[-1]
ambiguous = build(c['book'], c['focus'], integrated=True, reference_sources=c['reference_sources'])
assert len(ambiguous['catalogs']) == 1 and len(ambiguous['material']['recorded_feedback']) == 1
assert source_key(c['reference_sources'][0]) != source_key(c['reference_sources'][1])
# XML comments change original source identity while preserving visible text/positions.
x = c['reference_sources'][0]
raw = x['uslm_source']['xml']
y = prepare_xml(raw.replace('</uscDoc>', '<!-- Constructed identity control --></uscDoc>'))
assert x['text'] == y['text'] and source_key(x) != source_key(y)
catalog = b['catalogs']['S1']['passages']
separate = {alias: {'source_id': source_key(doc), 'document': doc, 'passages': catalog}
            for alias, doc in [('S0', x), ('S1', y)]}
key = next(iter(catalog))
left, right = [resolve({'source': alias, 'passage': key}, separate) for alias in separate]
assert left['quote'] == right['quote'] and left['start'] == right['start']
assert left['source_id'] != right['source_id']

sys.path.insert(0, str(REPO/'packages/rulespec-extrapolator/tests'))
from test_discovery_source_map import mapped_document
doc = mapped_document([('source', 'Staff must:'), ('inserted', '\n\n'), ('source', 'log requests.')])
catalog = e.passage_catalog(doc, {'start': 0, 'end': len(doc['text']), 'context_spans': []})
keys = list(catalog)
span = resolve({'source': 'S0', 'passage': keys[0]+':'+keys[-1]},
               {'S0': {'source_id': doc['id'], 'document': doc, 'passages': catalog}})
assert span['quote'] == doc['text'] and len(span['evidence']) == 2
doc = prepare_document('First unless closed Last')
try:
    resolve({'source': 'S0', 'passage': 'F000:F001'}, {'S0': {
        'source_id': doc['id'], 'document': doc,
        'passages': {'F000': {'start': 0, 'end': 5}, 'F001': {'start': 20, 'end': 24}}}})
except ValueError:
    pass
else:
    raise AssertionError('Unseen source content admitted')

with tempfile.TemporaryDirectory() as temp:
    directory = Path(temp)
    book = compile_candidates(c['book']['document'], [], {})
    for name, value in [('document.json', book['document']), ('rulebook.json', book), ('run.json', {})]:
        (directory/name).write_text(canonical(value))
    original = (directory/'rulebook.json').read_bytes()
    store = ReviewStore(directory)
    store.apply({'action': 'observe', 'expected_revision': 0, 'actor': 'Constructed control',
                 'actor_kind': 'aiAgent', 'targets': [], 'rationale': 'Experimental feedback control.',
                 'observations': c['book']['enrichment_issues']})
    reloaded = ReviewStore(directory).snapshot()
    rebuilt = build(reloaded, c['focus'], integrated=True, reference_sources=c['reference_sources'])
    assert rebuilt['material']['recorded_feedback'] == ambiguous['material']['recorded_feedback']
    assert not reloaded['accepted'] and not reloaded['attestations']
    assert (directory/'rulebook.json').read_bytes() == original

probe = 'from rulespec_extrapolator import extraction as e; import json; print(json.dumps({n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}))'
env = dict(os.environ); env.pop('PYTHONPATH', None)
installed = json.loads(subprocess.check_output([sys.executable, '-c', probe], env=env, text=True))
current = {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()}
assert current == installed, [k for k in current if current[k] != installed.get(k)]
receipt = {'provider_calls': 0, 'passages_grounded': count, 'runtime_files_equal': len(current),
           'frozen_inputs_reproduced': True, 'repeated_targets_deduplicated': True,
           'budget_missing_ambiguous_targets_checked': True, 'separate_sources_same_positions_checked': True,
           'inserted_whitespace_and_unseen_gap_checked': True, 'feedback_reload_original_unchanged': True}
print(json.dumps(receipt, indent=2))
