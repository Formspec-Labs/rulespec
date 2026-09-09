"""Deterministic evidence check on four saved refused rows. No model calls."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import rulespec_extrapolator

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'audit-grounding-experiment'
CAPTURE = ROOT.parent / 'low-extract-medium-audit'


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(directory):
    for name, expected in read(directory / 'manifest.json')['artifacts_sha256'].items():
        assert digest(directory / name) == expected, name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    args = parser.parse_args()
    design = read(ROOT / 'design.json')
    for name, directory in (('prototype', BASE), ('capture', CAPTURE)):
        assert digest(directory / 'manifest.json') == design[name + '_manifest_sha256']
        verify(directory)
    for name, expected in design['inputs_sha256'].items():
        assert digest(ROOT / name) == expected, name
    rulespec_extrapolator.__path__ = [str(BASE / 'frozen/application')]
    from rulespec_extrapolator import audit as passage, extraction as e
    spec = importlib.util.spec_from_file_location('rulespec_extrapolator._quotation_check', BASE / 'control-audit.py')
    quote = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quote)
    assert {name: e._digest(path.read_bytes()) for name, path in e._runtime_sources().items()} == design['runtime_sources_sha256']
    fixture = read(ROOT / 'fixture.json')
    doc, window = fixture['document'], fixture['window']
    original_run = read(CAPTURE / 'audit/audit.json')
    original = quote._inventory(CAPTURE / 'audit/inventory', doc, [window], original_run['inventory_attempts'])
    assert original == read(CAPTURE / 'audit/inventory.json')
    assert [i['row_index'] for i in original['issues']] == [18, 19, 20, 21]
    payload, errors = quote._read_response(CAPTURE / 'audit/inventory', original_run['inventory_attempts'][0])
    assert not errors
    catalog = e.passage_catalog(doc, window)
    results = {'original_inventory_identical': True, 'original_accepted': len(original['units']),
               'original_issues': original['issues'], 'cases': []}

    def evaluate(name, module, rows):
        # Explicit local test fixture, not an API response or an extraction repair.
        response = {'fixture_only': True, 'not_provider_output': True, 'candidates': [
            {'finish_reason': 'STOP', 'content': {'parts': [{'text': e._canonical({'units': rows})}]}}]}
        path = ROOT / 'fixtures' / (name + '.response.json')
        attempt = {'id': 'fixture-' + name, 'window_id': window['id'],
                   'response_file': path.name, 'error_code': None, 'status': 'local_test_fixture'}
        if args.mode == 'run':
            e._save(path, response)
        else:
            assert read(path) == response
        return module._inventory(path.parent, doc, [window], [attempt])

    mapped_rows = []
    for selection in fixture['selections']:
        index, ref = selection['raw_row'], selection['passage_ref']
        row = payload['units'][index]
        assert row == selection['original_unit']
        main = quote._span(doc, row['quote'], window, focus=True)
        selected = e.resolve_passage(ref, catalog, doc, focus=True)
        assert selected['start'] <= main['start'] < main['end'] <= selected['end']
        marker = row['scope_quotes'][0]
        occurrences = [i for i in range(len(doc['text'])) if doc['text'].startswith(marker, i)]
        try:
            quote._span(doc, marker, window)
        except ValueError:
            pass
        else:
            raise AssertionError('Original bad scope unexpectedly accepted')
        full_quote = {**row, 'scope_quotes': [selected['quote']]}
        mapped = {'quote_ref': ref, 'scope_refs': [], 'kind': row['kind'], 'meaning': row['meaning']}
        raw_result = evaluate(str(index) + '-original', quote, [row])
        quote_result = evaluate(str(index) + '-full-quote', quote, [full_quote])
        id_result = evaluate(str(index) + '-passage-id', passage, [mapped])
        assert len(raw_result['issues']) == 1 and not raw_result['units']
        for output in (quote_result, id_result):
            assert not output['issues'] and len(output['units']) == 1
            assert output['units'][0]['meaning'] == row['meaning']
            assert output['units'][0]['kind'] == row['kind']
        results['cases'].append({'raw_row': index, 'original_marker': marker,
            'marker_offsets': occurrences, 'main_quote_resolves': True,
            'reviewed_passage_ref': ref, 'selected_passage': selected,
            'original': raw_result, 'full_quote': quote_result, 'passage_id': id_result,
            'meaning_and_kind_unchanged': True})
        mapped_rows.append(mapped)

    negative_rows = {
        'missing-main': {**mapped_rows[1], 'quote_ref': 'F999'},
        'missing-scope': {**mapped_rows[1], 'scope_refs': ['F999']},
        'missing-range-member': {**mapped_rows[1], 'quote_ref': 'F014:F999'},
        'unrelated-valid-main': {**mapped_rows[1], 'quote_ref': 'F016'},
    }
    results['negative_controls'] = {}
    for name, row in negative_rows.items():
        result = evaluate(name, passage, [row])
        if name == 'unrelated-valid-main':
            assert len(result['units']) == 1 and not result['issues']
        else:
            assert not result['units'] and len(result['issues']) == 1
        results['negative_controls'][name] = result
    if args.mode == 'run':
        e._save(ROOT / 'results.json', results)
    else:
        verify(ROOT)
        assert read(ROOT / 'results.json') == results
    print('Original four refusals reproduced; full-text and passage-ID selections resolve 4/4 with unchanged meanings.')
    print('Three invalid-reference controls refused; one unrelated valid passage passes structural checks only.')
    print('No provider calls, source-capture changes, or audit-report repairs.')


if __name__ == '__main__':
    main()
