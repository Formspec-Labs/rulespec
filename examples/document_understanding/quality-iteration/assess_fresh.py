"""Reproduce the integrator's explicit, source-based fresh-passage judgments.

These judgments were authored after reading source and outputs. This script is
bookkeeping, not an automatic semantic grader. Pre-extraction labels stay fixed.
"""
from pathlib import Path
from rulespec_extrapolator import extraction as e
from rulespec_extrapolator.evaluation import MEANING_DIMENSIONS, claim_digest, content_digest, evaluate

ROOT = Path(__file__).resolve().parent


def main():
    output = ROOT / 'fresh-assessment'
    output.mkdir(exist_ok=False)
    labels = e._load(ROOT / 'source/fresh-labels.json')
    units = labels['expected_units']
    results = []
    for name, mapping in [('fresh-01', [0, 0, 1, 2, 3, 4, 5, 5, 6]), ('fresh-02', list(range(7)))]:
        book = e._load(ROOT / 'runs' / name / 'rulebook.json')
        assert len(book['accepted']) == len(mapping)
        judgments = {'schema_version': 'rulespec-evaluation-judgments/1',
            'rulebook_sha256': content_digest(book), 'labels_sha256': content_digest(labels),
            'review_provenance': {'reviewer': 'Codex integrator source review', 'reviewer_kind': 'aiAgent',
                'method': 'source_review', 'limitation': 'Same agent prepared labels and implemented the iteration; not blind human gold.'},
            'claim_judgments': [], 'unit_judgments': []}
        for index, (claim, unit_index) in enumerate(zip(book['accepted'], mapping, strict=True)):
            dimensions = {d: 'not_applicable' for d in MEANING_DIMENSIONS}
            dimensions.update(summary='correct', boundary='correct', support='correct', links='correct', modality='correct')
            for field in ['actor', 'action', 'object']:
                if claim.get(field):
                    dimensions[field] = 'correct'
            if claim.get('scope_text'):
                dimensions['scope'] = 'correct'
            if claim.get('choice_text') or claim.get('alternative_quotes'):
                dimensions['alternatives'] = 'correct'
            notes = ['The explicit meaning and preserved logic retain the expected source statement, including applicable conjunctions, sequencing and examples.']
            if name == 'fresh-01' and index < 4:
                dimensions['modality'] = 'error'
                notes.append('The source states a fact, but the profile classified it as possible. Its descriptive kind is appropriate; modality should be not_stated.')
            unresolved = [issue.get('field') for issue in claim['issues'] if issue['code'] == 'component_evidence_unresolved']
            if unresolved:
                dimensions['support'] = 'unknown'
                notes.append('Exact component anchoring remains unresolved for: ' + ', '.join(unresolved) + '. Main source support is exact; do not treat unresolved components as independently verified.')
            if name == 'fresh-02' and index == 6:
                notes.append('The summary says information or documentation; the explicit logic_text preserves the full information and/or documentation wording and then-suspend-or-refer sequence.')
            judgments['claim_judgments'].append({'claim_id': claim['id'], 'claim_sha256': claim_digest(claim),
                'unit_ids': [units[unit_index]['id']], 'dimensions': dimensions,
                'rationale': ' '.join(notes), 'source_spans': units[unit_index]['source_spans']})
        for index, unit in enumerate(units):
            partial = name == 'fresh-01' and index < 3
            judgments['unit_judgments'].append({'unit_id': unit['id'],
                'claim_ids': [c['id'] for c, m in zip(book['accepted'], mapping, strict=True) if m == index],
                'status': 'partial' if partial else 'covered',
                'rationale': 'Content is retained but factual statements are incorrectly marked as possibilities.' if partial else 'The unit is represented in the complete meaning, including explicit logic and governing conditions where applicable.',
                'source_spans': unit['source_spans']})
        report = evaluate(book, labels, judgments)
        e._save(output / (name + '.judgments.json'), judgments)
        e._save(output / (name + '.report.json'), report)
        results.append({'run': name, 'status': report['status'], 'review_complete': report['review_complete'],
                        'coverage': report['coverage'], 'modality': report['dimensions']['modality']})
    e._save(output / 'summary.json', {'labels_frozen_before_first_extraction': True,
        'first_extraction_is_the_fresh_assessment': 'fresh-01',
        'followup': 'fresh-02 is a development follow-up after observing factual-modality errors; not a second blind holdout.',
        'results': results})
    print([(r['run'], r['status'], r['coverage']['covered']) for r in results])


if __name__ == '__main__':
    main()
