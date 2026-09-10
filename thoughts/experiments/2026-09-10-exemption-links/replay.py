"""Keep captured reclassifications refused; test explicit link-only adaptations."""
import argparse
from copy import deepcopy
from pathlib import Path
from shutil import copy2

from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.review_store import ReviewStore

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / '2026-09-10-relationship-audit'
REPO = ROOT.parents[2]


def run(output):
    output.mkdir(parents=True, exist_ok=False)
    results = []
    for case, indices in [('extinguishers', [1]), ('seatbelts', [0, 1])]:
        book = e._load(PREVIOUS / 'inputs' / case / 'book.json')
        labels = e._load(PREVIOUS / 'inputs' / case / 'labels.json')
        capture = PREVIOUS / 'relationships' / case
        attempt, = e._load(capture / 'attempts.json')
        payload, errors = a._read_response(capture, attempt)
        window, = e.plan_windows(book['document'], 24000)
        packet = r._packet(book, {'labels': labels}, window)
        _, issues = r._decode_proposals(payload, errors, book['document'], window, packet, 'relationships')
        refused = {i['index'] for i in issues if i['code'] == 'proposal_refused'}
        assert set(indices) <= refused
        for index in indices:
            original = payload['proposals'][index]
            prior = packet['claims'][original['target']]
            assert prior['kind'] == 'exemption' and prior['modality'] == 'not_required'
            item = deepcopy(original)
            properties = r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
            item['fields'] = {key: deepcopy(prior[key]) for key in properties}
            item['fields']['relation'] = 'exception'
            item['quote'] = prior['quote']
            item['rationale'] = 'Constructed link-only adaptation of saved proposal: preserve the existing exemption and add its proposed target.'
            parsed, problems = r._decode_proposals({'proposals': [item], 'observations': []}, [],
                book['document'], window, packet, 'relationships')
            assert not problems, problems
            path = output / f'{case}-{index}'
            if case == 'seatbelts':
                source = REPO / 'examples/document_understanding/consistency-transfer/cells/cell-00'
                manifest = e._verify_manifest(source)
                assert e._load(source / 'rulebook.json') == book
                for name in [*manifest['artifacts_sha256'], 'manifest.json']:
                    destination = path / name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    copy2(source / name, destination)
            else:
                for name, value in [('document.json', book['document']), ('rulebook.json', book), ('run.json', book['run'])]:
                    e._save(path / name, value)
            store = ReviewStore(path)
            before = store.snapshot()
            after = store.apply(r._action(parsed[0], before, 'constructed replay test'))
            rule_id = next(c['rule_id'] for c in book['accepted'] if c['id'] == prior['id'])
            linked, = [c for c in after['accepted'] if c['rule_id'] == rule_id]
            assert len(after['accepted']) == len(before['accepted'])
            assert linked['id'] != prior['id'] and linked['supersedes'] == [prior['id']]
            for key in properties:
                if key != 'relation':
                    assert linked[key] == prior[key], key
            assert linked['quote'] == prior['quote']
            assert linked['target_ids'] == sorted(parsed[0]['qualification_ids'])
            assert linked['review_status'] == 'pending'
            assert ReviewStore(path).snapshot() == after
            export = export_discovery(after)
            statement, = [c for c in export['statements'] if c['id'] == linked['id']]
            assert statement['kind'] == 'exemption' and statement['modality'] == 'not_required'
            assert statement['qualification_targets'] == linked['target_ids']
            e._save(path / 'adaptation.json', item)
            e._save(path / 'reviewed.json', after)
            e._save(path / 'discovery.json', export)
            results.append({'case': case, 'raw_proposal_index': index,
                'raw_reclassification': 'still refused', 'adaptation': 'constructed, not provider output',
                'old_revision': prior['id'], 'new_revision': linked['id'], 'rule_id': linked['rule_id'],
                'kind': linked['kind'], 'modality': linked['modality'], 'statement': linked['summary'],
                'targets': linked['target_ids'], 'unchanged_meaning_and_evidence': True,
                'reload_and_export': 'passed'})
    e._save(output / 'results.json', {'provider_calls': 0, 'cases': results,
        'limitation': 'Tests supported operations using constructed adaptations; no new model behavior or target-discovery accuracy claim.'})
    print('All three original reclassifications refused; all three explicit link-only adaptations preserved meaning and reloaded.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.output)
