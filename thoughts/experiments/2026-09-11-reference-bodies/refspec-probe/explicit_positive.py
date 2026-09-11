"""Actual explicit USC pinpoint from saved Federal Register source."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import hashlib,json,time
from refspec.input_pin import read_verified_file_pin
from refspec.registry.uslm import read_text
ROOT=Path(__file__).resolve().parent
base=json.loads((ROOT/'results.json').read_text());pin=base['source_archive']['pin'];archive=read_verified_file_pin(Path(base['source_archive']['path']),expected_sha256='sha256:'+pin['sha256'],expected_byte_length=int(pin['bytes']))
with ZipFile(BytesIO(archive)) as z:xml=z.read('usc05.xml')
start=time.monotonic();reader=read_text(xml);parse_seconds=time.monotonic()-start
# One index per supplied title; no repeated title parsing for these lookups.
start=time.monotonic();identifiers={}
for path,node in reader['nodes'].items():
 if node.get('identifier'):identifiers.setdefault(node['identifier'],[]).append((path,node))
index_seconds=time.monotonic()-start
identifier='/us/usc/t5/s553/b/B';matches=identifiers.get(identifier,[]);assert len(matches)==1
path,node=matches[0];body=reader['text'][node['start']:node['end']]
(ROOT/'s553-b-B.txt').write_text(body)
s=xml.decode();at=s.index('identifier="'+identifier+'"');left=s.rfind('<',0,at);right=s.find('</'+node['tag']+'>',at)+len('</'+node['tag']+'>')
(ROOT/'raw-s553-b-B-context.xml.txt').write_text(s[max(0,left-450):right+400]);(ROOT/'raw-title5-metadata.xml.txt').write_text(s[:1300])
source=Path('/Users/mikewolfd/Work/rulespec/thoughts/experiments/2026-09-10-reference-real-positives/sources/2025-24202.txt')
st=source.read_text();q='5 U.S.C. 553(b)(B)';at=st.index(q)
selection={'identifier':identifier,'node':node,'xpath':path,'body':body,'source_map_overlapping_title_ranges':[p for p in reader['source_map'] if p['start']<node['end'] and p['end']>node['start']],'source_archive_pin':pin,'member':{'name':'usc05.xml','sha256':hashlib.sha256(xml).hexdigest(),'bytes':len(xml)},'requested_edition':'not stated; citing source is 2025 Federal Register','returned_edition':'Online@119-102','edition_match':'not established','source_reference':{'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'start':at,'end':at+len(q),'quote':q,'context':st[max(0,at-220):at+len(q)+300]},'timing':{'prepare_entire_title_seconds':parse_seconds,'index_once_seconds':index_seconds},'reader_node_count':len(reader['nodes']),'status':'actual explicit target found; source edition qualification retained'}
(ROOT/'explicit-positive.json').write_text(json.dumps(selection,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'body':body,'node':node,'timing':selection['timing']},indent=2))
