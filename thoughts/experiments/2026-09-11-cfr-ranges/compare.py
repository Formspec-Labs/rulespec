"""Compare complete CFR readings using pinned XML, index keys and mutations."""
import argparse
from collections import Counter
import csv
from dataclasses import asdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREVIOUS = HERE.parent / '2026-09-11-cfr-whole-tokens'
sys.path[:0] = [str(ROOT.parent/'RefSpec/src'), str(ROOT/'packages/rulespec-extrapolator/src')]
from refspec.registry import citation_grammar as current
from rulespec_extrapolator.documents import prepare_document
from rulespec_extrapolator.references import scan_references

spec = importlib.util.spec_from_file_location('baseline_cfr_ranges', PREVIOUS/'baseline.py')
baseline = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = baseline
spec.loader.exec_module(baseline)


def readings(reader, text):
    return [asdict(row) for row in reader.find_cfr_citations(text)]


def matches_expected(rows, expected):
    if any(r.get('refusal') for r in rows):
        return False
    if 'parts' in expected:
        return [r['citation'].get('cfr_part') for r in rows] == expected['parts'] and all(
            r['citation']['part_is_plausible'] is not False for r in rows)
    if len(rows) != 1:
        return False
    c = rows[0]['citation']
    def coordinate(endpoint):
        return endpoint['cfr_part'] + ('.'+endpoint['cfr_section'] if endpoint['cfr_section'] else '')
    return 'start' in c and coordinate(c['start']) == expected['range_start'] and coordinate(c['end']) == expected['range_end']


def main():
    args = argparse.ArgumentParser()
    args.add_argument('run', help='New output directory name, e.g. run-01')
    out = HERE/args.parse_args().run
    out.mkdir()
    def save(name, data):
        (out/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
    counts = Counter()
    source_rows = []
    for case in json.loads((PREVIOUS/'source-cases.json').read_text()):
        for mutation, text in [('original', case['focus']), ('unicode_dash', case['focus'].replace('-', '–')),
                               ('linebreak', case['focus'].replace(' ', '\n')), ('neighbor', case['focus']+'; 5 USC 552.'),
                               ('full_paragraph', case['text'])]:
            row = {'case':case['id'], 'mutation':mutation, 'text':text, 'expected':case['expected'],
                   'baseline':readings(baseline,text), 'current':readings(current,text),
                   'authority':[asdict(r) for r in current.parse_authority_citation(text)],
                   'application':scan_references(prepare_document(text))}
            # The full paragraph may contain other citation families, but each
            # selected paragraph has only the CFR item/list under assessment.
            row['baseline_pass'] = matches_expected(row['baseline'],case['expected'])
            row['current_pass'] = matches_expected(row['current'],case['expected'])
            counts['source_cases'] += 1
            counts['baseline_source_pass'] += row['baseline_pass']
            counts['current_source_pass'] += row['current_pass']
            source_rows.append(row)
    save('source-results.json',source_rows)
    control_texts = [r['text'] for r in json.loads((PREVIOUS/'controls.json').read_text())] + [
        '40 CFR §§ 60.1(a) through 61.2(b), and 63.3(c)',
        '41 CFR parts 60-1, 60-3 through 60-4, and 102-193',
        '40 CFR parts 60 through', '40 CFR parts 60 through unknown',
        '40 CFR parts 60 through 123456', '40 CFR parts 60\n\nthrough 63',
        '16 CFR 0.1', '5 CFR part 10001',
        '49 CFR part 172 subparts E and F; 49 CFR part 172 subparts E and F',
    ]
    save('controls.json',[{'text':t,'baseline':readings(baseline,t),'current':readings(current,t),
                          'application':scan_references(prepare_document(t))} for t in control_texts])
    pin = json.loads((PREVIOUS/'summary.json').read_text())
    index = Path(pin['index_path'])
    assert hashlib.sha256(index.read_bytes()).hexdigest() == pin['index_sha256']
    keys = sorted({(r['cfr_title'],r['cfr_part']) for r in csv.DictReader(index.open())})
    with gzip.open(out/'index-results.jsonl.gz','xt') as f:
        for title,part in keys:
            text=f'{title} CFR {part}'
            old,new=readings(baseline,text),readings(current,text)
            counts['index_keys'] += 1
            counts['baseline_complete_index'] += matches_expected(old,{'parts':[part]})
            counts['current_complete_index'] += matches_expected(new,{'parts':[part]})
            # Strip newly introduced empty fields for comparison of old singles.
            equivalent = [{k:v for k,v in r.items() if k not in {'range_end_pinpoint','refusal'}} for r in new] == old
            if not equivalent:
                counts['changed_compound' if title=='41' and '-' in part else 'unexpected_index_change'] += 1
            f.write(json.dumps({'text':text,'expected_part':part,'baseline':old,'current':new})+'\n')
    summary={**counts,'control_cases':len(control_texts),'model_calls':0,
             'grammar_sha256':hashlib.sha256(Path(current.__file__).read_bytes()).hexdigest(),
             'baseline_sha256':hashlib.sha256((PREVIOUS/'baseline.py').read_bytes()).hexdigest(),
             'limitation':'Pinned development cases and structured keys, not general extraction accuracy.'}
    save('summary.json',summary)
    print(json.dumps(summary,indent=2))
    assert counts['current_source_pass']==counts['source_cases']
    assert counts['current_complete_index']==len(keys)
    assert counts['unexpected_index_change']==0


if __name__=='__main__':
    main()
