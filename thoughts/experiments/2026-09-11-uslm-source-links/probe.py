"""Direct-import consumer probe using existing Rulespec evidence helpers.

The decoded text is a diagnostic coordinate space, not an adopted XML-to-readable-
document formatter. Keep publisher XPath evidence beside those text positions.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from refspec.registry import uslm
from rulespec_extrapolator.core import NS, _evidence, digest
from rulespec_extrapolator.documents import prepare_document

HERE = Path(__file__).resolve().parent


def locate(xml, title):
    root = ET.fromstring(xml)
    text_parts, nodes, identifiers = [], {}, defaultdict(list)
    cursor = 0

    def append(text):
        nonlocal cursor
        if text:
            text_parts.append(text)
            cursor += len(text)

    def visit(node, path):
        start = cursor
        append(node.text)
        for index, child in enumerate(node, 1):
            visit(child, path + f'/*[{index}]')
            append(child.tail)
        location = {'start':start, 'end':cursor, 'sourceXPath':path}
        nodes[path] = location
        if node.get('identifier'):
            identifiers[node.get('identifier')].append(location)

    visit(root, '/*[1]')
    text = ''.join(text_parts)
    assert text == ''.join(root.itertext())
    document = prepare_document(text, title=f'USLM title {title} source selection')
    xml_sha = digest(xml)
    source_id = NS+'xml:'+xml_sha

    def xml_fragment(location):
        return {'@id':NS+'xml-fragment:'+digest([source_id,location['sourceXPath']]),
            '@type':'rkaf:SourceFragment','oa:hasSource':source_id,
            'oa:hasSelector':[{'@type':'oa:XPathSelector','rdf:value':location['sourceXPath']}],
            'rkaf:selectorKind':['oa:XPathSelector'],
            'rkaf:sourceArtifactDigest':'sha256:'+xml_sha,
            'rkaf:fragmentContentDigest':'sha256:'+digest(text[location['start']:location['end']])}

    def support(location, role):
        start,end=location['start'],location['end']
        quote=text[start:end]
        evidence=_evidence(document,quote,role,start,end) if quote else None
        if quote:
            assert evidence is not None
        return {'xml_fragment':xml_fragment(location), 'text_evidence':evidence,
                'text_status':'located' if quote else 'no_visible_text'}

    skipped=Counter()
    occurrences=[]
    for row in uslm.iter_edges(xml,title,skipped,include_source_path=True):
        location=nodes[row['sourceXPath']]
        targets=identifiers.get(row['href'],[])
        occurrences.append({'reading':row,'source':support(location,'reference'),
            'target':{'status':'located' if len(targets)==1 else 'ambiguous' if targets else 'not_in_selected_source',
                      'sources':[support(target,'reference_target') for target in targets]}})
    return {'document':document,'xml_source':{'id':source_id,'sha256':xml_sha},
            'text_method':'xml-itertext/1; exact decoded text nodes and tails, no formatting or normalization',
            'occurrences':occurrences,'skipped':dict(skipped)}


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    cases=json.loads((HERE/'cases.json').read_text())
    results=[]
    for case in cases:
        result=locate((HERE/case['capture']).read_bytes(),case['title'])
        assert [{k:v for k,v in row['reading'].items() if k!='sourceXPath'}
                for row in result['occurrences']] == case['baseline']
        assert result['skipped']==case['skipped']
        results.append({'id':case['id'],'capture':case['capture'],**result})
        print(case['id'],len(result['occurrences']),
              dict(Counter(x['reading']['context'] for x in result['occurrences'])),
              dict(Counter(x['target']['status'] for x in result['occurrences'])))
    with args.output.open('x') as f:
        json.dump(results,f,indent=2,ensure_ascii=False);f.write('\n')
