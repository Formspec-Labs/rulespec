"""One fixed-data comparison of existing RIN helpers; never edits its inputs."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

import pyarrow.parquet as pq
from spicysearch import identifiers
from refspec.registry import identifier_shapes, iri_minting, unified_agenda_parquet
from rulespec_projection import citations
from rulespec_extrapolator.documents import load_document, prepare_document
from rulespec_extrapolator.references import scan_references

ROOT = Path(__file__).resolve().parents[3]
SAVED = ROOT / 'thoughts/experiments/2026-09-11-uslm-readable-text'
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=False)


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def readings(text):
    rows = []
    for match in identifiers.detect_identifiers(text):
        row = {'kind': str(match.kind), 'value': match.value, 'span': list(match.span),
               'quote': text[slice(*match.span)], 'components': dict(match.components)}
        if match.kind == 'rin':
            minted = iri_minting.mint_rin_iri(match.value)
            row.update(refspec_normalized=identifier_shapes.normalize_rin(match.value),
                       arm_b=asdict(minted) if minted else None,
                       arm_c=citations.normalize_rin(match.value))
        rows.append(row)
    return rows


cases = {
    'amendment': '1998—Pars. (6), (7). Pub. L. 105–264 added pars. (6) and (7).',
    'bare': '2060-AS32',
    'labeled_lowercase': 'Agenda entry for RIN 2060-as32.',
    'unicode_repeats': '🧭 RIN 2060–AS32.\n\nRIN 2060—AS32.',
    'unsupported_letters': 'Agenda entry for RIN 0648-ABCD.',
    'product_lookalike': 'Our replacement product has SKU 9999-ZZ99.',
    'null_label': 'RIN: Not Assigned',
    'spaced_damage': 'RIN 2060 - AS32',
    'omb_number': 'OMB Control Number 2060-0314',
    'other_families': 'Pub. L. 119-20; E.O. 12866; docket EPA-HQ-OAR-2021-0317.',
}
for value in ('0648-XD990', '0648-XC705', '3090-00XX', '1115-09AE', '2070-78AB'):
    cases['historical_publisher_exception_' + value] = 'RIN: ' + value

case_rows = []
for name, text in cases.items():
    doc = prepare_document(text)
    scan = scan_references(doc)
    save(name + '-baseline.json', scan)
    case_rows.append({'id': name, 'source': text, 'sha256': sha(text.encode()),
                      'readings': readings(text)})
save('cases.json', case_rows)

source_rows = []
for source in (SAVED.parent / '2026-09-11-uslm-source-links/title-05-s423.xml',
               SAVED.parent / '2026-09-11-uslm-source-links/title-42-s242c.xml',
               SAVED / 'fresh-title-05-pair.xml'):
    doc = load_document(source)
    scan = scan_references(doc)
    save(source.stem + '-baseline.json', scan)
    source_rows.append({'source': str(source), 'sha256': sha(source.read_bytes()),
                        'rin_readings': [r for r in readings(doc['text']) if r['kind'] == 'rin']})
save('sources.json', source_rows)

corpus = Path('/Users/mikewolfd/Work/corpora/refspec-registry-unified-agenda-parquet')
problems = unified_agenda_parquet.verify_unified_agenda_parquet(corpus)
report = {'directory': str(corpus), 'verification_problems': problems}
if not problems:
    receipt = json.loads((corpus / 'receipt.json').read_text())
    table = pq.read_table(corpus / 'unified_agenda_actions.parquet')
    values = sorted(set(table.column('rin').to_pylist()))
    mismatches, unsupported, not_detected = [], [], []
    for value in values:
        b = iri_minting.mint_rin_iri(value)
        c = citations.normalize_rin(value)
        if bool(b) != bool(c) or (b and b.iri != 'urn:rkaf:us:rin:' + c):
            mismatches.append({'raw': value, 'b': asdict(b) if b else None, 'c': c})
        if not b:
            unsupported.append(value)
        if not any(m.kind == 'rin' and m.value == value for m in identifiers.detect_identifiers(value)):
            not_detected.append(value)
    report.update(rows=table.num_rows, distinct_rins=len(values),
                  values_sha256=sha(json.dumps(values, separators=(',', ':')).encode()),
                  receipt_sha256=sha((corpus / 'receipt.json').read_bytes()),
                  source_editions=receipt.get('editions'), output_hashes=receipt['outputs'],
                  schema=str(table.schema), raw_row_samples=table.slice(0, 3).to_pylist(),
                  b_c_mismatches=mismatches, unsupported=unsupported, not_detected=not_detected)
save('corpus.json', report)
save('modules.json', {module.__name__: {'path': module.__file__,
     'sha256': sha(Path(module.__file__).read_bytes())} for module in
     (identifiers, identifier_shapes, iri_minting, citations, unified_agenda_parquet)})

amendment = [r for r in case_rows[0]['readings'] if r['kind'] == 'rin']
product = [r for r in next(r for r in case_rows if r['id'] == 'product_lookalike')['readings'] if r['kind'] == 'rin']
all_rins = [r for case in case_rows for r in case['readings'] if r['kind'] == 'rin']
checks = {
    'actual_heading_refused_by_b_and_c': len(amendment) == 1 and amendment[0]['value'] == '1998-PARS'
        and amendment[0]['arm_b'] is None and amendment[0]['arm_c'] is None,
    'normalization_alone_does_not_fix_heading': len(amendment) == 1 and amendment[0]['refspec_normalized'] == '1998-PARS',
    'product_code_proves_shape_is_not_identity': len(product) == 1 and product[0]['arm_b'] is not None,
    'all_case_candidates_agree_b_c': all(bool(r['arm_b']) == bool(r['arm_c']) for r in all_rins),
    'corpus_verification_passes': not problems,
    'supported_corpus_retained': not problems and not report['unsupported'] and not report['not_detected'],
    'corpus_helpers_agree': not problems and not report['b_c_mismatches'],
    'full_saved_sources_reproduce_one_false_rin': [r['value'] for case in source_rows for r in case['rin_readings']] == ['1998-PARS'],
}
save('decision-checks.json', checks)
print(json.dumps({'checks': checks, 'corpus_rows': report.get('rows'), 'distinct_rins': report.get('distinct_rins')}, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
