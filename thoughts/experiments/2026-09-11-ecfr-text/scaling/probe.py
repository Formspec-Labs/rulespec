"""One full pinned title per process; retain measurements, never copy full XML."""
from pathlib import Path
import hashlib,json,platform,resource,subprocess,sys,time
from refspec.input_pin import read_verified_file_pin
from refspec.registry.ecfr import read_text
ROOT=Path(__file__).resolve().parent
REF=Path('/Users/mikewolfd/Work/RefSpec')
ART=Path('/Users/mikewolfd/Work/corpora/_salvage-2026-08-28/refspec-output/ecfr-title-xml-2026-08-24')
title=int(sys.argv[1]);out=ROOT/f'title-{title}.json';assert not out.exists()
def run(cmd):return subprocess.check_output(cmd,text=True).strip()
def sha(b):return hashlib.sha256(b).hexdigest()
modules={str(p.relative_to(REF)):sha(p.read_bytes()) for p in [REF/'src/refspec/registry'/name for name in ['uslm.py','ecfr.py','xml_text.py']]}
frozen=json.loads((ROOT.parent/'upstream/source-freeze.json').read_text())
assert all(frozen[n]==v for n,v in modules.items())
manifest=json.loads((ART/'manifest.json').read_text());pin=next(x for x in manifest['titles'] if x['title']==title)
preflight={cmd[0]:run(cmd) for cmd in [['memory_pressure','-Q'],['sysctl','vm.swapusage'],['vm_stat'],['uptime']]}
receipt={'title':title,'input':{'path':str(ART/pin['path']),'manifest_sha256':sha((ART/'manifest.json').read_bytes()),'pin':pin},'modules':modules,'platform':platform.platform(),'python':sys.version,'rss_units':'bytes on Darwin; KiB on Linux','preflight':preflight,'network_calls':0,'status':'started'}
(ROOT/f'title-{title}-start.json').write_text(json.dumps(receipt,indent=2)+'\n')
start=time.monotonic();cpu=time.process_time()
try:
 xml=read_verified_file_pin(ART/pin['path'],expected_sha256='sha256:'+pin['sha256'],expected_byte_length=pin['bytes'])
 receipt['input_read_and_verify_seconds']=time.monotonic()-start
 read_start=time.monotonic();read_cpu=time.process_time();data=read_text(xml)
 receipt.update(reader_seconds=time.monotonic()-read_start,reader_cpu_seconds=time.process_time()-read_cpu,reader_max_rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 receipt['counts']={'input_bytes':len(xml),'source_chars':len(data['source_text']),'readable_chars':len(data['text']),'nodes':len(data['nodes']),'source_map_entries':len(data['source_map']),'inserted_entries':sum(p['kind']=='inserted' for p in data['source_map']),'table_cells':sum(n['tag'].upper() in {'TD','TH'} for n in data['nodes'].values()),'sections':sum(n['attributes'].get('TYPE')=='SECTION' for n in data['nodes'].values())}
 cursor=source_cursor=0
 for part in data['source_map']:
  assert part['start']==cursor;cursor=part['end']
  text=data['text'][part['start']:part['end']]
  if part['kind']=='source':
   assert part['source_start']==source_cursor;source_cursor=part['source_end']
   assert text==data['source_text'][part['source_start']:part['source_end']]
  else:assert text==part['text'] and text.isspace()
 assert cursor==len(data['text']) and source_cursor==len(data['source_text'])
 receipt.update(status='complete',source_map_exact=True,total_seconds=time.monotonic()-start,total_cpu_seconds=time.process_time()-cpu,final_max_rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,postflight={'memory_pressure':run(['memory_pressure','-Q']),'swap':run(['sysctl','vm.swapusage'])})
except Exception as exc:
 receipt.update(status='refused-or-failed',error_type=type(exc).__name__,error=str(exc),total_seconds=time.monotonic()-start,max_rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
