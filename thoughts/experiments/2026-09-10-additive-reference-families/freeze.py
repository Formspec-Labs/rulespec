"""Fixed new-case labels; no parser calls."""
import json
from hashlib import sha256
from pathlib import Path

root=Path(__file__).parent
prior=json.loads(root.parent.joinpath('2026-09-10-broader-parser-comparison/cases.json').read_text())['cases']
# Normalize only human-written expected values; no output-driven labeling.
def expected(kind,value,quote): return {'kind':kind,'value':value,'quote':quote}
new=[
 ('unicode-law','🧭 Pursuant to Pub. L. 117–58, action may follow.',[expected('public_law','Public Law 117-58','Pub. L. 117–58')]),
 ('repeated-eo','E.O. 12866 applies; E.O. 12866 also appears here.',[expected('executive_order','Executive Order 12866','E.O. 12866')]*2),
 ('mixed','Pub. L. 117-58, 135 Stat. 429, and Executive Order 12866.',[
  expected('public_law','Public Law 117-58','Pub. L. 117-58'),expected('statutes_at_large','135 Stat. 429','135 Stat. 429'),expected('executive_order','Executive Order 12866','Executive Order 12866')]),
 ('docket-context','The docket (EPA-HQ-OAR-2023-0234) remains open.',[expected('docket','EPA-HQ-OAR-2023-0234','EPA-HQ-OAR-2023-0234')]),
 ('rin-context','Follow RIN 2120-AK94.',[expected('rin','2120-AK94','2120-AK94')]),
 ('rin-list','RINs 2120-AK94 and 2120-AK95',[expected('rin','2120-AK94','2120-AK94'),expected('rin','2120-AK95','2120-AK95')]),
 ('incomplete-law','Pub. L. 117-',[]),
 ('fused-law','Pub. L. 117-58draft',[]),
 ('compound-law','Pub. L. 117-58-2',[]),
 ('fused-eo','E.O. 12866draft',[]),
 ('compound-eo','E.O. 12866-2',[]),
 ('page-suffix','135 Stat. 429a',[]),
 ('document-not-docket','EPA-HQ-OAR-2023-0234-0001',[]),
 ('fused-docket','EPA-HQ-OAR-2023-0234extra',[]),
 ('compound-rin','RIN 2120-AK94-extra',[]),
 ('ordinary','The public law seminar reviewed statistics; Romeo spoke.',[]),
 ('excluded-families','See 89 FR 91529 and 5401-5405.',[]),
]
old_expected={
 'public-law':[expected('public_law','Public Law 117-58','Pub. L. 117-58')],
 'statutes-page':[expected('statutes_at_large','135 Stat. 429','135 Stat. 429')],
 'executive-order':[expected('executive_order','Executive Order 12866','E.O. 12866')],
 'docket':[expected('docket','EPA-HQ-OAR-2023-0234','EPA-HQ-OAR-2023-0234')],
 'rin':[expected('rin','2120-AK94','2120-AK94')],
}
cases=[{**c,'group':'development','expected_additions':old_expected.get(c['name'],[])} for c in prior]
for name,text,labels in new:
 cases.append({'id':f'new-{len(cases)-len(prior)+1:02d}','name':name,'raw':text,
               'origin':'new constructed diagnostic','group':'new-diagnostic','expected_additions':labels})
paths=[Path('examples/document_understanding/low-thinking-experiment/runs/leave-full-low-1/document.json'),Path('examples/document_understanding/hierarchy-boundary-experiment/runs/baggage/whole/control/1/document.json'),Path('examples/document_understanding/sparse-meaning-check/extraction/waste/document.json')]
root.joinpath('documents').mkdir(exist_ok=True)
for i,p in enumerate(paths):
 d=json.loads(p.read_text());d=d.get('document',d)
 assert sha256(d['text'].encode()).hexdigest()==d['sha256']
 target=root/'documents'/f'source-{i+1}.json'
 target.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
 cases.append({'id':f'source-{i+1}','name':d['title'],'raw':d['text'],'text_sha256':d['sha256'],
               'origin':'saved full document, newly tested in this parser comparison','group':'new-source',
               'source_path':str(p),'source_copy':str(target),'source_url':d.get('source_url'),
               'expected_additions':[]})
assert len(cases)-len(prior)<=20
for c in cases:
 c['text_sha256']=sha256(c['raw'].encode()).hexdigest()
 cursor={}
 for label in c['expected_additions']:
  quote=label['quote'];start=c['raw'].index(quote,cursor.get(quote,0));cursor[quote]=start+len(quote)
  # Copy repeated labels before assigning independent occurrence spans.
  label_index=c['expected_additions'].index(label)
  c['expected_additions'][label_index]={**label,'span':[start,start+len(quote)]}
with root.joinpath('cases.json').open('x') as f:json.dump(cases,f,indent=2,ensure_ascii=False)
