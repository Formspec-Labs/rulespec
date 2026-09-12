"""Freeze source-derived questions before viewing extraction output."""
import json
from pathlib import Path
import re
from prepare import save

HERE = Path(__file__).resolve().parent
DOCS = {name: json.loads((HERE / f'sources/{name}.document.json').read_text())
        for name in ('manual', 'annual', 'uslm')}
questions = []


def paragraph(source, snippet):
    matches = [p for p in re.split(r'\n\s*\n', DOCS[source]['text']) if snippet in p]
    assert len(matches) == 1, (source, snippet, len(matches))
    return matches[0]


def add(identity, source, query, snippets, expectation):
    quotes = [paragraph(source, s) for s in snippets]
    questions.append(dict(id=identity, source=source, query=query, required_quotes=quotes,
                          expected_meaning=expectation, label_status='agent-authored, source-supported, revisable'))


add('M1', 'manual', 'What marriage assistance can consular officers provide now?',
    ['a. The role of the consular officer'],
    'Limited to information obtained from foreign officials and notarial/authentication services; historical witness authority is not a current power.')
add('M2', 'manual', 'Can an ambassador or consular officer conduct a marriage ceremony?',
    ['a. Diplomatic and Consular officers'],
    'Diplomatic officers, consular officers and US ambassadors cannot conduct ceremonies; all named actor classes survive.')
add('M3', 'manual', 'Can a consular officer certify that someone living in the United States is eligible to marry abroad?',
    ['c.\u00a0 You cannot make any official certification'],
    'Cannot officially certify status/eligibility of US residents proposing marriage abroad; preserve residence and destination scope.')
add('M4', 'manual', 'Are old FS-87 Certificates of Witness to Marriage still valid?',
    ['d. Certificates of Witness to Marriage'],
    'Certificates issued under the stated authority before repeal remain valid; this does not authorize new certificates.')
add('A1', 'annual', 'How much waste can a generator keep at a satellite accumulation point without a permit?',
    ['(a) A generator may accumulate'],
    '55 gallons non-acute; either one quart liquid acute or 1 kg solid acute, listed waste qualifications; at/near generation under operator control and all exemption conditions. Do not make this unconditional.')
add('A2', 'annual', 'When may a hazardous waste container be left open for venting?',
    ['(4) A container holding hazardous waste', '(ii) When temporary venting', '(A) For the proper operation', '(B) To prevent dangerous'],
    'Closed by default; temporary venting only when necessary for proper equipment operation or prevention of dangerous situations. General permission to leave open is wrong.')
add('A3', 'annual', 'What must a generator immediately do when a waste container leaks?',
    ['(1) If a container holding hazardous waste'],
    'Immediately transfer to a sound nonleaking container OR transfer and manage in a compliant central accumulation area; not both, not unrestricted disposal.')
add('A4', 'annual', 'What are the options and continuing duties after satellite waste exceeds the limit?',
    ['(6) A generator who accumulates', '(i) Comply within three consecutive', '(ii) Remove the excess', '(A) A central accumulation area', '(B) An on-site interim', '(C) An off-site designated', '(iii) During the three-consecutive'],
    'Within three consecutive calendar days comply with central-area rules OR remove excess to one of three specified destinations; during the period continue (a)(1)-(5) and date-label the excess containers. Preserve OR versus AND.')
add('U1', 'uslm', 'How much military leave accrues each fiscal year, including for part-time employees?',
    ['(1) Subject to paragraph (2)', '(2) In the case of an employee'],
    '20 days per fiscal year for eligible covered service; unused carryover capped at 20 at start of fiscal year. Part-time career accrual prorated scheduled weekly hours divided by 40. Not a blanket 20-day award to everyone.')
add('U2', 'uslm', 'Can service under section 6323(b) use annual leave, compensatory time, or sick leave?',
    ['is entitled, during and because of such service'],
    'Annual leave or available compensatory time instead of military leave only upon employee request; period may not be charged to sick leave; do not generalize this beyond (b).')
add('U3', 'uslm', 'What conditions govern the 44-day military reserve technician leave?',
    ['(1) A military reserve technician described', 'Section 8401(30) of this title, referred'],
    'At request, covered technician, active duty without pay under cited authorities, operations outside US/territories/possessions, max 44 workdays/calendar year. Preserve editorial warning that the cited definition no longer describes technicians; target identity unresolved.')
add('U4', 'uslm', 'Does the historical substitute postal employee definition make 80 hours the general military leave allowance?',
    ['(1) Subject to paragraph (2)', 'struck out subsec. (b) relating to military leave', 'Act July 1, 1947, ch. 192'],
    'No general 80-hour allowance: distinguish current (a) 20-day accrual from the historical substitute-worker note and stated repeal. Do not link every modern employee mention to that old definition as an equivalent sense.')
assert len(questions) == 12
save('questions.json', questions)
