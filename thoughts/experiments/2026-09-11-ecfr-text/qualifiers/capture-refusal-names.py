"""Compare current output against original capture, allowing only refusal renames."""
from pathlib import Path
from dataclasses import asdict
import hashlib
import json
import sys

ROOT = Path('/Users/mikewolfd/Work/RefSpec')
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from refspec.registry.citation_grammar import find_cfr_citations, parse_cfr_citations, parse_authority_citation

original = json.loads((HERE / 'results.json').read_text())
renames = {'cfr_note_target_unresolved': 'note_target_unresolved',
           'cfr_open_ended_reference_unresolved': 'open_ended_reference_unresolved'}
changes = []
for row in original['results']:
    source = row['source']
    for field, callable_, refusal_key in [('after', find_cfr_citations, 'refusal'),
                                          ('authority_after', parse_authority_citation, 'cfr_refusal')]:
        expected = [dict(item) for item in row[field]]
        for item in expected:
            if item.get(refusal_key) in renames:
                item[refusal_key] = renames[item[refusal_key]]
        actual = json.loads(json.dumps([asdict(item) for item in callable_(source)]))
        assert actual == expected, (row['id'], field)
        if actual != row[field]:
            changes.append({'id': row['id'], 'field': field,
                            'refusals_before': [item.get(refusal_key) for item in row[field]],
                            'refusals_after': [item.get(refusal_key) for item in actual]})
    assert json.loads(json.dumps([asdict(item) for item in parse_cfr_citations(source)])) == row['identity_after']
paths = [ROOT / 'src/refspec/registry/citation_grammar.py',
         ROOT / 'tests/cfr_scope_tail_oracle.py', ROOT / 'tests/test_cfr_scope_tails.py']
receipt = [{'path': str(path), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]
report = {'comparison': 'Original saved results versus current source; only two upstream refusal names may differ.',
          'cases': len(original['results']), 'unlisted_differences': 0, 'identity_differences': 0,
          'renames': renames, 'source_freeze': receipt, 'changes': changes}
(HERE / 'refusal-name-followup.json').write_text(json.dumps(report, indent=2) + '\n')
(HERE / 'source-freeze-followup.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'cases': report['cases'], 'changed_records': len(changes), 'unlisted_differences': 0}))
