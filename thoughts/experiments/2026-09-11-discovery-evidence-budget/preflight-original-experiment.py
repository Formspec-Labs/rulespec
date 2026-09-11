"""Frozen, provider-free comparison of existing evidence with a display budget."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

from rulespec_extrapolator import core, discovery, documents, reference_sources, references, uslm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PRIOR = HERE.parent / '2026-09-10-design-retrieval'
PATHS = {name: str((PRIOR / 'inputs' / (name + '.json')).relative_to(REPO))
         for name in ('alcohol', 'rail', 'leave', 'refrigerants')}
PATHS['vending'] = 'thoughts/experiments/2026-09-11-extraction-retention/combined-result/title-20-ch6A.1.A.rulebook.json'
HARNESS = REPO / 'packages/rulespec-extrapolator/evaluation/discovery_trial.py'
spec = importlib.util.spec_from_file_location('discovery_trial', HARNESS)
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)
LIMIT = 1500


def write(name, value):
    with (HERE / name).open('x') as out:
        json.dump(value, out, indent=2, ensure_ascii=False)
        out.write('\n')


def books():
    return {key: json.loads((REPO / path).read_text()) for key, path in PATHS.items()}


def prepare():
    data = books()
    questions = []

    def add(identity, source, query, quotes):
        text = data[source]['document']['text']
        required = []
        for quote in quotes:
            assert text.count(quote) == 1, (identity, quote, text.count(quote))
            start = text.index(quote)
            required.append({'start': start, 'end': start + len(quote), 'quote': quote})
        questions.append({'id': identity, 'group': 'new_query', 'source': source,
                          'query': query, 'required': required})

    add('N1', 'vending', 'Who receives priority for vending facilities on Federal property?', [
        'In authorizing the operation of vending facilities on Federal property, priority shall be given to blind persons licensed by a State agency as provided in this chapter'])
    add('N2', 'vending', 'Who decides whether a restriction on a blind vending facility is justified, and where is the decision published?', [
        'Any limitation on the placement or operation of a vending facility based on a finding that such placement or operation would adversely affect the interests of the United States shall be fully justified in writing to the Secretary, who shall determine whether such limitation is justified.',
        'A determination made by the Secretary pursuant to this provision shall be binding on any department, agency, or instrumentality of the United States affected by such determination.',
        'The Secretary shall publish such determination, along with supporting documentation, in the Federal Register.'])
    add('N3', 'vending', 'Does a blind vendor license expire automatically, or can the State terminate it?', [
        'Each such license shall be issued for an indefinite period but may be terminated by the State licensing agency if it is satisfied that the facility is not being operated in accordance with the rules and regulations prescribed by such licensing agency.'])
    vending = data['vending']['document']['text']
    start = vending.index('The State licensing agency designated by the Secretary is authorized')
    add('N4', 'vending', 'Can the State licensing agency choose a vending site and facility type without federal approval?', [vending[start:vending.index('\n', start)]])
    alcohol = data['alcohol']['document']['text']
    start = alcohol.index('(3) Be on duty')
    add('N5', 'alcohol', 'Does wine carried by a bus passenger violate the driver possession restriction?', [
        alcohol[start:alcohol.index('\n\n', start)], '(ii) Possessed or used by bus passengers.'])
    rail = data['rail']['document']['text']
    add('N6', 'rail', 'Which railroad stopping duties apply to an empty tank used to transport hazardous material?', [
        rail[:rail.index('\n\n')],
        '(4) Every cargo tank motor vehicle, whether loaded or empty, used for the transportation of any hazardous material as defined in the Hazardous Materials Regulations of the Department of Transportation, parts 107 through 180 of this title.',
        rail[rail.index('(b) A stop need not be made at:'):].rstrip()])
    leave = data['leave']['document']['text']
    start = leave.index('(4) Nothing in this section prevents')
    add('N7', 'leave', 'May an employer voluntarily count service before a long break for selected employees only?', [leave[start:leave.index('\n\n', start)]])
    refrigerants = data['refrigerants']['document']['text']
    start = refrigerants.index('(2)')
    add('N8', 'refrigerants', 'Which alternative compliance paths are required for the de minimis release exception beyond good faith recovery?', [
        refrigerants[start:refrigerants.index('\n\n(3)', start)]])
    for question in json.loads((PRIOR / 'queries.json').read_text()):
        if question['id'] in {'A1', 'R4', 'L1', 'F3'}:
            questions.append({**question, 'group': 'historical_control'})
    write('queries.json', questions)
    paths = [HERE / 'PLAN.md', HERE / 'queries.json', Path(__file__), HARNESS,
             *[REPO / p for p in PATHS.values()], PRIOR / 'queries.json',
             *[Path(m.__file__) for m in (core, discovery, documents, reference_sources, references, uslm)]]
    write('freeze.json', {'books': PATHS, 'budget': LIMIT, 'top_k': 3,
          'files': {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
          'labels': 'Agent-authored source-support selections; revisable development labels, not legal gold.',
          'provider_calls': 0})


def allocate(items, budget):
    covered, decisions, used = {}, [], 0
    for item in items:
        support = item['evidence']
        existing = covered.setdefault(item['source'], set())
        extra = set(range(support['start'], support['end'])) - existing
        admitted = budget is None or used + len(extra) <= budget
        decisions.append({**item, 'admitted': admitted, 'new_chars': len(extra),
                          'reason': 'already_present' if not extra else 'included' if admitted else 'budget'})
        if admitted:
            existing.update(extra)
            used += len(extra)
    return covered, decisions, used


def items(hits):
    return [{'source': h['source'], 'hit_id': h['id'], 'rank': rank, 'evidence': e}
            for rank, h in enumerate(hits, 1) for e in h['evidence']]


def intervals(positions):
    result = []
    for position in sorted(positions):
        if result and result[-1][1] == position:
            result[-1][1] += 1
        else:
            result.append([position, position + 1])
    return result


def evaluate(sequence, question, data):
    covered, trace, used = allocate(sequence, LIMIT)
    uncapped, _, _ = allocate(sequence, None)
    source = question['source']
    required = question.get('required')
    if required is None:
        text = data[source]['document']['text']
        required = [{'quote': q, 'start': text.index(q), 'end': text.index(q) + len(q)}
                    for q in question['required_quotes']]
    def found(positions):
        return [set(range(e['start'], e['end'])) <= positions.get(source, set()) for e in required]
    segments = [{'source': key, 'document': {k: data[key]['document'][k] for k in ('id', 'sha256')},
                 'start': a, 'end': b, 'text': data[key]['document']['text'][a:b]}
                for key, positions in covered.items() for a, b in intervals(positions)]
    admitted = [item for item in trace if item['admitted']]
    quoted = sum(len(item['evidence']['quote']) for item in admitted)
    return {'found': found(covered), 'uncapped_found': found(uncapped),
            'unique_chars': used, 'repeated_quote_chars': quoted - used,
            'budget_omissions': sum(not item['admitted'] for item in trace),
            'serialized_segments_bytes': len(json.dumps(segments, ensure_ascii=False).encode('utf-8')),
            'serialized_admitted_evidence_bytes': len(json.dumps(admitted, ensure_ascii=False).encode('utf-8')),
            'segments': segments, 'trace': trace}


def controls(data):
    book = data['alcohol']
    base = discovery.records(book, 'alcohol', 'source')
    empty = deepcopy(book)
    empty['accepted'] = []
    assert discovery.records(empty, 'alcohol', 'packets') == base
    dup = deepcopy(book)
    dup['accepted'].append(deepcopy(dup['accepted'][0]))
    normal = discovery.records(book, 'alcohol', 'packets')
    duplicate = discovery.records(dup, 'alcohol', 'packets')
    assert [r['evidence'] for r in duplicate] == [r['evidence'] for r in normal]
    forged = deepcopy(book)
    forged['accepted'][0]['evidence'].append({'field': 'context:0', 'start': 0, 'end': 6, 'quote': 'forged'})
    assert discovery.records(forged, 'alcohol', 'packets') == normal
    sample = [{'source': 'a', 'evidence': {'start': 0, 'end': 4, 'quote': 'same'}},
              {'source': 'b', 'evidence': {'start': 0, 'end': 4, 'quote': 'same'}}]
    covered, trace, used = allocate(sample, 7)
    assert used == 4 and trace[0]['admitted'] and not trace[1]['admitted']
    assert not covered['b']  # Equal text in another pinned source is not free evidence.
    external = data['vending']['document']
    primary = documents.prepare_document('20 USC 107a(b). 20 USC 107a(z).')
    scan = references.scan_references(primary, reference_sources=[external])
    assert [r['resolution']['status'] for r in scan['candidates']] == ['located', 'not_in_selected_sources']
    alternate = uslm.prepare_xml(external['uslm_source']['xml'].replace('<uscDoc ', '<uscDoc data-experiment="alternate" ', 1))
    ambiguous = references.scan_references(documents.prepare_document('20 USC 107a(b).'), reference_sources=[external, alternate])
    assert ambiguous['candidates'][0]['resolution']['status'] == 'ambiguous'
    assert ambiguous['candidates'][0]['resolution']['edition_match'] == 'not_established'
    return {'zero_statements_preserve_source': True, 'duplicate_evidence_unchanged': True,
            'fabricated_context_refused': True, 'distinct_sources_and_whole_spans': True,
            'native_lookup_scan': scan, 'ambiguous_lookup_scan': ambiguous}


def run():
    freeze = json.loads((HERE / 'freeze.json').read_text())
    for path, expected in freeze['files'].items():
        assert hashlib.sha256((REPO / path).read_bytes()).hexdigest() == expected, path
    data = books()
    source = [r for key, b in data.items() for r in discovery.records(b, key, 'source')]
    packets = [r for key, b in data.items() for r in discovery.records(b, key, 'packets')]
    assert [(r['source'], r['id'], r['text']) for r in source] == [(r['source'], r['id'], r['text']) for r in packets]
    packet_map = {(r['source'], r['id']): r for r in packets}
    for row in packets:
        for e in row['evidence']:
            assert data[row['source']]['document']['text'][e['start']:e['end']] == e['quote']
    checks = controls(data)
    results = []
    for q in json.loads((HERE / 'queries.json').read_text()):
        ranking = trial.search(source, q['query'], len(source))
        other = trial.search(packets, q['query'], len(packets))
        assert [(r['id'], r['score']) for r in ranking] == [(r['id'], r['score']) for r in other]
        hits = ranking[:3]
        a = items(hits)
        b = items([packet_map[(h['source'], h['id'])] for h in hits])
        c = a + [item for item in b if item['evidence']['field'] != 'source']
        result = {**q, 'ranking': [{k: h[k] for k in ('id', 'source', 'score')} for h in ranking],
                  'arms': {name: evaluate(sequence, q, data) for name, sequence in [('A', a), ('B', b), ('C', c)]}}
        results.append(result)
    summary = {}
    for group in ('new_query', 'historical_control'):
        selected = [q for q in results if q['group'] == group]
        summary[group] = {arm: {'all_selected_support': sum(all(q['arms'][arm]['found']) for q in selected),
                     'all_selected_support_uncapped': sum(all(q['arms'][arm]['uncapped_found']) for q in selected),
                     'unique_chars': sum(q['arms'][arm]['unique_chars'] for q in selected),
                     'repeated_quote_chars': sum(q['arms'][arm]['repeated_quote_chars'] for q in selected),
                     'budget_omissions': sum(q['arms'][arm]['budget_omissions'] for q in selected),
                     'serialized_segments_bytes': sum(q['arms'][arm]['serialized_segments_bytes'] for q in selected)}
                          for arm in ('A', 'B', 'C')}
    return {'provider_calls': 0, 'budget': LIMIT, 'source_rows': len(source),
            'summary': summary, 'controls': checks, 'queries': results}


if __name__ == '__main__':
    if '--prepare' in sys.argv:
        prepare()
        print('Frozen eight new query records and four original controls; no ranking run.')
    else:
        began = time.perf_counter()
        result = run()
        if '--replay' in sys.argv:
            assert result == json.loads((HERE / 'results.json').read_text())
            write('replay.json', {'exact': True, 'provider_calls': 0})
        else:
            write('results.json', result)
            write('runtime.json', {'elapsed_seconds': time.perf_counter() - began, 'provider_calls': 0})
        print(json.dumps(result['summary'], indent=2))
