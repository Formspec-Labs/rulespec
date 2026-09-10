from copy import deepcopy
from experiment import *
p=e._load(ROOT/'inputs/rail-packet.json');b=e._load(ROOT/'inputs/rail-book.json');w,=e.plan_windows(b['document'],24000)
row={'target':'C0009','qualifies':['C0000'],'rationale':'Constructed test'}
checks={}
for name,changes in [('missing',{'qualifies':[]}),('self',{'qualifies':['C0009']}),('nonexistent',{'qualifies':['C9999']}),('meaning-change',{'summary':'Changed meaning'})]:
    try:expand({'proposals':[{**row,**changes}]},p);checks[name]=False
    except Exception:checks[name]=True
base=expand({'proposals':[row]},p)
valid,issues=r._decode_proposals(base,[],b['document'],w,p,'relationships');checks['full-proposal-valid']=len(valid)==1 and not issues
changed=deepcopy(base);changed['proposals'][0]['fields']['summary']='Changed meaning'
rejected,issues=r._decode_proposals(changed,[],b['document'],w,p,'relationships');checks['ordinary-meaning-equality-protection']=not rejected and bool(issues)
wrong=expand({'proposals':[{**row,'qualifies':['C0002']}]},p)
accepted,issues=r._decode_proposals(wrong,[],b['document'],w,p,'relationships');checks['wrong-existing-target-is-mechanically-valid']=len(accepted)==1 and not issues
# Do not silently conflate mechanical grounding with semantic applicability.
actual=e._load(ROOT/'inputs/alcohol.json')
checks['historical-driver-copy-unresolved']=all(core._evidence(actual['document'],'driver','actor',within=(c['start'],c['end'])) is None for c in actual['claims'])
for reference in ['F999','F003:F999']:
    try:e.resolve_passage(reference,actual['catalog'],actual['document']);checks[reference]=False
    except ValueError:checks[reference]=True
text='Staff must file reports.\n\nStaff must file reports.'
doc=prepare_document(text,title='Constructed identical passages')
w,=e.plan_windows(doc,24000);cat=e.passage_catalog(doc,w);span=e.resolve_passage('F001',cat,doc)
exact=core._evidence(doc,span['quote'],'actor',span['start'],span['end'])
checks['identical-passage-selected-offset-preserved']=exact['start']==cat['F001']['start']
checks['identical-full-quote-without-offset-refused']=core._evidence(doc,span['quote'],'actor') is None
assert all(checks.values()),checks
e._save(ROOT/'controls.json',dict(checks=checks,semantic_wrong_target=wrong,wrong_target_warning='Schema accepts C0009 to C0002: decoder cannot establish semantic applicability. This constructed negative is not submitted or applied.',repeated_passages={'document':doc,'catalog':cat,'selected_evidence':exact}))
print(checks)
