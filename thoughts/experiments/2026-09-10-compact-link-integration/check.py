"""Two-call integration smoke check with production mixed proposal schema."""
from pathlib import Path
from rulespec_extrapolator import extraction as e, refinement as r, audit as a
from rulespec_extrapolator.review_store import ReviewStore
ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'2026-09-10-evidence-catalog'
assert not (ROOT/'proposal').exists(), 'Keep the original capture'
book=e._load(OLD/'inputs/rail-crossings/book.json')
packet=e._load(OLD/'inputs/rail-crossings/packet.json')
window,=e.plan_windows(book['document'],24000)
schema=r.proposal_schema('relationships')
for name,value in [('before.json',book),('packet.json',packet),('runtime.json',e._freeze(ROOT,[],schema))]: e._save(ROOT/name,value)
r._copy_run(ROOT.parent/'2026-09-10-exemption-end-to-end/cases/rail-crossings/extraction',ROOT/'workspace')
store=ReviewStore(ROOT/'workspace'); assert store.snapshot()==book
key=e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
payload,errors,attempt=r._call(ROOT/'proposal',r._proposal_prompt(r.RELATIONSHIPS,packet),schema,e.DEFAULT_MODEL,key,None)
prepared,issues=r._decode_proposals(payload,errors,book['document'],window,packet,'relationships')
for p in prepared: store.preview(r._action(p,book,e.DEFAULT_MODEL))
checks={};outcomes=[]
if prepared:
    response,failures,check_attempt=r._call(ROOT/'challenge',r._challenge_prompt(packet,prepared,book['document']),r.CHECK_SCHEMA,e.DEFAULT_MODEL,key,None)
    checks,check_issues=r._decode_checks(response,failures,prepared,book['document'],packet)
    issues.extend(check_issues)
    replay,replay_errors=a._read_response(ROOT/'challenge',check_attempt)
    assert r._decode_checks(replay,replay_errors,prepared,book['document'],packet)==(checks,check_issues)
    for p in prepared:
        if checks.get(p['id'],{}).get('verdict')=='supported':
            action=r._action(p,store.snapshot(),e.DEFAULT_MODEL)
            action['provenance']=e.captured_provenance(ROOT/'proposal',attempt,'proposal')
            after=store.apply(action)
            outcomes.append({'proposal_id':p['id'],'event':after['history'][-1]})
replay,replay_errors=a._read_response(ROOT/'proposal',attempt)
assert r._decode_proposals(replay,replay_errors,book['document'],window,packet,'relationships')[0]==prepared
snapshot=store.snapshot();assert ReviewStore(ROOT/'workspace').snapshot()==snapshot
for old in book['accepted']:
    new=next(c for c in snapshot['accepted'] if c['rule_id']==old['rule_id'])
    for field in r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']:
        if field!='relation': assert new[field]==old[field],field
    assert new['quote']==old['quote'] and new['evidence']==old['evidence']
e._save(ROOT/'after.json',snapshot)
e._save(ROOT/'result.json',{'raw_operations':[p.get('operation') for p in payload.get('proposals',[])], 'prepared':prepared,'checks':checks,'issues':issues,'outcomes':outcomes})
print({'decoded':len(prepared),'applied':len(outcomes),'issues':issues,'replay_provider_calls':0})
