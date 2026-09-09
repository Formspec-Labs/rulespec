"""Prepare two declared source sections without model-based preprocessing."""
from pathlib import Path
from bs4 import BeautifulSoup
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
harness = ROOT.parent / 'low-extract-medium-audit/experiment.py'
assert not (ROOT / 'design.json').exists()
p = BeautifulSoup((ROOT / 'passport-source.html').read_bytes(), 'html.parser')
paragraphs = [' '.join(t.get_text(' ', strip=True).split()) for t in p.find_all('p')]
start = next(i for i,t in enumerate(paragraphs) if t.startswith('8 FAM 801.2-1 '))
end = next(i for i,t in enumerate(paragraphs) if t.startswith('8 FAM 801.2-2 '))
passport = '\n\n'.join(paragraphs[start:end])
w = BeautifulSoup((ROOT / 'waste-source.html').read_bytes(), 'html.parser')
body = w.select_one('p.first-paragraph').parent
waste = '\n\n'.join([' '.join(w.h1.get_text(' ',strip=True).split())] +
    [' '.join(t.get_text(' ',strip=True).split()) for t in body.find_all('p')])
rows = [('passport',passport,'8 FAM 801.2-1 Introduction','https://fam.state.gov/fam/08fam/08fam080102.html','passport-source.html'),
        ('waste',waste,'Ohio Administrative Code 3745-52-15','https://codes.ohio.gov/ohio-administrative-code/rule-3745-52-15','waste-source.html')]
runtime = {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}
metadata = []
for name,text,title,url,raw in rows:
    directory=ROOT/name
    document=prepare_document(text,title=title,source_url=url)
    assert len(e.plan_windows(document,24000)) == 1
    e._save(directory/'document.json',document)
    e._save(directory/'design.json',{'runtime_sources_sha256':runtime,
        'inputs_sha256':{'document.json':e._digest((directory/'document.json').read_bytes())},
        'model':e.DEFAULT_MODEL,'temperature':0,'extraction_thinking':'low','audit_thinking':'medium',
        'max_output_tokens':None,'max_calls':3})
    metadata.append({'case':name,'source_url':url,'raw_file':raw,'raw_sha256':e._digest((ROOT/raw).read_bytes()),
        'prepared_sha256':document['sha256'],'prepared_chars':len(text),
        'source_paragraphs':len(text.split('\n\n'))})
e._save(ROOT/'design.json',{'integration_commit':'83caace','source_metadata':metadata,'max_provider_calls':6,
    'harness_sha256':e._digest(harness.read_bytes()), 'runtime_sources_sha256':runtime,
    'inputs_sha256':{name:e._digest((ROOT/name).read_bytes()) for name in
        ['PLAN.md','prepare.py','run.py','passport-source.html','waste-source.html',
         'passport/document.json','passport/design.json','waste/document.json','waste/design.json']}})
print(metadata)
