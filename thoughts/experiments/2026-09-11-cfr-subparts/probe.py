"""Capture native and application output on fixed sources; never overwrite."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from refspec.registry import citation_grammar as grammar
from rulespec_extrapolator import references
from rulespec_extrapolator.documents import prepare_document

HERE = Path(__file__).resolve().parent
args = argparse.ArgumentParser()
args.add_argument('--output', type=Path, required=True)
output = args.parse_args().output
cases = json.loads((HERE / 'cases.json').read_text())
result = {'provider_calls': 0, 'modules': {
    m.__name__: {'path': m.__file__, 'sha256': hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()}
    for m in (grammar, references)}, 'cases': {}}
for case in cases:
    raw = case['raw']
    result['cases'][case['id']] = {
        'identities': [asdict(x) for x in grammar.parse_cfr_citations(raw)],
        'occurrences': [asdict(x) for x in grammar.find_cfr_citations(raw)],
        'scan': references.scan_references(prepare_document(raw))}
with output.open('x') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
    f.write('\n')
print(f'Captured {len(cases)} fixed cases in {output}')
