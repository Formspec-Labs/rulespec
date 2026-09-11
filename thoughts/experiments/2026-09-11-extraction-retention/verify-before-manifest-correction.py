"""Check source support, retained meaning and review boundaries of the fixed outputs."""
from collections import Counter
import json
from pathlib import Path
import shutil
import tempfile

from rulespec_extrapolator import core, extraction as ex
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.review_store import ReviewStore

HERE = Path(__file__).resolve().parent
SOURCE = Path(ex._load(HERE / 'input.json')['source_experiment'])
checks = []
stable_fields = ('kind', 'summary', 'actor', 'action', 'object', 'modality',
                 'scope_text', 'choice_text', 'jurisdiction', 'references',
                 'concepts', 'claimants', 'typed_values', 'effective_periods')


def key(claim):
    return tuple(claim.get(k) for k in ('quote', 'summary', 'kind', 'actor'))


for cell in ex._load(SOURCE / 'cells.json'):
    directory = SOURCE / 'cells' / cell['id']
    old = ex._load(directory / 'rulebook.json')
    book = ex._load(HERE / 'combined-result' / (cell['id'] + '.rulebook.json'))
    parsed = ex._load(HERE / 'combined-result' / (cell['id'] + '.parsed.json'))
    doc = book['document']
    current = {key(c): c for c in book['accepted']}
    assert len(current) == len(book['accepted']), cell['id']
    identity_changes = []
    for claim in old['accepted']:
        retained = current[key(claim)]
        assert all(retained.get(k) == claim.get(k) for k in stable_fields), (cell['id'], key(claim))
        if retained['id'] != claim['id']:
            identity_changes.append({'quote': claim['quote'], 'old': claim['id'], 'new': retained['id'],
                                     'rule_id_changed': retained['rule_id'] != claim['rule_id']})
    for claim in book['accepted']:
        assert doc['text'][claim['start']:claim['end']] == claim['quote']
        for evidence in claim['evidence']:
            assert core._evidence(doc, evidence['quote'], evidence['field'], evidence['start'], evidence['end']) == evidence
    assert all(r['reason'] == 'Candidate kind contradicts its declared modality' for r in book['rejected'])
    assert not any(r['code'] == 'passage_not_in_request' for r in parsed['refusals'])
    if old['run']['status'] == 'failed':
        assert not book['accepted'] and not parsed['candidates']
    validation = core.validate_graph(book['graph'])
    discovery = export_discovery(book, include_references=True)
    old_discovery = ex._load(directory / 'discovery.json')
    assert [(r['id'], r['text']) for r in discovery['records']] == [(r['id'], r['text']) for r in old_discovery['records']]
    for identity, evidence in discovery['evidence'].items():
        start, end = evidence['start'], evidence['end']
        assert core._evidence(doc, doc['text'][start:end], 'source', start, end)['fragment_id'] == identity
    # Review the changed records without pretending they are the old model run.
    reviewer = object.__new__(ReviewStore)
    reviewer.document, reviewer.run = doc, book['run']
    assert reviewer._validated_graph(book['accepted'], []) == book['graph']
    # Existing captures keep their own identities and review content. Copy them
    # because opening ReviewStore creates a database; never write in sealed input.
    with tempfile.TemporaryDirectory(prefix='rulespec-old-review-') as temporary:
        copied = Path(temporary) / 'run'
        shutil.copytree(directory, copied)
        store = ReviewStore(copied)
        assert store._validated_graph(store.base['accepted'], []) == old['graph']
        assert store.snapshot() == ReviewStore(copied).snapshot()
    ex._save(HERE / 'combined-result' / (cell['id'] + '.discovery.json'), discovery)
    checks.append({'cell': cell['id'], 'old_accepted': len(old['accepted']),
                   'accepted': len(book['accepted']), 'rejected': len(book['rejected']),
                   'validation': validation, 'retained_base_meaning': True,
                   'all_original_evidence_verified': True, 'source_records_unchanged': True,
                   'old_review_graph_and_reload_unchanged': True,
                   'reprocessing_identity_changes': identity_changes})
    print(json.dumps({k: checks[-1][k] for k in ('cell', 'old_accepted', 'accepted', 'rejected')}), flush=True)

ex._save(HERE / 'checks.json', checks)
print(json.dumps({'cells': len(checks), 'recovered': sum(r['accepted'] - r['old_accepted'] for r in checks),
                  'remaining_rejected': sum(r['rejected'] for r in checks),
                  'identity_changes_on_reprocessing': sum(len(r['reprocessing_identity_changes']) for r in checks)}))
