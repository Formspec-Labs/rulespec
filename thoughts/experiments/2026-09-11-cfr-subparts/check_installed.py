"""Exercise both packaged commands outside the checkout on two real sources."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--output-dir', type=Path, required=True)
out = parser.parse_args().output_dir.resolve()
out.mkdir()  # Preserve prior runs, including failures.
cases = json.loads((HERE / 'cases.json').read_text())
commands = []
for case in (c for c in cases if c['id'] in ('ohio', 'ecfr-49-2')):
    directory = out / case['id']
    directory.mkdir()
    doc = prepare_document(case['raw'])
    run = {'id': 'urn:test:subpart-cli:' + case['id']}
    book = compile_candidates(doc, [], run)
    for name, value in [('document', doc), ('rulebook', book), ('run', run)]:
        (directory / (name + '.json')).write_text(json.dumps(value, indent=2))
    for name, args in [('references', ['references']), ('default', ['discovery-export']),
                       ('discovery', ['discovery-export', '--references'])]:
        argv = [str(Path(sys.executable).with_name('rulespec-understand')), *args,
                str(directory), '--output', str(directory / (name + '.json'))]
        result = subprocess.run(argv, cwd='/tmp', capture_output=True, text=True)
        commands.append({'argv': argv, 'returncode': result.returncode,
                         'stdout': result.stdout, 'stderr': result.stderr})
        (out / 'commands.json').write_text(json.dumps(commands, indent=2))
        result.check_returncode()
    read = lambda name: json.loads((directory / (name + '.json')).read_text())
    scan, default, enriched = read('references'), read('default'), read('discovery')
    shared = enriched.pop('reference_scan')
    for state in ('candidates', 'rejected'):
        for native, exported in zip(scan[state], shared[state], strict=True):
            assert 'evidence' not in exported
            for support, ref in zip(native['evidence'], exported['evidence_refs'], strict=True):
                assert (ref['id'], ref['roles']) == (support['fragment_id'], [support['field']])
                span = enriched['evidence'][ref['id']]
                assert doc['text'][span['start']:span['end']] == support['quote']
    enriched['evidence'] = {k: enriched['evidence'][k] for k in default['evidence']}
    assert enriched == default
    if case['id'] == 'ohio':
        assert [r['reading']['subpart'] for r in scan['candidates'] if 'subpart' in r.get('reading', {})] == ['E', 'F']
        assert not scan['rejected']
    else:
        assert [r['reading']['subpart'] for r in scan['rejected']] == ['A', 'E']
        assert {r['code'] for r in scan['rejected']} == {'cfr_ambiguous_part_scope'}
print('Passed six CLI calls from /tmp: alternatives, ambiguity, shared evidence and unchanged default records.')
print('Source captures with manually compiled empty rulebooks; no model output or semantic-accuracy claim.')
