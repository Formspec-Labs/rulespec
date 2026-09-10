"""Production workflow smoke using this trial's actual paragraph extraction.

No sentence override; enrichment and audit make three new provider calls. Manual
correction is a labeled agent judgment, not provider output or human approval.
"""
from pathlib import Path
import argparse
import shutil
from rulespec_extrapolator import extraction as e, audit
from rulespec_extrapolator import core
from rulespec_extrapolator.structure import enrich_run, replay_enrichment
from rulespec_extrapolator.review_store import ReviewStore
from rulespec_extrapolator.discovery import export_discovery

ROOT = Path(__file__).resolve().parent


def main(env):
    root = ROOT / 'integration'
    root.mkdir(exist_ok=False)
    shutil.copytree(ROOT / 'cells/cell-04', root / 'workspace')
    e._save(root / 'input.json', {'origin': '../cells/cell-04', 'arm': 'P',
        'limitation': 'Reuse of a fresh experiment extraction, not another independent quality sample.'})
    e.replay_run(root / 'workspace', root / 'extraction-replay')
    enrichment = enrich_run(root / 'workspace', root / 'enrichment', env_file=env)
    replay_enrichment(root / 'enrichment', root / 'enrichment-replay')
    print('Enrichment:', enrichment['status'], enrichment['applied_actions'], flush=True)
    store = ReviewStore(root / 'workspace')
    before = store.snapshot()
    e._save(root / 'before-correction.json', before)
    result = audit.audit_run(before, root / 'audit', env_file=env, max_chars=24000,
                             max_output_tokens=32768, thinking_level='medium')
    audit.replay_audit(root / 'audit', root / 'audit-replay')
    print('Audit:', result['status'], result['semantic_completeness'], flush=True)
    # Preidentified imprecise structured scope, not an invented failure.
    claim = next(c for c in before['accepted'] if c['summary'].startswith('Consultation from'))
    assert claim['scope_text'] == 'to employers in these circumstances'
    action = {'action': 'edit', 'expected_revision': before['revision'],
        'actor': 'Codex source review', 'actor_kind': 'aiAgent', 'targets': [claim['id']],
        'replacements': [{'scope_text': 'Employers with unique or changing first-aid needs in their workplace'}],
        'rationale': 'Resolve these circumstances in the optional applicability field from the same source paragraph; retain the already complete statement and original evidence. Agent judgment, not human approval.'}
    e._save(root / 'correction.json', action)
    after = store.apply(action)
    e._save(root / 'reviewed-rulebook.json', after)
    e._save(root / 'discovery.json', export_discovery(after))
    reloaded = ReviewStore(root / 'workspace').snapshot()
    assert reloaded == after
    assert export_discovery(reloaded) == e._load(root / 'discovery.json')
    changed = next(c for c in reloaded['accepted'] if c['rule_id'] == claim['rule_id'])
    assert changed['id'] != claim['id'] and changed['review_status'] == 'pending'
    assert len(reloaded['history']) == len(before['history']) + 1
    validation = core.validate_graph(reloaded['graph'])
    e._save(root / 'checks.json', {'extraction_replay': 'passed', 'enrichment_replay': 'passed',
        'audit_replay': 'passed', 'review_reload': 'identical', 'discovery_reload': 'identical',
        'corrected_rule_identity': 'preserved', 'corrected_revision': 'new and pending',
        'graph_validation': validation, 'enrichment': enrichment,
        'audit_status': result['status'], 'semantic_completeness': result['semantic_completeness'],
        'new_provider_usage': {'enrichment': e.recorded_usage(root / 'enrichment'), 'audit': e.recorded_usage(root / 'audit')}})
    print('Correction/export/reload and graph validation passed.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--env-file', type=Path, required=True)
    main(parser.parse_args().env_file)
