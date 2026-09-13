"""Construct and validate frozen decision fixtures before any checker calls."""
from copy import deepcopy
import json
from pathlib import Path
import random
import shutil
import tempfile
import run as x
from rulespec_extrapolator import audit as a, core, extraction as e, refinement as r
from rulespec_extrapolator.context import export_context
from rulespec_extrapolator.review_store import ReviewStore


def navigation(book):
    aliases={c['id']:f'C{i:04d}' for i,c in enumerate(book['accepted'])}; rows={}
    for claim in book['accepted']:
        for reading in export_context(book,claim)['material']['reference_readings']:
            if reading.get('direction')!='outgoing' or not reading.get('referenced_claim_ids'): continue
            rows[reading['id']]=dict(reference=reading['value'],source_claim=aliases[claim['id']],
                target_claims=[aliases[i] for i in reading['referenced_claim_ids']],
                semantic_role=reading['semantic_role'],native_reading=reading.get('reading',{}))
    return list(rows.values())


def fields(claim):
    return {k:deepcopy(v) for k,v in claim.items() if k in core.CANDIDATE_SCHEMA['properties']}


def proposal(alias,values,operation='edit'):
    return {'id':'','proposal':dict(operation=operation,target=alias,qualifies=[],
        rationale='Candidate decision for independent assessment.'),'fields':deepcopy(values)}


def main():
    x.pins(); assert not (x.HERE/'cells.json').exists()
    selection={name:(2 if name=='inspection' else 0) for name in x.NAMES}
    complete_names={'inspection','jury','compensatory'}
    groups={}; labels={}; books={}; packets={}; nav={}; previews=[]
    for name in x.NAMES:
        book=e._load(x.HERE/f'extract/{name}/rulebook.json'); books[name]=book
        window=e.plan_windows(book['document'])[0]; assert len(e.plan_windows(book['document']))==1
        packet=r._packet(book,{'labels':{'expected_units':[]}},window); packets[name]=(window,packet)
        nav[name]=navigation(book)
        claim=book['accepted'][selection[name]]; alias=f'C{selection[name]:04d}'; original=fields(claim)
        good=deepcopy(original)
        if name=='privacy':
            good['summary']+=' This access right under this section does not extend to information compiled in reasonable anticipation of a civil action or proceeding.'
            good['context_quotes']=list(dict.fromkeys([*good['context_quotes'],book['accepted'][7]['quote']]))
        elif name=='bankruptcy':
            good['summary']=('If an individual debtor in a voluntary chapter 7 or 13 case fails to file all information required under subsection (a)(1) within 45 days after filing the petition, the case is automatically dismissed effective on day 46, notwithstanding section 707(a), subject to the following provisions. '
                'For that case, any party in interest may request a dismissal order, which the court must enter within seven days of the request, subject to paragraph (4). '
                'On a debtor request made within 45 days after petition filing, the court may allow up to 45 additional days to file the subsection (a)(1) information if it finds justification, also subject to paragraph (4). '
                'Notwithstanding the other provisions, on a trustee motion filed before expiration of the applicable period in paragraph (1), (2), or (3), and after notice and a hearing, the court may decline dismissal if it finds both that the debtor attempted in good faith to file all information required by subsection (a)(1)(B)(iv) and that administering the case would serve creditors’ best interests.')
            good['context_quotes']=list(dict.fromkeys([*good['context_quotes'],*[c['quote'] for c in book['accepted'][1:]]]))
        elif name=='credit':
            good['summary']+=' For an agency described in section 1681a(p), this duty applies only if the consumer makes the request using the centralized source established in accordance with section 211(c) of the Fair and Accurate Credit Transactions Act of 2003.'
            good['context_quotes']=list(dict.fromkeys([*good['context_quotes'],book['accepted'][1]['quote']]))
        elif name=='medical':
            good['summary']=('A covered entity may require a job applicant to undergo a medical examination after an employment offer and before employment duties begin, and may condition the offer on its results, provided all three conditions are met: all entering employees are examined regardless of disability; medical-condition or medical-history information is collected and maintained on separate forms and in separate medical files and treated as confidential, subject to the exceptions below; and the results are used only in accordance with this subchapter. '
                'Under the confidentiality exceptions, supervisors and managers may be informed of necessary work or duty restrictions and necessary accommodations; first aid and safety personnel may be informed when appropriate if the disability might require emergency treatment; and government officials investigating compliance with this chapter must be provided relevant information on request.')
            good['context_quotes']=list(dict.fromkeys([*good['context_quotes'],*[c['quote'] for c in book['accepted'][1:]]]))
        elif name=='recall':
            good['summary']+=(' Failure to repair adequately within 60 days after presentation is prima facie evidence of failure to repair within a reasonable time. The Secretary may extend the 60-day period by order for good cause if the reason is published in the Federal Register before the period ends. Presentation before the manufacturer-specified date in a notice under section 30119(a)(5) or 30121(c)(2) does not count as presentation under this subsection.')
            good['context_quotes']=list(dict.fromkeys([*good['context_quotes'],*[c['quote'] for c in book['accepted'][1:4]]]))
        wrong=deepcopy(good)
        replacements={
            'privacy':("except that the agency may require the individual to furnish a written statement authorizing discussion of that individual's record in the accompanying person's presence", "and the agency must require every individual, whether accompanied or unaccompanied, to furnish written authorization before access"),
            'bankruptcy':('the court may decline dismissal','the court must decline dismissal'),
            'credit':('For an agency described in section 1681a(p),','For every agency described in section 1681a(p) or (w),'),
            'inspection':('at any time with respect to records','not more than once during any 12-month period with respect to records'),
            'jury':('unless the person:','unless all of the following are true of the person:'),
            'compensatory':('within a reasonable period after making the request, if the use of the compensatory time does not unduly disrupt the operations of the public agency','immediately after the request, even if the use of the compensatory time unduly disrupts the operations of the public agency'),
            'medical':('provided all three conditions are met:','provided any one of these three alternative conditions is met:'),
            'recall':('or, for a vehicle, refund the purchase price','or, for either a vehicle or replacement equipment, refund the purchase price')}
        before,after=replacements[name]; assert before in wrong['summary'],name
        wrong['summary']=wrong['summary'].replace(before,after)
        if name=='jury': wrong['summary']=wrong['summary'].replace('; or (5)','; and (5)')
        if name=='medical': wrong['summary']=wrong['summary'].replace('; and the results are used only','; or the results are used only')
        rows=[proposal(alias,good,'no_change' if name in complete_names else 'edit'),proposal(alias,wrong)]
        if name in complete_names:
            enriched=deepcopy(original)
            action,quote={'inspection':('inspect or examine','inspect or examine'),
                'jury':('deem','deem'),
                'compensatory':('permit use of compensatory time','shall be permitted by the employee’s employer to use such time')}[name]
            assert not enriched['action']
            enriched.update(action=action,action_quote=quote)
            rows.append(proposal(alias,enriched))
        else: rows.append(proposal(alias,original,'no_change'))
        for i,p in enumerate(rows):
            p['id']=f'P{i:04d}'
            labels[name+'/'+p['id']]=dict(expected='supported' if i==0 else 'unsupported',
                category=('complete_noop' if name in complete_names else 'complete_repair') if i==0 else
                    'wrong_meaning' if i==1 else ('unnecessary_enrichment' if name in complete_names else 'incomplete_noop'),
                origin='unchanged production extraction' if p['proposal']['operation']=='no_change' else 'constructed diagnostic candidate',
                target=alias,baseline_complete=name in complete_names)
            if p['proposal']['operation']=='no_change': continue
            # Exercise source quotations, CUE-derived fields and the actual review preview.
            raw=deepcopy(p['proposal']); raw['quote']=p['fields']['quote']
            raw['fields']={k:v for k,v in p['fields'].items() if k in r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']}
            decoded,issues=r._decode_proposals(dict(proposals=[raw],observations=[]),[],book['document'],window,packet,'recovery')
            assert not issues and len(decoded)==1,(name,p['id'],issues)
            with tempfile.TemporaryDirectory() as temp:
                shutil.copytree(x.HERE/'extract'/name,temp,dirs_exist_ok=True)
                store=ReviewStore(temp); snapshot=store.snapshot(); preview=store.preview(r._action(decoded[0],snapshot,e.DEFAULT_MODEL))
                assert store.snapshot()==snapshot
                previews.append(dict(source=name,candidate=p['id'],revision=preview['revision'],accepted_count=len(preview['accepted'])))
        groups[name]=rows
    x.save('groups.json',groups); x.save('labels.json',labels); x.save('preview-checks.json',previews)
    x.save('generation-task.txt.json',{'description':r.RECOVERY+'\n'+x.prior.TASK,'executed':False,'purpose':'Same shared criterion would govern proposed construction; no repair generation in this checker experiment.'})
    combinations=[(name,arm,rep) for name in x.NAMES for arm in ('A','B') for rep in range(2)]
    random.Random(91381).shuffle(combinations); cells=[]; key={}
    for i,(name,arm,rep) in enumerate(combinations):
        window,packet=packets[name]; rows=deepcopy(groups[name]); random.Random(91381+100*x.NAMES.index(name)+rep).shuffle(rows)
        if arm=='A': rows=[p for p in rows if p['proposal']['operation']!='no_change']
        prompt=r._challenge_prompt(packet,rows,books[name]['document'])
        if arm=='B': prompt=x.prior.CHECK_TASK+prompt[len(r.CHECK):]
        prompt+=x.prior.INDEPENDENT+'\nReference navigation: '+e._canonical(nav[name])
        if arm=='B': prompt+='\nSelected statement aliases: '+e._canonical([f'C{selection[name]:04d}'])
        cell=f'cell-{i+1:02d}'; cells.append(cell); key[cell]=dict(source=name,arm=arm,repeat=rep,fresh=True)
        x.save(f'inputs/{cell}.json',dict(document=books[name]['document'],window=window,packet=packet,candidates=rows,prompt=prompt))
    for rep in range(2):
        for arm,oldcell in [('A','cell-09'),('B','cell-01')]:
            old=e._load(x.OLD/f'inputs/{oldcell}.json'); cell=f'regression-{arm}-{rep}'
            cells.append(cell); key[cell]=dict(source='notice',arm=arm,repeat=rep,fresh=False)
            x.save(f'inputs/{cell}.json',dict(document=e._load(x.OLD/'books.json')['notice']['document'],**{k:old[k] for k in ('window','packet','candidates','prompt')}))
    x.save('cells.json',cells); x.save('arm-key.json',key); x.save('schema.json',r.CHECK_SCHEMA)
    paths=list((x.HERE/'inputs').glob('*.json'))+[x.HERE/n for n in ('groups.json','labels.json','BASELINE-REVIEW.md','preview-checks.json','cells.json','arm-key.json','schema.json','prepare_checks.py')]
    x.freeze('check-pins.json',paths)
    print('24 fresh candidate decisions, 32 paired calls and 4 separate regression calls frozen; all edited candidates preview-valid.')


if __name__=='__main__': main()
