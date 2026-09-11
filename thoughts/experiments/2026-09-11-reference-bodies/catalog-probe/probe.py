"""Read-only, network-disabled catalog and publisher XML lookup probe.

Not a parser/service: query existing Parquet columns and publisher SECTION nodes.
Retain original XML bytes alongside a plainly labelled text rendering.
"""
from pathlib import Path
import hashlib,json,os,re,sys,socket,xml.etree.ElementTree as ET
from unittest.mock import patch
import pyarrow.parquet as pq
from spicy_regs.sources.cfr_sections import CfrSectionsReader
from spicy_regs.transforms.build_cfr_sections import _shape,COLUMNS
import spicy_regs.sources.cfr_sections as reader_module
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
CORPUS=Path('/Users/mikewolfd/Work/corpora/_salvage-2026-08-28/refspec-output/ecfr-title-xml-2026-08-24')
CATALOG=Path('/Users/mikewolfd/Work/spicy-regs/output/mixed-real-data-corpus-v2/cfr_sections.parquet')
manifest=json.loads((CORPUS/'manifest.json').read_text())
def sha(path):
 with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def write(name,value):
 with (ROOT/name).open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2)
refs=[{'id':'rail-definition','title':49,'section':'390.5','book':'thoughts/experiments/2026-09-10-evidence-catalog/inputs/rail-crossings/book.json','needle':'390.5'}, {'id':'alcohol-definition','title':49,'section':'382.107','book':'thoughts/experiments/2026-09-10-evidence-catalog/inputs/alcohol/book.json','needle':'382.107'}, {'id':'refrigerant-equipment','title':40,'section':'82.158','book':'thoughts/experiments/2026-09-10-evidence-catalog/inputs/refrigerants/book.json','needle':'82.158'}]
results={'network_calls':0,'scope':'3 reference occurrences; metadata catalog sample and2 pinned publisher title files, not corpuswide completeness','paths':{'home_corpora_exists':Path('/Users/mikewolfd/corpora').exists(),'work_corpora_exists':Path('/Users/mikewolfd/Work/corpora').exists()},'runtime':{'reader_module':reader_module.__file__,'reader_sha256':sha(reader_module.__file__)},'manifest_sha256':sha(CORPUS/'manifest.json')}
# Never permit a dependency to connect during this offline probe.
with patch.object(socket.socket,'connect',side_effect=RuntimeError('Network forbidden in offline probe')):
 keyless=CfrSectionsReader(api_key='');results['keyless_reader_records']=list(keyless.iter_records())
 # Existing reader test fixture is explicitly constructed, not a provider capture.
 g={'granuleId':'CFR-2024-title40-vol1-sec1-1','granuleClass':'CONTENT','title':'Definitions.','dateIssued':'2024-07-01'}
 reader=CfrSectionsReader(api_key='offline-fixture')
 with patch.object(reader,'_get',return_value={'granules':[g]}):
  raw=list(reader._iter_granules({'packageId':'CFR-2024-title40-vol1','lastModified':'2026-07-16T20:57:39Z','title':'Protection of Environment'}))
 results['constructed_reader_control']={'raw':raw,'shaped':[_shape(x) for x in raw],'has_body_field':any('text' in c or 'body' in c for c in COLUMNS)}
 results['catalog']={'path':str(CATALOG),'sha256':sha(CATALOG),'columns':pq.read_schema(CATALOG).names,'rows':pq.read_metadata(CATALOG).num_rows}
 for ref in refs:
  bookpath=REPO/ref['book'];b=json.loads(bookpath.read_text());text=b['document']['text'];at=text.index(ref['needle'])
  ref.update(book_sha256=sha(bookpath),source_document={k:v for k,v in b['document'].items() if k!='text'},original_context=text[max(0,at-180):at+200],source_reference_character=at)
  part,section=ref['section'].split('.',1)
  ref['catalog_hits']=pq.read_table(CATALOG,filters=[('title','=',str(ref['title'])),('part','=',part),('section','=',section)]).to_pylist()
 results['references']=refs
 results['publisher_titles']=[]
 for title in [49,40]:
  receipt=next(x for x in manifest['titles'] if x['title']==title);path=CORPUS/receipt['path'];digest=sha(path);assert digest==receipt['sha256']
  results['publisher_titles'].append({'receipt':receipt,'verified_sha256':digest,'verified_bytes':path.stat().st_size})
  wanted={r['section']:r for r in refs if r['title']==title};found={x:[] for x in wanted}; missing=[]
  # Existing stdlib XML parser reads publisher's TYPE and N attributes directly.
  # Clear completed SECTION nodes to keep memory bounded; no paragraph segmentation.
  for event,element in ET.iterparse(path,events=('end',)):
   if element.get('TYPE')=='SECTION':
    number=element.get('N')
    if number in wanted:
     content=''.join(element.itertext());found[number].append({'xml_tag':element.tag,'attributes':dict(element.attrib),'heading':element.findtext('HEAD'),'rendered_text':content})
    if number=='999999.999999':missing.append(number)
    element.clear()
  # Match the selected publisher node's original start/end bytes, preserving raw.
  raw=path.read_bytes()
  for section,ref in wanted.items():
   matches=found[section];ref['xml_match_count']=len(matches);ref['publisher_effective_date']=receipt['date'];ref['body_status']='different-edition candidate; source edition compatibility not established'
   ref['section_matches']=[]
   for index,match in enumerate(matches):
    tag=match['xml_tag'].encode();pattern=rb'<'+tag+rb'\b[^>]*\bN="'+re.escape(section.encode())+rb'"[^>]*>'
    starts=list(re.finditer(pattern,raw));assert len(starts)==len(matches)
    start=starts[index].start();end=raw.index(b'</'+tag+b'>',starts[index].end())+len(tag)+3;part=raw[start:end]
    parsed=ET.fromstring(part);assert parsed.get('TYPE')=='SECTION' and parsed.get('N')==section
    assert ''.join(parsed.itertext())==match['rendered_text']
    filename=f"{ref['id']}-{index}.xml";(ROOT/filename).write_bytes(part)
    (ROOT/f"{ref['id']}-{index}.txt").write_text(match.pop('rendered_text'))
    ref['section_matches'].append({**match,'raw_file':filename,'raw_sha256':hashlib.sha256(part).hexdigest(),'source_byte_start':start,'source_byte_end':end})
  results.setdefault('controls',[]).append({'type':'nonexistent-section','title':title,'section':'999999.999999','match_count':len(missing)})
 results['controls'].extend([{'type':'title-unspecified','citation':'§ 390.5','status':'ambiguous without document title context; no body lookup attempted'},{'type':'edition-unspecified','citation':'49 CFR 390.5','status':'edition unresolved; local XML is a dated candidate, not an automatic edition choice'}])
write('results.json',results)
print(json.dumps({'refs':[{k:r[k] for k in ('id','xml_match_count','publisher_effective_date','body_status')} for r in refs],'catalog':results['catalog'],'network_calls':0},indent=2))
