"""Provider-free compatibility, correction history and capture preservation checks."""
from copy import deepcopy
from pathlib import Path
import json
import shutil

from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.core import validate_graph
from rulespec_extrapolator.review_store import ReviewStore

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def main():
    target = REPO / '.tools/quality-v2-delivery'
    target.mkdir(exist_ok=False)
    e._create_model = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('Verification must not call a provider'))
    original = REPO / 'examples/document_understanding/manual-slice'
    rows = []
    for name in ['development-01', 'holdout-01', 'holdout-02', 'section-01', 'section-02']:
        source = original / 'runs' / name
        processed = target / name
        before = {p.name: e._digest(p.read_bytes()) for p in source.glob('*.json')}
        book = e.reprocess_run(source, processed)
        assert e.replay_run(processed, target / (name + '-replay')) == book
        assert before == {p.name: e._digest(p.read_bytes()) for p in source.glob('*.json')}
        assert all('modality' not in c for c in book['accepted'])
        rows.append({'run': name, 'status': 'verified', 'accepted': len(book['accepted']),
                     'original_captures_unchanged': True, 'invented_v2_meaning': False})

    demo = ROOT / 'review-demo'
    demo.mkdir(exist_ok=False)
    run_dir = target / 'review-demo'
    e.replay_run(target / 'section-01', run_dir)
    store = ReviewStore(run_dir)
    before = store.snapshot()
    base_files = {p.name: e._digest(p.read_bytes()) for p in run_dir.glob('*.json')}
    actions = sorted((original / 'review-demo/actions').glob('*.json'))
    for index, path in enumerate(actions):
        request = e._load(path)
        # These original actions intentionally retain their exact targets.
        result = store.apply(request)
        e._save(demo / path.name, request)
        assert result['revision'] == index + 1
    result = store.snapshot()
    assert ReviewStore(run_dir).snapshot() == result
    assert base_files == {p.name: e._digest(p.read_bytes()) for p in run_dir.glob('*.json')}
    current_ids = {c['id'] for c in result['accepted']}
    assert all(t in current_ids for c in result['accepted'] for t in c['target_ids'])
    before_nodes = {n['@id']: n for n in before['graph']['@graph']}
    after_nodes = {n['@id']: n for n in result['graph']['@graph']}
    assert all(after_nodes.get(k) == v for k, v in before_nodes.items())
    validate_graph(result['graph'])
    e._save(demo / 'reviewed-rulebook.json', result)
    e._save(demo / 'review-history.json', result['history'])
    e._save(demo / 'verification.json', {
        'case_id': 'NREG-15', 'status': 'verified', 'action_count': len(actions),
        'reopened_identically': True, 'original_json_unchanged': True,
        'original_graph_nodes_unchanged': len(before_nodes), 'current_targets_resolve': True,
        'source_run': str(original / 'runs/section-01'), 'local_review_workspace': str(run_dir),
        'remaining_gaps': 'These three historical corrections do not add the missing might-require-ID or generally-needs-documentation statements; do not equate corrections with complete coverage.',
        'attribution': 'Original action files retain aiAgent attribution; this is not human approval.',
    })
    pins = e._load(REPO / '.tools/quality-v2-baseline/before-sha256.json')
    # The baseline includes changing package files too; preserve source/review artifacts.
    protected = {name: digest for name, digest in pins.items()
                 if name.startswith(('examples/document_understanding/manual-slice/',
                                     'thoughts/reviews/2026-09-07-document-understanding-adversarial/'))}
    changed = [name for name, digest in protected.items() if e._digest((REPO / name).read_bytes()) != digest]
    assert not changed, changed
    e._save(ROOT / 'compatibility-verification.json', {'provider_calls': 0, 'legacy_runs': rows,
            'protected_original_files': len(protected), 'changed_original_files': changed,
            'correction_case': 'review-demo/verification.json'})
    print(json.dumps({'legacy_runs': len(rows), 'protected_files': len(protected), 'corrections': len(actions)}))


if __name__ == '__main__':
    main()
