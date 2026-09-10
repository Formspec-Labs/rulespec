"""One additional live integration call after the invalid-definition edge fix.

Explicit constructed mutations to a real captured extraction test completion of
partly populated data. These mutations and recovery are not quality-trial results.
"""
import argparse
from pathlib import Path
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.structure import enrich_run, replay_enrichment
from rulespec_extrapolator.review_store import ReviewStore
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.core import validate_graph

ROOT = Path(__file__).resolve().parent


def main(env):
    root = ROOT / 'partial-enrichment'
    root.mkdir(exist_ok=False)
    # Reprocessing records the small post-trial runtime change and preserves captures.
    book = e.reprocess_run(ROOT / 'cells/cell-03', root / 'workspace')
    e.replay_run(root / 'workspace', root / 'extraction-replay')
    store = ReviewStore(root / 'workspace')
    initial = store.snapshot()
    comparison = next(c for c in initial['accepted'] if c['summary'] == 'An access record is not an annual report.')
    actor = next(c for c in initial['accepted'] if c['summary'] == 'Staff must file the access record.')
    for claim, fields in [(comparison, {'term_refs': comparison['term_refs'][:1]}),
                          (actor, {'actor': '', 'actor_quote': ''})]:
        before = store.snapshot()
        action = {'action': 'edit', 'expected_revision': before['revision'],
            'actor': 'Codex integration fixture', 'actor_kind': 'aiAgent', 'targets': [claim['id']],
            'replacements': [fields], 'rationale': 'Constructed removal for a live partial-enrichment integration test; not a model extraction defect.'}
        e._save(root / f'fixture-edit-{before["revision"]}.json', action)
        store.apply(action)
    before = store.snapshot()
    result = enrich_run(root / 'workspace', root / 'capture', env_file=env)
    replay_enrichment(root / 'capture', root / 'replay')
    after = store.snapshot()
    reloaded = ReviewStore(root / 'workspace').snapshot()
    assert reloaded == after
    e._save(root / 'discovery.json', export_discovery(after))
    added = after['history'][len(before['history']):]
    assert all(event.get('provenance', {}).get('request_sha256') for event in added)
    current = {c['rule_id']: c for c in after['accepted']}
    checks = {'enrichment_status': result['status'], 'applied_actions': result['applied_actions'],
        'restored_partial_term_list': current[comparison['rule_id']]['term_refs'] == comparison['term_refs'],
        'restored_actor': current[actor['rule_id']]['actor'] == actor['actor'],
        'statements_unchanged': [c['summary'] for c in before['accepted']] == [c['summary'] for c in after['accepted']],
        'captured_provenance_on_new_events': len(added), 'reload': 'identical', 'replay': 'passed',
        'graph_validation': validate_graph(after['graph']), 'usage': e.recorded_usage(root / 'capture')}
    e._save(root / 'checks.json', checks)
    print(e._canonical(checks), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--env-file', type=Path, required=True)
    main(parser.parse_args().env_file)
