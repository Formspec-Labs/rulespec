"""Run or replay a declared audit of an immutable saved low extraction."""
import argparse
from pathlib import Path
from rulespec_extrapolator import audit as a, extraction as e
R=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('run','replay'));p.add_argument('cell')
    p.add_argument('--env-file',type=Path);p.add_argument('--output',type=Path)
    args=p.parse_args();d=e._load(R/'design.json');cell=d['runs'][args.cell]
    for name,digest in d['inputs_sha256'].items():
        if e._digest((R/name).read_bytes())!=digest:raise ValueError('Pinned input changed: '+name)
    if {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}!=d['runtime_sources_sha256']:raise ValueError('Runtime changed')
    run=R/'runs'/args.cell
    if args.mode=='run':
        report=a.audit_run(e._load(R/cell['input']),run,env_file=args.env_file,max_chars=24000,thinking_level='high',max_output_tokens=None)
    else:
        if args.output is None:raise ValueError('Replay needs a new output directory')
        report=a.replay_audit(run,args.output)
    print(e._canonical({'cell':args.cell,'processing':e._load(run/'audit.json')['status'],'assessment':report['status'],'coverage':report.get('coverage'),'audit_issues':report.get('audit_issues',[])}),flush=True)
if __name__=='__main__':main()
