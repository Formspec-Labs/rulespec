"""Counterexamples for formatting, XML identity and original-source evidence."""
import json
from pathlib import Path

from lxml import etree
import pytest
from rulespec_extrapolator.core import _evidence
from prepare import prepare

HERE = Path(__file__).resolve().parent
NS = 'http://xml.house.gov/schemas/uslm/1.0'


def check(body):
    xml = f'<uscDoc xmlns="{NS}">{body}</uscDoc>'.encode()
    result = prepare(xml)
    verify_xml(xml, result)
    return result


def verify_xml(xml, result):
    root = etree.fromstring(xml)
    doc, source = result['document'], result['source_text']
    assert source == ''.join(root.itertext())
    source_parts = [p for p in doc['source_map'] if p['kind'] == 'source']
    assert ''.join(doc['text'][p['start']:p['end']] for p in source_parts) == source
    for path, node in result['nodes'].items():
        selected = root.xpath(path)
        assert len(selected) == 1
        assert ''.join(selected[0].itertext()) == source[node['source_start']:node['source_end']]
        if 'start' in node:
            included = [p for p in source_parts if p['start'] < node['end'] and node['start'] < p['end']]
            assert ''.join(doc['text'][max(p['start'],node['start']):min(p['end'],node['end'])] for p in included) == ''.join(selected[0].itertext())


def test_inline_words_punctuation_entities_unicode_and_line_endings():
    result = check('<p>non<inline>discretionary</inline>, café &amp; <b>🦉</b>—x.\r\nNext.</p>')
    assert result['document']['text'] == 'nondiscretionary, café & 🦉—x.\nNext.'
    assert all(p['kind']=='source' for p in result['document']['source_map'])


def test_heading_boundary_preserves_inline_body_and_refuses_inserted_quote():
    result = check('<subsection><num>(b)</num><heading> Functions</heading><chapeau>The Secretary shall—</chapeau></subsection>')
    doc = result['document']
    assert doc['text'] == '(b) Functions The Secretary shall—'
    assert _evidence(doc, 'Functions The Secretary', 'summary') is None
    assert _evidence(doc, 'The Secretary shall—', 'summary') is not None


def test_existing_heading_space_is_not_duplicated():
    result = check('<paragraph><heading>Rule </heading><content>applies.</content></paragraph>')
    assert result['document']['text'] == 'Rule applies.'


def test_repeated_mentions_and_duplicate_identifiers_stay_distinct():
    result = check('<p><ref href="/us/usc/t5/s1">Same</ref></p><p><ref href="/us/usc/t5/s1">Same</ref></p><section identifier="/us/usc/t5/s1">One</section><section identifier="/us/usc/t5/s1">Two</section>')
    refs = [n for n in result['nodes'].values() if n['tag']=='ref']
    assert len(refs) == 2 and refs[0]['start'] != refs[1]['start']
    assert len([n for n in result['nodes'].values() if n.get('identifier')=='/us/usc/t5/s1']) == 2


def test_empty_reference_retains_xml_location():
    result = check('<p>Before<ref href="/us/usc/t5/s1"/>after.</p>')
    refs = [n for n in result['nodes'].values() if n['tag']=='ref']
    assert len(refs)==1 and refs[0]['source_start']==refs[0]['source_end']
    assert 'start' not in refs[0]
    assert result['document']['text']=='Beforeafter.'


def test_table_columns_and_multiple_paragraphs_inside_a_cell():
    result = check('<table><tr><th><p>A</p></th><th><p>B</p></th></tr><tr><td><p>One</p><p>continued</p></td><td><p>Two</p></td></tr></table>')
    assert result['document']['text']=='A\tB\n\nOne\n\ncontinued\tTwo'


def test_footnote_text_remains_separate_from_body():
    result = check('<p>Rule<ref class="footnoteRef">1</ref><note type="footnote"><num>1</num> So in original.</note>Next.</p>')
    assert result['document']['text']=='Rule1\n\n1 So in original.\n\nNext.'


def test_foreign_root_is_refused():
    with pytest.raises(ValueError, match='USLM uscDoc'):
        prepare(b'<html><p>Other format</p></html>')


@pytest.mark.parametrize('case', json.loads((HERE/'v2/prepared.json').read_text()))
def test_saved_sources_against_independent_xpath_engine(case):
    verify_xml(Path(case['capture']).read_bytes(), case)
