"""Freeze publisher source cases and the unchanged native reader once."""
from collections import Counter
import hashlib
import importlib.util
from io import BytesIO
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
REFSPEC = HERE.parents[3] / 'RefSpec'
ARCHIVE = REFSPEC / 'output/usc-annual-2026-08-24/xml_uscAll_119-102.zip'
RECEIPT = REFSPEC / 'output/usc-source-credit-index-2026-08-02/receipt.json'
TOOL = REFSPEC / 'tools/extract_uslm_reference_edges.py'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(name, value):
    with (HERE/name).open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2)
        f.write('\n')


pins = json.loads(RECEIPT.read_text())['inputs']
archive = ARCHIVE.read_bytes()
assert 'sha256:'+sha(archive) == pins['archive_digest']
with (HERE/'native_oracle.py').open('xb') as f:
    f.write(TOOL.read_bytes())
spec = importlib.util.spec_from_file_location('native_oracle',HERE/'native_oracle.py')
native = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = native
spec.loader.exec_module(native)
cases=[]
with zipfile.ZipFile(BytesIO(archive)) as z:
    for title in ('05','42'):
        member=f'usc{title}.xml'
        raw=z.read(member)
        pin=next(x for x in pins['titles'] if x['member']==member)
        assert 'sha256:'+sha(raw)==pin['digest']
        root_open=re.search(rb'<uscDoc\b[^>]*>',raw)[0]
        selected=None
        for _,section in ET.iterparse(BytesIO(raw),events=('end',)):
            if section.tag.rsplit('}',1)[-1] != 'section':
                continue
            size=len(ET.tostring(section))
            identifier=section.get('identifier')
            descendants=list(section.iter())
            links=[x.get('href') for x in descendants if x.get('href') is not None]
            nested=[x.get('identifier') for x in descendants if x is not section and x.get('identifier')]
            eligible=(identifier and 1000<=size<=25000 and 2<=len(links)<=40
                      and set(links)&set(nested)
                      and sum(x.tag.rsplit('}',1)[-1]=='section' for x in descendants)==1)
            if eligible:
                selected=identifier
                break
            section.clear()
        assert selected,(title,'no qualifying section')
        markers=list(re.finditer(rb'<section\b[^>]*\bidentifier="'+re.escape(selected.encode())+rb'"[^>]*>',raw))
        assert len(markers)==1,(selected,len(markers))
        start=markers[0].start()
        end=raw.index(b'</section>',start)+len(b'</section>')
        fragment=raw[start:end]
        name=f'title-{title}-{selected.rsplit("/",1)[-1]}.xml'
        wrapped=root_open+fragment+b'</uscDoc>'
        with (HERE/name).open('xb') as f:
            f.write(wrapped)
        counts=Counter()
        rows=list(native.iter_edges(wrapped,title,counts))
        cases.append({'id':selected,'title':title,'capture':name,
            'source':{'archive':str(ARCHIVE),'archive_sha256':sha(archive),
                'member':member,'member_sha256':sha(raw),
                'section_start':start,'section_end':end,'section_sha256':sha(fragment),
                'capture_sha256':sha(wrapped),'release_point':pins['release_point'],
                'preparation':'exact section bytes wrapped in the original uscDoc opening tag'},
            'baseline':rows,'skipped':dict(counts)})
        print(selected,len(fragment),'bytes',len(rows),'native occurrences',dict(counts))
        print(fragment[:1100].decode())
save('cases.json',cases)
save('freeze.json',{'files':{p.name:sha(p.read_bytes()) for p in HERE.iterdir() if p.is_file()}})
