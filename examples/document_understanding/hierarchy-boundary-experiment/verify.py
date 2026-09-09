"""Check paired requests and replay whole-document and split-window captures."""
from pathlib import Path
from copy import deepcopy
import importlib.util,json,subprocess,sys
from rulespec_extrapolator import extraction as e

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('hierarchy_experiment',ROOT/'experiment.py')
h=importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def main():
    replay_root=Path(sys.argv[1]).resolve()
    replay_root.mkdir(parents=True,exist_ok=False)
    design=e._load(ROOT/'design.json')
    results=[]
    for s,mode,v,r in design['runs']:
        cell=[s,mode,v,r]
        run=ROOT/'runs'/s/mode/v/str(r)
        p=subprocess.run([sys.executable,str(ROOT/'experiment.py'),'replay',*map(str,cell),
            '--output',str(replay_root/s/mode/v/str(r))],capture_output=True,text=True)
        if p.returncode:
            raise RuntimeError('Replay failed: '+str(cell))
        book=e._load(run/'rulebook.json')
        doc=e._load(run/'document.json')
        checks=[]
        for i,w in enumerate(book['run']['windows']):
            name=f'attempt-{i:04d}'
            request=e._load(run/(name+'.request.json'))
            control=e._load(ROOT/'runs'/s/mode/'control/1'/(name+'.request.json'))
            base=e._canonical(h.ORIGINAL_CATALOG(doc,w))
            rich=e._canonical(h.hierarchy_catalog(doc,w))
            expected=deepcopy(control)
            if v=='hierarchy':
                assert expected['contents'].count(base)==1
                expected['contents']=expected['contents'].replace(base,rich,1)
            assert json.dumps(request)==json.dumps(expected), 'More than parent hints changed'
            response=e._load(run/(name+'.response.json'))
            text=''.join(p['text'] for p in response['candidates'][0]['content']['parts']
                if p.get('text') and not p.get('thought'))
            try:
                raw=json.loads(text)['extractions']
            except (ValueError,KeyError):
                raw=None
            accepted=[x for x in book['accepted'] if x['window_id']==w['id']]
            preserved=raw is not None and len(raw)==len(accepted) and all(all(a['unit_attributes'][x]==b[y]
                for x,y in [('statement','summary'),('scope_text','scope_text'),('kind','kind'),('modality','modality')])
                for a,b in zip(raw,accepted))
            usage=response['usage_metadata']
            checks.append({'window':i,'raw_rows':None if raw is None else len(raw),'accepted':len(accepted),
                'raw_json_valid':raw is not None,
                'only_declared_metadata_changed':True,'raw_meaning_preserved':preserved,
                'tokens':usage['total_token_count'],'prompt_tokens':usage['prompt_token_count'],
                'output_tokens':usage['candidates_token_count'],'thought_tokens':usage.get('thoughts_token_count',0),
                'finish_reason':response['candidates'][0].get('finish_reason'),
                'request_sha256':e._digest((run/(name+'.request.json')).read_bytes()),
                'response_sha256':e._digest((run/(name+'.response.json')).read_bytes())})
        results.append({'cell':cell,'replay_identical':True,'status':book['run']['status'],
            'accepted':len(book['accepted']),'rejected':len(book['rejected']),
            'refusals':len(book['extraction_refusals']),'validation':e._load(run/'validation.json'),
            'attempts':checks})
    total=sum(a['tokens'] for r in results for a in r['attempts'])
    calls=sum(len(r['attempts']) for r in results)
    assert calls==design['provider_calls']
    e._save(ROOT/'verification.json',{'provider_calls':calls,'replay_provider_calls':0,
        'total_reported_tokens':total,'results':results})
    print(e._canonical({'replayed':len(results),'provider_calls':calls,'reported_tokens':total}))

if __name__=='__main__':
    main()
