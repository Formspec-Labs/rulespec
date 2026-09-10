"""Check preserved records, final consumer links and captured workflow usage."""
from collections import Counter
from pathlib import Path

from rulespec_extrapolator import extraction as e, refinement as r
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.review_store import ReviewStore

ROOT=Path(__file__).resolve().parent
results={}
for case in ['alcohol','rail-crossings']:
    directory=ROOT/'cases'/case
    e._verify_manifest(directory/'extraction')
    before=e._load(directory/'refinement/before.json')
    after=e._load(directory/'refinement/after.json')
    assert ReviewStore(directory/'workspace').snapshot()==after
    assert export_discovery(after)==e._load(directory/'discovery.json')
    originals={c['rule_id']:c for c in before['accepted']}
    current={c['rule_id']:c for c in after['accepted']}
    fields=r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
    for rule_id,original in originals.items():
        revised=current[rule_id]
        assert all(original[k]==revised[k] for k in fields if k!='relation')
        assert original['quote']==revised['quote'] and original['evidence']==revised['evidence']
    links=[c for c in after['accepted'] if c['target_ids']]
    expected_baseline=before['accepted'][2 if case=='alcohol' else 0]['id']
    assert len(links)==(2 if case=='alcohol' else 5)
    graph=after['graph']['@graph']
    for claim in links:
        assert claim['target_ids']==[expected_baseline]
        assert claim['review_status']=='pending'
        edge,=[n for n in graph if n.get('rkaf:assertsSubject')==claim['id']
               and n.get('rkaf:assertsObject')==expected_baseline
               and n.get('@type')=='rkaf:RelationshipAssertion']
        assert edge['rkaf:assertsPredicate'].endswith(':exception')
        assert any(n.get('rkaf:bindsAssertion')==edge['@id'] and
                   n.get('rkaf:evidentiaryFunction')=='rkaf:qualifies' for n in graph)
        if case=='rail-crossings':
            prior=originals[claim['rule_id']]
            assert claim['kind']=='exemption' and claim['modality']=='not_required'
            assert claim['supersedes']==[prior['id']]
    changes=e._load(directory/'refinement/changes.json')
    assert len(changes)==len(links)
    assert all(c['judgment']['verdict']=='supported' for c in changes)
    assert after['history']==[c['event'] for c in changes]
    summaries={}
    for phase in ['initial-audit','final-audit']:
        report=e._load(directory/'refinement'/phase/'report.json')
        summaries[phase]={k:report[k] for k in ['status','counts','coverage','semantic_completeness','audit_issues']}
    stats={}
    for phase in ['extraction','refinement']:
        stats[phase]=e.recorded_usage(directory/phase)
    issues={}
    for name,book in [('before',before),('after',after)]:
        issues[name]=dict(Counter(i['code'] for c in book['accepted'] for i in c.get('issues',[])+c.get('link_issues',[])))
    exemption_quotes=[c for c in before['accepted'] if c['kind']=='exemption']
    results[case]=dict(initial_claims=len(originals),final_claims=len(current),
        initial_links=sum(len(c['target_ids']) for c in before['accepted']),final_links=len(links),
        actions=len(changes),all_original_meaning_and_evidence_preserved=True,
        review_reload_and_consumer_export='matched',core_relationships_and_evidence='verified',
        extraction_status=e._load(directory/'extraction/run.json')['status'],
        refinement_status=e._load(directory/'refinement/refinement.json')['status'],
        workflow_issues=e._load(directory/'refinement/issues.json'),claim_issues=issues,
        usage=stats,audits=summaries,
        exemption_main_quote_characters=[len(c['quote']) for c in exemption_quotes],
        exemption_main_quote_total=sum(len(c['quote']) for c in exemption_quotes))
e._save(ROOT/'verification.json',results)
for case,result in results.items():
    print(case,e._canonical({k:v for k,v in result.items() if k!='audits'}))
