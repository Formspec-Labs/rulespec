"""Replay captures and isolate thinking-level changes for each source."""
from pathlib import Path
from copy import deepcopy
import json,subprocess,sys
from rulespec_extrapolator import extraction as e
R=Path(__file__).resolve().parent


def main():
    out=Path(sys.argv[1]).resolve();out.mkdir(parents=True,exist_ok=False)
    design=e._load(R/'design.json');results=[]
    for name,cell in design['runs'].items():
        run=R/'runs'/name
        p=subprocess.run([sys.executable,str(R/'experiment.py'),'replay',name,'--output',str(out/name)],capture_output=True,text=True)
        if p.returncode:raise RuntimeError('Replay failed: '+name)
        book=e._load(run/'rulebook.json');attempts=[]
        for i,w in enumerate(book['run']['windows']):
            stem=f'attempt-{i:04d}'
            req=e._load(run/(stem+'.request.json'));resp=e._load(run/(stem+'.response.json'))
            reference=R.parent/'thinking-level-experiment/provider-limit/runs'/f"{cell['sample']}-high-1"/(stem+'.request.json')
            expected=deepcopy(e._load(reference));expected['config']['thinking_config']={'thinking_level':cell['thinking_level']}
            assert json.dumps(req)==json.dumps(expected), 'Unplanned request change'
            assert 'max_output_tokens' not in req['config']
            assert req['config']['thinking_config']=={'thinking_level':cell['thinking_level']}
            text=''.join(p['text'] for p in resp['candidates'][0]['content']['parts'] if p.get('text') and not p.get('thought'))
            try:rows=json.loads(text)['extractions']
            except (ValueError,KeyError):rows=None
            accepted=[a for a in book['accepted'] if a['window_id']==w['id']]
            same=rows is not None and len(rows)==len(accepted) and all(all(x['unit_attributes'][a]==y[b] for a,b in [('statement','summary'),('scope_text','scope_text'),('kind','kind'),('modality','modality')]) for x,y in zip(rows,accepted))
            u=resp['usage_metadata']
            attempts.append({'window':i,'raw_json_valid':rows is not None,'raw_rows':None if rows is None else len(rows),
                'raw_meaning_preserved':same,'accepted':len(accepted),'finish_reason':resp['candidates'][0].get('finish_reason'),
                'tokens':u['total_token_count'],'prompt_tokens':u['prompt_token_count'],'output_tokens':u['candidates_token_count'],
                'thought_tokens':u.get('thoughts_token_count',0),'request_sha256':e._digest((run/(stem+'.request.json')).read_bytes()),
                'response_sha256':e._digest((run/(stem+'.response.json')).read_bytes())})
        results.append({'cell':name,**cell,'replay_identical':True,'status':book['run']['status'],
            'accepted':len(book['accepted']),'refusals':len(book['extraction_refusals']),'rejected':len(book['rejected']),
            'validation':e._load(run/'validation.json'),'attempts':attempts})
    calls=sum(len(r['attempts']) for r in results);tokens=sum(a['tokens'] for r in results for a in r['attempts'])
    assert calls==design['provider_calls']
    e._save(R/'verification.json',{'provider_calls':calls,'replay_provider_calls':0,'total_reported_tokens':tokens,'results':results})
    print(e._canonical({'replayed':len(results),'provider_calls':calls,'tokens':tokens}))

if __name__=='__main__':main()
