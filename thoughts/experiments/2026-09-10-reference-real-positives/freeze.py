"""Manual source labels, fixed before parser execution; no parser imports."""
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parent
specs = [
    ('2025-24202', 4, [('docket', 'EPA-HQ-OAR-2023-0330', 'EPA-HQ-OAR-2023-0330'), ('rin', '2060-AW28', '2060-AW28')]),
    ('2025-24202', 18, [('executive_order', f'Executive Order {n}', f'Executive Order {n}') for n in ('12866', '14192', '13132', '13175', '13045', '13211')]),
    ('2025-24202', 28, [('public_law', 'Public Law 119-20', 'Public Law (Pub. L.) 119-20')]),
    ('2025-24202', 64, [('public_law', 'Public Law 119-20', 'Public Law \n119-20'), ('statutes_at_large', '139 Stat. 71', '139 Stat. 71')]),
    ('2024-07412', 16, [('docket', 'EPA-HQ-OW-2022-0901', 'EPA-HQ-OW-2022-0901'), ('rin', '2040-AG25', '2040-AG25')]),
    ('2024-07412', 27, []),
    ('2024-07412', 87, [('public_law', 'Public Law 104-113', 'Public Law \n104-113')]),
    ('2024-07412', 120, [('public_law', 'Public Law 95-217', 'Pub. L. 95-217'), ('statutes_at_large', '91 Stat. 1566', '91 Stat. 1566')]),
]
cases = []
for document, block_index, labels in specs:
    source_path = root / 'sources' / f'{document}.txt'
    source = source_path.read_text()
    blocks = list(re.finditer(r'\S[\s\S]*?(?=\n[ \t]*\n|\Z)', source))
    start, end = blocks[block_index].start(), blocks[block_index + 1].end()
    text = source[start:end]
    expected = []
    for kind, value, quote in labels:
        a = text.index(quote)
        expected.append({'kind': kind, 'value': value, 'quote': quote, 'span': [a, a + len(quote)]})
    cases.append({'id': f'{document}-block-{block_index}', 'name': f'{document} paragraphs {block_index}–{block_index+1}',
                  'group': 'real-positive', 'raw': text, 'text_sha256': hashlib.sha256(text.encode()).hexdigest(),
                  'origin': 'manually selected published source blocks, not parser-selected',
                  'source_path': str(source_path.relative_to(root)), 'source_span': [start, end],
                  'source_sha256': hashlib.sha256(source.encode()).hexdigest(), 'expected_additions': expected})
previous = json.loads((root.parent / '2026-09-10-additive-reference-families/cases.json').read_text())
ohio = next(case for case in previous if case['id'] == 'source-3')
cases.append({**ohio, 'group': 'historical-noise-control', 'origin': 'unchanged prior Ohio negative control'})
with (root / 'cases.json').open('x') as f:
    json.dump(cases, f, ensure_ascii=False, indent=2)
print(json.dumps({'cases': len(cases), 'expected_occurrences': sum(len(c['expected_additions']) for c in cases)}))
