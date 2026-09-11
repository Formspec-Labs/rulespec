"""Read-only capability probes, not a benchmark or production adapter."""
import hashlib
import json
import subprocess
from dataclasses import asdict
from pathlib import Path

from refspec.registry.citation_grammar import parse_cfr_citations, usc_section_pinpoint
from spicy_regs.ontology.citations import parse_cfr_citation

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parents[3]
cases = []
for raw in ['40 CFR 82.154(a)(2)', '14 CFR § 91.107(a)(3)(iii)(B)( 4 )',
            '§ 91.107(a)(3)(iii)(B)( 4 )', 'paragraph (a)(3)(iii)(B)( 4 ) of this section',
            '§§ 82.155, 82.156, and 82.157', '40 CFR §§ 82.155, 82.156, and 82.157',
            'paragraphs (b)(1) through (4), (c), and (d)(1) of this section',
            '3 CFR, 1977 Comp., p. 123', '5401-5405']:
    cases.append({'origin': 'constructed capability probe', 'raw': raw})
prior = json.loads((ROOT.parent / '2026-09-10-design-context/cases.json').read_text())
for name, text, start, end in [
    ('seatbelt label parent', prior[1]['document']['text'], '(B) Except as provided', '\n\n( 1 )'),
    ('seatbelt booster restriction', prior[1]['document']['text'], '( 4 ) Except as provided', '\n\n(C)'),
    ('refrigerant compliance route', prior[0]['document']['text'], '(i) The applicable practices', '\n\n(ii)')]:
    lo = text.index(start); hi = text.index(end, lo)
    cases.append({'origin': 'actual pinned source paragraph', 'name': name,
                  'document_sha256': hashlib.sha256(text.encode()).hexdigest(),
                  'start': lo, 'end': hi, 'raw': text[lo:hi]})
for case in cases:
    case['refspec'] = [asdict(c) for c in parse_cfr_citations(case['raw'])]
    case['spicyregs'] = [asdict(c) for c in parse_cfr_citation(case['raw'])]
files = ['RefSpec/src/refspec/registry/citation_grammar.py',
         'spicy-regs/src/spicy_regs/ontology/citations.py']
result = {'purpose': 'Inspection probes; selected cases, no aggregate accuracy claim',
          'provider_calls': 0, 'cases': cases,
          'usc_pinpoint_control': {'raw': '49 USC 1651(b)(2)', 'result': usc_section_pinpoint('49 USC 1651(b)(2)', '1651')},
          'heads': {repo: subprocess.check_output(['git', '-C', str(WORK / repo), 'rev-parse', 'HEAD'], text=True).strip() for repo in ['RefSpec', 'spicy-regs']},
          'file_hashes': {name: hashlib.sha256((WORK / name).read_bytes()).hexdigest() for name in files},
          'initial_probe_failure': 'Rulespec document-poc environment could import RefSpec grammar, but Spicy Regs package import failed: ModuleNotFoundError: pyarrow. Probes then ran in the existing Spicy Regs environment; no dependencies installed.'}
target = ROOT / 'results.json'
if target.exists():
    assert json.loads(target.read_text()) == result
    print('Parser probes reproduced exactly; no files changed.')
else:
    with target.open('x') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print('Saved twelve capability probes, both repository heads, and grammar hashes.')
