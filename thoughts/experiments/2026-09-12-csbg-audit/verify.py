"""Check full adapter configuration, including MIME type omitted by run.py."""
from unittest.mock import patch
from langextract.providers.schemas.gemini import GeminiSchema
from run import HERE, BASE, MODEL, a, e, save, verify_pins

verify_pins()
cells = e._load(HERE / 'cells.json')
groups = {g['id']: g for g in cells['groups']}
doc = e._load(BASE.parent / '2026-09-12-csbg/sources/document.json')
checks = []


def check(name, prompt, schema):
    directory = HERE / 'captures' / name
    attempts = e._load(directory / 'attempts.json')
    assert len(attempts) == 1
    config = {'temperature': 0, 'candidate_count': 1, 'max_output_tokens': 32768,
              'thinking_config': {'thinking_level': 'medium'},
              **GeminiSchema(schema, _use_json_schema=True).to_provider_config()}
    assert e._load(directory / attempts[0]['request_file']) == {
        'model': MODEL, 'contents': prompt, 'config': config}
    return directory, attempts


with patch.object(e, '_create_model', side_effect=AssertionError('Unexpected provider call')):
    for g in cells['groups']:
        prompt = e._window_prompt(e._prompt_generator([], a.INVENTORY_PROMPT), doc, g['window'])
        assert prompt == g['prompt']
        directory, attempts = check('inventory-' + g['id'], prompt, a.INVENTORY_SCHEMA)
        inventory = a._inventory(directory, doc, [g['window']], attempts)
        assert inventory == e._load(HERE / f"inventory/{g['id']}.json")
        assert a._labels(doc, inventory, MODEL) == e._load(HERE / f"labels/{g['id']}.json")
        checks.append({'cell': 'inventory-' + g['id'], 'units': len(inventory['units']),
                       'issues': inventory['issues'], 'request_and_replay_equal': True})
    for c in cells['comparisons']:
        book = e._load(BASE / f"decoded/{c['draft']}.json")['book']
        labels = e._load(HERE / f"labels/{c['group']}.json")
        window = groups[c['group']]['window']
        directory, attempts = check(c['id'], a._comparison_request(book, labels, window), a.COMPARISON_SCHEMA)
        judgments, issues = a._judgments(directory, book, labels, [window], attempts, MODEL)
        assert {'judgments': judgments, 'issues': issues} == e._load(HERE / f"decoded/{c['id']}.json")
        _, claims, units = a._comparison_input(book, labels, window)
        assert {c['id'] for c in claims.values()} == {c['claim_id'] for c in judgments['claim_judgments']}
        assert {u['id'] for u in units.values()} == {u['unit_id'] for u in judgments['unit_judgments']}
        claim_edges = {(c['claim_id'], u) for c in judgments['claim_judgments'] for u in c['unit_ids']}
        unit_edges = {(c, u['unit_id']) for u in judgments['unit_judgments'] for c in u['claim_ids']}
        checks.append({'cell': c['id'], 'claims': len(claims), 'units': len(units), 'issues': issues,
                       'reciprocal_links': claim_edges == unit_edges, 'request_and_replay_equal': True})
save('verification.json', {'provider_calls': 0, 'checks': checks,
    'scope': 'selected-window diagnostic only', 'checker_correction': 'VERIFICATION-NOTE.md'})
print('Verified all nine actual requests, complete judgments and replayed observations')
