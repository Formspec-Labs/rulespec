"""Run a new checker against saved inventories; replay without model calls."""
import argparse, shutil
from pathlib import Path
from rulespec_extrapolator import audit as a, extraction as e
R=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('run','replay'));p.add_argument('cell');p.add_argument('--env-file',type=Path)
 args=p.parse_args();d=e._load(R/'design.json');old=R.parent/'low-extract-high-audit/runs'/args.cell
 for name,digest in d['inputs_sha256'].items():
  if e._digest((R.parent/name).read_bytes())!=digest:raise ValueError('Pinned input changed')
 if {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()}!=d['runtime_sources_sha256']:raise ValueError('Runtime changed')
 saved=a.load_audit(old);book=saved['book'];labels=saved['labels'];windows=saved['run']['windows'];run=R/'runs'/args.cell
 generator=e._prompt_generator([],a.comparison_prompt())
 prompts=[e._window_prompt(generator,book['document'],w)+'\nDraft and inventory: '+e._canonical(a._model_input(a._comparison_input(book,labels,w)[0])) for w in windows]
 if args.mode=='run':
  run.mkdir(parents=True,exist_ok=False)
  for name,path in e._runtime_sources().items():
   target=run/'frozen'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
  e._save(run/'configuration.json',{'prompt':a.comparison_prompt(),'schema':a.COMPARISON_SCHEMA,'source_audit':str(old),'source_manifest_sha256':e._digest((old/'manifest.json').read_bytes())})
  attempts=a._capture(run/'comparison',book['document'],windows,prompts,a.COMPARISON_SCHEMA,e.DEFAULT_MODEL,e._credential(args.env_file),None,max_output_tokens=None,thinking_level='high')
  e._save(run/'attempts.json',attempts)
 else:
  e._verify_manifest(run);attempts=e._load(run/'attempts.json')
 for i,attempt in enumerate(attempts):
  if attempt.get('request_file'):
   req=e._load(run/'comparison'/attempt['request_file']);base=e._load(old/'comparison'/attempt['request_file'])
   expected={**base,'contents':prompts[i]}
   if req!=expected:raise ValueError('Unexpected request difference')
 judgments,issues=a._judgments(run/'comparison',book,labels,windows,attempts,e.DEFAULT_MODEL)
 report=a._assessment(book,labels,judgments,issues)
 if args.mode=='run':
  e._save(run/'judgments.json',judgments);e._save(run/'report.json',report);e._write_manifest(run)
 else:
  if judgments!=e._load(run/'judgments.json') or report!=e._load(run/'report.json'):raise ValueError('Replay differs')
 print(e._canonical({'cell':args.cell,'mode':args.mode,'assessment':report['status'],'review_complete':report['review_complete'],'audit_issues':report['audit_issues'],'issues':report['issues']}),flush=True)
if __name__=='__main__':main()
