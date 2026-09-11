"""Capture installed/source reader parity; no model calls or accuracy scoring."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from rulespec_extrapolator import references
from rulespec_extrapolator.core import compile_candidates
from rulespec_extrapolator.documents import prepare_document
from refspec.registry import citation_grammar
from spicysearch import identifiers

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def save(path, value):
    with path.open('x') as file:
        json.dump(value, file, indent=2, ensure_ascii=False)
        file.write('\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--cli', action='store_true')
    args = parser.parse_args()
    cases = json.loads((ROOT / 'packages/rulespec-extrapolator/tests/fixtures/reference-occurrences.json').read_text())['cases']
    captured = {}
    for case in cases:
        scan = references.scan_references(prepare_document(case['raw']))
        captured[case['id']] = scan
    result = {'cwd': str(Path.cwd()), 'python': sys.executable, 'provider_calls': 0,
              'modules': {m.__name__: {'path': m.__file__, 'sha256': hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()}
                          for m in (references, identifiers, citation_grammar)}, 'scans': captured}
    if args.cli:
        fixture = HERE / 'fixture-run'
        fixture.mkdir()
        text = 'Operators must consult 40 CFR §§ 82.155(a), 82.156(b).\n\nCompare Pub. L. 119-20 and 99 CFR 1.2.'
        doc = prepare_document(text, title='Constructed CLI integration control')
        sentence = text.split('\n')[0]
        run = {'id': 'urn:test:cfr-installed-cli'}
        book = compile_candidates(doc, [{'summary': sentence, 'quote': sentence, 'actor': 'Operators',
            'actor_quote': 'Operators', 'kind': 'requirement', 'modality': 'must', 'modality_quote': 'must'}], run)
        assert len(book['accepted']) == 1
        for name, value in [('document', doc), ('rulebook', book), ('run', run)]:
            save(fixture / (name + '.json'), value)
        commands = [
            ['references', str(fixture), '--output', str(HERE / 'cli-references.json')],
            ['discovery-export', str(fixture), '--output', str(HERE / 'cli-default.json')],
            ['discovery-export', str(fixture), '--references', '--output', str(HERE / 'cli-discovery.json')],
        ]
        result['commands'] = []
        for command in commands:
            actual = [str(Path(sys.executable).with_name('rulespec-understand')), *command]
            completed = subprocess.run(actual, cwd='/tmp', text=True, capture_output=True, check=True)
            result['commands'].append({'argv': actual, 'stdout': completed.stdout, 'stderr': completed.stderr})
        scan = json.loads((HERE / 'cli-references.json').read_text())
        exported = json.loads((HERE / 'cli-discovery.json').read_text())
        baseline = json.loads((HERE / 'cli-default.json').read_text())
        shared = exported.pop('reference_scan')
        assert [row['value'] for row in scan['candidates']] == ['40 CFR 82.155(a)', '40 CFR 82.156(b)', 'Public Law 119-20']
        assert [row['code'] for row in scan['rejected']] == ['cfr_title_impossible']
        for state in ('candidates', 'rejected'):
            for standalone, row in zip(scan[state], shared[state], strict=True):
                supports = standalone['evidence']
                refs = row['evidence_refs']
                assert [(s['fragment_id'], [s['field']]) for s in supports] == [(s['id'], s['roles']) for s in refs]
                for support, ref in zip(supports, refs, strict=True):
                    span = exported['evidence'][ref['id']]
                    assert (span['start'], span['end']) == (support['start'], support['end'])
        exported['evidence'] = {key: exported['evidence'][key] for key in baseline['evidence']}
        assert exported == baseline
        result['cli_checks'] = 'passed: list context, refused evidence, unchanged statements and default records'
        result['fixture_origin'] = 'Constructed source and manually compiled statement, not a provider output'
    save(args.output, result)


if __name__ == '__main__':
    main()
