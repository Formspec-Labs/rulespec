"""Run the real two-stage checker against two deliberately defective drafts.

These are development controls, not fresh extraction or human review. Originals
are read only. Each attempt retains the complete request, response and runtime.
"""
import argparse
import json
from pathlib import Path

from rulespec_extrapolator import audit as a, extraction as e
from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'negative-controls')
    args = parser.parse_args()
    output = args.output
    output.mkdir(exist_ok=False)
    cases = e._load(REPO / 'thoughts/reviews/2026-09-07-document-understanding-adversarial/names-adversarial-regressions.json')['cases']
    cases = {c['case_id']: c for c in cases}
    alternative_text = cases['NREG-01']['source_pieces'][0]['text']
    alternative = {
        'kind': 'requirement', 'modality': 'must', 'modality_quote': 'must',
        'quote': alternative_text,
        'summary': 'Material name discrepancies must be documented with one or more of: court orders or decrees (name change orders or divorce decrees), certificates of naturalization, marriage certificates, or documentation of a change by operation of state law.',
        'choice_text': 'one or more', 'choice_quote': 'one or more',
        'alternative_quotes': ['Name change orders', 'Divorce decrees', 'Certificates of naturalization', 'Marriage certificates', 'Documentation demonstrating change of name by operation of state law'],
        'references': ['8 FAM 403.1-4(C)', '22 CFR 51.25'],
    }
    previous, clearance = [p['text'] for p in cases['NREG-05']['source_pieces']]
    exception = 'unless the name change documentation specifically permits the applicant to continue using that name'
    wrong_link = [
        {'kind': 'prohibition', 'modality': 'must_not', 'modality_quote': 'may not',
         'quote': previous, 'summary': 'After a material name change, an applicant may not continue using the previous name unless the name change documentation specifically permits it.',
         'scope_text': 'After a material name change.', 'scope_quotes': ['after a material name change']},
        {'kind': 'requirement', 'modality': 'must', 'modality_quote': 'must',
         'quote': clearance, 'summary': "You must clear the applicant's pending name even though the change is not final and even if no passport is being issued now."},
        {'kind': 'exception', 'modality': 'not_stated', 'quote': exception,
         'summary': 'Specific name-change documentation allowing continued use of the previous name is an exception.',
         'relation': 'exception', 'applies_to': [clearance]},
    ]
    controls = [
        ('omitted-alternative', 'NREG-01', alternative_text, [alternative],
         'Customary-usage documentation is omitted from meaning despite appearing in the full source quotation.'),
        ('wrong-exception-target', 'NREG-05', previous + '\n\n' + clearance, wrong_link,
         'The exact exception quote resolves to the pending-name clearance duty instead of the previous-name-use prohibition.'),
    ]

    def run(control):
        name, case, source, candidates, defect = control
        doc = prepare_document(source)
        candidates = [{'actor': '', **c} for c in candidates]
        book = compile_candidates(doc, candidates, {})
        assert len(book['accepted']) == len(candidates) and not book['rejected'], book['rejected']
        if name == 'wrong-exception-target':
            assert book['accepted'][2]['target_ids'] == [book['accepted'][1]['id']]
        e._save(output / (name + '.input.json'), {'case_id': case, 'deliberate_defect': defect,
                'source': doc, 'candidates': candidates, 'rulebook_sha256': e._digest(book)})
        report = a.audit_run(book, output / name, env_file=Path('/Users/mikewolfd/Work/spicy-regs/.env'))
        # Report the actual result; a miss remains a failed control, never hidden.
        receipt = {'control': name, 'case_id': case, 'deliberate_defect': defect,
                   'report_status': report['status'], 'coverage': report['coverage'],
                   'dimensions': report['dimensions'], 'review_complete': report['review_complete']}
        print(json.dumps({'control': name, 'status': report['status'],
                          'review_complete': report['review_complete'],
                          'missing': report['coverage']['missing'],
                          'alternatives_errors': report['dimensions']['alternatives']['error'],
                          'links_errors': report['dimensions']['links']['error']}), flush=True)
        return receipt

    # Core's RDF/SHACL parser initializes shared state; validate sequentially.
    results = [run(control) for control in controls]
    e._save(output / 'results.json', results)
    e._write_manifest(output)


if __name__ == '__main__':
    main()
