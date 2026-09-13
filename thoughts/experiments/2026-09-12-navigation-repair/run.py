"""Paired recovery with current navigation; no new meaning schema or production pass."""
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import sys
import tempfile
import time
from unittest.mock import patch

from rulespec_extrapolator import audit as a, core, extraction as e, refinement as r
from rulespec_extrapolator.context import export_context
from rulespec_extrapolator.review_store import ReviewStore
from rulespec_extrapolator.uslm import prepare_xml

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / '2026-09-12-extractor-confidence/decoded/iep-1.json'
MODEL = 'gemini-3.8-flash'
CONFIG = dict(temperature=0, thinking_level='medium', max_output_tokens=32768)
GUIDANCE = '\nOptional reference navigation locates text and current claims, not governing relationships; validate its semantic relevance against the supplied source.\n'


def save(name, value):
    path = HERE / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert e._load(path) == value, name
    else:
        e._save(path, value)


def temporary_store(directory, book):
    for name, value in [('document.json', book['document']), ('rulebook.json', book), ('run.json', book['run'])]:
        e._save(Path(directory) / name, value)
    return ReviewStore(directory)


def control_book():
    rows = [
        ('A', 'i', 'Applicants may submit a request electronically.', 'permission', 'may', 'Applicants'),
        ('A', 'ii', "An electronic request under clause (i) must include the applicant’s name and reference number.", 'requirement', 'must', ''),
        ('A', 'iii', 'The agency must publish annual statistics on requests submitted under clause (i).', 'requirement', 'must', 'The agency'),
        ('B', 'i', 'Applicants may inspect public records during opening hours.', 'permission', 'may', 'Applicants'),
        ('B', 'ii', 'The agency must publish annual statistics on inspections under clause (i).', 'requirement', 'must', 'The agency'),
    ]
    body = ''
    for branch in ('A', 'B'):
        address = '/us/usc/t5/s1/' + branch
        clauses = ''.join(f'<clause identifier="{address}/{label}"><num>({label})</num><content>{text}</content></clause>'
                          for b, label, text, *_ in rows if b == branch)
        body += f'<subparagraph identifier="{address}">{clauses}</subparagraph>'
    doc = prepare_xml('<uscDoc xmlns="http://xml.house.gov/schemas/uslm/1.0" identifier="/us/usc/t5">'
                      '<section identifier="/us/usc/t5/s1">' + body + '</section></uscDoc>',
                      title='Constructed reference noninheritance control')
    candidates = [dict(quote=text, summary=text, kind=kind, modality=force, modality_quote=force,
                       actor=actor, actor_quote=actor) for _, _, text, kind, force, actor in rows]
    book = core.compile_candidates(doc, candidates, {'model': 'constructed-fixture'})
    assert len(book['accepted']) == 5 and not book['rejected']
    return book


def packet(book):
    window = dict(index=0, id='whole-source', start=0, end=len(book['document']['text']), context_spans=[])
    return window, r._packet(book, {'labels': {'expected_units': []}}, window)


def navigation(book):
    aliases = {c['id']: f'C{i:04d}' for i, c in enumerate(book['accepted'])}
    rows = {}
    for claim in book['accepted']:
        context = export_context(book, claim)
        for reading in context['material']['reference_readings']:
            if reading.get('direction') != 'outgoing' or not reading.get('referenced_claim_ids'):
                continue
            rows[reading['id']] = dict(reference=reading['value'], source_claim=aliases[claim['id']],
                target_claims=[aliases[i] for i in reading['referenced_claim_ids']],
                semantic_role=reading['semantic_role'], native_reading=reading.get('reading', {}))
    return list(rows.values())


def proof(book):
    """Constructed edits demonstrate existing representation, not model quality."""
    results = []
    with tempfile.TemporaryDirectory() as directory:
        store = temporary_store(directory, book)
        before = store.snapshot()
        for index, sentence in [(4, 'The parent’s agreement under this attendance provision must be in writing.'),
                                (5, 'The parent’s consent under this excusal provision must be in writing.')]:
            claim = before['accepted'][index]
            fields = {k: deepcopy(v) for k, v in claim.items() if k in core.CANDIDATE_SCHEMA['properties'] and k != 'window_id'}
            fields['summary'] += ' ' + sentence
            fields['context_quotes'] = list(dict.fromkeys([*fields['context_quotes'], before['accepted'][6]['quote']]))
            action = dict(action='edit', actor='Constructed representation check', actor_kind='aiAgent',
                expected_revision=before['revision'], targets=[claim['id']], replacements=[fields],
                rationale='Constructed source-checked example; no model result or approval.')
            preview = store.preview(action)
            new = next(c for c in preview['accepted'] if c['rule_id'] == claim['rule_id'])
            assert new['id'] != claim['id'] and new['quote'] == claim['quote']
            assert (new['kind'], new['modality']) == (claim['kind'], claim['modality'])
            assert before['accepted'][6] in preview['accepted']
            assert not new['target_ids'] and not any(i['code'] == 'component_evidence_unresolved' for i in new['issues'])
            assert any(v['field'].startswith('context:') and v['quote'] == before['accepted'][6]['quote'] for v in new['evidence'])
            assert store.snapshot() == before
            results.append(dict(row=index, fields=fields, evidence=new['evidence'], issues=new['issues'],
                                source_requirement_unchanged=True, preview_only=True))
    return results


def prepare():
    assert not (HERE / 'cells.json').exists()
    cases = {'iep': e._load(ORIGINAL)['book'], 'control': control_book()}
    save('representation-proof.json', proof(cases['iep']))
    save('schema.json', r.proposal_schema())
    save('books.json', cases)
    cells, key = [], {}
    combinations = [(case, arm) for case in cases for arm in ('A', 'B')]
    random.Random(91237).shuffle(combinations)
    for index, (case, arm) in enumerate(combinations):
        name = f'cell-{index + 1}'
        window, data = packet(cases[case])
        nav = navigation(cases[case])
        assert len(nav) == (2 if case == 'iep' else 3)
        prompt = r._proposal_prompt(r.RECOVERY + GUIDANCE, data)
        if arm == 'B':
            prompt += '\nReference navigation: ' + json.dumps(nav, ensure_ascii=False, separators=(',', ':'))
        save(f'inputs/{name}.json', dict(prompt=prompt, packet=data, window=window, model=MODEL, config=CONFIG))
        cells.append(dict(id=name, case=case))
        key[name] = arm
    save('cells.json', cells)
    save('arm-key.json', key)
    paths = [HERE / name for name in ('PLAN.md', 'run.py', 'books.json', 'schema.json', 'cells.json', 'arm-key.json')]
    paths += sorted((HERE / 'inputs').glob('*.json')) + [ORIGINAL]
    paths += list(e._runtime_sources().values()) + [Path(export_context.__code__.co_filename)]
    save('precall-pins.json', {os.path.relpath(p, HERE): sha256(p.read_bytes()).hexdigest() for p in paths})
    save('runtime-versions.json', e._runtime_versions())
    print('Prepared four cells and two existing-schema preview proofs; no model calls.')


def pins():
    for name, expected in e._load(HERE / 'precall-pins.json').items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == expected, name


def decode(cell):
    book = e._load(HERE / 'books.json')[cell['case']]
    data = e._load(HERE / f'inputs/{cell["id"]}.json')
    directory = HERE / 'captures' / cell['id']
    attempt = e._load(directory / 'attempt.json')
    payload, errors = a._read_response(directory, attempt)
    prepared, issues = r._decode_proposals(payload, errors, book['document'], data['window'], data['packet'], 'recovery')
    previews = []
    with tempfile.TemporaryDirectory() as temporary:
        store = temporary_store(temporary, book)
        before = store.snapshot()
        for proposal in prepared:
            try:
                preview = store.preview(r._action(proposal, before, MODEL))
                changed = [c for c in preview['accepted'] if c['id'] not in {v['id'] for v in before['accepted']}]
                previews.append(dict(proposal_id=proposal['id'], replacements=changed))
            except ValueError as error:
                issues.append(dict(code='preview_refused', proposal_id=proposal['id'], reason=str(error)))
        assert before == store.snapshot()
    return dict(payload=payload, errors=errors, prepared=prepared, issues=issues,
                previews=[dict(proposal_id=p['proposal_id'], replacements=[{k: c[k] for k in
                    ('summary', 'kind', 'modality', 'quote', 'evidence', 'issues')} for c in p['replacements']]) for p in previews])


def capture():
    pins()
    assert not (HERE / 'captures').exists()
    key = e._credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    start = time.monotonic()
    for index, cell in enumerate(e._load(HERE / 'cells.json')):
        usage = e.recorded_usage(HERE / 'captures').get('tokens', {}).get('total_token_count', 0)
        if index >= 4 or time.monotonic() - start >= 900 or usage >= 120000:
            save('stopped.json', dict(reason='predeclared_bound', completed=index)); break
        data = e._load(HERE / f'inputs/{cell["id"]}.json')
        book = e._load(HERE / 'books.json')[cell['case']]
        directory = HERE / 'captures' / cell['id']
        begin = time.monotonic()
        assert CONFIG['temperature'] == 0  # Existing capture uses the production zero default.
        attempts = a._capture(directory, book['document'], [data['window']], [data['prompt']],
                              e._load(HERE / 'schema.json'), MODEL, key, None,
                              max_output_tokens=CONFIG['max_output_tokens'], thinking_level=CONFIG['thinking_level'])
        save(f'captures/{cell["id"]}/attempt.json', attempts[0])
        save(f'captures/{cell["id"]}/timing.json', {'seconds': time.monotonic() - begin})
        result = decode(cell)
        save(f'decoded/{cell["id"]}.json', result)
        print(f'{cell["id"]}: {len(result["prepared"])} proposals; {len(result["issues"])} observations/refusals', flush=True)
    save('usage.json', e.recorded_usage(HERE / 'captures'))
    pins()


def verify():
    pins()
    with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected model call')):
        for cell in e._load(HERE / 'cells.json'):
            assert decode(cell) == e._load(HERE / f'decoded/{cell["id"]}.json')
    print('Four responses decode/preview identically with provider construction blocked; originals unchanged.')


if __name__ == '__main__':
    {'prepare': prepare, 'capture': capture, 'verify': verify}[sys.argv[1]]()
