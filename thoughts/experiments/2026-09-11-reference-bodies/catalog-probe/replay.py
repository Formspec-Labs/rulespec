"""Reconstruct saved section slices from pinned original title bytes, offline."""
from pathlib import Path
import hashlib,json,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'results.json').read_text())
corpus=Path('/Users/mikewolfd/Work/corpora/_salvage-2026-08-28/refspec-output/ecfr-title-xml-2026-08-24')
checks=[]
for title in r['publisher_titles']:
 path=corpus/title['receipt']['path']
 with path.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==title['verified_sha256']
 for ref in r['references']:
  if ref['title']!=title['receipt']['title']:continue
  for s in ref['section_matches']:
   with path.open('rb') as f:f.seek(s['source_byte_start']);raw=f.read(s['source_byte_end']-s['source_byte_start'])
   assert raw==(ROOT/s['raw_file']).read_bytes()
   assert hashlib.sha256(raw).hexdigest()==s['raw_sha256']
   assert ''.join(ET.fromstring(raw).itertext())==(ROOT/s['raw_file'].replace('.xml','.txt')).read_text()
   checks.append(ref['id'])
out={'network_calls':0,'status':'all pinned title hashes, exact source byte slices, and derived text renderings reproduced','references':checks}
if (ROOT/'replay.json').exists():assert out==json.loads((ROOT/'replay.json').read_text())
else:
 with (ROOT/'replay.json').open('x') as f:json.dump(out,f,indent=2)
print(json.dumps(out))
