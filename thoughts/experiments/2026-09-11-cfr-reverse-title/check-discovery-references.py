"""Correct the original CLI capture, which omitted --references; preserve it."""
import hashlib
import json
from pathlib import Path
import sys
import sysconfig

from refspec.registry import citation_grammar
from rulespec_extrapolator import cli

HERE = Path(__file__).resolve().parent
mode = sys.argv[1]
assert mode in {'baseline', 'source-final', 'isolated', 'working'}
out = HERE / mode


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


reader = Path(citation_grammar.__file__)
expected = json.loads((out / 'summary.json').read_text())['reader_sha256']
assert digest(reader) == expected
if mode != 'source-final':
    site = Path(sysconfig.get_paths()['purelib'])
    assert reader.is_relative_to(site) and Path(cli.__file__).is_relative_to(site)

original = json.loads((out / 'discovery.json').read_text())
assert 'reference_scan' not in original  # Retain the incomplete original check.
target = out / 'discovery-with-references.json'
args = ['discovery-export', str(out / 'run'), '--references', '--output', str(target)]
cli.main(args)
result = json.loads(target.read_text())
scan = result['reference_scan']
rows = [r for r in scan['candidates'] if r['kind'] == 'cfr']
reference_rows = json.loads((out / 'references.json').read_text())['candidates']
assert len(rows) == len(reference_rows) == 3 and not scan['rejected']
document = json.loads((out / 'run/document.json').read_text())
for row, reference in zip(rows, reference_rows, strict=True):
    assert (row['id'], row['value'], row['reading']) == (
        reference['id'], reference['value'], reference['reading'])
    support, = row['evidence_refs']
    evidence = result['evidence'][support['id']]
    assert document['text'][evidence['start']:evidence['end']] == row['value']
    assert support['roles'] == ['reference']
coordinates = [(r['reading']['cfr_title'], r['reading']['cfr_part'],
                r['reading']['cfr_section']) for r in rows]
assert coordinates == ([(29, None, None)] * 3 if mode == 'baseline' else [
    (29, '1910', None), (29, '1954', '3'), (29, '1910', None)])
if mode != 'baseline':
    assert rows[1]['reading']['pinpoint'] == ['d', '1', 'i']
    assert rows[0]['id'] != rows[2]['id']
receipt = {
    'mode': mode, 'python': sys.executable, 'cli_args': args,
    'reader_sha256': digest(reader), 'check_sha256': digest(Path(__file__)),
    'original_capture_omitted_references': True, 'reference_count': len(rows),
    'coordinates': coordinates, 'exact_source_evidence_checked': True,
    'output_sha256': digest(target), 'model_calls': 0,
}
with (out / 'discovery-references-check.json').open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
print(json.dumps(receipt))
