"""Read-only trace of native references, current claim spans and context export."""
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
from unittest.mock import patch

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.context import export_context
from rulespec_extrapolator.references import scan_references

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-09-12-extractor-confidence'


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as out:
        json.dump(value, out, ensure_ascii=False, indent=2, allow_nan=False)
        out.write('\n')


def run():
    paths = [HERE / 'PLAN.md', Path(__file__)]
    paths += [BASE / f'decoded/{case}.json' for case in ('iep-1', 'lea-1')]
    paths += list(e._runtime_sources().values())
    save('pretrace-pins.json', {os.path.relpath(p, HERE): sha256(p.read_bytes()).hexdigest() for p in paths})
    save('runtime.json', e._runtime_versions())
    summaries = []
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider call')):
        for case in ('iep-1', 'lea-1'):
            book = e._load(BASE / f'decoded/{case}.json')['book']
            before = e._canonical(book)
            doc, claims = book['document'], book['accepted']
            scan = scan_references(doc)
            save(f'{case}/references.json', scan)
            associations = []
            for occurrence in scan['candidates']:
                resolution = occurrence.get('resolution', {})
                owner_rows = [i for i, c in enumerate(claims) if any(
                    c['start'] <= ev['start'] < ev['end'] <= c['end']
                    for ev in occurrence.get('evidence', []))]
                for target_id in resolution.get('target_ids', []):
                    target = scan.get('targets', {}).get(target_id)
                    if not target or target.get('text_status') != 'available':
                        continue
                    # A spatial join only. Never promote overlap/containment to
                    # a governs/exception edge or choose one of several claims.
                    contained = [i for i, c in enumerate(claims)
                        if target['start'] <= c['start'] < c['end'] <= target['end']]
                    overlap = [i for i, c in enumerate(claims)
                        if c['start'] < target['end'] and target['start'] < c['end']]
                    associations.append({'occurrence_id': occurrence['id'],
                        'reference_text': [v['quote'] for v in occurrence.get('evidence', [])],
                        'owner_rows': owner_rows, 'target_id': target_id, 'target_address': target['value'],
                        'target_text': doc['text'][target['start']:target['end']],
                        'contained_claim_rows': contained, 'overlapping_claim_rows': overlap,
                        'resolution': resolution, 'semantic_role': 'not_assessed'})
            save(f'{case}/associations.json', associations)
            observed = []
            selected_rows = (3, 4, 5, 6, 7) if case == 'iep-1' else (0, 2, 7)
            for index in selected_rows:
                claim = claims[index]
                context = export_context(book, claim)
                save(f'{case}/context-R{index:03d}.json', context)
                observed.append({'row': index, 'claim_id': claim['id'], 'kind': claim['kind'],
                    'modality': claim['modality'], 'target_ids': claim['target_ids'],
                    'related_claims': context['material']['related_claims'],
                    'reference_readings': len(context['material']['reference_readings']),
                    'contains_writing_source': any('A parent’s agreement under clause (i)' in span['text']
                        for source in context['material']['sources'].values() for span in source['passages'].values()),
                    'incoming_spatial_candidates': [a for a in associations if index in a['contained_claim_rows']],
                    'accounting': context['accounting']})
            assert e._canonical(book) == before
            summary = {'case': case, 'claims': len(claims), 'located_associations': len(associations),
                'resolution_counts': dict(Counter(r.get('resolution', {}).get('status', 'no_resolution')
                                                 for r in scan['candidates'])),
                'rejected_references': len(scan['rejected']), 'contexts': observed, 'book_unchanged': True}
            save(f'{case}/summary.json', summary)
            summaries.append(summary)
            print(case, summary['resolution_counts'], 'claim target sets:', [c['target_ids'] for c in claims])
            for a in associations:
                if 6 in a['owner_rows'] and case == 'iep-1':
                    print('Writing source target:', a['target_address'], 'contained rows:', a['contained_claim_rows'])
    save('summary.json', {'provider_calls': 0, 'cases': summaries})
    for path, digest in e._load(HERE / 'pretrace-pins.json').items():
        assert sha256((HERE / path).read_bytes()).hexdigest() == digest, path
    e._write_manifest(HERE)


if __name__ == '__main__':
    run()
