"""Verify the declared comparisons and replay every captured cell without a model."""
import json
from pathlib import Path
import subprocess
import sys
from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent


def main():
    if len(sys.argv) != 2:
        raise SystemExit('Supply a new directory for replay outputs')
    replay_root = Path(sys.argv[1]).resolve()
    replay_root.mkdir(parents=True, exist_ok=False)
    design = e._load(ROOT / 'design.json')
    rows = []
    for sample, variant in design['calls']:
        run = ROOT / 'runs' / sample / variant
        result = subprocess.run([sys.executable, str(ROOT / 'experiment.py'), 'replay', sample, variant,
            '--output', str(replay_root / sample / variant)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError('Replay failed for ' + sample + '/' + variant)
        request = e._load(run / 'attempt-0000.request.json')
        response = e._load(run / 'attempt-0000.response.json')
        control = e._load(ROOT / 'runs' / sample / 'control/attempt-0000.request.json')
        expected = dict(control)
        if variant != 'control':
            base = (ROOT / 'base-prompt.txt').read_text()
            expected['contents'] = control['contents'].replace(base,
                base + '\n\n' + (ROOT / (variant + '.txt')).read_text(), 1)
        if request != expected:
            raise ValueError('The comparison changed more than the declared appended instructions')
        book = e._load(run / 'rulebook.json')
        raw = json.loads(''.join(p['text'] for p in response['candidates'][0]['content']['parts']
            if p.get('text') and not p.get('thought')))
        # These particular captures have no refused/rejected rows; verify the
        # converter did not repair their prose or classifications for the review.
        for source, claim in zip(raw['extractions'], book['accepted'], strict=True):
            attrs = source['unit_attributes']
            if any(attrs[a] != claim[b] for a, b in [('statement','summary'),
                    ('scope_text','scope_text'),('kind','kind'),('modality','modality')]):
                raise ValueError('Conversion changed a reviewed meaning field')
        u = response['usage_metadata']
        rows.append({'sample': sample, 'variant': variant, 'replay_identical': True,
            'only_declared_prompt_changed': True, 'raw_meaning_preserved': True,
            'status': book['run']['status'], 'accepted': len(book['accepted']),
            'refusals': len(book['extraction_refusals']), 'rejected': len(book['rejected']),
            'tokens': u['total_token_count'], 'prompt_tokens': u['prompt_token_count'],
            'output_tokens': u['candidates_token_count'], 'thought_tokens': u.get('thoughts_token_count', 0),
            'validation': e._load(run / 'validation.json'),
            'request_sha256': e._digest((run / 'attempt-0000.request.json').read_bytes()),
            'response_sha256': e._digest((run / 'attempt-0000.response.json').read_bytes())})
    prior = ROOT.parent / 'meaning-first-adoption/final'
    repeat = {s: e._load(prior / s / 'attempt-0000.request.json') ==
        e._load(ROOT / 'runs' / s / 'control/attempt-0000.request.json') for s in ('baggage','photos','leave')}
    e._save(ROOT / 'verification.json', {'provider_calls': len(rows), 'replay_provider_calls': 0,
        'total_reported_tokens': sum(r['tokens'] for r in rows),
        'control_requests_identical_to_prior_capture': repeat, 'results': rows})
    print(e._canonical({'runs_replayed': len(rows), 'provider_calls_during_verification': 0,
        'total_experiment_tokens': sum(r['tokens'] for r in rows)}))


if __name__ == '__main__':
    main()
