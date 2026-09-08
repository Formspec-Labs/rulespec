"""Recorded transport/shape diagnostics; not an extraction quality benchmark."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from importlib.metadata import version
import json
from pathlib import Path

from google import genai
from rulespec_extrapolator.core import KINDS, MODALITIES
from rulespec_extrapolator.extraction import _credential, _save_provider_json

ROOT = Path(__file__).resolve().parent


def native(schema):
    if isinstance(schema, list):
        return [native(item) for item in schema]
    if not isinstance(schema, dict):
        return schema
    result = {key: native(value) for key, value in schema.items() if key != "nullable"}
    if schema.get("nullable"):
        result["type"] = [result["type"], "null"]
    return result


def main():
    key = _credential(Path('/Users/mikewolfd/Work/spicy-regs/.env'))
    runs = ROOT.parent / 'runs'
    full = json.loads((runs / 'names-02/frozen/provider-schema.json').read_text())
    shared = json.loads((runs / 'names-03/frozen/provider-schema.json').read_text())
    strict = native(deepcopy(shared))
    row = strict['properties']['extractions']['items']
    attrs = row['properties']['unit_attributes']
    attrs['type'] = 'object'
    attrs['required'] = list(attrs['properties'])
    attrs['additionalProperties'] = False
    attrs['properties']['kind']['enum'] = sorted(KINDS)
    attrs['properties']['modality']['enum'] = list(MODALITIES)
    attrs['properties']['relation']['enum'] = ['none', 'scope', 'prerequisite', 'trigger', 'exception']
    row['required'] = ['unit', 'unit_attributes']
    row['additionalProperties'] = False
    strict['additionalProperties'] = False
    variants = [('full-openapi', 'response_schema', full),
                ('full-native', 'response_json_schema', native(full)),
                ('shared-openapi', 'response_schema', shared),
                ('shared-strict-native', 'response_json_schema', strict)]
    output = ROOT / 'probes-01'
    output.mkdir(exist_ok=False)

    def run(variant):
        name, field, schema = variant
        request = {'model': 'gemini-3.8-flash',
                   'contents': 'There is no source text. Return an empty extractions array.',
                   'config': {'temperature': 0, 'candidate_count': 1,
                              'max_output_tokens': 256, 'response_mime_type': 'application/json', field: schema}}
        _save_provider_json(output / (name + '.request.json'), request, key)
        result = {'name': name, 'field': field, 'schema_bytes': len(json.dumps(schema)),
                  'status': 'failed'}
        try:
            with genai.Client(api_key=key, http_options={'timeout': 45000, 'retry_options': {'attempts': 1}}) as client:
                response = client.models.generate_content(**request)
            _save_provider_json(output / (name + '.response.json'),
                                response.model_dump(mode='json', exclude={'sdk_http_response'}), key)
            result.update(status='response_received', model_version=response.model_version,
                          text=response.text)
        except Exception as error:
            # Never save SDK error strings, headers, URLs or credentials.
            result.update(error_class=type(error).__name__, code=getattr(error, 'code', None),
                          error_status=getattr(error, 'status', None))
        _save_provider_json(output / (name + '.result.json'), result, key)
        print(json.dumps(result), flush=True)
        return result

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(run, variants))
    _save_provider_json(output / 'report.json', {
        'purpose': 'Request acceptance only; all inputs intentionally empty.',
        'versions': {name: version(name) for name in ['google-genai', 'langextract']},
        'results': results,
    }, key)


if __name__ == '__main__':
    main()
