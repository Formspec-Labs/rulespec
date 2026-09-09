"""Compare configurable library matchers through the saved audit experiment."""
import argparse
from dataclasses import asdict
import importlib.metadata
import importlib.util
import math
from pathlib import Path
from unittest.mock import patch

import fuzzysearch
from langextract import resolver
from langextract.core import data
from rulespec_projection.evidence import EvidenceOffsetResolution
from rulespec_extrapolator import audit as a, extraction as e

ROOT = Path(__file__).resolve().parent
PREVIOUS = ROOT.parent / 'whitespace-evidence-experiment'
spec = importlib.util.spec_from_file_location('previous_whitespace_experiment', PREVIOUS / 'experiment.py')
previous = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous)


def library_files():
    directory = Path(fuzzysearch.__file__).parent
    return {str(p.relative_to(directory)): e._digest(p.read_bytes())
            for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def library_matches(quote, source, config):
    if config['library'] == 'fuzzysearch':
        kwargs = {k: config[k] for k in ('max_l_dist', 'max_insertions', 'max_deletions', 'max_substitutions') if k in config}
        if 'edit_fraction' in config:
            kwargs['max_l_dist'] = min(config['edit_cap'], math.floor(len(quote) * config['edit_fraction']))
        return [{'start': m.start, 'end': m.end, 'distance': m.dist, 'parameters': kwargs}
                for m in fuzzysearch.find_near_matches(quote, source, **kwargs)]
    kwargs = {k: config[k] for k in ('fuzzy_alignment_threshold', 'fuzzy_alignment_min_density',
                                    'fuzzy_alignment_algorithm', 'accept_match_lesser')}
    rows = resolver.Resolver().align([data.Extraction('evidence', quote)], source,
        token_offset=0, char_offset=0, enable_fuzzy_alignment=True, **kwargs)
    return [{'start': row.char_interval.start_pos, 'end': row.char_interval.end_pos,
             'alignment_status': row.alignment_status.value, 'parameters': kwargs}
            for row in rows if row.char_interval is not None]


def make_resolver(config, diagnostics):
    def resolve(document, quote, window, *, focus=False, receipts=None):
        try:
            return previous.ORIGINAL_SPAN(document, quote, window, focus=focus)
        except ValueError:
            pass
        if not quote.strip():
            raise ValueError('Empty evidence')
        ranges = [(window['start'], window['end'])]
        if not focus:
            ranges += [(s['start'], s['end']) for s in window.get('context_spans', [])]
        candidates = {}
        for lo, hi in ranges:
            for match in library_matches(quote, document['text'][lo:hi], config):
                start, end = lo + match['start'], lo + match['end']
                if lo <= start < end <= hi:
                    candidates[start, end] = {**match, 'start': start, 'end': end,
                                             'source_text': document['text'][start:end]}
        diagnostic = {'model_quote': quote, 'candidates': list(candidates.values()),
                      'accepted': False, 'reason': 'not_one_returned_candidate'}
        diagnostics.append(diagnostic)
        if len(candidates) != 1:
            raise ValueError('No single library alignment')
        (start, end), match = next(iter(candidates.items()))
        diagnostic['reason'] = 'source_guard'
        span = a._source_span(document, {'quote': document['text'][start:end], 'start': start, 'end': end})
        diagnostic.update(accepted=True, reason='one_returned_candidate')
        if receipts is not None:
            receipts.append({'model_quote': quote, 'source_span': span, 'library_match': match,
                'resolved': asdict(EvidenceOffsetResolution(start, end, config['name']))})
        return span
    return resolve


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('run', 'replay'))
    args = parser.parse_args()
    design = e._load(ROOT / 'design.json')
    assert e._digest((PREVIOUS / 'manifest.json').read_bytes()) == design['previous_manifest_sha256']
    previous.verify(PREVIOUS)
    previous.verify(previous.BASE)
    assert {n: importlib.metadata.version(n) for n in design['library_versions']} == design['library_versions']
    assert library_files() == design['fuzzysearch_files_sha256']
    assert {n: e._digest(p.read_bytes()) for n, p in e._runtime_sources().items()} == design['runtime_sources_sha256']
    for name, digest in design['inputs_sha256'].items():
        assert e._digest((ROOT / name).read_bytes()) == digest, name
    if args.mode == 'replay':
        previous.verify(ROOT)
    elif (ROOT / 'results.json').exists():
        raise ValueError('Results already recorded')
    cases, results = e._load(ROOT / 'cases.json'), []
    baseline = previous.run_audit('baseline')
    for config in e._load(ROOT / 'configuration.json'):
        diagnostics = []
        with patch.object(previous, 'tolerant_span', make_resolver(config, diagnostics)):
            controls = previous.controls(cases)
            control_diagnostics = list(diagnostics)
            diagnostics.clear()
            audit = previous.run_audit('treatment')
        for field, identity in [('claim_judgments', 'claim_id'), ('unit_judgments', 'unit_id')]:
            after = {x[identity]: x for x in audit['judgments'][field]}
            assert all(after[x[identity]] == x for x in baseline['judgments'][field])
        row = {'configuration': config, 'controls': controls, 'audit': audit,
               'control_diagnostics': control_diagnostics, 'audit_diagnostics': diagnostics}
        results.append(row)
        false_accepts = [c['case'] for c in controls if not c['expected_accept'] and c['treatment']['accepted']]
        print(config['name'], 'recovered', len(audit['recoveries']),
              'controls accepted', sum(c['treatment']['accepted'] for c in controls),
              'unexpected', false_accepts, flush=True)
    if args.mode == 'run':
        e._save(ROOT / 'results.json', results)
        e._write_manifest(ROOT)
    else:
        assert results == e._load(ROOT / 'results.json')
        print('All nine configurations replay identically; no provider calls.')


if __name__ == '__main__':
    main()
