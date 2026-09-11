"""Independently evaluate generated selectors with lxml's XPath engine."""
import hashlib
import json
from pathlib import Path
from lxml import etree

HERE=Path(__file__).resolve().parent
sources=json.loads((HERE/'source-probe.json').read_text())
cases=[(x['id'],(HERE/x['capture']).read_bytes(),x) for x in sources]
cases += [(x['id'],x['xml'].encode(),x['result'])
          for x in json.loads((HERE/'control-results.json').read_text()) if x['result']]
checked=0
for name,xml,result in cases:
    root=etree.fromstring(xml,parser=etree.XMLParser(resolve_entities=False,no_network=True))
    text=result['document']['text']
    for row in result['occurrences']:
        selected=root.xpath(row['reading']['sourceXPath'])
        assert len(selected)==1 and selected[0].get('href')==row['reading']['href'],name
        supports=[row['source']]+row['target']['sources']
        for support in supports:
            fragment=support['xml_fragment']
            matches=root.xpath(fragment['oa:hasSelector'][0]['rdf:value'])
            assert len(matches)==1,name
            decoded=''.join(matches[0].itertext())
            assert fragment['rkaf:fragmentContentDigest']=='sha256:'+hashlib.sha256(decoded.encode()).hexdigest(),name
            evidence=support['text_evidence']
            if evidence:
                assert text[evidence['start']:evidence['end']]==decoded==evidence['quote'],name
            else:
                assert decoded=='' and support['text_status']=='no_visible_text',name
            checked+=1
report={'engine':'lxml XPath','lxml_version':list(etree.LXML_VERSION),'libxml_version':list(etree.LIBXML_VERSION),
        'cases_checked':len(cases),'source_and_target_fragments_checked':checked,'all_passed':True}
with (HERE/'xpath-verification.json').open('x') as f:
    json.dump(report,f,indent=2);f.write('\n')
print(json.dumps(report))
