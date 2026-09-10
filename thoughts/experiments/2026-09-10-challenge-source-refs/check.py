"""One captured live challenge using fixed prior proposals; no retries."""
from pathlib import Path
from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.review_store import ReviewStore

ROOT = Path(__file__).resolve().parent
OLD = ROOT.parent / '2026-09-10-evidence-catalog'

def main():
    assert not (ROOT / 'challenge').exists(), 'Preserve existing capture; no retry'
    book = e._load(OLD / 'inputs/rail-crossings/book.json')
    packet = e._load(OLD / 'inputs/rail-crossings/packet.json')
    prepared = e._load(OLD / 'cells/cell-05/result.json')['prepared']
    for name, value in [('book.json', book), ('packet.json', packet), ('prepared.json', prepared)]:
        e._save(ROOT / name, value)
    e._save(ROOT / 'runtime.json', e._freeze(ROOT, [], r.CHECK_SCHEMA))
    r._copy_run(ROOT.parent / '2026-09-10-exemption-end-to-end/cases/rail-crossings/extraction', ROOT / 'workspace')
    store = ReviewStore(ROOT / 'workspace')
    assert store.snapshot() == book
    prompt = r._challenge_prompt(packet, prepared, book['document'])
    payload, errors, attempt = r._call(ROOT / 'challenge', prompt, r.CHECK_SCHEMA,
        e.DEFAULT_MODEL, e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env')), None)
    checks, issues = r._decode_checks(payload, errors, prepared, book['document'], packet)
    e._save(ROOT / 'decoded.json', {'checks': checks, 'issues': issues})
    outcomes = []
    for proposal in prepared:
        check = checks.get(proposal['id'])
        if check and check['verdict'] == 'supported':
            after = store.apply(r._action(proposal, store.snapshot(), e.DEFAULT_MODEL))
            outcomes.append({'proposal_id': proposal['id'], 'event': after['history'][-1]})
    after = store.snapshot()
    e._save(ROOT / 'after.json', after)
    e._save(ROOT / 'outcomes.json', outcomes)
    replay, replay_errors = a._read_response(ROOT / 'challenge', attempt)
    assert r._decode_checks(replay, replay_errors, prepared, book['document'], packet) == (checks, issues)
    assert ReviewStore(ROOT / 'workspace').snapshot() == after
    e._save(ROOT / 'verification.json', {'provider_calls': 1, 'decode_replay_provider_calls': 0,
        'decoded': len(checks), 'applied': len(outcomes), 'issues': issues,
        'source_spans_exact': all(s['quote'] == book['document']['text'][s['start']:s['end']]
            for c in checks.values() for s in c['source_spans'])})
    print(e._canonical(e._load(ROOT / 'verification.json')))

if __name__ == '__main__':
    main()
