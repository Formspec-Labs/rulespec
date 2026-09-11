"""Use existing Core parity checks; retain each arm's verdicts and RDF terms."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import constraints_parity as parity

rows = []
for constraint, shape, fixture, expected in parity.FIXTURE_BINDINGS:
    if constraint != 'source-fragment':
        continue
    path = ROOT / fixture
    rows.append({'shape': shape, 'fixture': fixture, 'expected': expected,
                 'json_schema': parity.run_jsonschema(constraint, shape, path),
                 'shacl': parity.run_shacl(constraint, shape, path)})
numeric = ROOT / 'fixtures/negatives/xpath-selector-nonstring-value-negative.jsonld'
graph = parity.rdflib.Graph().parse(str(numeric), format='json-ld')
result = {'rows': rows, 'numeric_rdf_values': [value.n3() for value in graph.objects(
    predicate=parity.rdflib.RDF.value)], 'hashes': {str(path.relative_to(ROOT)):
    hashlib.sha256(path.read_bytes()).hexdigest() for path in (
        ROOT / 'tools/constraints_compile.py', ROOT / 'constraints/core/source-fragment.cue',
        ROOT / 'context/rkaf-context.jsonld', ROOT / 'compiled/shacl/core/source-fragment.ttl')}}
Path(sys.argv[1]).write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'rows': len(rows), 'mismatches': [row for row in rows
    if row['json_schema'] != row['expected'] or row['shacl'] != row['expected']],
    'numeric_rdf_values': result['numeric_rdf_values']}))
