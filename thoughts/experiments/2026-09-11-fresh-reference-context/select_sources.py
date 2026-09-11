"""Select untuned source opportunities before labels, prompts or model output."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile

from rulespec_extrapolator.documents import source_passages
from rulespec_extrapolator.extraction import plan_windows
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator.uslm import prepare_uslm

HERE = Path(__file__).resolve().parent
ARCHIVE = Path('/Users/mikewolfd/Work/RefSpec/output/usc-annual-2026-08-24/xml_uscAll_119-102.zip')
RECEIPT = Path('/Users/mikewolfd/Work/RefSpec/output/usc-source-credit-index-2026-08-02/receipt.json')
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def save(path, data):
    with path.open('x') as f:
        json.dump(data, f, indent=2, ensure_ascii=False); f.write('\n')


pins = json.loads(RECEIPT.read_text())['inputs']
archive_sha = sha(ARCHIVE.read_bytes())
assert 'sha256:' + archive_sha == pins['archive_digest']
selected, considered = [], []
with zipfile.ZipFile(ARCHIVE) as archive:
    for title in ('29', '38', '20'):
        member = f'usc{title}.xml'
        raw = archive.read(member)
        member_sha = sha(raw)
        assert 'sha256:' + member_sha == next(p['digest'] for p in pins['titles'] if p['member'] == member)
        root = ET.fromstring(raw)
        root_open = re.search(rb'<uscDoc\b[^>]*>', raw)[0]
        found = False
        for chapter in root.iter('{http://xml.house.gov/schemas/uslm/1.0}chapter'):
            identity = chapter.get('identifier')
            if not identity or len(list(chapter.iter(chapter.tag))) != 1:
                continue
            text = ''.join(chapter.itertext())
            if not 30000 <= len(text) <= 150000:
                continue
            markers = list(re.finditer(rb'<chapter\b[^>]*\bidentifier="' + re.escape(identity.encode()) + rb'"[^>]*>', raw))
            assert len(markers) == 1, identity
            start = markers[0].start()
            end = raw.index(b'</chapter>', start) + len(b'</chapter>')
            fragment = raw[start:end]
            capture = root_open + fragment + b'</uscDoc>'
            parsed = ET.fromstring(capture)
            assert ''.join(parsed.itertext()) == text
            doc = prepare_uslm(capture.decode(), title=identity, source_url='https://uscode.house.gov/download/releasepoints/us/pl/119/102/xml_uscAll@119-102.zip')
            windows = plan_windows(doc)
            scan = scan_references(doc)
            opportunities = []
            for window in windows:
                for occurrence in scan['candidates']:
                    if occurrence['kind'] != 'publisher_reference' or occurrence['reading']['context'] != 'operative':
                        continue
                    evidence = occurrence.get('evidence', [])
                    if not evidence or not window['start'] <= evidence[0]['start'] < evidence[-1]['end'] <= window['end']:
                        continue
                    if occurrence['resolution']['status'] != 'located':
                        continue
                    target = scan['targets'][occurrence['resolution']['target_ids'][0]]
                    if 'start' not in target or not (target['end'] <= window['start'] or target['start'] >= window['end']):
                        continue
                    target_text = doc['text'][target['start']:target['end']]
                    if not 150 <= len(target_text) <= 12000 or not re.search(r'\b(means|except|unless|shall)\b', target_text, re.I):
                        continue
                    opportunities.append({'window_index': window['index'], 'occurrence_id': occurrence['id'],
                        'source_unit': occurrence['reading']['sourceUnit'], 'href': occurrence['value'],
                        'quote': ''.join(e['quote'] for e in evidence), 'target_id': target['id'],
                        'target_start': target['start'], 'target_end': target['end'],
                        'target_preview': target_text[:650]})
            considered.append({'chapter': identity, 'prepared_chars': len(doc['text']),
                'windows': len(windows), 'operative_links': sum(r['kind'] == 'publisher_reference' and r['reading']['context'] == 'operative' for r in scan['candidates']),
                'opportunities': len(opportunities)})
            if not opportunities:
                continue
            first = opportunities[0]
            case_id = 'title-' + title + '-' + identity.rsplit('/', 1)[-1]
            folder = HERE / 'sources' / case_id; folder.mkdir(parents=True, exist_ok=False)
            (folder / 'source.xml').write_bytes(capture)
            (folder / 'prepared.txt').write_text(doc['text'])
            save(folder / 'document.json', doc)
            save(folder / 'references.json', scan)
            save(folder / 'windows.json', windows)
            window = windows[first['window_index']]
            (folder / 'focus.txt').write_text(doc['text'][window['start']:window['end']])
            record = {'id': case_id, 'chapter': identity, 'selected_window_index': first['window_index'],
                'source': {'archive': str(ARCHIVE), 'archive_sha256': archive_sha, 'member': member,
                           'member_sha256': member_sha, 'chapter_start': start, 'chapter_end': end,
                           'chapter_sha256': sha(fragment), 'capture_sha256': sha(capture),
                           'release_point': pins['release_point'], 'preparation': 'exact chapter bytes in original uscDoc wrapper'},
                'prepared_chars': len(doc['text']), 'source_passages': len(source_passages(doc)),
                'focus_start': window['start'], 'focus_end': window['end'],
                'opportunities': [r for r in opportunities if r['window_index'] == first['window_index']]}
            save(folder / 'selection.json', record); selected.append(record)
            print(json.dumps({'selected': case_id, 'prepared_chars': record['prepared_chars'], 'focus': [window['start'], window['end']], 'first_opportunity': first}, ensure_ascii=False), flush=True)
            found = True
            break
        if not found:
            print('No eligible chapter in title', title, flush=True)
save(HERE / 'source-selection.json', {'selected': selected, 'considered': considered,
    'selection_is_opportunity_based': True, 'labels_and_requests_frozen': False, 'provider_calls': 0})
