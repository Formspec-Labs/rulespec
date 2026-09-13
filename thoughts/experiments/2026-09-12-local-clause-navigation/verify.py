"""Verify the saved failure and unchanged controls through installed public code."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.context import export_context
from rulespec_extrapolator.references import scan_references

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-09-12-extractor-confidence'
OLD = HERE.parent / '2026-09-12-existing-qualification-links'


def save(name, value):
    path = HERE / name
    if path.exists():
        assert json.loads(path.read_text()) == value, name
    else:
        e._save(path, value)


def run():
    for name, expected in e._load(OLD / 'manifest.json')['artifacts_sha256'].items():
        assert sha256((OLD / name).read_bytes()).hexdigest() == expected, name
    runtime = {k: sha256(v.read_bytes()).hexdigest() for k, v in e._runtime_sources().items()}
    runtime['application/context.py'] = sha256(Path(export_context.__code__.co_filename).read_bytes()).hexdigest()
    save('runtime.json', {'versions': e._runtime_versions(), 'sources_sha256': runtime})
    results = []
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider call')):
        for case, selected in [('iep-1', (3, 4, 5, 6, 7)), ('lea-1', (0, 2, 7))]:
            path = BASE / f'decoded/{case}.json'
            input_digest = sha256(path.read_bytes()).hexdigest()
            book = e._load(path)['book']
            before = e._canonical(book)
            scan = scan_references(book['document'])
            assert scan == scan_references(book['document'])
            baseline = e._load(OLD / case / 'references.json')
            publisher = [r for r in scan['candidates'] if r['kind'] == 'publisher_reference']
            assert publisher == baseline['candidates']
            save(f'{case}/references.json', scan)
            contexts = []
            for index in selected:
                result = export_context(book, book['accepted'][index])
                assert result == export_context(book, book['accepted'][index])
                material = result['material']
                related_rows = [i for i, c in enumerate(book['accepted'])
                                if c['id'] in {r['id'] for r in material['related_claims']}]
                expected = ([6] if index in (4, 5) else [4, 5] if index == 6 else []) if case == 'iep-1' else []
                assert related_rows == expected, (case, index, related_rows)
                # This change assigns no semantic qualification links.
                assert all(not r['target_ids'] for r in material['related_claims'])
                save(f'{case}/material-R{index:03d}.json', material)
                contexts.append({'row': index, 'related_rows': related_rows,
                                 'context_sha256': e._digest(result), 'accounting': result['accounting']})
            assert e._canonical(book) == before
            assert sha256(path.read_bytes()).hexdigest() == input_digest
            results.append({'case': case, 'input_sha256': input_digest,
                'reference_scan_sha256': e._digest(scan),
                'resolution_counts': dict(Counter(r.get('resolution', {}).get('status') for r in scan['candidates'])),
                'refused_readings': [{'text': r['value'], 'code': r['code']} for r in scan['rejected']],
                'unchanged_publisher_readings': len(publisher), 'book_unchanged': True,
                'contexts': contexts})
    save('verification.json', {'provider_calls': 0, 'original_trace_manifest_unchanged': True, 'cases': results})
    print('Verified two reference scans and eight context exports twice; original books and trace unchanged; zero model calls.')


if __name__ == '__main__':
    run()
