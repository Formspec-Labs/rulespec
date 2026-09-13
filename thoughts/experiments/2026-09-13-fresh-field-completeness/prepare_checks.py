"""Freeze source-reviewed decisions, retaining native captures unchanged."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import random
import shutil
import tempfile
import run as exp
from rulespec_extrapolator import core, extraction as e, refinement as r
from rulespec_extrapolator.review_store import ReviewStore

spec = importlib.util.spec_from_file_location('prior_fixtures', exp.PREVIOUS / 'prepare_checks.py')
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)
SELECTION = dict(leave=2, billing=0, hazard=0, debt=0, offset=0, workplace=0, jury_fee=2, religious=1)
COMPLETE = {'leave', 'hazard', 'debt', 'workplace'}
NOISE = {'leave', 'hazard', 'workplace'}


def main():
    exp.x.pins()
    books, groups, labels, packets, nav, previews = {}, {}, {}, {}, {}, []
    for name in exp.x.NAMES:
        book = e._load(exp.HERE / f'extract/{name}/rulebook.json')
        books[name] = book
        window, = e.plan_windows(book['document'])
        packet = r._packet(book, {'labels': {'expected_units': []}}, window)
        packets[name] = (window, packet)
        nav[name] = fixtures.navigation(book)
        alias = f'C{SELECTION[name]:04d}'
        original = fixtures.fields(book['accepted'][SELECTION[name]])
        good = deepcopy(original)
        if name == 'billing':
            good['summary'] += (' For the acknowledgment exception, the action required in subparagraph (B) is either making appropriate corrections in the account, including crediting finance charges on erroneously billed amounts, and notifying the obligor of the corrections and explaining any change in the indicated amount, with copies of documentary evidence if a change is made and the obligor requests them; or, after investigation, sending a written explanation or clarification of why the account was correctly shown, to the extent applicable, and providing copies of documentary evidence on request. '
                'For an alleged failure to deliver goods to the obligor or designee as agreed, treating the amount as correctly shown requires a determination that the goods were delivered, mailed or otherwise sent to the obligor and a statement of that determination to the obligor. '
                'The separate subparagraph (B) response duty must be completed within two complete billing cycles, in no event later than 90 days after receipt, and before taking action to collect any part of the disputed amount; completing that action within the first 30 days waives the acknowledgment. '
                'After compliance with this subsection concerning an alleged error, the creditor has no further responsibility under this section if the obligor continues substantially the same allegation about that error.')
            good['context_quotes'] = list(dict.fromkeys([*good['context_quotes'], *[c['quote'] for c in book['accepted'][1:]]]))
        elif name == 'offset':
            good['summary'] += (' The agency head may do so only after giving the debtor all four of the following: written notice of the claim type and amount, the intention to collect by administrative offset, and the debtor’s rights under this section; an opportunity to inspect and copy agency records related to the claim; an opportunity for agency review of the decision related to the claim; and an opportunity to make a written agreement with the agency head to repay the claim. The last prerequisite is the opportunity to make an agreement, not the execution of one.')
            good['context_quotes'] = list(dict.fromkeys([*good['context_quotes'], book['accepted'][1]['quote']]))
        elif name == 'jury_fee':
            good['summary'] += (' The attendance fee referred to here is $50 per day for actual attendance at the place of trial or hearing; the juror also receives that attendance fee for necessary travel time at the beginning, end or during the service. Certification of additional attendance fees may be ordered by the judge effective from the first day of extended service, without reference to the date of certification.')
            good['context_quotes'] = list(dict.fromkeys([*good['context_quotes'], *[book['accepted'][i]['quote'] for i in (0, 1, 5)]]))
        elif name == 'religious':
            good.update(kind='permission', modality='may')
        wrong = deepcopy(good)
        replacements = {
            'leave': ('except that if the date of the treatment requires leave to begin in less than 30 days, the employee shall provide such notice as is practicable', 'even if the date of the treatment requires leave to begin in less than 30 days'),
            'billing': ('not later than 30 days after receipt of the notice, send a written acknowledgment', 'not later than 90 days after receipt of the notice, send a written acknowledgment'),
            'hazard': ('has actual knowledge that the Commission has been adequately informed', 'reasonably believes that the Commission has been adequately informed'),
            'debt': ('unless the information is contained in the initial communication or the consumer has paid the debt', 'unless both the information is contained in the initial communication and the consumer has paid the debt'),
            'offset': ('an opportunity to make a written agreement with the agency head to repay the claim. The last prerequisite is the opportunity to make an agreement, not the execution of one.', 'execution by the debtor of a written agreement with the agency head to repay the claim.'),
            'workplace': ('upon presenting appropriate credentials to the owner, operator, or agent in charge, ', ''),
            'jury_fee': ('may be paid, in the discretion of the trial judge,', 'must be paid, without trial-judge discretion,'),
            'religious': ('or if the curriculum of such school', 'and if the curriculum of such school')}
        before, after = replacements[name]
        assert wrong['summary'].count(before) == 1, name
        wrong['summary'] = wrong['summary'].replace(before, after)
        rows = [fixtures.proposal(alias, good, 'no_change' if name in COMPLETE else 'edit'), fixtures.proposal(alias, wrong)]
        categories = [('complete_noop' if name in COMPLETE else 'native_component_fix' if name == 'religious' else 'complete_repair'), 'wrong_meaning']
        if name not in COMPLETE:
            rows.append(fixtures.proposal(alias, original, 'no_change'))
            categories.append('incorrect_component_noop' if name == 'religious' else 'incomplete_noop')
        if name in NOISE:
            enriched = deepcopy(original)
            action = {'leave': 'provide', 'hazard': 'inform', 'workplace': 'enter'}[name]
            assert not enriched['action'] and not enriched['action_quote']
            enriched.update(action=action, action_quote=action)
            rows.append(fixtures.proposal(alias, enriched))
            categories.append('unnecessary_enrichment')
            cosmetic = deepcopy(enriched)
            before, after = {'leave': ('the employee shall provide', 'the employee must provide'),
                'hazard': ('shall immediately inform the Commission', 'must immediately inform the Commission'),
                'workplace': ('is authorized to enter', 'is permitted to enter')}[name]
            assert before in cosmetic['summary']
            cosmetic['summary'] = cosmetic['summary'].replace(before, after)
            rows.append(fixtures.proposal(alias, cosmetic))
            categories.append('cosmetic_enrichment')
        for i, (p, category) in enumerate(zip(rows, categories)):
            p['id'] = f'P{i:04d}'
            labels[name + '/' + p['id']] = dict(category=category, expected='supported' if i == 0 else 'unsupported',
                origin='unchanged native extraction' if p['proposal']['operation'] == 'no_change' else 'constructed decision on native extraction',
                target=alias, original_complete=name in COMPLETE,
                uncertainty='See BASELINE-REVIEW.md' if name in {'debt', 'jury_fee', 'religious'} else None)
            if p['proposal']['operation'] == 'no_change': continue
            decoded = validate(p, book['document'], window, packet)
            with tempfile.TemporaryDirectory() as tmp:
                shutil.copytree(exp.HERE / 'extract' / name, tmp, dirs_exist_ok=True)
                store = ReviewStore(tmp)
                snapshot = store.snapshot()
                preview = store.preview(r._action(decoded, snapshot, e.DEFAULT_MODEL))
                assert store.snapshot() == snapshot
                previews.append(dict(source=name, candidate=p['id'], preview_revision=preview['revision']))
        groups[name] = rows
    # Deliberately faulty diagnostic packet; no native extraction is modified.
    window, packet = deepcopy(packets['leave'])
    book = books['leave']
    correct_actor = fixtures.fields(packet['claims']['C0002'])
    packet['claims']['C0002'].update(actor='the employer', actor_quote='the employer')
    exception = deepcopy(correct_actor)
    quote = 'except that if the date of the treatment requires leave to begin in less than 30 days, the employee shall provide such notice as is practicable.'
    assert quote in book['document']['text']
    exception.update(quote=quote, kind='exception', modality='not_stated', modality_quote='', relation='none', applies_to=[],
        summary=('For foreseeable leave based on planned medical treatment under subsection (a)(1)(C) or (D) or subsection (a)(3), the fixed 30-day advance notice requirement is relaxed when the treatment date requires leave to begin in less than 30 days; the employee must still give the employer such notice as is practicable.'),
        scope_text='When the date of the planned medical treatment requires the specified leave to begin in less than 30 days.',
        scope_quotes=[quote], context_quotes=[book['accepted'][2]['quote']])
    start = book['document']['text'].index(quote)
    claim = deepcopy(packet['claims']['C0002'])
    claim.update(exception, id='urn:rulespec:experiment:fresh-field-completeness:notice-exception', target_ids=[],
        reference_links=[], issues=[], link_issues=[], evidence=[core._evidence(book['document'], quote, 'summary', start, start + len(quote))])
    packet['claims']['C0004'] = claim
    packet['initial_audit_aliases']['C0004'] = 'C0004'
    good_actor = fixtures.proposal('C0002', correct_actor)
    bad_actor = deepcopy(good_actor)
    bad_actor['fields'].update(actor='the health care provider', actor_quote='the health care provider')
    linked = deepcopy(exception)
    linked.update(relation='exception', applies_to=[packet['claims']['C0002']['id']])
    good_link = fixtures.proposal('C0004', linked)
    good_link['proposal']['qualifies'] = ['C0002']
    bad_link = deepcopy(good_link)
    bad_link['proposal']['qualifies'] = ['C0001']
    bad_link['fields']['applies_to'] = [packet['claims']['C0001']['id']]
    rows = [good_actor, bad_actor, good_link, bad_link]
    for i, p in enumerate(rows):
        p['id'] = f'P{i:04d}'
        labels['diagnostic/' + p['id']] = dict(expected='supported' if i in (0, 2) else 'unsupported',
            category={0:'actor_fix', 1:'wrong_actor', 2:'qualification_link', 3:'wrong_target'}[i], origin='constructed diagnostic draft and decision')
        validate(p, book['document'], window, packet)
    groups['diagnostic'] = rows
    packets['diagnostic'] = (window, packet)
    nav['diagnostic'] = nav['leave']
    books['diagnostic'] = book
    exp.x.save('groups.json', groups)
    exp.x.save('labels.json', labels)
    exp.x.save('preview-checks.json', previews)
    instructions = e._load(exp.HERE / 'instructions.json')
    combos = [(name, arm, rep) for name in groups for arm in ('A', 'B') for rep in range(2)]
    random.Random(913218).shuffle(combos)
    cells, key = [], {}
    for i, (name, arm, rep) in enumerate(combos):
        window, packet = packets[name]
        rows = deepcopy(groups[name])
        random.Random(913218 + 100 * list(groups).index(name) + rep).shuffle(rows)
        if arm == 'A': rows = [p for p in rows if p['proposal']['operation'] != 'no_change']
        prompt = instructions[arm] + r._challenge_prompt(packet, rows, books[name]['document'])[len(r.CHECK):]
        prompt += exp.x.prior.INDEPENDENT + '\nReference navigation: ' + e._canonical(nav[name])
        if arm == 'B': prompt += '\nSelected statement aliases: ' + e._canonical(sorted({p['proposal']['target'] for p in rows}))
        cell = f'cell-{i+1:02d}'
        cells.append(cell)
        key[cell] = dict(source=name, arm=arm, repeat=rep, fresh=name != 'diagnostic')
        exp.x.save(f'inputs/{cell}.json', dict(document=books[name]['document'], window=window, packet=packet, candidates=rows, prompt=prompt))
    exp.x.save('cells.json', cells)
    exp.x.save('arm-key.json', key)
    exp.x.save('schema.json', r.CHECK_SCHEMA)
    paths = list((exp.HERE / 'inputs').glob('*.json')) + [exp.HERE / n for n in
        ('groups.json', 'labels.json', 'preview-checks.json', 'BASELINE-REVIEW.md', 'cells.json', 'arm-key.json', 'schema.json', 'prepare_checks.py')]
    paths += [exp.PREVIOUS / 'prepare_checks.py']
    exp.x.freeze('check-pins.json', paths)
    print('Frozen 32 native-source checker calls plus four separate diagnostic calls;', len(previews), 'native edit previews validated.')


def validate(p, document, window, packet):
    raw = deepcopy(p['proposal'])
    raw['quote'] = p['fields']['quote']
    properties = r.proposal_schema()['properties']['proposals']['items']['properties']['fields']['properties']
    raw['fields'] = {k:v for k,v in p['fields'].items() if k in properties}
    decoded, issues = r._decode_proposals(dict(proposals=[raw], observations=[]), [], document, window, packet, 'recovery')
    assert len(decoded) == 1 and not issues, (p['id'], issues)
    return decoded[0]


if __name__ == '__main__': main()
