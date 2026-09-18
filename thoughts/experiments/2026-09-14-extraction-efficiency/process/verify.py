"""Provider-free integrity, size accounting and explicit Core compatibility rehearsal."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
from rulespec_extrapolator import audit, core, extraction as e

HERE=Path(__file__).resolve().parent
results=e._load(HERE/'results.json');inputs=e._load(HERE/'inputs.json')
schemas=e._load(HERE/'schemas.json');doc=e._load(HERE/'document.json')
pins=e._load(HERE/'pins.json')
assert all(sha256(Path(path).read_bytes()).hexdigest()==digest for path,digest in pins.items())
sizes={};compilation={}
for name,result in results.items():
    data=inputs[name];directory=HERE/'captures'/name
    request=e._load(directory/'attempt-0000.request.json')
    assert request['model']=='gemini-3.8-flash' and request['contents']==data['prompt']
    assert request['config']==dict(max_output_tokens=16384,response_mime_type='application/json',
        response_json_schema=schemas[data['arm']],thinking_config=dict(thinking_level='low'))
    attempt=e._load(directory/'attempt-0000.json');payload,errors=audit._read_response(directory,attempt)
    assert not errors and not result['schema_errors']
    assert not [i for row in result['rows'] for i in row['issues']]
    spans=[p for row in result['rows'] for role in ('main','governing') for p in row['components'][role]]
    covered=set(pos for p in spans for pos in range(p['start'],p['end']))
    generated='\n'.join(row['attributes'].get('statement','') for row in result['rows']).strip()
    rendered='\n'.join(p['quote'] for row in result['rows'] for role in ('governing','main') for p in row['components'][role])
    sizes[name]=dict(arm=data['arm'],source=data['source'],rows=len(result['rows']),
        raw_generated_statement_words=len(generated.split()),quoted_reading_words=len(rendered.split()),
        quote_characters=sum(p['end']-p['start'] for p in spans),unique_quote_characters=len(covered),
        source_characters=data['window']['end']-data['window']['start'],
        literal_actor_rows=sum(bool(r['attributes'].get('actor')) for r in result['rows']))
    if data['arm']=='B':
        # An explicit experiment-only adapter. It does not reclassify model errors,
        # assert quote selection correct or adopt a new interpretation profile.
        transformed=deepcopy(payload)
        for raw,row in zip(transformed['extractions'],result['rows']):
            attrs=raw['unit_attributes'];attrs.pop('unresolved_references',None)
            attrs['scope_text']='\n'.join(p['quote'] for p in row['components']['governing']) or None
            attrs['statement']='\n'.join(p['quote'] for role in ('governing','main') for p in row['components'][role])
        parsed=e.parse_response_text(json.dumps(transformed),doc,data['window'])
    else:
        parsed=e.parse_response_text(json.dumps(payload),doc,data['window'])
    book=core.compile_candidates(doc,parsed['candidates'],{'model':'Research-only deterministic source assembly compatibility rehearsal' if data['arm']=='B' else 'Current baseline compatibility rehearsal'})
    compilation[name]=dict(parsed_candidates=len(parsed['candidates']),parse_refusals=parsed['refusals'],
        accepted=len(book['accepted']),rejected=book['rejected'],
        accepted_issues=[dict(summary=c['summary'],issues=c['issues']) for c in book['accepted'] if c['issues']],
        graph_validation=core.validate_graph(book['graph']))
e._save(HERE/'sizes.json',sizes)
e._save(HERE/'core-compatibility.json',compilation)
e._save(HERE/'verification.json',dict(pins_match=True,actual_requests_match=True,valid_json=4,
    all_selected_references_resolve=True,calls=4,retries=0,
    semantic_completeness='not established',production_changes=False,
    core_rehearsal='Source text assembled locally into current candidate fields; no reviewed or approved production records created'))
print(json.dumps(dict(sizes=sizes,core={k:{n:v[n] for n in ('parsed_candidates','accepted')} for k,v in compilation.items()}),indent=2))
