"""One shared fresh extraction and six paired proposal/challenge paths."""
import argparse
from copy import deepcopy
from pathlib import Path
import random
import shutil
import time
from unittest.mock import patch

from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore, ReviewError

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'2026-09-10-evidence-catalog'
SOURCES={'refrigerants':OLD/'fresh-extraction', 'seatbelts':Path('examples/document_understanding/consistency-transfer/cells/cell-00').resolve()}
ENV=Path('/Users/mikewolfd/Work/spicy-regs/.env')


def prompt(packet,document,arm,prepared=None):
    if prepared is not None: return r._challenge_prompt(packet,prepared,document)
    base=r._proposal_prompt(r.RELATIONSHIPS,packet)
    if arm=='A': return base
    qualifications=[key for key,c in packet['claims'].items() if c['kind'] in {'condition','exception','exemption'}]
    targets=[key for key,c in packet['claims'].items() if c['kind'] not in {'condition','exception','exemption'}]
    matrix=[dict(qualification=q,candidate_targets=targets) for q in qualifications]
    return base+"\nTARGET DISCOVERY: For each existing qualification below, consider EACH candidate local target against the source. A qualification can govern multiple rules, including rules elsewhere in this section. A separate exemption record or a target that already mentions the exclusion does not by itself represent a qualification link. Propose all missing source-supported links using the existing operations and fields, preserving the qualification's exact meaning and evidence. No supported link is a valid result for any pair: proximity or a shared term is insufficient. Preserve each qualification's scope; nearby duties outside that scope remain binding. Do not expand external references beyond available source. This list contains candidates, not approved relationships. Return only the ordinary proposal output, without a new matrix field.\nCandidate pairs: "+e._canonical(matrix)


def prepare():
    assert not (ROOT/'design.json').exists()
    for case in SOURCES:
        source=OLD/'inputs'/case if case=='refrigerants' else ROOT.parent/'2026-09-10-relationship-audit/inputs/seatbelts'
        for name in ['book.json','packet.json']:
            e._save(ROOT/'inputs'/case/name,e._load(source/name))
        book=e._load(ROOT/'inputs'/case/'book.json')
        baseline=ROOT/'baseline'/case
        if not baseline.exists(): r._copy_run(SOURCES[case],baseline)
        current=ReviewStore(baseline).snapshot()
        if case=='seatbelts':
            e._save(ROOT/'inputs'/case/'historical-book.json',book)
            book=current
            window,=e.plan_windows(book['document'],24000)
            packet=r._packet(book,{'labels':{'expected_units':[]}},window)
            e._save(ROOT/'inputs'/case/'book.json',book)
            e._save(ROOT/'inputs'/case/'packet.json',packet)
        assert current==book
    pairs=[(case,arm) for case in SOURCES for arm in ['A','B']]
    random.Random(20260917).shuffle(pairs)
    for case,arm in pairs:
        packet=e._load(ROOT/'inputs'/case/'packet.json');book=e._load(ROOT/'inputs'/case/'book.json')
        e._save(ROOT/'inputs'/case/f'prompt-{arm}.json',{'text':prompt(packet,book['document'],arm)})
    paths=[ROOT/'PLAN.md',Path(__file__),*sorted((ROOT/'inputs').rglob('*.json'))]
    e._save(ROOT/'design.json',dict(model=e.DEFAULT_MODEL,max_calls=8,max_seconds=1200,
        cells=[dict(id=f'cell-{i:02d}',case=case,arm=arm) for i,(case,arm) in enumerate(pairs)],
        inputs={str(p.relative_to(ROOT)):e._digest(p.read_bytes()) for p in paths},
        runtime=e._runtime_versions(),fingerprints=e._freeze(ROOT,[],r.proposal_schema())))
    print('Frozen historical inputs, target criteria and four randomized cells.',flush=True)


def verify():
    design=e._load(ROOT/'design.json')
    for name,digest in design['inputs'].items(): assert e._digest((ROOT/name).read_bytes())==digest,name
    assert design['runtime']==e._runtime_versions()
    assert design['fingerprints']['sources_sha256']=={n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}
    return design


def run(replay=False):
    design=verify()
    for name,digest in design['inputs'].items(): assert e._digest((ROOT/name).read_bytes())==digest,name
    key='' if replay else e._credential(ENV)
    start=time.monotonic();calls=0
    def call(path,text,schema):
        nonlocal calls
        if replay:
            attempt=e._load(path/'attempt-0000.json')
            request=e._load(path/attempt['request_file']) if attempt.get('request_file') else None
            if request:
                assert request['contents']==text
                assert request['config']['response_json_schema']==schema
            payload,errors=a._read_response(path,attempt)
            return payload,errors,attempt
        assert calls<8 and time.monotonic()-start<1200,'Experiment bound reached'
        calls+=1;print(f'Comparison call {calls}/8: {path.relative_to(ROOT)}',flush=True)
        return r._call(path,text,schema,e.DEFAULT_MODEL,key,None)
    for cell in design['cells']:
        path=ROOT/'cells'/cell['id'];case=cell['case'];arm=cell['arm']
        book=e._load(ROOT/'inputs'/case/'book.json');packet=e._load(ROOT/'inputs'/case/'packet.json')
        window,=e.plan_windows(book['document'],24000)
        text=prompt(packet,book['document'],arm)
        assert text==e._load(ROOT/'inputs'/case/f'prompt-{arm}.json')['text']
        payload,errors,attempt=call(path/'proposal',text,r.proposal_schema())
        proposals,issues=r._decode_proposals(payload,errors,book['document'],window,packet,'relationships')
        if replay:
            saved=e._load(path/'result.json')
            assert proposals==saved['proposals']
            prepared=saved['prepared']
        else:
            source=ROOT/'baseline'/case
            r._copy_run(source,path/'workspace')
            store=ReviewStore(path/'workspace');before=store.snapshot()
            assert before==book
            prepared=[]
            for p in proposals:
                try:
                    preview=store.preview(r._action(p,before,e.DEFAULT_MODEL))
                    if set(preview['history'][-1]['replacements'][0]['target_ids'])!=set(p['qualification_ids']): raise ValueError('Target mismatch')
                    prepared.append(p)
                except (ValueError,ReviewError) as exc:
                    issues.append(dict(code='invalid_correction',proposal_id=p['id'],reason=str(exc)))
        checks={};challenge_attempt=None
        if prepared:
            text=prompt(packet,book['document'],arm,prepared)
            answer,errors,challenge_attempt=call(path/'challenge',text,r.CHECK_SCHEMA)
            checks,problems=r._decode_checks(answer,errors,prepared,book['document'],packet)
            issues+=problems
        if replay:
            assert checks==saved['checks'] and issues==saved['issues']
            continue
        outcomes=[]
        for p in prepared:
            check=checks.get(p['id']);outcome=dict(proposal_id=p['id'],status='not_applied',judgment=check)
            if check and check['verdict']=='supported':
                try:
                    action=r._action(p,store.snapshot(),e.DEFAULT_MODEL)
                    provenance=e.captured_provenance(path/'proposal',attempt,'proposal')
                    if provenance: action['provenance']=provenance
                    after=store.apply(action)
                    outcome.update(status='applied',event=after['history'][-1])
                except (ValueError,ReviewError) as exc:
                    outcome.update(status='refused',reason=str(exc))
            outcomes.append(outcome)
        after=store.snapshot()
        e._save(path/'result.json',dict(proposals=proposals,prepared=prepared,checks=checks,issues=issues,outcomes=outcomes))
        e._save(path/'after.json',after);e._save(path/'discovery.json',export_discovery(after))
        print(cell['id'],'applied',sum(o['status']=='applied' for o in outcomes),'issues',len(issues),flush=True)
    e._save(ROOT/('replay-checks.json' if replay else 'completion.json'),dict(provider_calls=0 if replay else calls,
        status='decoding matched' if replay else 'captured; manual review pending'))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','run','replay'])
    mode=parser.parse_args().mode
    {'prepare':prepare,'run':run,'replay':lambda:run(True)}[mode]()
