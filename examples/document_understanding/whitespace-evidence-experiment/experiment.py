"""Test a whitespace-only evidence fallback without changing production code."""
import argparse
from dataclasses import asdict
from pathlib import Path
import re
from unittest.mock import patch

from rulespec_projection.evidence import EvidenceOffsetResolution
from rulespec_extrapolator import audit as a, extraction as e
from rulespec_extrapolator.documents import prepare_document

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'minor-audit-improvements'
ORIGINAL_SPAN = a._span


def verify(directory):
    manifest = e._load(directory / 'manifest.json')['artifacts_sha256']
    for name, digest in manifest.items():
        assert e._digest(e._contained(directory, name).read_bytes()) == digest, name
    return manifest


def tolerant_span(document, quote, window, *, focus=False, receipts=None):
    try:
        return ORIGINAL_SPAN(document, quote, window, focus=focus)
    except ValueError:
        pass
    if not quote.strip():
        raise ValueError('Empty evidence')
    # Every non-whitespace character remains literal; retain overlapping matches.
    pattern = r'\s+'.join(re.escape(part) for part in re.split(r'\s+', quote.strip()))
    ranges = [(window['start'], window['end'])]
    if not focus:
        ranges += [(s['start'], s['end']) for s in window.get('context_spans', [])]
    matches = set()
    for lo, hi in ranges:
        for match in re.finditer('(?=(' + pattern + '))', document['text'][lo:hi]):
            start, end = match.span(1)
            matches.add((lo + start, lo + end))
    if len(matches) != 1:
        raise ValueError('Absent or ambiguous whitespace-equivalent evidence')
    start, end = next(iter(matches))
    resolved = EvidenceOffsetResolution(start, end, 'unique-whitespace-match')
    span = a._source_span(document, {
        'quote': document['text'][start:end], 'start': start, 'end': end})
    if receipts is not None:
        receipts.append({'model_quote': quote, 'resolved': asdict(resolved), 'source_span': span})
    return span


def controls(cases):
    results = []
    for case in cases:
        doc = prepare_document(case['source'])
        if 'source_map' in case:
            doc['source_map'] = case['source_map']
        window = {'start': case.get('start', 0), 'end': case.get('end', len(doc['text'])),
                  'context_spans': case.get('context_spans', [])}
        assert 0 <= window['start'] < window['end'] <= len(doc['text'])
        for span in window['context_spans']:
            assert 0 <= span['start'] < span['end'] <= len(doc['text'])
        row = {'case': case['name'], 'expected_accept': case['expected_accept']}
        for arm, resolver in [('baseline', ORIGINAL_SPAN), ('treatment', tolerant_span)]:
            try:
                span = resolver(doc, case['quote'], window)
                assert span['quote'] == doc['text'][span['start']:span['end']]
                result = {'accepted': True, 'source_span': span}
            except ValueError:
                result = {'accepted': False}
            result['expectation_met'] = result['accepted'] == case['expected_accept']
            row[arm] = result
        results.append(row)
    return results


def run_audit(arm):
    directory = BASE / 'fresh/audit'
    book, labels = e._load(directory / 'rulebook.json'), e._load(directory / 'labels.json')
    run = e._load(directory / 'audit.json')
    receipts = []

    def resolver(*args, **kwargs):
        return tolerant_span(*args, **kwargs, receipts=receipts)

    with patch.object(a, '_span', ORIGINAL_SPAN if arm == 'baseline' else resolver):
        judgments, issues = a._judgments(directory / 'comparison', book, labels,
            run['windows'], run['comparison_attempts'], run['model'])
        report = a._assessment(book, labels, judgments, issues)
    if arm == 'baseline':
        assert judgments == e._load(directory / 'judgments.json')
        assert report == e._load(directory / 'report.json')
    for field in ('claim_judgments', 'unit_judgments'):
        for judgment in judgments[field]:
            for span in judgment['source_spans']:
                assert book['document']['text'][span['start']:span['end']] == span['quote']
    return {'judgments': judgments, 'report': report, 'recoveries': receipts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    args = parser.parse_args()
    design = e._load(ROOT / 'design.json')
    assert e._digest((BASE / 'manifest.json').read_bytes()) == design['base_manifest_sha256']
    verify(BASE)
    for name, digest in design['inputs_sha256'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest, name
    runtime = {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()}
    assert runtime == design['runtime_sources_sha256']
    if args.mode == 'run':
        if (ROOT / 'results.json').exists():
            raise ValueError('Results already recorded')
    else:
        verify(ROOT)
    results = {'controls': controls(e._load(ROOT / 'cases.json')),
               'audits': {arm: run_audit(arm) for arm in ('baseline', 'treatment')}}
    # Prior accepted judgments must remain byte-for-byte equivalent as records.
    for field, identity in [('claim_judgments', 'claim_id'), ('unit_judgments', 'unit_id')]:
        before = results['audits']['baseline']['judgments'][field]
        after = {x[identity]: x for x in results['audits']['treatment']['judgments'][field]}
        assert all(after[x[identity]] == x for x in before)
    results['prior_judgments_unchanged'] = True
    if args.mode == 'run':
        e._save(ROOT / 'results.json', results)
        e._write_manifest(ROOT)
    else:
        assert results == e._load(ROOT / 'results.json')
    for row in results['controls']:
        print(row['case'], 'expected', row['expected_accept'],
              'exact', row['baseline']['accepted'], 'whitespace', row['treatment']['accepted'])
    for arm, result in results['audits'].items():
        report = result['report']
        print(arm, report['counts'], {k: report['coverage'][k] for k in ('covered', 'partial', 'unknown')},
              'complete', report['review_complete'], 'status', report['status'],
              'recovered', len(result['recoveries']))


if __name__ == '__main__':
    main()
