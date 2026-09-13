"""Replay the saved read-only trace and constructed native-address controls."""
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.context import export_context
from rulespec_extrapolator.core import evidence_parts
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator.uslm import SourceIndex

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-09-12-extractor-confidence'


def verify():
    for name, expected in e._load(HERE / 'pretrace-pins.json').items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name
    checks = []
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider call')):
        for case in ('iep-1', 'lea-1'):
            book = e._load(BASE / f'decoded/{case}.json')['book']
            before = e._canonical(book)
            scan = scan_references(book['document'])
            assert scan == e._load(HERE / case / 'references.json')
            assert not any(c['target_ids'] for c in book['accepted'])
            summary = e._load(HERE / case / 'summary.json')
            for row in summary['contexts']:
                context = export_context(book, book['accepted'][row['row']])
                assert context == e._load(HERE / case / f'context-R{row["row"]:03d}.json')
            assert e._canonical(book) == before
            checks.append({'case': case, 'reference_replay_equal': True,
                           'context_replays_equal': len(summary['contexts']), 'book_unchanged': True})
        book = e._load(BASE / 'decoded/iep-1.json')['book']
        index = SourceIndex(book['document'])
        controls = e._load(HERE / 'manual-address-controls.json')
        assert controls['input_sha256'] == sha256((BASE / 'decoded/iep-1.json').read_bytes()).hexdigest()
        observed = []
        for link in controls['links']:
            path, node = index.identifiers[link['target']['value']][0]
            target = index.target(path, node)
            assert target == link['target']
            source = book['accepted'][6]
            assert link['reference_evidence'] == evidence_parts(book['document'], link['literal_reference'],
                'reference', within=(source['start'], source['end']))
            rows = [i for i, c in enumerate(book['accepted'])
                    if target['start'] <= c['start'] < c['end'] <= target['end']]
            assert rows == [r['row'] for r in link['contained_claims']]
            observed.extend(rows)
        assert observed == [4, 5]
        assert not set(controls['unrelated_claim_controls']).intersection(observed)
    result = {'provider_calls': 0, 'checks': checks, 'manual_lookup_matches': observed,
              'manual_lookup_controls_excluded': [3, 7], 'automatic_local_reference_discovery': False}
    destination = HERE / 'verification.json'
    if destination.exists():
        assert e._load(destination) == result
    else:
        e._save(destination, result)
    print('Verified two reference scans, eight context replays, two manual target lookups, and unchanged books; zero provider calls.')


if __name__ == '__main__':
    verify()
