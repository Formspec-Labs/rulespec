"""Pinned native CFR navigation is not legal edition or extraction-quality proof.

Constructed identity/ambiguity controls supplement two exact publisher XML
components embedded below so the suite needs no sibling checkout or corpus.
"""
from copy import deepcopy

import pytest

from rulespec_extrapolator import uslm
from rulespec_extrapolator.discovery import export_discovery
from rulespec_extrapolator.documents import load_document, prepare_document
from rulespec_extrapolator.references import scan_references


def xml(body='<P>Business district definition.</P>', *, title='49', part='390',
        section='390.5', edition='2026-08-19', extra=''):
    return (f'<ECFR {extra}><DIV1 N="{title}" TYPE="TITLE" DATE="{edition}">'
            f'<HEAD>Title {title}</HEAD><DIV5 N="{part}" TYPE="PART">'
            f'<DIV8 N="{section}" TYPE="SECTION"><HEAD>§ {section} Definitions.</HEAD>'
            f'{body}</DIV8></DIV5></DIV1></ECFR>')


def source(**kwargs):
    return uslm.prepare_xml(xml(**kwargs), title='Dated publisher XML')


def scan(text, *sources):
    return scan_references(prepare_document(text), reference_sources=sources)


def test_same_section_number_in_two_titles_never_cross_resolves():
    a, b = source(), source(title='40', body='<P>Different title meaning.</P>')
    result = scan('49 CFR 390.5. 40 CFR 390.5.', a, b)
    rows = result['candidates']
    assert len(rows) == 2
    assert all(r['resolution']['status'] == 'located' for r in rows)
    targets = [result['targets'][r['resolution']['target_ids'][0]] for r in rows]
    assert {t['value'] for t in targets} == {'49 CFR 390.5', '40 CFR 390.5'}
    assert targets[0]['source_id'] != targets[1]['source_id']
    assert all(r['resolution']['edition_match'] == 'not_established' for r in rows)


@pytest.mark.parametrize('other', [{'edition':'2025-01-01'}, {'extra':'id="different-xml-only"'}])
def test_distinct_pins_remain_ambiguous_even_when_readable_text_matches(other):
    a, b = source(), source(**other)
    assert a['text'] == b['text']
    result = scan('49 CFR 390.5', a, b)
    row, = result['candidates']
    assert row['resolution']['status'] == 'ambiguous'
    assert len(row['resolution']['target_ids']) == 2
    assert len(result['reference_sources']) == 2
    assert len({t['source_id'] for t in result['targets'].values()}) == 2


def test_repeated_input_source_deduplicates_without_merging_citation_occurrences():
    external = source()
    result = scan('49 CFR 390.5. Again 49 CFR 390.5.', external, external)
    a, b = result['candidates']
    assert a['id'] != b['id']
    assert a['resolution'] == b['resolution']
    assert len(result['targets']) == len(result['reference_sources']) == 1


def test_duplicate_native_section_identifiers_do_not_choose_first():
    section = '<DIV8 N="390.5" TYPE="SECTION"><P>Other body.</P></DIV8>'
    external = uslm.prepare_xml(xml().replace('</DIV5>', section + '</DIV5>'))
    result = scan('49 CFR 390.5', external)
    assert result['candidates'][0]['resolution']['status'] == 'ambiguous'
    assert len(result['targets']) == 2


@pytest.mark.parametrize('citation', [
    '49 CFR 390.5(a)', '49 CFR 390.5 note', '49 CFR 390.5 et seq.',
    '49 CFR 390.5-390.6', '49 CFR part 390', 'Appendix A to 49 CFR part 390',
])
def test_pinpoints_qualifiers_ranges_and_appendices_do_not_fall_back(citation):
    result = scan(citation, source())
    assert not result['targets']
    assert all(not r.get('resolution', {}).get('target_ids')
               for r in result['candidates'] + result['rejected'])


def test_section_suffix_is_not_erased():
    result = scan('49 CFR 390.5T. 49 CFR 390.5.', source())
    rows = result['candidates']
    assert len(rows) == 2
    assert rows[0]['resolution']['status'] == 'not_in_selected_sources'
    assert not rows[0]['resolution']['target_ids']
    assert rows[1]['resolution']['status'] == 'located'


def test_native_section_without_title_is_readable_but_not_external_lookup():
    external = uslm.prepare_xml('<DIV8 N="390.5" TYPE="SECTION"><P>Body.</P></DIV8>')
    assert 'Body.' in external['text']
    with pytest.raises(ValueError, match='[Tt]itle'):
        scan('49 CFR 390.5', external)


def test_native_part_and_section_mismatch_refuses():
    with pytest.raises(ValueError):
        scan('49 CFR 390.5', source(part='382'))


@pytest.mark.parametrize('mutation', ['xml', 'text', 'source_map', 'preparation'])
def test_saved_transformation_mutations_are_refused(mutation):
    external = source()
    if mutation == 'xml':
        external['ecfr_source']['xml'] += ' '
    elif mutation == 'text':
        external['text'] += 'changed'
    elif mutation == 'source_map':
        next(p for p in external['source_map'] if p['kind'] == 'source')['source_start'] += 1
    else:
        external['ecfr_source']['preparation'] = 'unknown-reader'
    with pytest.raises(ValueError):
        uslm.read_xml(external)
    with pytest.raises(ValueError):
        scan('49 CFR 390.5', external)


def test_loader_detects_both_native_xml_formats(tmp_path):
    cfr = tmp_path/'cfr.xml'
    usc = tmp_path/'usc.xml'
    cfr.write_text(xml())
    usc.write_text('<uscDoc xmlns="http://xml.house.gov/schemas/uslm/1.0">'
                   '<section identifier="/us/usc/t5/s553"><content>USC body.</content>'
                   '</section></uscDoc>')
    a, b = load_document(cfr), load_document(usc)
    assert 'ecfr_source' in a and 'uslm_source' not in a
    assert 'uslm_source' in b and 'ecfr_source' not in b
    result = scan('49 CFR 390.5. 5 USC 553.', a, b)
    assert len(result['targets']) == len(result['reference_sources']) == 2
    assert {t['value'] for t in result['targets'].values()} == {'49 CFR 390.5', '/us/usc/t5/s553'}
    assert all(r['resolution']['status'] == 'located' for r in result['candidates'])


def test_discovery_keeps_external_evidence_owned_by_its_source():
    external = source()
    before = deepcopy(external)
    document = prepare_document('49 CFR 390.5')
    result = export_discovery({'document':document, 'accepted':[]}, reference_sources=[external])
    reference_scan = result['reference_scan']
    target, = reference_scan['targets'].values()
    src = reference_scan['reference_sources'][target['source_id']]
    record = src['records'][target['record_id']]
    assert target['evidence_refs'] and 'evidence' not in target
    for ref in target['evidence_refs']:
        assert ref['id'] not in result['evidence']
        position = src['evidence'][ref['id']]
        own_text = external['text'][position['start']:position['end']]
        assert record['text'][position['start']-record['start']:position['end']-record['start']] == own_text
        assert not any(p['kind']=='inserted' and p['start']<position['end'] and position['start']<p['end']
                       for p in external['source_map'])
    assert result['records'][0]['text'] == document['text']
    assert result['accounting']['semantic_completeness'] == 'not_established'
    assert external == before


# Exact TABLE/EFFDNOT components from the already pinned publisher captures.
# Surrounding TITLE/PART scaffolding in these tests is constructed. This checks
# transport of native layout/notes, not the source's operative legal edition.
# Source: title-40.xml (2026-08-20), section82.158; title-49.xml (2026-08-19),390.5.
# Parent section byte pins remain in the dated reference-body experiment.

# Original section SHA-256: d21962f557bcba7f415951a26cc29369bea88d76a42121494fb2bf2b0712210d
PUBLISHER_TABLE = """<TABLE border="1" cellpadding="1" cellspacing="1" class="gpo_table" frame="void" width="100%">
<CAPTION><P class="title">Table 2—Levels of Evacuation Which Must Be Achieved by Recovery and/or Recycling Equipment</P><P class="headnote">[Except for small appliances, MVACs, and MVAC-like appliances.]
</P></CAPTION>
<THEAD>
<TR>
<TH rowspan="2" class="center border-top-single border-bottom-single border-right-single">Type of appliance with which recovery and/or recycling machine is intended to be used</TH>
<TH colspan="2" class="center border-top-single border-bottom-single">Inches of Hg vacuum<br/>(relative to standard atmospheric pressure of 29.9 inches Hg)</TH>
</TR>
<TR>
<TH class="center border-bottom-single border-right-single">Manufactured or<br/>imported before<br/>November 15, 1993</TH>
<TH class="center border-bottom-single">Manufactured or<br/>imported on or after<br/>November 15, 1993</TH>
</TR>
</THEAD>
<TBODY>
<TR>
<TD class="left border-right-single">HCFC-22 appliances, or isolated component of such appliances, with a full charge of less than 200 pounds of refrigerant</TD>
<TD class="left border-right-single">0</TD>
<TD class="left">0.</TD>
</TR>
<TR>
<TD class="left border-right-single">HCFC-22 appliances, or isolated component of such appliances, with a full charge of 200 pounds or more of refrigerant</TD>
<TD class="left border-right-single">4</TD>
<TD class="left">10.</TD>
</TR>
<TR>
<TD class="left border-right-single">Very high-pressure appliances</TD>
<TD class="left border-right-single">0</TD>
<TD class="left">0.</TD>
</TR>
<TR>
<TD class="left border-right-single">Other high-pressure appliances, or isolated component of such appliances, with a full charge of less than 200 pounds of refrigerant</TD>
<TD class="left border-right-single">4</TD>
<TD class="left">10.</TD>
</TR>
<TR>
<TD class="left border-right-single">Other high-pressure appliances, or isolated component of such appliances, with a full charge of 200 pounds or more of refrigerant</TD>
<TD class="left border-right-single">4</TD>
<TD class="left">15.</TD>
</TR>
<TR>
<TD class="left border-right-single">Medium-pressure appliances, or isolated component of such appliances, with a full charge of less than 200 pounds of refrigerant</TD>
<TD class="left border-right-single">4</TD>
<TD class="left">10.</TD>
</TR>
<TR>
<TD class="left border-right-single">Medium-pressure appliances, or isolated component of such appliances, with a full charge of 200 pounds or more of refrigerant</TD>
<TD class="left border-right-single">4</TD>
<TD class="left">15.</TD>
</TR>
<TR>
<TD class="left border-bottom-single border-right-single">Low-pressure appliances</TD>
<TD class="left border-bottom-single border-right-single">25 mm Hg absolute</TD>
<TD class="left border-bottom-single">25 mm Hg absolute.</TD>
</TR>
</TBODY>
</TABLE>"""

# Original section SHA-256: d9a673e09b64db6707ae5e7e4e30368517fe12a8639bd58503b1e58c25209026
PUBLISHER_SUSPENSION = """<EFFDNOT>
<HED>Effective Date Note:</HED><PSPACE>At 82 FR 5311, Jan. 17, 2017, § 390.5 was suspended, effective Jan. 14, 2017. At 84 FR 40293, Aug. 14, 2019, the suspension was lifted and amendments were made to § 390.5. In that same document, § 390.5 was again suspended indefinitely. At 86 FR 35642, July 7, 2021, the suspension was lifted and amendments were made to § 390.5. In that same document, § 390.5 was again suspended indefinitely. 

At 86 FR 57072, Oct. 14, 2021, the suspension was lifted and amendments were made to § 390.5. In that same document, § 390.5 was again suspended indefinitely. At 87 FR 13208, Mar. 9, 2022, the suspension was lifted and an amendment was made to § 390.5. In that same document, § 390.5 was again suspended indefinitely. At 88 FR 80183, Nov. 17, 2023, the suspension was lifted, § 390.5 was amended, and the section was again suspended indefinitely, effective Nov. 17, 2023. At 88 FR 70907, Oct. 13, 2023, the suspension was lifted, § 390.5 was amended, and the section was again suspended indefinitely, effective Dec. 12, 2023. At 91 FR 45661, July 21, 2026, the suspension was lifted, § 390.5 was amended, and the section was again suspended indefinitely, effective July 21, 2026.</PSPACE></EFFDNOT>"""


def test_actual_table_layout_and_native_attributes_survive_application_preparation():
    external = source(title='40', part='82', section='82.158', body=PUBLISHER_TABLE)
    prepared = uslm.read_xml(external)
    cells = [n for n in prepared['nodes'].values() if n['tag'] in {'TD', 'TH'}]
    assert len(cells) == 28
    assert any(n['attributes'].get('colspan') == '2' for n in cells)
    assert any(n['attributes'].get('rowspan') == '2' for n in cells)
    assert '\t' in external['text']
    assert 'Manufactured or\n\nimported before\n\nNovember 15, 1993' in external['text']
    assert 'Manufactured orimported' not in external['text']
    assert ''.join(external['text'][p['start']:p['end']]
                   for p in external['source_map'] if p['kind'] == 'source') == prepared['source_text']
    result = scan('40 CFR 82.158', external)
    target, = result['targets'].values()
    record = result['reference_sources'][target['source_id']]['records'][target['record_id']]
    assert '25 mm Hg absolute' in record['text']
    assert record['text'].count('HCFC-22 appliances') == 2


def test_actual_suspension_note_remains_context_without_establishing_edition():
    external = source(body='<P>Business district definition.</P>' + PUBLISHER_SUSPENSION)
    result = scan('49 CFR 390.5', external)
    row, = result['candidates']
    target, = result['targets'].values()
    record = result['reference_sources'][target['source_id']]['records'][target['record_id']]
    assert row['resolution']['status'] == 'located'
    assert row['resolution']['edition_match'] == 'not_established'
    assert 'Effective Date Note:' in record['text']
    assert 'again suspended indefinitely, effective July 21, 2026' in record['text']
    assert result['semantic_completeness'] == 'not_established'
    assert any(n['tag']=='EFFDNOT' for n in uslm.read_xml(external)['nodes'].values())


def test_unsupported_native_section_range_preserves_source_issue_and_exact_sibling():
    # Native range shape observed in title49. Keep it as a source reading;
    # neither its first endpoint nor its last endpoint denotes this whole node.
    external = uslm.prepare_xml(
        '<ECFR><DIV1 N="49" TYPE="TITLE"><DIV5 N="11" TYPE="PART">'
        '<DIV8 N="11.100" TYPE="SECTION"><HEAD>§ 11.100</HEAD><P>Exact body.</P></DIV8>'
        '<DIV8 N="11.105-11.106" TYPE="SECTION">'
        '<HEAD>§§ 11.105-11.106 [Reserved]</HEAD></DIV8>'
        '</DIV5></DIV1></ECFR>')
    result = scan('49 CFR 11.100. 49 CFR 11.105. 49 CFR 11.106. 49 CFR 11.105-11.106.', external)
    target, = result['targets'].values()
    assert target['value'] == '49 CFR 11.100'
    located = [r for r in result['candidates'] if r.get('resolution', {}).get('target_ids')]
    assert len(located) == 1
    assert located[0]['resolution']['status'] == 'located'
    src, = result['reference_sources'].values()
    issue, = [i for i in src['issues'] if i['code'] == 'native_section_scope_not_supported']
    assert issue['value'] == '49 CFR 11.105-11.106'
    assert issue['xml_evidence_refs']
    nodes = uslm.read_xml(external)['nodes']
    for identity in issue['xml_evidence_refs']:
        fragment = src['xml_fragments'][identity]
        selector, = fragment['oa:hasSelector']
        node = nodes[selector['rdf:value']]
        assert node['attributes']['N'] == '11.105-11.106'
        assert node['attributes']['TYPE'] == 'SECTION'
    assert not any(t['value'] in {'49 CFR 11.105', '49 CFR 11.106', '49 CFR 11.105-11.106'}
                   for t in result['targets'].values())
