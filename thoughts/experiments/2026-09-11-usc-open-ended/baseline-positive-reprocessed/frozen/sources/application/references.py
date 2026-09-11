"""Optional reference recognition and named-act identity lookup over pinned data."""
from bisect import bisect_left, bisect_right
from dataclasses import asdict
from importlib.metadata import version
from pathlib import Path

from .core import NS, _evidence, digest, sparse
from .documents import source_passages, validate_document

SPICYSEARCH_KINDS = frozenset({"public_law", "statutes_at_large", "executive_order", "docket", "rin"})


def scan_references(document, *, act_index=None, source_credit_index=None):
    """Scan pinned source with existing readers, preserving occurrences and evidence."""
    validate_document(document)
    if source_credit_index is not None and act_index is None:
        raise ValueError("A source-credit index requires an act index")
    try:
        from spicysearch import identifiers
        from refspec.registry import citation_grammar as grammar
        from refspec.registry import iri_minting
    except ModuleNotFoundError as error:
        raise RuntimeError("Reference scanning requires verified SpicySearch and RefSpec wheels; see the extractor README.") from error

    text = document['text']
    passages = source_passages(document)
    starts, ends = [p['start'] for p in passages], [p['end'] for p in passages]
    candidates, rejected = [], []
    parsers = [('spicysearch.identifiers.detect_identifiers', 'spicysearch', identifiers),
               ('refspec.registry.citation_grammar.find_cfr_citations', 'refspec', grammar),
               ('refspec.registry.iri_minting.mint_rin_iri', 'refspec', iri_minting)]
    indexes = {}
    def evidence(start, end, field):
        if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
            raise ValueError("Reference parser returned invalid source coordinates")
        return _evidence(document, text[start:end], field, start, end)

    def record(kind, value, start, end, *, reading=None, context=None, refusal=None):
        support = evidence(start, end, 'reference')
        row = {'kind': kind, 'value': value, 'start': start, 'end': end}
        if reading is not None:
            row['reading'] = reading
        if support is None:
            rejected.append({**row, 'code': 'reference_not_grounded_in_source'})
            return
        row['evidence'] = [support]
        if context is not None:
            context_evidence = evidence(*context, 'reference_context')
            if context_evidence is None:
                rejected.append({**row, 'context_span': list(context), 'code': 'reference_context_not_grounded_in_source'})
                return
            row['evidence'].append(context_evidence)
        if refusal:
            rejected.append({**row, 'code': refusal})
            return
        row.pop('start')
        row.pop('end')
        row.update(id=NS + 'reference:' + digest([support['fragment_id'], kind, value]),
                   record_ids=[p['id'] for p in passages[bisect_right(ends, start):bisect_left(starts, end)]])
        candidates.append(row)
        return row

    for match in identifiers.detect_identifiers(text):
        if match.kind in SPICYSEARCH_KINDS:
            refusal = ('rin_outside_supported_identifier_space'
                       if match.kind == 'rin' and iri_minting.mint_rin_iri(match.value) is None else None)
            record(str(match.kind), match.value, *match.span, refusal=refusal)
    for match in grammar.find_cfr_citations(text):
        if text[match.start:match.end] != match.text:
            raise ValueError("Reference parser quotation differs from the pinned source")
        reading = {**asdict(match.citation), 'pinpoint': list(match.pinpoint)}
        reading.update({key: getattr(match, key) for key in
                        ('subpart', 'subpart_end', 'appendix', 'qualifier_status')
                        if getattr(match, key) is not None})
        value = f'{match.citation.cfr_title} CFR'
        if match.citation.cfr_part is not None:
            value += ' ' + match.citation.cfr_part
        if match.citation.cfr_section is not None:
            value += '.' + match.citation.cfr_section
        value += ''.join(f'({label})' for label in match.pinpoint)
        if match.appendix is not None:
            value += ' appendix ' + match.appendix + ' to'
        if match.subpart is not None:
            value += ' subpart ' + match.subpart
        if match.subpart_end is not None:
            value += ' through ' + match.subpart_end
        context = None if match.context_start is None else (match.context_start, match.context_end)
        refusal = ('cfr_title_impossible' if not match.citation.title_is_possible else
                   'cfr_part_implausible' if match.citation.part_is_plausible is False else
                   'cfr_' + match.qualifier_status if match.qualifier_status else None)
        record('cfr', value, match.start, match.end, reading=reading, context=context, refusal=refusal)
    if act_index is not None:
        from refspec.registry import act_resolution as acts
        index = acts.ActIndex.from_artifact(Path(act_index))
        credits = None if source_credit_index is None else acts.SourceCreditIndex.from_artifact(Path(source_credit_index))
        for role, directory, files in [
            ('acts', act_index, ('receipt.json', 'usc-popular-names.parquet', 'usc-act-sections.parquet', 'quarantine.parquet')),
            ('source_credits', source_credit_index, ('receipt.json', 'usc-source-credits.parquet')),
        ]:
            if directory is not None:
                indexes[role] = {'directory': str(Path(directory).resolve()),
                                 'sha256': {name: digest((Path(directory) / name).read_bytes()) for name in files}}
        names = set(index.table3_key_by_name) | set(index.alias_by_name)
        for match in grammar.find_act_relative_occurrences(text, act_names=names):
            if text[match.start:match.end] != match.text:
                raise ValueError("Reference parser quotation differs from the pinned source")
            value = f'{match.citation.act_name} section {match.citation.section}' + ''.join(f'({p})' for p in match.pinpoint)
            row = record('act_relative', value, match.start, match.end,
                         reading={**asdict(match.citation), 'pinpoint': list(match.pinpoint)})
            if row is not None:
                resolution = asdict(acts.resolve_act_relative_citation(match.citation, index=index, source_credits=credits))
                resolution.pop('citation')  # Already retained as the native reading.
                for candidate in resolution.get('candidate_resolutions', ()):
                    candidate.pop('citation')  # Each candidate answers that same reading.
                row['resolution'] = sparse(resolution)
                if match.pinpoint:
                    row['resolution']['pinpoint_mapping'] = 'not_performed'
        parsers += [('refspec.registry.citation_grammar.find_act_relative_occurrences', 'refspec', grammar),
                    ('refspec.registry.act_resolution.resolve_act_relative_citation', 'refspec', acts)]
    candidates.sort(key=lambda row: (row['evidence'][0]['start'], row['evidence'][0]['end'], row['kind']))
    result = {'schema_version': 'document-references/2',
            'document': {key: document[key] for key in ('id', 'sha256', 'title', 'source_url')},
            'parsers': [{'name': name, 'version': version(package),
                         'module_sha256': digest(Path(module.__file__).read_bytes())}
                        for name, package, module in parsers],
            **({'indexes': indexes} if indexes else {}),
            'supported_kinds': sorted(SPICYSEARCH_KINDS | {'cfr'} | ({'act_relative'} if act_index is not None else set())),
            'candidates': candidates, 'rejected': rejected,
            'target_resolution': 'named_act_section_identity_only' if indexes else 'not_performed',
            'semantic_completeness': 'not_established',
            'limitation': 'Explicit mentions of the supported reference types only. Passage links locate occurrences; '
                          'they do not establish target existence, legal version, applicability, or citation completeness. '
                          'Optional act mappings identify code sections in the supplied indexes, not target text or matching historical editions.'}
    if 'uslm_source' in document:
        from .uslm import attach_publisher_links
        return attach_publisher_links(document, result, passages)
    return result
