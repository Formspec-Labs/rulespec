"""Freeze manually specified labels before running any parser."""
import json
from hashlib import sha256
from pathlib import Path

root = Path(__file__).parent
old = json.loads(root.parent.joinpath('2026-09-10-reference-tool-reuse/inputs.json').read_text())
cases = []
for case in old:
    if case['origin'] != 'actual pinned source paragraph':
        continue
    expected = {'seatbelt label parent': ['local|a.3.iii.B.4'],
                'seatbelt booster restriction': ['cfr|49|571|213', 'local|91.107.B.3.iii', 'local|91.107.B.3.iv'],
                'refrigerant compliance route': [f'local|82.{n}' for n in (155,156,157,158,161,164)]}[case['name']]
    cases.append({**case, 'expected': expected, 'negative': False,
                  'label_note': 'Explicit CFR identity scored; local references stay local, with no inferred title.'})
rows = [
 ('lettered-part', '7 CFR 15a', ['cfr|7|15a|']),
 ('compound-usc', '42 U.S.C. 1395w-4', ['usc|42|1395w-4']),
 ('usc-in-prose', 'The agency acts under 5 U.S.C. 552, as discussed below.', ['usc|5|552']),
 ('usc-chapter', '5 U.S.C. chapter 5', ['usc_chapter|5|5']),
 ('usc-appendix', '5 U.S.C. App. 3', ['usc_appendix|5|3']),
 ('usc-note', '42 U.S.C. 1983 note', ['usc_note|42|1983']),
 ('public-law', 'The authority is Pub. L. 117-58.', ['public_law|117-58']),
 ('statutes-page', 'See 135 Stat. 429.', ['statute|135|429']),
 ('fr-page', 'See 89 FR 91529.', ['federal_register|89|91529']),
 ('executive-order', 'E.O. 12866 applies.', ['executive_order|12866']),
 ('proclamation', 'Proclamation 9980.', ['proclamation|9980']),
 ('constitution', 'U.S. Const. art. I, sec. 8', ['constitution|I|8']),
 ('treaty', '27 U.S.T. 1087', ['treaty|UST|27|1087']),
 ('reorganization', 'Reorganization Plan No. 3 of 1970', ['reorganization_plan|3-of-1970']),
 ('case-reporter', 'See 410 U.S. 113 (1973).', ['case|U.S.|410|113']),
 ('docket', 'See EPA-HQ-OAR-2023-0234.', ['docket|EPA-HQ-OAR-2023-0234']),
 ('rin', 'RIN 2120-AK94', ['rin|2120-AK94']),
 ('named-act', 'Section 112 of the Clean Air Act applies.', ['act_relative|clean air act|112']),
 ('eo-compilation', '3 CFR, 1977 Comp., p. 123', ['eo_compilation|1977|123']),
 ('usc-list', '5 USC 552 and 552a', ['usc|5|552', 'usc|5|552a']),
 ('cfr-list', '40 CFR §§ 82.155(a), 82.156(b)', ['cfr|40|82|155', 'cfr|40|82|156']),
 ('plain-roles', 'Posts may consult the IRL and IN indexes.', []),
 ('ordinary-prose', 'Romeo met the staff. They discussed the status of the application.', []),
 ('bare-range', '5401-5405', []),
 ('malformed-cfr', '17 CFR 15c3-3', []),
 ('malformed-usc', '42 USC 1983affirmed', []),
 ('fused-title', '1345 CFR 1370', []),
 ('unknown-act', 'Section 8 of the Imaginary Compliance Act applies.', []),
 ('lowercase-fr', 'The tracking text reads 89 fr 91529.', []),
]
for name,text,expected in rows:
    cases.append({'origin':'constructed diagnostic, manually selected', 'name':name,'raw':text,
                  'expected':expected,'negative':not expected,
                  'label_note':'Lexical identity only; no legal existence or applicability judgment.'})
assert len(cases) <= 36
for i,c in enumerate(cases):
    c['id'] = f'case-{i+1:02d}'
    c['text_sha256'] = sha256(c['raw'].encode()).hexdigest()
with root.joinpath('cases.json').open('x') as f:
    json.dump({'act_names':['clean air act'], 'cases':cases},f,indent=2,ensure_ascii=False)
