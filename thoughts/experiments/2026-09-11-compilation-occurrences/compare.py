"""Compare frozen source readings; never overwrite an earlier observation."""
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pyarrow.parquet as pq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT.parent
sys.path[:0] = [str(WORK/'RefSpec/src'), str(WORK/'RefSpec/tests'),
               str(WORK/'spicysearch/src'), str(ROOT/'packages/rulespec-extrapolator/src')]
from refspec.registry import citation_grammar as grammar
import compilation_parser_oracle as old
from spicysearch.cfr_citations import extract_citations
from rulespec_extrapolator.documents import load_document, prepare_document
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator.discovery import export_discovery


def save(name, data):
    with (HERE/name).open('x') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def cfr(text, baseline=False):
    # The occurrence reader is unchanged; replace only the copied old grammar
    # that determines which spans it suppresses. No replaced check is imported.
    with patch.object(grammar, '_EO_COMPILATION', old._EO_COMPILATION if baseline else grammar._EO_COMPILATION):
        return [asdict(row) for row in grammar.find_cfr_citations(text)]


def readings(text):
    return {
        'old_locators': [asdict(row) for row in old.parse_eo_compilation_locators(text)],
        'new_occurrences': [asdict(row) for row in grammar.find_eo_compilation_locators(text)],
        'old_cfr': cfr(text, True), 'new_cfr': cfr(text),
        'spicysearch_strict': [asdict(row) for row in extract_citations(text, strict=True, keep_rejected=True)],
        'authority_rows': [asdict(row) for row in grammar.parse_authority_citation(text)],
    }


pins = json.loads((HERE/'source-pins.json').read_text())
source = Path(pins['parquet'])
assert hashlib.sha256(source.read_bytes()).hexdigest() == pins['parquet_sha256']
cases = json.loads((HERE/'source-cases.json').read_text())['cases']
out = []
for case in cases:
    result = readings(case['text'])
    match, = result['new_occurrences']
    assert match['locator'] == case['expected'] and match['refusal'] is None
    assert not result['new_cfr'] and not result['old_locators']
    doc = prepare_document(case['text'])
    result['references'] = scan_references(doc)
    result['discovery'] = export_discovery({'document': doc, 'accepted': []}, include_references=True)
    for layer in (result['references'], result['discovery']['reference_scan']):
        row, = layer['candidates']
        assert row['kind'] == 'eo_compilation'
        assert row['reading'] == {k: v for k, v in case['expected'].items() if v is not None}
    out.append({'id': case['id'], 'text': case['text'], **result})
save('case-results.json', out)

corpus = []
for row in pq.read_table(source, columns=['opinion_id', 'pdf_text']).to_pylist():
    text = row['pdf_text'] or ''
    before, after = cfr(text, True), cfr(text)
    native = [asdict(item) for item in grammar.find_eo_compilation_locators(text)]
    corpus.append({'opinion_id': row['opinion_id'], 'old_cfr_count': len(before), 'new_cfr_count': len(after),
                   'removed': [item for item in before if item not in after],
                   'added': [item for item in after if item not in before], 'compilations': native})
save('corpus-results.json', corpus)

gap = json.loads((HERE/'page-boundary-case.json').read_text())
gap_result = readings(gap['text'])
save('page-boundary-results.json', gap_result)

doc = load_document(HERE/'title-18-s798A.xml')
scan = scan_references(doc)
export = export_discovery({'document': doc, 'accepted': []}, include_references=True)
save('xml-results.json', {'document': doc, 'native': readings(doc['text']), 'references': scan, 'discovery': export})
assert len([r for r in scan['candidates'] if r['kind'] == 'eo_compilation']) == 2
assert len([r for r in scan['candidates'] if r['kind'] == 'publisher_reference']) == 12
assert 'probably should refer to Proc. 2914' in doc['text']

summary = {
    'contiguous_court_cases': len(out), 'correct_new_locators': len(out),
    'opinions_scanned': len(corpus), 'changed_opinions': sum(bool(r['removed'] or r['added']) for r in corpus),
    'removed_cfr_readings': sum(len(r['removed']) for r in corpus),
    'added_cfr_readings': sum(len(r['added']) for r in corpus),
    'new_corpus_compilations': sum(len(r['compilations']) for r in corpus),
    'xml_candidate_kinds': dict(Counter(r['kind'] for r in scan['candidates'])),
    'page_boundary_compilations': len(gap_result['new_occurrences']),
    'page_boundary_cfr': gap_result['new_cfr'],
    'model_calls': 0,
    'source_modules': {str(Path(module.__file__).resolve()): hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
                       for module in (grammar, old)},
    'limits': ['Selected development cases, not general accuracy rates.',
               'Interrupted PDF citation remains unresolved.',
               'AuthorityCitation remains partial and omits range ends; occurrence API and application exports retain them.'],
}
save('comparison.json', summary)
print(json.dumps({k: v for k, v in summary.items() if k not in ('page_boundary_cfr', 'source_modules')}, indent=2))
