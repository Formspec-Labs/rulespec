"""One shared fresh extraction and six paired proposal/challenge paths."""
import argparse
from copy import deepcopy
from pathlib import Path
import random
import shutil
import time
from unittest.mock import patch

import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/"2026-09-10-evidence-catalog"))
import catalog
from rulespec_extrapolator import audit as a, extraction as e, refinement as r
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.review_store import ReviewStore, ReviewError

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'2026-09-10-exemption-end-to-end'
ENV=Path('/Users/mikewolfd/Work/spicy-regs/.env')


def prompt(packet,document,arm,prepared=None):
    if arm=='A':
        return r._proposal_prompt(r.RELATIONSHIPS,packet) if prepared is None else r._challenge_prompt(packet,prepared,document)
    view=r._model_packet(packet)
    description=r.RELATIONSHIPS
    if prepared is not None:
        description=r.CHECK
        view.pop('focus');view.pop('context')
        proposals=[dict(id=p['id'],operation=p['proposal']['operation'],target=p['proposal']['target'],
                        qualifies=p['proposal']['qualifies'],rationale=p['proposal']['rationale'],fields=p['fields']) for p in prepared]
        view={'source_passages':r._challenge_catalog(document,packet),'draft_and_audit':view,'proposed_changes':proposals}
    encoded=catalog.encode(view,document['text'])
    assert catalog.decode(encoded)==view
    return description+catalog.GUIDANCE+'\nSource and draft packet (audit rationale aliases refer to initial_audit_aliases): '+e._canonical(encoded)


def prepare():
    assert not (ROOT/'design.json').exists()
    assert e._load(ROOT/'preflight.json')['gate_passed']
    doc=prepare_document((ROOT/'sources/mobile-phones.selected.txt').read_text(),title='49 CFR 392.82, 2025',source_url=(ROOT/'sources/mobile-phones.url').read_text().strip())
    assert len(e.plan_windows(doc,24000))==1
    e._save(ROOT/'inputs/mobile-phones/document.json',doc)
    for case in ['rail-crossings']:
        source=OLD/'cases'/case/'refinement'
        for name,path in [('book.json',source/'before.json'),('packet.json',source/'relationships/window-0000/packet.json')]:
            e._save(ROOT/'inputs'/case/name,e._load(path))
    paths=[ROOT/'PLAN.md',Path(catalog.__file__),Path(__file__),ROOT/'preflight.json',*sorted((ROOT/'sources').glob('*')),*sorted((ROOT/'inputs').rglob('*.json'))]
    e._save(ROOT/'design.json',dict(model=e.DEFAULT_MODEL,max_calls=9,max_seconds=1200,
        inputs={str(p.resolve()):e._digest(p.read_bytes()) for p in paths},
        runtime=e._runtime_versions(),fingerprints=e._freeze(ROOT,[],r.proposal_schema())))
    print('Frozen code, source and saved cases.',flush=True)


def verify():
    design=e._load(ROOT/'design.json')
    for name,digest in design['inputs'].items(): assert e._digest((ROOT/name).read_bytes())==digest,name
    assert design['runtime']==e._runtime_versions()
    assert design['fingerprints']['sources_sha256']=={n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}
    return design


def extract():
    verify()
    e.extract_run(e._load(ROOT/'inputs/mobile-phones/document.json'),ROOT/'fresh-extraction',env_file=ENV,max_chars=24000)
    book=ReviewStore(ROOT/'fresh-extraction').snapshot()
    e._save(ROOT/'inputs/mobile-phones/book.json',book)
    window,=e.plan_windows(book['document'],24000)
    packet=r._packet(book,{'labels':{'expected_units':[]}},window)
    assert packet['omitted_claim_count']==0
    e._save(ROOT/'inputs/mobile-phones/packet.json',packet)
    print('Fresh shared extraction saved; freeze alias expectations before comparison calls.',flush=True)


def freeze_cells():
    verify();assert not (ROOT/'cells-design.json').exists()
    assert (ROOT/'expected.json').exists()
    pairs=[(case,arm) for case in ['rail-crossings','mobile-phones'] for arm in ['A','B']]
    random.Random(20260920).shuffle(pairs)
    for case,arm in pairs:
        packet=e._load(ROOT/'inputs'/case/'packet.json');book=e._load(ROOT/'inputs'/case/'book.json')
        e._save(ROOT/'inputs'/case/f'prompt-{arm}.json',{'text':prompt(packet,book['document'],arm)})
    paths=[ROOT/'expected.json',*sorted((ROOT/'inputs').rglob('*.json'))]
    e._save(ROOT/'cells-design.json',dict(cells=[dict(id=f'cell-{i:02d}',case=case,arm=arm) for i,(case,arm) in enumerate(pairs)],
        inputs={str(p.resolve()):e._digest(p.read_bytes()) for p in paths}))
    print('Four randomized cells and target expectations frozen.',flush=True)


def run(replay=False):
    verify();design=e._load(ROOT/'cells-design.json')
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
            source=ROOT/'fresh-extraction' if case=='mobile-phones' else OLD/'cases'/case/'extraction'
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
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['prepare','extract','freeze','run','replay'])
    mode=parser.parse_args().mode
    {'prepare':prepare,'extract':extract,'freeze':freeze_cells,'run':run,'replay':lambda:run(True)}[mode]()
