"""Replay native extraction and checker captures with provider access blocked."""
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import run as x
from rulespec_extrapolator import audit as a, extraction as e, refinement as r


def restore_frozen(directory):
    # Each capture's original manifest independently verifies these shared bytes.
    if not (directory/'frozen').exists():
        shutil.copytree(x.HERE/'extract/privacy/frozen', directory/'frozen')


def main():
    x.pins(); x.pins('check-pins.json'); report={'extractions':[],'checks':[]}
    with patch.object(e,'_create_model',side_effect=AssertionError('Provider calls blocked')):
        with tempfile.TemporaryDirectory() as tmp:
            for name in x.NAMES:
                directory=x.HERE/'extract'/name
                restore_frozen(directory)
                book=e._load(directory/'rulebook.json')
                assert e.replay_run(directory,Path(tmp)/name)==book
                request=e._load(directory/'attempt-0000.request.json')
                assert not {'temperature','top_p','top_k','candidate_count'} & request['config'].keys()
                assert request['config']['thinking_config']=={'thinking_level':'low'}
                report['extractions'].append(dict(name=name,status=book['run']['status'],claims=len(book['accepted']),replayed=True))
        with tempfile.TemporaryDirectory() as tmp:
            sparse=Path(tmp)/'sparse'
            shutil.copytree(x.HERE/'extract/credit',sparse,ignore=shutil.ignore_patterns('frozen'))
            restore_frozen(sparse)
            assert e.replay_run(sparse,Path(tmp)/'replayed')==e._load(x.HERE/'extract/credit/rulebook.json')
            report['shared_runtime_restore_verified']=True
        for name in e._load(x.HERE/'cells.json'):
            data=e._load(x.HERE/f'inputs/{name}.json'); directory=x.HERE/'captures'/name
            attempt=e._load(directory/'attempt.json')
            request=e._load(directory/attempt['request_file'])
            assert request==dict(model=e.DEFAULT_MODEL,contents=data['prompt'],config=dict(max_output_tokens=32768,
                response_mime_type='application/json',response_json_schema=r.CHECK_SCHEMA,thinking_config=dict(thinking_level='medium')))
            payload,errors=a._read_response(directory,attempt)
            judgments,issues=r._decode_checks(payload,errors,data['candidates'],data['document'],data['packet'])
            assert dict(payload=payload,errors=errors,judgments=judgments,issues=issues)==e._load(x.HERE/f'decoded/{name}.json')
            report['checks'].append(dict(cell=name,judgments=len(judgments),issues=issues,redecoded=True))
    report['usage']=x.usage()
    report['call_seconds']=sum(c['seconds'] for c in e._load(x.HERE/'calls.json'))
    e._save(x.HERE/'verification.json',report)
    print('Eight native extractions and all checker captures verified without provider access.')


if __name__=='__main__': main()
