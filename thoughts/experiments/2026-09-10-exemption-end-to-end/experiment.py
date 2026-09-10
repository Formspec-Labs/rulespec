"""Use the existing complete workflow on fresh source; bound and retain calls."""
import argparse
from pathlib import Path
import shutil
import time
from unittest.mock import patch

from rulespec_extrapolator import extraction as e, refinement as r
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document

ROOT=Path(__file__).resolve().parent
CASES=['alcohol','rail-crossings']


def prepare():
    assert not (ROOT/'design.json').exists()
    for case in CASES:
        doc=prepare_document((ROOT/'sources'/f'{case}.txt').read_text(),title=f'49 CFR {"392.5" if case=="alcohol" else "392.10"}, 2025',
                             source_url=(ROOT/'sources'/f'{case}.url').read_text().strip())
        assert len(e.plan_windows(doc,3000))==1
        e._save(ROOT/'inputs'/f'{case}.json',doc)
    paths=[ROOT/'PLAN.md',Path(__file__),*sorted((ROOT/'sources').glob('*')),*sorted((ROOT/'inputs').glob('*'))]
    e._save(ROOT/'design.json',dict(cases=CASES,model=e.DEFAULT_MODEL,max_calls=18,max_seconds=1800,
        inputs={str(p.relative_to(ROOT)):e._digest(p.read_bytes()) for p in paths},
        fingerprints=e._freeze(ROOT,[],r.proposal_schema()),runtime=e._runtime_versions()))
    print('Two full source sections and criteria frozen; no calls.',flush=True)


def run():
    design=e._load(ROOT/'design.json')
    for name,digest in design['inputs'].items():
        assert e._digest((ROOT/name).read_bytes())==digest,name
    assert e._runtime_versions()==design['runtime']
    assert {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}==design['fingerprints']['sources_sha256']
    calls=[]; start=time.monotonic(); original=e._record_window
    def bounded(*args,**kwargs):
        assert len(calls)<18 and time.monotonic()-start<1800,'Experiment bound reached'
        destination=Path(args[2])
        entry=dict(index=len(calls)+1,path=str(destination.relative_to(ROOT)),status='started')
        calls.append(entry); e._save(ROOT/'calls.json',calls)
        print(f'Call {len(calls)}/18 started: {entry["path"]}',flush=True)
        attempt=original(*args,**kwargs)
        entry.update(status=attempt['status'],error_code=attempt.get('error_code'))
        e._save(ROOT/'calls.json',calls)
        print(f'Call {len(calls)}/18: {attempt["status"]}',flush=True)
        return attempt
    env=Path('/Users/mikewolfd/Work/spicy-regs/.env')
    with patch.object(e,'_record_window',bounded):
        for case in design['cases']:
            directory=ROOT/'cases'/case
            e.extract_run(e._load(ROOT/'inputs'/f'{case}.json'),directory/'extraction',env_file=env,max_chars=3000)
            shutil.copytree(directory/'extraction',directory/'workspace')
            result=r.refine_run(directory/'workspace',directory/'refinement',env_file=env,max_chars=3000)
            e._save(directory/'discovery.json',export_discovery(result['rulebook']))
            print(case,result['run']['status'],'applied',len(result['changes']),flush=True)
    e._save(ROOT/'completion.json',dict(calls=len(calls),seconds=time.monotonic()-start,status='captured; manual review pending'))


def replay():
    results={}
    for case in CASES:
        directory=ROOT/'cases'/case
        e.replay_run(directory/'extraction',ROOT/'replay'/case/'extraction')
        results[case]=r.replay_refinement(directory/'refinement',ROOT/'replay'/case/'refinement')
    e._save(ROOT/'replay-checks.json',results)
    print('Extraction and full refinement replays verified for both sources.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','run','replay'])
    args=parser.parse_args()
    {'prepare':prepare,'run':run,'replay':replay}[args.mode]()
