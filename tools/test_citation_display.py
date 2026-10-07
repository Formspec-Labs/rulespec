"""Citation display and illustrative-sample source/graph conformance checks.

Run with the existing tooling interpreter. These checks exercise CUE-generated
node schemas and authored graph invariants without building the Rust workspace.
"""
from __future__ import annotations

import copy
import json
import tempfile
import shutil
import subprocess
import unittest
from pathlib import Path

import rdflib
from jsonschema import Draft202012Validator
from pyshacl import validate

from tools.constraints_compile import (
    CompileError,
    _scan_global_enum_registry,
    parse_cue_file,
    target_json_schema,
    target_rust,
    target_shacl,
    target_typescript,
)

ROOT = Path(__file__).resolve().parents[1]
LANGUAGE_GRAMMAR = next(line for line in (ROOT / 'constraints' / 'core' / 'vocabulary-text.cue').read_text().splitlines() if line.startswith('#BCP47LanguageTag:'))


def compiled(source: str) -> tuple:
    path = ROOT / 'constraints' / 'core' / source
    document = parse_cue_file(path)
    return document, _scan_global_enum_registry(path)


def schema_validator(source: str, name: str) -> Draft202012Validator:
    document, registry = compiled(source)
    schema = json.loads(target_json_schema(document, registry=registry))
    return Draft202012Validator({**schema['$defs'][name], '$defs': schema['$defs']})


def fixture(name: str) -> dict:
    return json.loads((ROOT / 'fixtures' / f'{name}.jsonld').read_text())


def graph_conforms(payload: dict, *, include_compiled: bool = True) -> bool:
    payload = copy.deepcopy(payload)
    payload['@context'] = json.loads((ROOT / 'context' / 'rkaf-context.jsonld').read_text())['@context']
    graph = rdflib.Graph().parse(data=json.dumps(payload), format='json-ld')
    shapes = rdflib.Graph().parse(ROOT / 'shapes' / 'rkaf-shapes-warrant.ttl', format='turtle')
    if include_compiled:
        for source in ('artifact.cue', 'evidence-binding.cue', 'assertion.cue', 'value-assertion.cue', 'local-adoption.cue'):
            document, registry = compiled(source)
            shapes.parse(data=target_shacl(document, registry=registry), format='turtle')
    conforms, _, report = validate(graph, shacl_graph=shapes, inference='rdfs', advanced=True)
    if not isinstance(conforms, bool):
        raise AssertionError(report)
    return conforms


class CitationDisplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = schema_validator('artifact.cue', 'Artifact')

    def test_optional_metadata_preserves_legacy_artifacts_and_source_identity(self) -> None:
        self.validator.validate(fixture('artifact-doi-positive'))
        payload = fixture('artifact-citation-display-positive')
        identifiers = copy.deepcopy(payload['rkaf:hasArtifactIdentifier'])
        self.validator.validate(payload)
        self.assertEqual(payload['rkaf:hasArtifactIdentifier'], identifiers)
        self.assertTrue(graph_conforms(payload))
        legacy = copy.deepcopy(payload)
        legacy['dcterms:title'] = 'Existing untagged title'
        self.validator.validate(legacy)
        self.assertTrue(graph_conforms(legacy))

    def test_all_maintained_corpus_artifacts_keep_valid_authored_metadata(self) -> None:
        count = 0
        for path in (ROOT / 'reference-corpora').rglob('*.jsonld'):
            payload = json.loads(path.read_text())
            for node in payload.get('@graph', [payload]):
                kinds = node.get('@type', [])
                kinds = [kinds] if isinstance(kinds, str) else kinds
                if 'rkaf:Artifact' in kinds:
                    with self.subTest(path=path.name, node=node.get('@id')):
                        authored = dict(node, **{'@type': 'rkaf:Artifact'})
                        self.validator.validate(authored)
                        count += 1
        self.assertGreater(count, 0)

    def test_title_map_rejects_empty_invalid_language_and_non_text(self) -> None:
        for name in ('empty-map', 'invalid-language', 'non-text'):
            with self.subTest(name=name):
                payload = fixture(f'artifact-citation-display-{name}-negative')
                self.assertFalse(self.validator.is_valid(payload))
        payload = fixture('artifact-citation-display-positive')
        for title in ({'en': ''}, {'@none': 'Untagged'}, {'en': ['First', 'Second']}, 42):
            with self.subTest(title=title):
                payload['dcterms:title'] = title
                self.assertFalse(self.validator.is_valid(payload))

    def test_context_retains_languages_edition_and_issue_date(self) -> None:
        payload = fixture('artifact-citation-display-positive')
        payload['@context'] = json.loads((ROOT / 'context' / 'rkaf-context.jsonld').read_text())['@context']
        graph = rdflib.Graph().parse(data=json.dumps(payload), format='json-ld')
        subject = rdflib.URIRef(payload['@id'])
        self.assertEqual({(str(value), value.language) for value in graph.objects(subject, rdflib.DCTERMS.title)},
                         {('Illustrative source edition', 'en'), ('Edición de fuente ilustrativa', 'es-US')})
        self.assertEqual(str(graph.value(subject, rdflib.URIRef('http://www.w3.org/ns/dcat#version'))), 'example-2026')
        self.assertEqual(payload['dcterms:issued'], '2026-10-06')
        self.assertEqual(graph.value(subject, rdflib.DCTERMS.issued).datatype, rdflib.XSD.dateTime)

    def test_generated_carriers_preserve_map_and_legacy_text(self) -> None:
        document, registry = compiled('artifact.cue')
        rust = target_rust(document, registry=registry)
        self.assertIn('pub enum PreferredLabelMapOrString', rust)
        self.assertIn('#[serde(untagged)]', rust)
        self.assertIn('pub title: Option<PreferredLabelMapOrString>', rust)
        typescript = target_typescript(document, registry=registry)
        self.assertIn('"dcterms:title"?: PreferredLabelMap | string', typescript)
        self.assertIn('typeof v["dcterms:title"] !== "string"', typescript)

    def test_union_requires_an_actual_named_map(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'bad.cue'
            path.write_text('package test\n#Record: {\n "@type": "rkaf:Record"\n "rkaf:text"?: #MissingMap | string\n}\n')
            with self.assertRaises(CompileError):
                target_json_schema(parse_cue_file(path), registry={})

    def test_composition_narrows_legacy_text_in_both_directions(self) -> None:
        for base, derived in (('#Labels | string', '#Labels'), ('#Labels', '#Labels | string')):
            with self.subTest(base=base, derived=derived), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / 'maps.cue'
                path.write_text('package test\nimport "struct"\n' + LANGUAGE_GRAMMAR + '\n#Labels: struct.MinFields(1) & {\n [language=#BCP47LanguageTag]: string\n}\n'
                                + '#Base: {\n "@type": "rkaf:Example"\n "rkaf:text"?: ' + base + '\n}\n'
                                + '#Narrow: {\n #Base\n "rkaf:text"?: ' + derived + '\n}\n')
                document = parse_cue_file(path)
                schema = json.loads(target_json_schema(document, registry={}))
                validator = Draft202012Validator({**schema['$defs']['Narrow'], '$defs': schema['$defs']})
                self.assertFalse(validator.is_valid({'@type': 'rkaf:Example', 'rkaf:text': 'legacy'}))
                validator.validate({'@type': 'rkaf:Example', 'rkaf:text': {'en': 'example'}})
                self.assertNotIn('"rkaf:text"?: Labels | string', target_typescript(document, registry={}).split('export interface Narrow')[1])

    def test_union_carrier_name_collision_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'maps.cue'
            path.write_text('package test\nimport "struct"\n' + LANGUAGE_GRAMMAR + '\n#Labels: struct.MinFields(1) & {\n [language=#BCP47LanguageTag]: string\n}\n'
                            + '#LabelsOrString: "existing" | "other"\n'
                            + '#Record: {\n "@type": "rkaf:Record"\n "rkaf:text"?: #Labels | string\n}\n')
            with self.assertRaisesRegex(CompileError, 'conflicts with a CUE definition'):
                target_rust(parse_cue_file(path), registry={})

    def test_cue_source_validates_optional_map_and_legacy_title(self) -> None:
        cue = ROOT / '.tools' / 'cue'
        if not cue.exists():
            self.skipTest('repository-local CUE is unavailable')
        for title, accepted in (({'en': 'Example', 'es-US': 'Ejemplo'}, True), ('Legacy title', True), ({'en': ''}, False), ({'es_US': 'Ejemplo'}, False)):
            payload = fixture('artifact-citation-display-positive')
            payload.pop('@context'); payload.pop('@id')
            payload['dcterms:title'] = title
            with self.subTest(title=title), tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / 'artifact.json'
                path.write_text(json.dumps(payload))
                result = subprocess.run([str(cue), 'vet', *map(str, sorted((ROOT / 'constraints' / 'core').glob('*.cue'))), '-d', '#Artifact', str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode == 0, accepted, result.stderr)

    def test_generated_typescript_executes_title_validation(self) -> None:
        node = shutil.which('node')
        if not node:
            self.skipTest('Node is unavailable for generated TypeScript validation')
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            document, registry = compiled('vocabulary-text.cue')
            (directory / 'vocabulary-text.ts').write_text(target_typescript(document, registry=registry))
            document, registry = compiled('artifact.cue')
            (directory / 'artifact.ts').write_text(target_typescript(document, registry=registry).replace('"./vocabulary-text"', '"./vocabulary-text.ts"'))
            script = "import {validateArtifact} from " + json.dumps((directory / 'artifact.ts').as_uri()) + ";\n"
            script += "const titles = [{en:'Example','es-US':'Ejemplo'}, 'Legacy', {en:''}, {'es_US':'Ejemplo'}, {}, {en:42}];\n"
            script += "const base = " + json.dumps(fixture('artifact-citation-display-positive')) + ";\n"
            script += "const passed = titles.map(title => validateArtifact({...base, 'dcterms:title':title}).length === 0); console.log(JSON.stringify(passed));\n"
            result = subprocess.run([node, '--experimental-strip-types', '--input-type=module', '-e', script], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), [True, True, False, False, False, False])


class IllustrativeSampleTests(unittest.TestCase):
    def test_value_and_generic_assertions_need_no_safety_label(self) -> None:
        payload = fixture('evidencebinding-illustrative-sample-positive')
        for node in payload['@graph']:
            name = node['@type'].split(':')[1]
            source = 'value-assertion.cue' if name == 'ValueAssertion' else 'evidence-binding.cue'
            schema_validator(source, name).validate(node)
        self.assertTrue(graph_conforms(payload))
        for kind in ('rkaf:Assertion', 'rkaf:RelationshipAssertion'):
            generic = copy.deepcopy(payload)
            generic['@graph'][0]['@type'] = kind
            if kind == 'rkaf:RelationshipAssertion':
                generic['@graph'][0]['rkaf:assertsObject'] = 'urn:rkaf:example:rule'
                del generic['@graph'][0]['rkaf:assertsValue']
            self.assertTrue(graph_conforms(generic))

    def test_every_allowed_and_forbidden_usage_ceiling(self) -> None:
        payload = fixture('evidencebinding-illustrative-sample-positive')
        for value in ('notEligible', 'searchOnly', 'reviewQueueOnly', 'draftGenerationAllowed',
                      'localOperationalUse', 'publicationAllowed', 'officialUse'):
            payload['@graph'][0]['rkaf:usageEligibility'] = 'rkaf:' + value
            with self.subTest(value=value):
                self.assertEqual(graph_conforms(payload), value not in ('localOperationalUse', 'publicationAllowed', 'officialUse'))

    def test_sample_negative_fixtures_reject_at_graph_layer(self) -> None:
        for name in ('official', 'missing-eligibility', 'dangling'):
            with self.subTest(name=name):
                payload = fixture(f'evidencebinding-illustrative-sample-{name}-negative')
                self.assertFalse(graph_conforms(payload))
        payload = fixture('evidencebinding-illustrative-sample-positive')
        payload['@graph'][0]['@type'] = 'rkaf:Artifact'
        self.assertFalse(graph_conforms(payload, include_compiled=False))

    def test_fragment_or_other_binding_does_not_bypass_sample_cap(self) -> None:
        payload = fixture('evidencebinding-illustrative-sample-official-negative')
        binding = payload['@graph'][1]
        binding.update({'rkaf:bindsSourceFragment': ['urn:rkaf:example:fragment'],
                        'rkaf:evidenceRole': 'rkaf:textualEvidence',
                        'rkaf:evidentiaryFunction': 'rkaf:supports'})
        self.assertFalse(graph_conforms(payload))
        payload['@graph'].append({**binding, '@id': 'urn:rkaf:example:another-binding',
                                  'rkaf:noEvidenceReason': 'rkaf:axiomatic'})
        self.assertFalse(graph_conforms(payload))

    def test_adoption_cannot_broaden_validated_sample_eligibility(self) -> None:
        payload = fixture('evidencebinding-illustrative-sample-adoption-negative')
        adoption = payload['@graph'][2]
        schema_validator('local-adoption.cue', 'LocalAdoption').validate(adoption)
        for status in ('active', 'proposed', 'revoked', 'expired'):
            adoption['rkaf:adoptionStatus'] = 'rkaf:' + status
            for eligibility in ('localOperationalUse', 'publicationAllowed', 'officialUse', 'draftGenerationAllowed'):
                adoption['rkaf:usageEligibility'] = 'rkaf:' + eligibility
                with self.subTest(status=status, eligibility=eligibility):
                    self.assertEqual(graph_conforms(payload), eligibility == 'draftGenerationAllowed')
        adoption['rkaf:usageEligibility'] = 'rkaf:officialUse'
        # Evidence reasons other than illustrativeSample do not acquire this cap.
        payload['@graph'][1]['rkaf:noEvidenceReason'] = 'rkaf:axiomatic'
        self.assertTrue(graph_conforms(payload))

    def test_existing_evidence_reasons_keep_their_behavior(self) -> None:
        for name in ('evidencebinding-no-evidence-reason-positive', 'evidencebinding-declared-hypothesis-positive'):
            with self.subTest(name=name):
                self.assertTrue(graph_conforms(fixture(name)))


if __name__ == '__main__':
    unittest.main()
