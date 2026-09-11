"""Replay the bounded source-tail comparison; no network or model calls."""
import hashlib
import json
from dataclasses import asdict
from pathlib import Path
import sys

ROOT = Path('/Users/mikewolfd/Work/RefSpec')
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
from refspec.registry.citation_grammar import find_cfr_citations, parse_cfr_citations, parse_authority_citation
from cfr_scope_tail_oracle import find_cfr_citations as old_find, parse_cfr_citations as old_parse
from test_cfr_scope_tails import TAILS, ANCHORS, NEGATIVE_TAILS, SAVED

cases = [(name + ':' + anchor, anchor + tail, True)
         for name, (tail, _) in TAILS.items() for anchor in ANCHORS]
cases += [('prose:' + str(n), '49 CFR 390.5' + tail, False) for n, tail in enumerate(NEGATIVE_TAILS)]
cases += [('note-before-paragraph', '49 CFR 390.5 note\n\nThat provision has a separate context.', True)]
cases += [('publisher:' + name, text, False) for name, text in SAVED]
rows = []
for name, text, expected_difference in cases:
    before = [asdict(row) for row in old_find(text)]
    after = [asdict(row) for row in find_cfr_citations(text)]
    assert (before != after) == expected_difference, name
    old_identity = [asdict(row) for row in old_parse(text)]
    identity = [asdict(row) for row in parse_cfr_citations(text)]
    assert old_identity == identity, name
    rows.append({'id': name, 'source': text, 'expected_source_difference': expected_difference,
                 'before': before, 'after': after, 'identity_before': old_identity,
                 'identity_after': identity,
                 'authority_after': [asdict(row) for row in parse_authority_citation(text)]})
paths = [ROOT / 'src/refspec/registry/citation_grammar.py',
         ROOT / 'tests/cfr_scope_tail_oracle.py', ROOT / 'tests/test_cfr_scope_tails.py']
receipt = [{'path': str(path), 'bytes': path.stat().st_size,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in paths]
HERE.joinpath('results.json').write_text(json.dumps({'cases': len(rows),
    'intentional_source_differences': sum(row['before'] != row['after'] for row in rows),
    'identity_differences': 0, 'source_freeze': receipt, 'results': rows}, indent=2) + '\n')
HERE.joinpath('source-freeze.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'cases': len(rows), 'intentional_source_differences': sum(row['before'] != row['after'] for row in rows), 'identity_differences': 0}))
