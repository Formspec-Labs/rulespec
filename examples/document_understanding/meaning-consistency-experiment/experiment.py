"""Paired prompt-only probes using the normal extractor, schemas and replay."""
import argparse
from pathlib import Path
from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    parser.add_argument('sample')
    parser.add_argument('variant', choices=('control', 'classification', 'consistency'))
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    design = e._load(ROOT / 'design.json')
    if [args.sample, args.variant] not in design['calls']:
        raise ValueError('Call is outside the declared experiment')
    for name, expected in design['inputs_sha256'].items():
        if e._digest((ROOT / name).read_bytes()) != expected:
            raise ValueError('Experiment input changed: ' + name)
    if e._digest(e.load_schema('provider')) != design['provider_schema_sha256']:
        raise ValueError('Provider schema changed')
    if {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} != design['runtime_sources_sha256']:
        raise ValueError('Runtime changed')
    # Change instructions only; no alternative model schema, parser, or Core path.
    e.PROMPT = (ROOT / 'base-prompt.txt').read_text()
    if args.variant != 'control':
        e.PROMPT += '\n\n' + (ROOT / (args.variant + '.txt')).read_text()
    path = ROOT / 'runs' / args.sample / args.variant
    if args.mode == 'run':
        result = e.extract_run(e._load(ROOT / (args.sample + '.json')), path,
                               env_file=args.env_file, temperature=0)
    else:
        if args.output is None:
            raise ValueError('Replay requires a new output directory')
        result = e.replay_run(path, args.output)
        if result != e._load(path / 'rulebook.json'):
            raise ValueError('Replay differs')
    print(e._canonical({'sample': args.sample, 'variant': args.variant,
        'status': result['run']['status'], 'accepted': len(result['accepted']),
        'refusals': len(result['extraction_refusals']), 'rejected': len(result['rejected'])}))


if __name__ == '__main__':
    main()
