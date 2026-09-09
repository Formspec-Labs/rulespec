"""Compare one native CUE description through normal extraction and replay."""
import argparse
from pathlib import Path
import random
import tempfile
from unittest.mock import patch

from langextract.providers.schemas.gemini import GeminiSchema
from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent


def verify(directory):
    for name,digest in e._load(directory/'manifest.json')['artifacts_sha256'].items():
        assert e._digest((directory/name).read_bytes()) == digest, name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run','replay'))
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    design = e._load(ROOT/'design.json')
    for name,digest in design['inputs_sha256'].items():
        assert e._digest((ROOT/name).read_bytes()) == digest, name
    assert {n:e._digest(p.read_bytes()) for n,p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    schemas = {arm:e._load(ROOT/(arm+'-schema.json')) for arm in ('B','T')}
    results = {}
    for cell in design['cells']:
        case,arm = cell.split('/')
        directory = ROOT/'runs'/case/arm
        # The only override supplies the experimental, native-generated response schema.
        with patch.object(e, 'provider_schema', lambda: GeminiSchema(schemas[arm], _use_json_schema=True)):
            if args.mode == 'run':
                book = e.extract_run(e._load(ROOT/'fixtures'/(case+'.json')),directory,
                    model_id=e.DEFAULT_MODEL,env_file=args.env_file,max_chars=24000,
                    temperature=0,max_output_tokens=None,thinking_level='low')
            else:
                verify(directory)
                with tempfile.TemporaryDirectory(prefix='rulespec-standalone-replay-') as replay:
                    book = e.replay_run(directory,Path(replay)/'replay')
                assert book == e._load(directory/'rulebook.json')
        run = e._load(directory/'run.json')
        assert len(run['windows']) == 1 and len(run['windows'][0]['attempts']) == 1
        attempt = e._load(directory/run['windows'][0]['attempts'][0])
        if attempt.get('request_file'):
            request = e._load(directory/attempt['request_file'])
            expected = {'model':e.DEFAULT_MODEL,'contents':design['prompts'][case],'config':{
                'temperature':0,'candidate_count':1,'thinking_config':{'thinking_level':'low'},
                **GeminiSchema(schemas[arm], _use_json_schema=True).to_provider_config()}}
            assert request == expected
            assert list(request['config']['response_json_schema']['properties']['extractions']['items']['properties']['unit_attributes']['properties']) == list(
                schemas[arm]['properties']['extractions']['items']['properties']['unit_attributes']['properties'])
        raw = e._load(directory/attempt['response_file']) if attempt.get('response_file') else {}
        row = {'accepted':len(book['accepted']),'rejected':len(book['rejected']),
            'refusals':book['extraction_refusals'],'status':book['run']['status'],
            'usage':raw.get('usage_metadata'),'finish_reason':raw.get('candidates',[{}])[0].get('finish_reason'),
            'started_at':attempt['started_at'],'finished_at':attempt['finished_at']}
        results[cell] = row
        print(cell,row['status'],row['accepted'],'accepted',row['rejected'],'rejected',len(row['refusals']),'refusals',flush=True)
    if args.mode == 'run':
        e._save(ROOT/'results.json',results)
        packet,mapping = {},{}
        for case in design['cases']:
            arms=['B','T'];random.SystemRandom().shuffle(arms)
            packet[case]={}
            for index,arm in enumerate(arms):
                label=f'R{index+1}'
                mapping[case+'/'+label]=arm
                book=e._load(ROOT/'runs'/case/arm/'rulebook.json')
                # Preserve candidate order for source traceability; hide arm and evidence syntax.
                packet[case][label]=[{k:c.get(k) for k in ('kind','summary','scope_text','logic_text','modality','choice_text')}
                    for c in book['accepted']]
        e._save(ROOT/'blind-review.json',packet)
        e._save(ROOT/'review-key.json',mapping)
    else:
        assert results == e._load(ROOT/'results.json')
        print('All eight full extraction replays identical; no provider calls.')


if __name__ == '__main__':
    main()
