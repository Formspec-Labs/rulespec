"""Read raw model fields, including complete prefixes of truncated responses.

Inspection only: never feed a recovered prefix to compilation or count it as a
successful response. Null keys can be hidden in the display; original bytes stay
in the provider capture.
"""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
cell, start, stop = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
folder = root / 'cells' / cell
raw = json.loads(next(folder.glob('attempt-*.response.json')).read_text())
text = ''.join(p['text'] for c in raw['candidates'] for p in c['content']['parts']
               if p.get('text') and not p.get('thought'))
complete = True
try:
    payload = json.loads(text)
except json.JSONDecodeError:
    complete = False
    # The actual response begins with its complete terms array. Decode that
    # array, then the extraction objects individually until the incomplete one.
    decoder = json.JSONDecoder()
    terms, pos = decoder.raw_decode(text, text.index('['))
    pos = text.index('[', pos) + 1
    rows = []
    while True:
        while pos < len(text) and text[pos] in ' \n\r\t,':
            pos += 1
        try:
            row, pos = decoder.raw_decode(text, pos)
        except json.JSONDecodeError:
            break
        rows.append(row)
    payload = {'terms':terms,'extractions':rows}
    print('INCOMPLETE RESPONSE. Remaining undecodable characters:',len(text)-pos)
print(cell, 'complete:',complete, 'finish:',[c.get('finish_reason') for c in raw['candidates']])
if start == 0:
    print('TERMS',json.dumps(payload['terms'],ensure_ascii=False))
for i,row in enumerate(payload['extractions'][start:stop], start):
    print(i,row['unit'],json.dumps({k:v for k,v in row['unit_attributes'].items() if v is not None},ensure_ascii=False))
print('TOTAL DISPLAYABLE ROWS',len(payload['extractions']))
