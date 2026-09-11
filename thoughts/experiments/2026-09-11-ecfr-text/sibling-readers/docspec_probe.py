"""Offline native XML visible-text and local-file API probe; no segmentation."""
from pathlib import Path
import dataclasses,hashlib,json,socket
from unittest.mock import patch
from docspec.processing.visible_text import XmlVisibleTextExtractor,VisibleTextError
import docspec.processing.visible_text as visible_module
from docspec.adapters.content_fetchers import LocalFileContentFetcher
from docspec.domain.content import CandidateFile
ROOT=Path(__file__).resolve().parent
INPUT=ROOT.parents[1]/'2026-09-11-reference-bodies/catalog-probe'
# Actual files plus controls for unsupported inherited container/table layout.
inputs={p.stem:p.read_bytes() for p in sorted(INPUT.glob('*-0.xml'))}
controls={'table-empty-cells':b'<DIV8><HEAD>Control</HEAD><TABLE><TR><TH>Type</TH><TH>Limit</TH></TR><TR><TD></TD><TD>20</TD></TR><TR><TD>A</TD><TD></TD></TR></TABLE></DIV8>','mixed-blocks':b'<DIV8>Lead-in<P>Child one</P><P>Child two</P></DIV8>','malformed':b'<DIV8><P>broken</DIV8>','entity-unicode':b'<DIV8><P>Alpha &amp; beta \xe2\x80\x89 unless waived.</P></DIV8>'}
results={'network_calls':0,'segmentation_calls':0,'module_path':visible_module.__file__,'module_sha256':hashlib.sha256(Path(visible_module.__file__).read_bytes()).hexdigest(),'cases':[]}
with patch.object(socket.socket,'connect',side_effect=RuntimeError('Offline only')):
 for name,raw in {**inputs,**controls}.items():
  for arm,extractor in [('defaults',XmlVisibleTextExtractor()),('head-config',XmlVisibleTextExtractor(heading_levels={'HEAD':1}))]:
   case={'input':name,'constructed':name in controls,'input_sha256':hashlib.sha256(raw).hexdigest(),'arm':arm,'configuration':extractor.configuration}
   try:
    output=extractor.extract(raw);body=output.content.decode(); filename=f'{name}.{arm}.txt';(ROOT/filename).write_text(body)
    ranges=[]
    for marker in ['Business district','suspended indefinitely','Alcohol means','Starting January 1, 2017','Alpha & beta','20']:
     at=output.content.find(marker.encode())
     if at>=0:
      low,high=output.rendition_range(at,at+len(marker.encode()));ranges.append({'selected_text':marker,'representation_start':at,'representation_end':at+len(marker.encode()),'source_start':low,'source_end':high,'raw_source_fragment':raw[low:high].decode()})
    case.update(output_file=filename,output_bytes=len(output.content),metadata=dict(output.metadata),blocks=[dataclasses.asdict(x) for x in output.blocks],runs=[dataclasses.asdict(x) for x in output.runs],sampled_ranges=ranges)
   except VisibleTextError as e:case['error']={'reason_code':e.reason_code,'reason':e.reason}
   results['cases'].append(case)
 # Existing local fetcher streams selected whole files; no XML section resolution.
 name=next(iter(inputs));raw=inputs[name]; candidate=CandidateFile(candidate_id='offline-probe',locator=name+'.xml',media_type='application/xml',expected_size=len(raw),expected_digest='sha256:'+hashlib.sha256(raw).hexdigest())
 fetcher=LocalFileContentFetcher(INPUT)
 with fetcher.fetch(candidate,max_bytes=len(raw),task_id='probe',attempt_id='1') as stream:got=b''.join(stream.chunks)
 results['local_fetch']={'candidate':candidate.to_dict(),'byte_identical':got==raw}
 try:fetcher.fetch(candidate,max_bytes=len(raw)-1,task_id='probe',attempt_id='2')
 except Exception as e:results['local_fetch']['undersized_bound_refusal']={'type':type(e).__name__,'message':str(e)}
with (ROOT/'docspec-results.json').open('x') as f:json.dump(results,f,ensure_ascii=False,indent=2)
print(json.dumps({'actual_sources':len(inputs),'case_arms':len(results['cases']),'local_fetch':results['local_fetch'],'outcomes':[{'input':c['input'],'arm':c['arm'],'metadata':c.get('metadata'),'error':c.get('error')} for c in results['cases']]},indent=2))
