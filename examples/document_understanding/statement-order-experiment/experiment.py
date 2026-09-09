"""Change only statement property position in the current CUE-generated schema."""
import argparse
from pathlib import Path
from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent
ORIGINAL_SCHEMA = e.provider_schema


def schema_for(variant):
    schema = ORIGINAL_SCHEMA()
    if variant == 'statement-first':
        attrs = schema.schema_dict['properties']['extractions']['items']['properties']['unit_attributes']
        props = attrs['properties']
        attrs['properties'] = {'statement': props['statement'],
                               **{k: v for k, v in props.items() if k != 'statement'}}
    return schema


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    parser.add_argument('sample')
    parser.add_argument('variant', choices=('control', 'statement-first'))
    parser.add_argument('repeat', type=int)
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    design = e._load(ROOT / 'design.json')
    if [args.sample, args.variant, args.repeat] not in design['calls']:
        raise ValueError('Call outside declared experiment')
    for name, digest in design['inputs_sha256'].items():
        if e._digest((ROOT / name).read_bytes()) != digest:
            raise ValueError('Pinned input changed: ' + name)
    if {n: e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()} != design['runtime_sources_sha256']:
        raise ValueError('Runtime changed')
    e.provider_schema = lambda: schema_for(args.variant)
    run = ROOT / 'runs' / args.sample / args.variant / str(args.repeat)
    if args.mode == 'run':
        result = e.extract_run(e._load(ROOT / (args.sample + '.json')), run,
            model_id=design['model'], temperature=design['temperature'], env_file=args.env_file)
    else:
        if args.output is None:
            raise ValueError('Replay requires a new output directory')
        result = e.replay_run(run, args.output)
        if result != e._load(run / 'rulebook.json'):
            raise ValueError('Replay differs')
    print(e._canonical({'sample': args.sample, 'variant': args.variant, 'repeat': args.repeat,
        'status': result['run']['status'], 'accepted': len(result['accepted']),
        'refusals': len(result['extraction_refusals']), 'rejected': len(result['rejected'])}), flush=True)


if __name__ == '__main__':
    main()
