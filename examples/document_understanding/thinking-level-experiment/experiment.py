"""Run declared thinking-level comparisons through normal extraction."""
import argparse
from pathlib import Path
from rulespec_extrapolator import extraction as e
ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('run','replay'))
    p.add_argument('cell')
    p.add_argument('--env-file',type=Path)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    design=e._load(ROOT/'design.json')
    cell=design['runs'][args.cell]
    for name,digest in design['inputs_sha256'].items():
        if e._digest((ROOT/name).read_bytes())!=digest:
            raise ValueError('Pinned input changed: '+name)
    if {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}!=design['runtime_sources_sha256']:
        raise ValueError('Runtime changed')
    run=ROOT/'runs'/args.cell
    if args.mode=='run':
        book=e.extract_run(e._load(ROOT/(cell['sample']+'.json')),run,env_file=args.env_file,
            max_chars=cell['max_chars'],max_output_tokens=cell['max_output_tokens'],temperature=0,thinking_level=cell['thinking_level'])
    else:
        if args.output is None:raise ValueError('Replay requires a new output directory')
        book=e.replay_run(run,args.output)
        if book!=e._load(run/'rulebook.json'):raise ValueError('Replay differs')
    print(e._canonical({'cell':args.cell,'status':book['run']['status'],'accepted':len(book['accepted']),
        'refusals':len(book['extraction_refusals']),'rejected':len(book['rejected'])}),flush=True)

if __name__=='__main__':main()
