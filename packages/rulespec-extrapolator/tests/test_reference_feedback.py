"""Reference observations preserve the challenged version without editing claims."""
from copy import deepcopy
from functools import partial
import json
from pathlib import Path
import sys

import pytest

from rulespec_extrapolator import cli, uslm
from rulespec_extrapolator.core import canonical, compile_candidates, digest, validate_graph
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import load_document, prepare_document
from rulespec_extrapolator.reference_feedback import reference_observation as make_observation
from rulespec_extrapolator.references import scan_references
from rulespec_extrapolator.review_store import ReviewStore, RevisionConflict

FIXTURES = Path(__file__).with_name('fixtures')
reference_observation = partial(make_observation, message='Fixture observation: check this reading.')


def make_run(tmp_path, document, candidates=()):
    run = tmp_path / 'run'
    run.mkdir()
    book = compile_candidates(document, list(candidates), {})
    for name, value in {'document.json': document, 'run.json': {}, 'rulebook.json': book}.items():
        (run / name).write_text(canonical(value))
    return run


def action(observation, revision=0, rationale='Constructed feedback; inspect this reading.'):
    return {'action': 'observe', 'expected_revision': revision, 'actor': 'Fixture reviewer',
            'actor_kind': 'humanUser', 'targets': [], 'rationale': rationale,
            'observations': [observation]}


def test_actual_xml_repeats_retain_distinct_source_and_challenged_versions(tmp_path):
    doc = load_document(FIXTURES / 'cfr-reverse-title.xml')
    scan = scan_references(doc)
    first = reference_observation(doc, scan, 'candidates', 0)
    last = reference_observation(doc, scan, 'candidates', 2)
    assert first['reference']['value'] == last['reference']['value']
    assert first['reference']['id'] != last['reference']['id']
    assert first['reference']['evidence'] != last['reference']['evidence']
    old_id_only = {'reference_id': first['reference']['id']}
    changed = deepcopy(scan)  # Deliberate reader-regression control; not new source truth.
    changed['candidates'][0]['reading']['cfr_part'] = '1911'
    later = reference_observation(doc, changed, 'candidates', 0)
    assert old_id_only == {'reference_id': later['reference']['id']}
    assert first['scan_sha256'] != later['scan_sha256']
    assert first['reference']['reading']['cfr_part'] == '1910'
    store = ReviewStore(make_run(tmp_path, doc))
    for i, observation in enumerate((first, last, later)):
        store.apply(action(observation, i))
    saved = ReviewStore(store.run_dir).snapshot()
    assert [e['observations'][0] for e in saved['history']] == [first, last, later]
    assert [i['reference'] for i in export_discovery(saved)['enrichment_issues']] == [
        first['reference'], last['reference'], later['reference']]
    assert saved['attestations'] == [] and saved['accepted'] == []
    assert validate_graph(saved['graph'])['shacl_conforms']
    # The helper returns a snapshot, not references into a caller's mutable scan.
    scan['candidates'][0]['reading']['cfr_part'] = 'changed again'
    assert first['reference']['reading']['cfr_part'] == '1910'


def test_reported_refusal_preserves_native_reason_and_exact_evidence(tmp_path):
    # Real title-21 paragraph selected before the preceding connector comparison.
    text = ('(i) Authorized under their registration under 21 CFR 1301.13(e)(1)(iv) '
            'to prescribe the basic class of controlled substance specified on the prescription; or\n')
    doc = prepare_document(text)
    scan = scan_references(doc)
    refused, = scan['rejected']
    assert refused['code'] == 'cfr_range_end_unread'
    observation = reference_observation(doc, scan, 'rejected', 0)
    store = ReviewStore(make_run(tmp_path, doc))
    store.apply(action(observation))
    saved = export_discovery(ReviewStore(store.run_dir).snapshot(), include_references=True)
    assert saved['enrichment_issues'][0]['reference'] == refused
    assert observation['context']['parsers'] == scan['parsers']
    assert 'id' not in refused  # No new ID system is necessary for a captured rejected reading.
    assert saved['reference_scan']['rejected'][0]['code'] == refused['code']


def test_feedback_cli_preserves_claim_approval_and_rejects_stale_revision(tmp_path, capsys):
    text = 'Visitors must retain records. See 40 CFR 82.155.'
    doc = prepare_document(text)
    statement = 'Visitors must retain records.'
    run = make_run(tmp_path, doc, [{'kind': 'requirement', 'quote': statement, 'summary': statement,
                                   'actor': 'Visitors', 'actor_quote': 'Visitors',
                                   'modality': 'must', 'modality_quote': 'must'}])
    store = ReviewStore(run)
    before = store.snapshot()
    approval = action({}, 0)
    approval.update(action='approve', targets=[before['accepted'][0]['id']])
    approval.pop('observations')
    before = store.apply(approval)
    scan_path = tmp_path / 'scan.json'
    cli.main(['references', str(run), '--output', str(scan_path)])
    capsys.readouterr()
    args = ['reference-feedback', str(run), '--scan', str(scan_path), '--candidate', '0',
            '--expected-revision', '1', '--actor', 'Fixture reviewer', '--rationale', 'Check this reference.']
    assert cli.main(args) == 0
    response = json.loads(capsys.readouterr().out)
    assert response['revision'] == 2 and response['event']['actor_kind'] == 'humanUser'
    after = ReviewStore(run).snapshot()
    assert after['accepted'] == before['accepted'] and after['attestations'] == before['attestations']
    assert after['history'][:1] == before['history']
    with pytest.raises(RevisionConflict):
        cli.main(args)
    assert ReviewStore(run).snapshot() == after
    output = tmp_path / 'discovery.json'
    cli.main(['discovery-export', str(run), '--references', '--output', str(output)])
    saved = json.loads(output.read_text())
    assert saved['enrichment_issues'][0]['code'] == 'reference_feedback'
    assert saved['enrichment_issues'][0]['message'] == 'Check this reference.'
    assert saved['statements'][0]['review_status'] == 'approved'


@pytest.mark.parametrize('mutation', ['document', 'quote', 'fragment', 'position', 'reader', 'negative', 'bool', 'outside'])
def test_wrong_source_evidence_or_selection_is_refused(mutation):
    doc = prepare_document('40 CFR 82.155.')
    scan = scan_references(doc)
    index = 0
    if mutation == 'document': scan['document']['sha256'] = 'wrong'
    elif mutation == 'quote': scan['candidates'][0]['evidence'][0]['quote'] = '40 CFR 82.156'
    elif mutation == 'fragment': scan['candidates'][0]['evidence'][0]['fragment_id'] = 'wrong'
    elif mutation == 'position': scan['candidates'][0]['evidence'][0]['start'] += 1
    elif mutation == 'reader': scan.pop('parsers')
    elif mutation == 'negative': index = -1
    elif mutation == 'bool': index = True
    elif mutation == 'outside': index = 1
    with pytest.raises(ValueError):
        reference_observation(doc, scan, 'candidates', index)


def test_ungrounded_refusal_is_retained_without_inventing_source_evidence():
    doc = prepare_document('Public Law 119-20')
    doc['source_map'] = [{'kind': 'inserted', 'start': 0, 'end': len(doc['text']), 'text': doc['text']}]
    scan = scan_references(doc)
    observation = reference_observation(doc, scan, 'rejected', 0)
    row = observation['reference']
    assert row['code'] == 'reference_not_grounded_in_source'
    assert (row['start'], row['end']) == (0, len(doc['text']))
    assert 'evidence' not in row and 'id' not in row


def test_target_context_keeps_editions_and_omits_unrelated_bodies():
    external = load_document(FIXTURES / 'uslm/reference-title5-s553.xml')
    doc = prepare_document('5 USC 553(b)(B). Also 5 USC 553(c).')
    scan = scan_references(doc, reference_sources=[external])
    assert len(scan['targets']) == 2
    observation = reference_observation(doc, scan, 'candidates', 0)
    context = observation['context']
    assert set(context['targets']) == set(scan['candidates'][0]['resolution']['target_ids'])
    target, = context['targets'].values()
    source = context['reference_sources'][target['source_id']]
    assert 'Except when notice or hearing is required by statute' in source['records'][target['record_id']]['text']
    assert any(p['value'] == 'Online@119-102' for p in source['publication'])
    assert target['evidence'][0]['quote'] in external['text']
    assert observation['reference']['resolution']['edition_match'] == 'not_established'
    bad = deepcopy(scan)
    bad['targets'].clear()
    with pytest.raises(ValueError, match='missing linked'):
        reference_observation(doc, bad, 'candidates', 0)


def test_publisher_link_and_disagreeing_text_reading_share_original_xml_context():
    doc = uslm.prepare_xml('<uscDoc xmlns="http://xml.house.gov/schemas/uslm/1.0">'
                          '<section><p><ref href="/us/usc/t5/s999">5 USC 553(b)(B)</ref></p></section></uscDoc>')
    scan = scan_references(doc)
    observation = reference_observation(doc, scan, 'candidates', 0)
    assert observation['reference']['value'] == '/us/usc/t5/s999'
    assert observation['reference']['text_readings'][0]['value'] == '5 USC 553(b)(B)'
    assert observation['context']['publisher_source'] == scan['publisher_source']
    assert set(observation['context']['xml_fragments']) == set(observation['reference']['xml_evidence_refs'])


def test_ambiguous_edition_feedback_keeps_both_sources():
    original = load_document(FIXTURES / 'uslm/reference-title5-s553.xml')
    changed = uslm.prepare_xml(original['uslm_source']['xml'].replace('Online@119-102', 'Constructed alternate edition'))
    doc = prepare_document('5 USC 553(b)(B).')
    scan = scan_references(doc, reference_sources=[original, changed])
    observation = reference_observation(doc, scan, 'candidates', 0)
    assert observation['reference']['resolution']['status'] == 'ambiguous'
    assert len(observation['context']['targets']) == len(observation['context']['reference_sources']) == 2
    assert {s['document']['sha256'] for s in observation['context']['reference_sources'].values()} == {
        original['sha256'], changed['sha256']}


def test_unlocated_target_feedback_keeps_native_source_issues(tmp_path):
    # Constructed source using the native combined-section form observed in title 49.
    external = uslm.prepare_xml(
        '<ECFR><DIV1 N="49" TYPE="TITLE"><DIV5 N="11" TYPE="PART">'
        '<DIV8 N="11.105-11.106" TYPE="SECTION">'
        '<HEAD>§§ 11.105-11.106 [Reserved]</HEAD></DIV8>'
        '</DIV5></DIV1></ECFR>')
    doc = prepare_document('49 CFR 11.105.')
    scan = scan_references(doc, reference_sources=[external])
    observation = reference_observation(doc, scan, 'candidates', 0)
    source, = scan['reference_sources'].values()
    retained, = observation['context']['reference_sources'].values()
    assert observation['reference']['resolution']['status'] == 'not_in_selected_sources'
    assert not scan['targets'] and 'records' not in retained
    assert retained['issues'] == source['issues']
    issue, = retained['issues']
    assert issue['code'] == 'native_section_scope_not_supported'
    assert issue['value'] == '49 CFR 11.105-11.106'
    for identity in issue['xml_evidence_refs']:
        assert retained['xml_fragments'][identity] == source['xml_fragments'][identity]
    store = ReviewStore(make_run(tmp_path, doc))
    store.apply(action(observation))
    saved = export_discovery(ReviewStore(store.run_dir).snapshot())
    assert saved['enrichment_issues'][0]['context'] == observation['context']


def test_reload_and_observation_capture_need_no_optional_readers(tmp_path, monkeypatch):
    doc = prepare_document('40 CFR 82.155.')
    scan = scan_references(doc)
    run = make_run(tmp_path, doc)
    monkeypatch.setitem(sys.modules, 'spicysearch', None)
    monkeypatch.setitem(sys.modules, 'refspec', None)
    observation = reference_observation(doc, scan, 'candidates', 0)
    ReviewStore(run).apply(action(observation))
    saved = ReviewStore(run).snapshot()
    assert saved['history'][0]['observations'][0]['scan_sha256'] == digest(scan)
    assert export_discovery(saved)['enrichment_issues'][0]['reference'] == scan['candidates'][0]
