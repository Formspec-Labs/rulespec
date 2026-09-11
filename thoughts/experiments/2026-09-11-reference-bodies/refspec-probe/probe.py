"""Direct offline RefSpec interfaces; no new source parser or network calls."""
from dataclasses import asdict
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import csv, hashlib,json,subprocess,time
from refspec.input_pin import read_verified_file_pin
from refspec.registry.uslm import read_text,section_identifiers
from refspec.registry.usc_section_oracle import UscSectionOracle
ROOT=Path(__file__).resolve().parent
REF=Path('/Users/mikewolfd/Work/RefSpec')
ART=Path('/Users/mikewolfd/Work/corpora/_salvage-2026-08-28/refspec-output/usc-annual-2026-08-24')
RULE=Path('/Users/mikewolfd/Work/rulespec')
def save(name,value): (ROOT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
pin=next(row for row in csv.DictReader((ART/'fetch_log.tsv').read_text().splitlines(),delimiter='\t') if row['file']=='xml_uscAll_119-102.zip')
archive=read_verified_file_pin(ART/pin['file'],expected_sha256='sha256:'+pin['sha256'],expected_byte_length=int(pin['bytes']))
with ZipFile(BytesIO(archive)) as z: xml=z.read('usc38.xml')
start=time.monotonic();reader=read_text(xml);elapsed=time.monotonic()-start
assert '/us/usc/t38/s4301' in section_identifiers(xml)
source=RULE/'examples/document_understanding/composed-extraction-experiment/runs/leave/relationships/rulebook.json'
book=json.loads(source.read_text());doc=book['document'];quote='38 U.S.C. 4301, et seq.';at=doc['text'].index(quote)
save('source-reference.json',{'path':str(source),'sha256':sha(source.read_bytes()),'document_source_url':doc.get('source_url'),'document_sha256':doc['sha256'],'text':quote,'start':at,'end':at+len(quote),'surrounding_source':doc['text'][max(0,at-160):at+len(quote)+400],'requested_scope':'et seq. open-ended; section4301 is only the explicit anchor, not complete resolution'})
rows=[]
for identifier in ['/us/usc/t38/s4301','/us/usc/t38/s4301/a/1','/us/usc/t38/s4301/z']:
 matches=[dict(v,xpath=k) for k,v in reader['nodes'].items() if v.get('identifier')==identifier]
 assert len(matches)<=1
 if not matches:rows.append({'identifier':identifier,'status':'missing-in-selected-XML','fixture_role':'constructed-missing-selector'});continue
 node=matches[0];lo,hi=node['start'],node['end'];body=reader['text'][lo:hi];rawlo,rawhi=node['source_start'],node['source_end'];name='s4301' if identifier.endswith('s4301') else 's4301-a-1'
 (ROOT/(name+'.txt')).write_text(body)
 maps=[x for x in reader['source_map'] if x['start']<hi and x['end']>lo]
 save(name+'.selection.json',{'identifier':identifier,'xpath':node['xpath'],'node':node,'readable_text_sha256':sha(body.encode()),'decoded_source_text':reader['source_text'][rawlo:rawhi],'source_map_overlapping_title_ranges':maps,'method':reader['method'],'coordinates':'Unicode codepoints of whole-title readable/decoded text; not original XML byte offsets'})
 rows.append({'identifier':identifier,'status':'found','tag':node['tag'],'xpath':node['xpath'],'chars':len(body),'body_file':name+'.txt','selection_file':name+'.selection.json','fixture_role':'actual-reference-anchor' if identifier.endswith('s4301') else 'constructed-precise-selector-control'})
s=xml.decode();at=s.index('identifier="/us/usc/t38/s4301"');left=s.rfind('<section',0,at);right=s.index('</section>',at)+len('</section>')
(ROOT/'raw-s4301-context.xml.txt').write_text(s[max(0,left-180):right+180]);(ROOT/'raw-title-metadata.xml.txt').write_text(s[:1600])
oracle=UscSectionOracle.from_repository(REF)
save('oracle-results.json',{'interface':'UscSectionOracle.from_repository; section_verdict; subsection_verdict','current':asdict(oracle.section_verdict(38,'4301')),'edition_2024':asdict(oracle.section_verdict(38,'4301',2024)),'edition_1990_control':asdict(oracle.section_verdict(38,'4301',1990)),'a':asdict(oracle.subsection_verdict(38,'4301','a')),'missing_z':asdict(oracle.subsection_verdict(38,'4301','z')),'limitation':'Existence and coverage attestations, not provision body or edition-specific text.'})
try:
 read_verified_file_pin(ART/pin['file'],expected_sha256='sha256:'+'0'*64,expected_byte_length=int(pin['bytes']))
 raise AssertionError('wrong pin accepted')
except ValueError as exc: wrongpin=str(exc)
save('results.json',{'refspec_head':subprocess.check_output(['git','-C',str(REF),'rev-parse','HEAD'],text=True).strip(),'source_archive':{'path':str(ART/pin['file']),'pin':pin,'pin_verified':True},'member':{'name':'usc38.xml','sha256':sha(xml),'bytes':len(xml),'publication_name':'Online@119-102','metadata_file':'raw-title-metadata.xml.txt'},'reader':{'call':'refspec.registry.uslm.read_text(xml: bytes)','method':reader['method'],'title_read_seconds':elapsed,'title_readable_chars':len(reader['text']),'title_nodes':len(reader['nodes'])},'targets':rows,'wrong_pin_control':wrongpin,'source_files':{str(p):sha(p.read_bytes()) for p in [REF/'src/refspec/registry/uslm.py',REF/'src/refspec/registry/usc_section_oracle.py',REF/'src/refspec/input_pin.py']},'network_calls':0,'body_edition_limit':'Release119-102 body only; oracle attestation for2024 does not establish this is the2024 body.'})
print(json.dumps({'targets':rows,'seconds':elapsed,'wrong_pin_refused':True},indent=2))
