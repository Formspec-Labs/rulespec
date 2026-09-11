"""Retain actual eCFR readable outputs and exact source-map receipts, offline."""
from pathlib import Path
import hashlib,json,time,xml.etree.ElementTree as ET
from refspec.registry.ecfr import read_text
ROOT=Path(__file__).resolve().parent
REF=Path('/Users/mikewolfd/Work/RefSpec')
FIXTURES=REF/'tests/fixtures/ecfr-text'
rows=[]
for pin in json.loads((FIXTURES/'pins.json').read_text()):
 xml=(FIXTURES/pin['file']).read_bytes();assert hashlib.sha256(xml).hexdigest()==pin['sha256']
 start=time.monotonic();r=read_text(xml);elapsed=time.monotonic()-start
 source=''.join(ET.fromstring(xml).itertext());assert r['source_text']==source
 assert ''.join(r['text'][p['start']:p['end']] for p in r['source_map'] if p['kind']=='source')==source
 name=Path(pin['file']).stem
 (ROOT/(name+'.readable.txt')).write_text(r['text']);(ROOT/(name+'.reader.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 rows.append({'file':pin['file'],'input_sha256':pin['sha256'],'native_attributes':r['nodes']['/*[1]']['attributes'],'raw_decoded_chars':len(source),'readable_chars':len(r['text']),'inserted_chars':sum(p['end']-p['start'] for p in r['source_map'] if p['kind']=='inserted'),'node_count':len(r['nodes']),'table_cell_count':sum(n['tag'].upper() in {'TD','TH'} for n in r['nodes'].values()),'note_nodes':{tag:sum(n['tag']==tag for n in r['nodes'].values()) for tag in ['EDNOTE','EFFDNOT']},'source_map_exact':True,'single_observation_seconds':elapsed})
(ROOT/'results.json').write_text(json.dumps({'network_calls':0,'model_calls':0,'rows':rows,'uslm_parity':'15 real-fixture/mutation comparisons, zero differing result dictionaries','focused_tests':{'command':'PYTHONPATH=src .venv/bin/python -m pytest tests/test_uslm_text.py tests/test_ecfr_text.py tests/test_uslm_source_paths.py tests/test_extract_uslm_reference_edges.py -q','passed':93}},indent=2)+'\n')
paths=[REF/'src/refspec/registry'/n for n in ['uslm.py','ecfr.py','xml_text.py']]+[REF/'tests'/n for n in ['test_ecfr_text.py','uslm_text_oracle.py']]+sorted(FIXTURES.iterdir())
(ROOT/'source-freeze.json').write_text(json.dumps({str(p.relative_to(REF)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')
print(json.dumps(rows,indent=2))
