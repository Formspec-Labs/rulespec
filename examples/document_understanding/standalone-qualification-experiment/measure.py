"""Verify raw-to-record preservation and report this experiment's mechanical results."""
from collections import Counter
from datetime import datetime
import json
from pathlib import Path

from rulespec_extrapolator import extraction as e

ROOT = Path(__file__).resolve().parent


def measure():
    results = e._load(ROOT / 'results.json')
    report = {}
    for cell, result in results.items():
        directory = ROOT / 'runs' / cell
        book = e._load(directory / 'rulebook.json')
        document = book['document']
        response = e._load(directory / 'attempt-0000.response.json')
        raw = json.loads(''.join(part.get('text', '') for part in
            response['candidates'][0]['content']['parts']))['extractions']
        assert len(raw) == len(book['accepted'])
        catalog = e.passage_catalog(document, e.plan_windows(document, max_chars=24000)[0])
        issues = Counter()
        evidence_count = 0
        for original, candidate in zip(raw, book['accepted'], strict=True):
            attributes = original['unit_attributes']
            for source, target in [('statement', 'summary'), ('scope_text', 'scope_text'),
                                   ('choice_text', 'choice_text'), ('kind', 'kind'),
                                   ('modality', 'modality')]:
                assert attributes[source] == candidate[target], (cell, source)
            selection = e.resolve_passage(original['unit'], catalog, document, focus=True)
            assert (selection['start'], selection['end']) == (candidate['start'], candidate['end'])
            logic = attributes['logic_quote']
            assert candidate['logic_text'] == (
                e.resolve_passage(logic, catalog, document)['quote'] if logic else '')
            for evidence in candidate['evidence']:
                assert document['text'][evidence['start']:evidence['end']] == evidence['quote']
                evidence_count += 1
            issues.update(issue['code'] for issue in candidate['issues'])
        report[cell] = {
            'raw_and_accepted_records': len(raw), 'verified_evidence_spans': evidence_count,
            'issues': dict(sorted(issues.items())), 'unresolved_records': len(book['unresolved']),
            'reported_input_tokens': result['usage']['prompt_token_count'],
            'reported_output_tokens': result['usage']['candidates_token_count'],
            'reported_total_tokens': result['usage']['total_token_count'],
            'attempt_seconds': round((datetime.fromisoformat(result['finished_at']) -
                datetime.fromisoformat(result['started_at'])).total_seconds(), 3),
        }
    return report


if __name__ == '__main__':
    report = measure()
    print(json.dumps(report, indent=2))
