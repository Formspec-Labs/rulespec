"""Exercise the real sibling tools; compare installed wheels with source imports.

This is an offline reference-candidate probe, not a Rulespec Core dependency or
an automatic qualification linker. Inputs and both parsers' outputs stay visible.
"""
import argparse
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path

from refspec.registry import citation_grammar as refspec
from spicysearch import cfr_citations as spicysearch


def probe(case):
    text = case['raw']
    occurrences = refspec.find_cfr_citations(text)
    for occurrence in occurrences:
        assert text[occurrence.start:occurrence.end] == occurrence.text
    # The consumer keeps the whole source paragraph, not just a normalized ID.
    # RefSpec supplies CFR identities and paragraph labels; SpicySearch outputs
    # remain diagnostics where their readings differ. Neither certifies targets.
    return {
        'input': case,
        'refspec_cfr': [asdict(c) for c in occurrences],
        'spicysearch_cfr': [asdict(c) for c in spicysearch.extract_citations(text, keep_rejected=True)],
        'spicysearch_usc': [asdict(c) for c in spicysearch.extract_usc_citations(text, keep_rejected=True)],
        'refspec_usc': [asdict(c) for c in refspec.parse_authority_citation(text)
                        if c.authority_type == 'usc'],
    }


def verify(rows):
    for row in rows:
        text = row['input']['raw']
        for citation in row['refspec_cfr']:
            assert 0 <= citation['start'] < citation['end'] <= len(text)
            assert text[citation['start']:citation['end']] == citation['text']
    by_text = {row['input']['raw']: row for row in rows}
    cfr = lambda text: by_text[text]['refspec_cfr']
    assert cfr('40 CFR 82.154(a)(2)')[0]['pinpoint'] == ['a', '2']
    assert cfr('7 CFR 15a')[0]['citation']['cfr_part'] == '15a'
    assert by_text['7 CFR 15a']['spicysearch_cfr'][0]['part'] == '15'
    assert by_text['42 U.S.C. 1395w-4']['spicysearch_usc'][0]['section'] == '1395w'
    assert by_text['42 U.S.C. 1395w-4']['refspec_usc'][0]['usc_section'] == '1395w-4'
    assert [c['citation']['cfr_section'] for c in cfr('40 CFR §§ 82.155(a), 82.156(b)')] == ['155', '156']
    assert not cfr('paragraphs (b)(1) through (4), (c), and (d)(1) of this section')
    assert not cfr('§ 91.107(a)(3)(iii)(B)( 4 )')
    assert not cfr('3 CFR, 1977 Comp., p. 123')
    assert not cfr('5401-5405')
    assert not cfr('No citation or requirement here.')
    assert not cfr('1345 CFR 1370.31(a)')[0]['citation']['title_is_possible']
    assert not cfr('40 CFR 82.154 (2025)')[0]['pinpoint']
    repeated = cfr('😀 40 CFR 82.154(a)(2); then 40 CFR 82.154(a)(2).')
    assert len(repeated) == 2 and repeated[0]['start'] == 2
    assert repeated[0]['start'] < repeated[1]['start']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--installed', action='store_true')
    parser.add_argument('--compare', type=Path)
    args = parser.parse_args()
    imports = {name: module.__file__ for name, module in [('refspec', refspec), ('spicysearch', spicysearch)]}
    assert all(('site-packages' in path) == args.installed for path in imports.values()), imports
    inputs = Path(__file__).with_name('inputs.json').read_bytes()
    # JSON roundtrip also proves the output is ordinary portable data.
    rows = json.loads(json.dumps([probe(case) for case in json.loads(inputs)], ensure_ascii=False))
    verify(rows)
    if args.compare:
        before = json.loads(args.compare.read_text())
        assert before['rows'] == rows
        assert before['inputs_sha256'] == sha256(inputs).hexdigest()
    result = {'purpose': 'Selected reference-candidate probes, not an accuracy benchmark',
              'imports': imports, 'inputs_sha256': sha256(inputs).hexdigest(),
              'module_sha256': {name: sha256(Path(path).read_bytes()).hexdigest() for name, path in imports.items()},
              'provider_calls': 0, 'installed': args.installed, 'rows': rows}
    with args.output.open('x') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'status': 'passed', 'imports': imports, 'cases': len(rows),
                      'source_wheel_equal': bool(args.compare), 'provider_calls': 0}))


if __name__ == '__main__':
    main()
