"""Retain complete native excerpts through the existing RefSpec/Rulespec reader."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from zipfile import ZipFile
import run as exp
from rulespec_extrapolator import refinement as r, uslm

ARCHIVE = Path('/Users/mikewolfd/Work/RefSpec/output/usc-annual-2026-08-24/xml_uscAll_119-102.zip')
CASES = [
    ('leave', 'usc29.xml', '/us/usc/t29/s2612/e', 'necessity for leave under subparagraph'),
    ('billing', 'usc15.xml', '/us/usc/t15/s1666/a', 'receives at the address disclosed under section 1637'),
    ('hazard', 'usc15.xml', '/us/usc/t15/s2064/b', 'Commission has been adequately informed'),
    ('debt', 'usc15.xml', '/us/usc/t15/s1692g/a', 'Within five days after the initial communication'),
    ('offset', 'usc31.xml', '/us/usc/t31/s3716/a', 'After trying to collect a claim from a person'),
    ('workplace', 'usc29.xml', '/us/usc/t29/s657/a', 'upon presenting appropriate credentials'),
    ('jury_fee', 'usc28.xml', '/us/usc/t28/s1871/b', 'A petit juror required to attend more than ten days'),
    ('religious', 'usc42.xml', '/us/usc/t42/s2000e–2/e', 'bona fide occupational qualification reasonably necessary')]


def main():
    receipts, freshness = [], []
    with ZipFile(ARCHIVE) as archive:
        for name, member, identifier, phrase in CASES:
            search = subprocess.run(['rg', '-l', '-F', '-e', identifier, '-e', phrase,
                'thoughts/experiments', 'examples', '-g', '!**/frozen/**', '-g', '!**/source-snapshot/**',
                '-g', '!**/2026-09-13-fresh-field-completeness/**'], capture_output=True, text=True)
            assert search.returncode == 1, (name, search.stdout, search.stderr)
            freshness.append(dict(name=name, identifier=identifier, phrase=phrase, prior_matches=[], returncode=search.returncode))
            raw = archive.read(member)
            root = ET.fromstring(raw)
            found = root.findall('.//*[@identifier="' + identifier + '"]')
            assert len(found) == 1
            wrapper = ET.Element(root.tag, root.attrib)
            wrapper.append(deepcopy(found[0]))
            xml = ET.tostring(wrapper, encoding='unicode')
            document = uslm.prepare_xml(xml, title=f'US Code {identifier} — fresh checker study',
                source_url='https://uscode.house.gov/download/releasepoints/us/pl/119/102/xml_uscAll@119-102.zip')
            exp.x.save(f'sources/{name}.json', document)
            receipts.append(dict(name=name, native_excerpt=identifier, member=member,
                member_sha256=sha256(raw).hexdigest(), serialized_sha256=sha256(xml.encode()).hexdigest(),
                text_sha256=sha256(document['text'].encode()).hexdigest(), characters=len(document['text'])))
            print(name, len(document['text']), 'characters')
    exp.x.save('source-receipts.json', dict(archive=str(ARCHIVE), archive_sha256=sha256(ARCHIVE.read_bytes()).hexdigest(),
                                         release='119-102', excerpts=receipts))
    exp.x.save('freshness-check.json', freshness)
    positive = exp.x.prior.e._load(exp.HERE.parent / '2026-09-13-checker-instruction-isolation/instructions.json')['M4b']['B']
    exp.x.save('instructions.json', dict(A=r.CHECK, B=positive))


if __name__ == '__main__': main()
