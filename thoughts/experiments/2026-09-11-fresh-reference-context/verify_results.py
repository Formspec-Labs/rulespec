"""Replay captured processing and record deterministic loss/usage diagnostics."""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from rulespec_extrapolator import extraction as ex
from rulespec_extrapolator import core
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import source_passages

HERE = Path(__file__).resolve().parent
load, save = ex._load, ex._save
for name, digest in load(HERE / 'prerun-pins.json').items():
    assert ex._digest((HERE / name).read_bytes()) == digest, name

results, failures = [], []
usage = defaultdict(Counter)
schema = load(HERE / 'frozen/provider-schema.json')
for cell in load(HERE / 'cells.json'):
    directory = HERE / 'cells' / cell['id']
    doc = load(directory / 'document.json')
    run = load(directory / 'run.json')
    window = load(HERE / 'contexts' / (cell['case']+'.json'))[cell['arm']]
    # Select the attempt metadata explicitly, not a glob's platform order.
    attempt = load(directory / f"attempt-{window['index']:04d}.json")
    request = load(directory / attempt['request_file'])
    raw = load(directory / attempt['response_file'])
    prompt = (HERE / 'prompts' / (cell['case']+'.'+cell['arm']+'.txt')).read_text()
    assert request['contents'] == prompt
    assert request['model'] == 'gemini-3.8-flash'
    assert request['config']['response_json_schema'] == schema
    assert request['config']['thinking_config'] == {'thinking_level':'low'}
    assert request['config']['temperature'] == 0
    assert request['config']['max_output_tokens'] == 16384
    assert request['config']['candidate_count'] == 1
    for name, digest in load(directory / 'manifest.json')['artifacts_sha256'].items():
        assert ex._digest((directory / name).read_bytes()) == digest, (cell['id'],name)
    parsed = ex._attempt_result(attempt,directory,doc,window)
    assert parsed['candidates'] == load(directory / 'candidates.json')
    assert parsed['refusals'] == load(directory / 'refusals.json')
    book = core.compile_candidates(doc,parsed['candidates'],run)
    book['extraction_refusals'] = parsed['refusals']
    assert book == load(directory / 'rulebook.json')
    discovery = export_discovery(book,include_references=True)
    assert discovery == load(directory / 'discovery.json')
    passages = source_passages(doc)
    assert [(r['id'],r['text']) for r in discovery['records']] == [(p['id'],doc['text'][p['start']:p['end']]) for p in passages]
    for identity, evidence in discovery['evidence'].items():
        start,end = evidence['start'],evidence['end']
        support = core._evidence(doc,doc['text'][start:end],'source',start,end)
        assert support is not None and support['fragment_id'] == identity
    row = {**cell,'finish_reason':raw['candidates'][0]['finish_reason'],
           'status':run['status'],'candidates':len(parsed['candidates']),
           'accepted':len(book['accepted']),'core_rejected':len(book['rejected']),
           'parse_refusals':dict(Counter(r['code'] for r in parsed['refusals'])),
           'core_reasons':dict(Counter(r['reason'] for r in book['rejected'])),
           'source_records':len(discovery['records']),'verified_export_fragments':len(discovery['evidence']),
           'usage':ex.recorded_usage(directory),'model_version':raw.get('model_version')}
    usage[cell['arm']].update(row['usage']['tokens'])
    for rejected in book['rejected']:
        c = rejected['candidate'];start,end = c['start'],c['end']
        inserted = [dict(start=max(start,p['start']),end=min(end,p['end']),
                         text=doc['text'][max(start,p['start']):min(end,p['end'])])
                    for p in doc.get('source_map',[]) if p['kind']!='source' and p['start']<end and start<p['end']]
        failures.append({'cell':cell['id'],'stage':'core','candidate_index':rejected['index'],
                         'reason':rejected['reason'],'range':[start,end],
                         'exact_prepared_quote':doc['text'][start:end]==c['quote'], 'inserted':inserted})
    catalog = ex.passage_catalog(doc,window)
    focused = [p for p in passages if p['start']<window['end'] and p['end']>window['start']]
    for refusal in parsed['refusals']:
        if refusal['code'] != 'passage_not_in_request':
            continue
        ref = refusal['raw']['unit']; match = re.fullmatch(r'(F|C)(\d+):\1(\d+)',ref)
        missing = []
        if match:
            for number in range(int(match[2]),int(match[3])+1):
                identifier = f'{match[1]}{number:03d}'
                if identifier not in catalog:
                    passage = focused[number] if match[1]=='F' and number<len(focused) else None
                    missing.append({'id':identifier,'text':doc['text'][passage['start']:passage['end']] if passage else None})
        failures.append({'cell':cell['id'],'stage':'passage','row_index':refusal['row_index'],'unit':ref,'missing':missing})
    answer = ''.join(p['text'] for c in raw['candidates'] for p in c['content']['parts'] if p.get('text') and not p.get('thought'))
    try:
        payload = json.loads(answer)
        attrs = [r['unit_attributes'] for r in payload['extractions']]
        row.update(raw_rows=len(attrs),null_fields=sum(v is None for a in attrs for v in a.values()),
                   literal_null_strings=sum(v=='null' for a in attrs for v in a.values() if isinstance(v,str)))
    except json.JSONDecodeError:
        row['raw_rows'] = None
    results.append(row)
    print(json.dumps({k:row[k] for k in ('id','accepted','core_rejected','core_reasons')}),flush=True)

summary = {'status':'replay_and_export_checks_passed','calls':len(results),
           'provider_incomplete':sum(r['finish_reason']!='STOP' for r in results),
           'usage_by_arm':{k:dict(v) for k,v in usage.items()},
           'mean_total_token_ratio_B_over_A':usage['B']['total_token_count']/usage['A']['total_token_count'],
           'preserved_source_records_and_verified_export_fragments':True,
           'semantic_quality':'manual labels in raw-review.md; these checks do not establish completeness'}
save(HERE / 'processing-checks.json',{'summary':summary,'cells':results,'losses':failures})
print(json.dumps(summary),flush=True)
