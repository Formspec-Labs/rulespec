"""Bounded full-versus-sparse repair generation through native validation/review."""
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import sys
import tempfile
import time
from unittest.mock import patch
from uuid import UUID

from rulespec_extrapolator import audit as a, core, extraction as e, refinement as r, review_store as rs
from rulespec_extrapolator.discovery import export_discovery
import source
import sparse

HERE = Path(__file__).resolve().parent
NAV = HERE.parent / '2026-09-12-navigation-repair/run.py'
spec = importlib.util.spec_from_file_location('navigation_helpers', NAV)
nav = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nav)
POLICY_FILE = HERE.parent / '2026-09-13-fresh-field-completeness/instructions.json'
PENSION = HERE.parent / '2026-09-12-fresh-focused-repair/extract/pension/rulebook.json'
SELECTED = dict(foia=['C0000', 'C0003', 'C0006'], denial=['C0000'],
    benefits=['C0003', 'C0021', 'C0027'], accommodation=['C0000', 'C0001'],
    pension=['C0001'], component=['C0021'])
ENV = Path('/Users/mikewolfd/Work/spicy-regs/.env')
SCOPE = '\nReturn at most one edit per selected statement. Do not add records or edit unselected statements. An empty proposal list is valid. Other statements remain context.\n'
FULL = 'Editing\nmeans supplying complete replacement fields, preserving every correct existing\ncondition, alternative, citation and component.'
SPARSE = 'Editing means returning only the fields that need changing, preserving every correct existing condition, alternative, citation and component. Omitted fields, quote and qualifies retain their current values; explicit empty values clear them and must still satisfy the field constraints. Rulespec merges the edit with the current record before validation.'


def save(path, value):
    source.x.save(path, value)


def store_for(directory, name, base):
    directory = Path(directory) / 'workspace'
    if name == 'component':
        return nav.temporary_store(directory, base)
    capture = PENSION.parent if name == 'pension' else HERE / 'extract' / name
    assert e._load(capture / 'rulebook.json') == base
    r._copy_run(capture, directory)
    return rs.ReviewStore(directory)


def request(prompt, schema):
    return dict(model=e.DEFAULT_MODEL, contents=prompt, config=dict(max_output_tokens=32768,
        response_mime_type='application/json', response_json_schema=schema,
        thinking_config=dict(thinking_level='medium')))


def make_input(book, selected, arm):
    window, packet = nav.packet(book)
    navigation = nav.navigation(book)
    shared = e._load(POLICY_FILE)['B'].split('\nCheck each supplied decision')[0]
    description = r.RECOVERY
    assert FULL in description
    if arm == 'B': description = description.replace(FULL, SPARSE)
    description += '\n' + shared + nav.GUIDANCE + SCOPE
    prompt = r._proposal_prompt(description, packet)
    prompt += '\nReference navigation: ' + e._canonical(navigation)
    prompt += '\nSelected statement aliases: ' + e._canonical(selected)
    schema = r.proposal_schema() if arm == 'A' else sparse.schema()
    return dict(window=window, packet=packet, navigation=navigation, selected=selected,
        prompt=prompt, schema=schema, expected_request=request(prompt, schema))


def prepare():
    source.x.pins()
    bases = {n: e._load(HERE / f'extract/{n}/rulebook.json') for n in source.CASES}
    bases['pension'] = e._load(PENSION)
    original = bases['benefits']
    candidates = [{k: deepcopy(v) for k,v in c.items() if k in core.CANDIDATE_SCHEMA['properties']}
                  for c in original['accepted']]
    correct_actor = candidates[21]['actor']
    assert correct_actor == 'the Secretary'
    candidates[21]['actor'] = 'the plan participant'
    bases['component'] = core.compile_candidates(original['document'], candidates,
        {'model': 'constructed actor-component error; original provider capture retained separately'})
    assert len(bases['component']['accepted']) == len(original['accepted']) and not bases['component']['rejected']
    assert bases['component']['accepted'][21]['summary'] == original['accepted'][21]['summary']
    books = {}
    for name, base in bases.items():
        with tempfile.TemporaryDirectory() as temp:
            books[name] = store_for(temp, name, base).snapshot()
    save('base-books.json', bases)
    save('books.json', books)
    save('selected.json', SELECTED)
    save('component-fixture.json', dict(source='benefits', alias='C0021', changed_field='actor',
        original=correct_actor, constructed='the plan participant', default_meaning_unchanged=True))
    combinations = [(name, arm, repeat) for name in SELECTED for arm in ('A','B') for repeat in range(2)]
    random.Random(913917).shuffle(combinations)
    key = {}
    for i,(name,arm,repeat) in enumerate(combinations,1):
        cell=f'cell-{i:02d}'
        data=make_input(books[name], SELECTED[name], arm)
        save(f'inputs/{cell}.json', data)
        key[cell]=dict(source=name, arm=arm, repeat=repeat)
    save('arm-key.json', key)
    save('cells.json', list(key))
    for name in SELECTED:
        left=make_input(books[name],SELECTED[name],'A')
        right=make_input(books[name],SELECTED[name],'B')
        assert left['packet']==right['packet'] and left['navigation']==right['navigation']
        assert left['prompt'].replace(FULL,SPARSE)==right['prompt']
    paths=[p for p in HERE.rglob('*') if p.is_file() and not p.is_relative_to(HERE/'extract')]
    paths += [HERE/'extract'/n/'rulebook.json' for n in source.CASES]
    paths += [NAV, POLICY_FILE, PENSION]
    source.x.freeze('generation-pins.json', paths)
    print('Twenty-four generation requests frozen; only edit response shape/instruction varies.')


def capture(name, data, document):
    source.x.pins(); source.x.pins('execution-pins.json')
    ledger=e._load(HERE/'calls.json')
    assert name not in {c['name'] for c in ledger}, 'No retries'
    assert len(ledger)<52 and sum(c['seconds'] for c in ledger)<2400
    assert source.x.usage()['tokens'].get('total_token_count',0)<650000
    if len(ledger)>=2:
        assert not all(c.get('status')=='provider_failure' for c in ledger[-2:]), 'Two systemic provider failures'
    directory=HERE/'captures'/name
    assert not directory.exists()
    ledger.append(dict(name=name,status='started',seconds=0))
    e._save(HERE/'calls.json',ledger)
    started=time.monotonic()
    try:
        attempt, = a._capture(directory,document,[data['window']],[data['prompt']],data['schema'],
            e.DEFAULT_MODEL,e._credential(ENV),None,max_output_tokens=32768,thinking_level='medium')
        ledger[-1]['status']='returned' if attempt['status']=='response_received' else 'provider_failure'
        save(f'captures/{name}/attempt.json',attempt)
        if attempt.get('request_file'):
            assert e._load(directory/attempt['request_file'])==data['expected_request']
        return a._read_response(directory,attempt)
    finally:
        ledger[-1]['seconds']=time.monotonic()-started
        e._save(HERE/'calls.json',ledger)


def deterministic_review(store, action, identity, *, preview=False):
    # Replay only: pin synthetic review-event identity/time, never model contents.
    with patch.object(rs,'uuid4',return_value=UUID(sha256(identity.encode()).hexdigest()[:32])), patch.object(rs,'datetime') as clock:
        clock.now.return_value=datetime.fromisoformat('2026-09-13T18:00:00+00:00')
        return store.preview(action) if preview else store.apply(action)


def decode_generation(cell, payload, errors):
    info=e._load(HERE/'arm-key.json')[cell]
    data=e._load(HERE/f'inputs/{cell}.json')
    book=e._load(HERE/'books.json')[info['source']]
    normalized, problems = sparse.expand(payload,data['packet']) if info['arm']=='B' and not errors else (payload,[])
    proposals, issues=r._decode_proposals(normalized,errors,book['document'],data['window'],data['packet'],'recovery')
    issues=problems+issues
    prepared, previews = [], []
    with tempfile.TemporaryDirectory() as temp:
        store=store_for(temp,info['source'],e._load(HERE/'base-books.json')[info['source']])
        assert store.snapshot()==book
        for p in proposals:
            try:
                if p['proposal']['operation']!='edit' or p['proposal']['target'] not in data['selected']:
                    raise ValueError('Outside selected edit scope')
                preview=deterministic_review(store,r._action(p,book,e.DEFAULT_MODEL),cell+'/'+p['id'],preview=True)
                prepared.append(p)
                previews.append(dict(proposal_id=p['id'],replacements=preview['history'][-1]['replacements']))
            except ValueError as exc:
                issues.append(dict(proposal_id=p['id'],code='preview_refused',reason=str(exc)))
        assert store.snapshot()==book
    return dict(payload=payload,errors=errors,normalized=normalized,proposals=proposals,
        prepared=prepared,issues=issues,previews=previews)


def generate():
    key=e._load(HERE/'arm-key.json'); books=e._load(HERE/'books.json')
    for cell,info in key.items():
        if (HERE/f'decoded/{cell}-generation.json').exists(): continue
        data=e._load(HERE/f'inputs/{cell}.json')
        payload,errors=capture(cell+'/generation',data,books[info['source']]['document'])
        decoded=decode_generation(cell,payload,errors)
        save(f'decoded/{cell}-generation.json',decoded)
        print(cell,len(decoded['prepared']),'prepared;',len(decoded['issues']),'issues',flush=True)
    e._save(HERE/'usage.json',source.x.usage())


def check_input(cell):
    info=e._load(HERE/'arm-key.json')[cell]
    data=e._load(HERE/f'inputs/{cell}.json')
    book=e._load(HERE/'books.json')[info['source']]
    proposals=deepcopy(e._load(HERE/f'decoded/{cell}-generation.json')['prepared'])
    for i,alias in enumerate(data['selected']):
        old=data['packet']['claims'][alias]
        fields={k:deepcopy(old[k]) for k in core.CANDIDATE_SCHEMA['properties'] if k in old}
        fields['applies_to']=deepcopy(old.get('target_ids',[]))
        proposals.append(dict(id=f'N{i:04d}',proposal=dict(operation='no_change',target=alias,
            qualifies=old['target_ids'],rationale='Assess this unchanged selected reading.',quote=old['quote']),
            fields=fields,target_id=old['id'],qualification_ids=old['target_ids']))
    random.Random(int(cell.split('-')[1])+913).shuffle(proposals)
    prompt=e._load(POLICY_FILE)['B']+r._challenge_prompt(data['packet'],proposals,book['document'])[len(r.CHECK):]
    prompt+='\nEach candidate is an independent alternative evaluated against the unchanged draft. Do not combine candidates.'
    prompt+='\nReference navigation: '+e._canonical(data['navigation'])
    prompt+='\nSelected statement aliases: '+e._canonical(data['selected'])
    return dict(window=data['window'],packet=data['packet'],candidates=proposals,prompt=prompt,
        schema=r.CHECK_SCHEMA,expected_request=request(prompt,r.CHECK_SCHEMA))


def simulate(cell, judgments):
    info=e._load(HERE/'arm-key.json')[cell]
    proposals=e._load(HERE/f'decoded/{cell}-generation.json')['prepared']
    changes,problems=[],[]
    with tempfile.TemporaryDirectory() as temp:
        store=store_for(temp,info['source'],e._load(HERE/'base-books.json')[info['source']])
        before=store.snapshot()
        for p in proposals:
            if judgments.get(p['id'],{}).get('verdict')!='supported':continue
            try:
                action=r._action(p,store.snapshot(),e.DEFAULT_MODEL)
                attempt=e._load(HERE/f'captures/{cell}/generation/attempt.json')
                action['provenance']=e.captured_provenance(HERE/f'captures/{cell}/generation',attempt,f'{cell}/generation')
                after=deterministic_review(store,action,cell+'/apply/'+p['id'])
                changes.append(dict(proposal_id=p['id'],action=action,event=after['history'][-1]))
            except ValueError as exc:problems.append(dict(proposal_id=p['id'],reason=str(exc)))
        after=store.snapshot(); exported=export_discovery(after)
        assert after['document']==before['document']
        assert not any(c['review_status']=='approved' for c in after['accepted'])
        return dict(simulation_only=True,changes=changes,issues=problems,
            after_sha256=r.content_digest(after),discovery_sha256=e._digest(e._canonical(exported).encode()),
            changed_readings=[c for c in after['accepted'] if c['id'] not in {old['id'] for old in before['accepted']}],
            retained_unchanged_ids=[c['id'] for c in after['accepted'] if c['id'] in {old['id'] for old in before['accepted']}])


def check():
    # All generation calls finish and their raw review is saved before any
    # checker responses can influence the source-based generation assessment.
    assert (HERE/'RAW-GENERATION-REVIEW.md').exists()
    for cell,info in e._load(HERE/'arm-key.json').items():
        if (HERE/f'decoded/{cell}-check.json').exists():continue
        data=check_input(cell)
        save(f'check-inputs/{cell}.json',data)
        doc=e._load(HERE/'books.json')[info['source']]['document']
        payload,errors=capture(cell+'/check',data,doc)
        judgments,issues=r._decode_checks(payload,errors,data['candidates'],doc,data['packet'])
        save(f'decoded/{cell}-check.json',dict(payload=payload,errors=errors,judgments=judgments,issues=issues))
        save(f'applied/{cell}.json',simulate(cell,judgments))
        print(cell,len(judgments),'advisory judgments;',len(issues),'issues',flush=True)
    e._save(HERE/'usage.json',source.x.usage())


if __name__=='__main__':
    {'prepare':prepare,'generate':generate,'check':check}[sys.argv[1]]()
