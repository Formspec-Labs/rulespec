"""Measure saved requests; serialized characters are not billed token counts."""
from collections import Counter
import json
from pathlib import Path

from rulespec_extrapolator import extraction as e

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-09-13-csbg-retest'


def measure(arm):
    directory = BASE / arm
    run = e._load(directory / 'run.json')
    doc = e._load(directory / 'document.json')
    section_index = [{'label':s['label'], 'start':s['start'], 'end':s['end']}
        for s in doc['sections']]
    index_chars = len(e._canonical(section_index))
    rows = []
    for i, window in enumerate(run['windows']):
        request = e._load(directory / f'attempt-{i:04d}.request.json')
        response = e._load(directory / f'attempt-{i:04d}.response.json')
        catalog = e.passage_catalog(doc, window)
        serialized = e._canonical(catalog)
        assert serialized in request['contents']
        assert e.PROMPT in request['contents']
        compact = e._canonical({key:value['text'] for key,value in catalog.items()})
        text = ''.join(part.get('text','') for candidate in response.get('candidates',[])
            for part in candidate.get('content',{}).get('parts',[]) if not part.get('thought'))
        rows.append(dict(index=i, section_labels=[s['label'] for s in doc['sections']
            if s['start'] < window['end'] and s['end'] > window['start']],
            focus_chars=window['end']-window['start'],
            source_text_chars_in_catalog=sum(len(v['text']) for v in catalog.values()),
            contents_chars=len(request['contents']), catalog_chars=len(serialized),
            catalog_without_offsets_chars=len(compact),
            schema_chars=len(e._canonical(request['config']['response_json_schema'])),
            instruction_chars=len(e.PROMPT), section_index_chars=index_chars,
            raw_answer_chars=len(text), candidate_count=window.get('candidate_count',0),
            status=window['status'], usage=response.get('usage_metadata',{})))
    fields = ('focus_chars','source_text_chars_in_catalog','contents_chars','catalog_chars',
        'catalog_without_offsets_chars','schema_chars','instruction_chars','section_index_chars','raw_answer_chars')
    return dict(calls=len(rows), usage=e.recorded_usage(directory), windows=rows,
        serialized_character_totals={field:sum(r[field] for r in rows) for field in fields})


if __name__ == '__main__':
    result = {'basis':'Exact saved source/request/answer character counts; token usage is provider-recorded separately. No estimated character reduction is a measured token, cost or quality improvement.',
        'arms':{arm:measure(arm) for arm in ('A','B')}}
    with (HERE / 'profile.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    for arm,data in result['arms'].items():
        print(arm,json.dumps(data['serialized_character_totals']))
        print('small windows',[(w['index'],w['focus_chars'],w['candidate_count'],w['usage'].get('prompt_token_count')) for w in data['windows'] if w['focus_chars']<2400])
