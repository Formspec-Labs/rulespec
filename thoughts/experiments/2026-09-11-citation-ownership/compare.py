"""Bounded reader comparison; source-index strings are constructed, not prose labels."""
import ast
import csv
from dataclasses import asdict
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WORK = ROOT.parent
BASE = '762900d'
MODULE = 'packages/rulespec-projection/src/rulespec_projection/citations.py'
sys.path[:0] = [str(ROOT / 'packages/rulespec-projection/src'),
               str(WORK / 'RefSpec/src'), str(WORK / 'spicysearch/src')]
from rulespec_projection import citations as current
from refspec.registry import citation_grammar as refspec
from spicysearch import cfr_citations as spicysearch


def sha(data):
    return hashlib.sha256(data).hexdigest()


def call(fn, value):
    try:
        return {'value': [asdict(c) for c in fn(value)]}
    except Exception as error:
        return {'error': f'{type(error).__name__}: {error}'}


def main():
    output = HERE / sys.argv[1]
    output.mkdir(exist_ok=False)
    baseline_bytes = subprocess.check_output(['git', 'show', f'{BASE}:{MODULE}'], cwd=ROOT)
    old = types.ModuleType('frozen_citations')
    sys.modules[old.__name__] = old
    exec(compile(baseline_bytes, f'{BASE}:{MODULE}', 'exec'), old.__dict__)
    csv_path = WORK / 'RefSpec/research/evidence/cfr-subject-index-2026-08-20/part-subjects.csv'
    csv_bytes = csv_path.read_bytes()
    parts = sorted({(r['cfr_title'], r['cfr_part']) for r in csv.DictReader(csv_bytes.decode().splitlines())})
    controls = [
        '7 CFR 15a', '7 CFR 15', '26 CFR 16A', '41 CFR 101-1',
        '41 CFR 60-1.4(a)', '41 CFR parts 60-1, 60-2', '40 CFR parts 60-63',
        '40 CFR 60-63', '17 CFR 15c3-3', '28 CFR 23-4', '49 CFR 571-108',
        '40 CFR §§ 82.155, 82.156, and 82.157', '17 CFR 240, 15 U.S.C. 78c',
        '40 CFR part 37, 12 people attended.', '1345 CFR 1370.31',
        '35 CFR 62', '3 CFR, 1977 Comp., p. 123; 40 CFR 60',
        '3 CFR 127 (1981 Comp.)', '5, part 2', 'title 40, part 60',
        '7-15a', '40-60.5', {'title': 7, 'part': '15a'},
        {'title': 40, 'part': 60, 'section': '5'}, None,
    ]
    counts = {key: {'correct_part': 0, 'wrong_part': 0, 'refused': 0} for key in ('projection', 'refspec', 'spicysearch')}
    differences = []
    with gzip.open(output / 'raw.jsonl.gz', 'wt', encoding='utf-8') as raw:
        for index, (value, expected) in enumerate(
            [(f'{t} CFR {p}', (t, p)) for t, p in parts] + [(v, None) for v in controls]
        ):
            readings = {
                'projection': call(old.parse_cfr_citation, value),
                'current': call(current.parse_cfr_citation, value),
                'refspec': call(refspec.find_cfr_citations, value),
                'spicysearch': call(lambda v: spicysearch.extract_citations(v, strict=True, keep_rejected=True), value),
            }
            assert readings['projection'] == readings['current'], (index, value)
            row = {'input': value, 'index_key': expected, 'readings': readings}
            raw.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
            if expected is None:
                differences.append(row)
                continue
            for arm in counts:
                got = readings[arm].get('value', [])
                if arm == 'refspec':
                    keys = [(str(c['citation']['cfr_title']), c['citation']['cfr_part']) for c in got]
                else:
                    keys = [(str(c['title']), c['part']) for c in got if not c.get('rejected')]
                key = ('refused' if not keys else 'correct_part' if keys == [expected] else 'wrong_part')
                counts[arm][key] += 1
    # Copy deletion must not alter any surviving function, type or expression.
    def definitions(source):
        return {node.name: ast.dump(node, include_attributes=False)
                for node in ast.parse(source).body if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    before, after = definitions(baseline_bytes), definitions((ROOT / MODULE).read_bytes())
    assert all(before.get(name) == value for name, value in after.items())
    def constants(source):
        return {node.targets[0].id: ast.dump(node, include_attributes=False)
                for node in ast.parse(source).body if isinstance(node, ast.Assign)
                and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)}
    old_constants, new_constants = constants(baseline_bytes), constants((ROOT / MODULE).read_bytes())
    assert all(old_constants.get(name) == value for name, value in new_constants.items())
    roots = {alias.name for node in ast.walk(ast.parse((ROOT / MODULE).with_name('projection.py').read_text()))
             if isinstance(node, ast.ImportFrom) and node.module == 'citations' for alias in node.names}
    nodes = {node.name: node for node in ast.parse(baseline_bytes).body
             if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    reachable, pending = set(), list(roots)
    while pending:
        name = pending.pop()
        if name not in nodes or name in reachable:
            continue
        reachable.add(name)
        pending.extend(node.id for node in ast.walk(nodes[name]) if isinstance(node, ast.Name))
    assert not (before.keys() - after.keys()) & reachable
    summary = {
        'baseline': BASE, 'baseline_module_sha256': sha(baseline_bytes),
        'current_module_sha256': sha((ROOT / MODULE).read_bytes()),
        'removed_definitions': sorted(before.keys() - after.keys()),
        'surviving_definitions_unchanged': len(after),
        'surviving_constants_unchanged': len(new_constants),
        'graph_citation_imports': sorted(roots),
        'graph_reachable_definitions': sorted(reachable),
        'source_index': {'path': str(csv_path), 'sha256': sha(csv_bytes), 'distinct_keys': len(parts)},
        'constructed_controls': len(controls), 'counts': counts,
        'modules': {m.__name__: {'path': m.__file__, 'sha256': sha(Path(m.__file__).read_bytes())}
                    for m in (current, refspec, spicysearch)},
        'commits': {repo: subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=WORK / repo, text=True).strip()
                    for repo in ('rulespec', 'RefSpec', 'spicysearch', 'spicy-regs')},
    }
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (output / 'controls.json').write_text(json.dumps(differences, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
