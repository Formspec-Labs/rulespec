"""Three frozen connector policies; no production edits or provider calls."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
from xml.etree import ElementTree

from refspec.registry import citation_grammar as g

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OLD = g._CFR_RANGE_CONNECTOR
PROSE = re.compile(r'\s+(?:to\s+(?:the\s+)?(?:same\s+)?(?:extent|manner)\b|through\s+(?:the\s+)?(?:use|application)\s+of\b)', re.I)


class Connector:
    def __init__(self, mode):
        self.mode = mode

    def match(self, text, pos):
        found = OLD.match(text, pos)
        if found is None:
            return None
        if self.mode == 'B' and g._CFR_COORDINATE.match(text, found.end()) is None:
            return None
        if self.mode == 'C' and PROSE.match(text, pos):
            return None
        return found


def capture(text):
    rows = g.find_cfr_citations(text)
    assert all(text[r.start:r.end] == r.text for r in rows)
    return {'occurrences': [asdict(r) for r in rows],
            'identities': [asdict(r) for r in g.parse_cfr_citations(text)],
            'authorities': [asdict(r) for r in g.parse_authority_citation(text)]}


def save(name, value):
    with (HERE / name).open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


publisher = json.loads((HERE / 'publisher-selection.json').read_text())['cases']
cases = [{'id':p['id'], 'kind':'publisher-prose', 'text':p['text'],
          'expected':{'readings':len(p['baseline']), 'refusals':0}} for p in publisher]
controls = [
    ('actual-explicit-counterpart', '41 CFR § 50-202.2 to the same extent such employment is permitted under section 14 of the Fair Labor Standards Act.', 1, 0),
    ('comparative-manner', '41 CFR § 50-202.2 to the same manner as specified elsewhere.', 1, 0),
    ('instrumental', '41 CFR § 50-202.2 through the use of existing forms.', 1, 0),
    ('agency-prose', '41 CFR § 50-202.2 through the agency.', 1, 0),
    ('complete-range', '41 CFR §§ 50-202.2 to 50-202.4', 1, 0),
    ('complete-through', '41 CFR §§ 50-202.2 through 50-202.4', 1, 0),
    ('complete-dash', '41 CFR §§ 50-202.2 - 50-202.4', 1, 0),
    ('missing-end', '41 CFR § 50-202.2 through', 1, 1),
    ('unknown-end', '41 CFR § 50-202.2 through unknown', 1, 1),
    ('plural-unknown', '40 CFR parts 60 through unknown', 1, 1),
    ('symbol-end', '41 CFR §§ 50-202.2 to ???', 1, 1),
    ('named-end', '41 CFR §§ 50-202.2 to the last section of this part', 1, 1),
    ('same-section-end', '41 CFR §§ 50-202.2 through the same section', 1, 1),
    ('damaged-end', '41 CFR §§ 50-202.2 through 50- 204.4', 1, 1),
    ('abbreviated-end', '40 CFR §§60.1(a) through (c)', 1, 1),
    ('cross-citation-end', '41 CFR parts 60-1 through 40 CFR part 60', 2, 1),
    ('mixed-range', '40 CFR parts 60 through 61.2', 1, 1),
    ('nested-range', '40 CFR parts 60 through 61 through 62', 1, 1),
    ('nested-unread', '40 CFR parts 60 through 61 through unknown', 1, 1),
    ('range-then-prose', '41 CFR §§ 50-202.2 to 50-202.4 to the same extent as other firms.', 1, 0),
    ('list-then-prose', '41 CFR §§ 50-202.2, 50-202.4 to the same extent as other firms.', 2, 0),
    ('reverse-complete', '§§ 50-202.2 to 50-202.4 of title 41, Code of Federal Regulations', 1, 0),
    ('reverse-unread', '§§ 50-202.2 to unknown of title 41, Code of Federal Regulations', 1, 1),
    ('line-wrap', '41 CFR § 50-202.2\nto the same extent as other firms.', 1, 0),
    ('paragraph-break', '41 CFR § 50-202.2\n\nto the same extent as other firms.', 1, 0),
    ('note-retained', '41 CFR § 50-202.2 note to the same extent as other firms.', 1, 1),
    ('existing-open-end', '41 CFR § 50-202.2 et seq.', 1, 1),
    ('prose-word-boundary', '41 CFR § 50-202.2 tomorrow', 1, 0),
]
for identity,text,count,refused in controls:
    cases.append({'id':identity,'kind':'constructed','text':text,
                  'expected':{'readings':count,'refusals':refused}})
xml_path = ROOT / 'thoughts/experiments/2026-09-11-cfr-native-context/inputs-complete/compound-part.xml'
xml = xml_path.read_text()
raw_text = ''.join(ElementTree.fromstring(xml).itertext())
cases.append({'id':'actual-bare-source', 'kind':'publisher-bare', 'text':raw_text,
              'expected':{'readings':0,'refusals':0}})
# Save criteria and input bytes before collecting the comparison outputs.
save('cases.json',cases)
save('original-source.json',{'path':str(xml_path),'sha256':hashlib.sha256(xml.encode()).hexdigest(),'xml':xml})
save('runtime.json',{'reader_path':g.__file__,'reader_sha256':hashlib.sha256(Path(g.__file__).read_bytes()).hexdigest(),
                     'old_connector_pattern':OLD.pattern,'old_connector_flags':OLD.flags,
                     'prose_pattern':PROSE.pattern,'prose_flags':PROSE.flags,
                     'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'model_calls':0})
all_results={}
try:
    for mode in ('A','B','C'):
        g._CFR_RANGE_CONNECTOR = OLD if mode == 'A' else Connector(mode)
        results=[]
        for case in cases:
            observed=capture(case['text'])
            rows=observed['occurrences']
            criteria=case['expected']
            passed=len(rows)==criteria['readings'] and sum(r['refusal'] is not None for r in rows)==criteria['refusals']
            results.append({'id':case['id'],'kind':case['kind'],'passed':passed,**observed})
        at=raw_text.index('50-202.2')
        item=g._read_cfr_item(raw_text,g._normalize_dashes(raw_text),41,at-2,at,False)
        save(f'{mode}.json',{'cases':results,'actual_source_item':asdict(item)})
        all_results[mode]=results
finally:
    g._CFR_RANGE_CONNECTOR=OLD
summary={mode:{'passed':sum(r['passed'] for r in rows), 'cases':len(rows),
               'publisher_prose_recovered':sum(r['passed'] for r in rows if r['kind']=='publisher-prose'),
               'failed_cases':[r['id'] for r in rows if not r['passed']]} for mode,rows in all_results.items()}
save('summary.json',summary)
print(json.dumps(summary,indent=2))
