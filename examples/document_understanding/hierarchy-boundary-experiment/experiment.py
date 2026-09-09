"""Compare structural parent hints with identical source windows and schemas."""
import argparse
from pathlib import Path
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.documents import source_passages

ROOT = Path(__file__).resolve().parent
ORIGINAL_CATALOG = e.passage_catalog


def hierarchy_catalog(document, window):
    catalog = ORIGINAL_CATALOG(document, window)
    passages = source_passages(document)
    origins = {alias: next(p for p in passages if p['start'] <= span['start'] and span['end'] <= p['end'])
               for alias, span in catalog.items()}
    for alias, span in catalog.items():
        parent = origins[alias]['parent_id']
        span['structural_parent_refs'] = [a for a,p in origins.items() if p['id'] == parent]
        if parent and not span['structural_parent_refs']:
            span['structural_parent_unsupplied'] = True
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run','replay'))
    parser.add_argument('sample')
    parser.add_argument('windowing', choices=('whole','split'))
    parser.add_argument('variant', choices=('control','hierarchy'))
    parser.add_argument('repeat', type=int)
    parser.add_argument('--env-file', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    design = e._load(ROOT/'design.json')
    cell = [args.sample,args.windowing,args.variant,args.repeat]
    if cell not in design['runs']:
        raise ValueError('Run outside declared experiment')
    for name,digest in design['inputs_sha256'].items():
        if e._digest((ROOT/name).read_bytes()) != digest:
            raise ValueError('Pinned input changed: ' + name)
    if {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()} != design['runtime_sources_sha256']:
        raise ValueError('Runtime changed')
    if args.variant == 'hierarchy':
        e.passage_catalog = hierarchy_catalog
    run = ROOT/'runs'/args.sample/args.windowing/args.variant/str(args.repeat)
    if args.mode == 'run':
        book = e.extract_run(e._load(ROOT/(args.sample+'.json')),run,
            model_id=design['model'],temperature=0,env_file=args.env_file,
            max_chars=design['window_limits'][args.sample][args.windowing])
    else:
        if args.output is None:
            raise ValueError('Replay requires a new output directory')
        book = e.replay_run(run,args.output)
        if book != e._load(run/'rulebook.json'):
            raise ValueError('Replay differs')
    print(e._canonical({'cell':cell,'status':book['run']['status'],
        'accepted':len(book['accepted']),'refusals':len(book['extraction_refusals']),
        'rejected':len(book['rejected'])}),flush=True)

if __name__ == '__main__':
    main()
