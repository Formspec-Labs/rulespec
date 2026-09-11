"""Offline source-profile/locator boundary checks; no fetches or interpretation."""
from pathlib import Path
import dataclasses,hashlib,json,socket
from unittest.mock import patch
from spicy_docs.catalog.profiles import declared_profile_for_table
from spicy_docs.sources.federal_register.body_sources import body_source_locators
import spicy_docs.sources.federal_register.body_sources as body_module
import spicy_docs.catalog.profiles as profile_module
ROOT=Path(__file__).resolve().parent
result={'network_calls':0,'modules':{m.__name__:{'path':m.__file__,'sha256':hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()} for m in [body_module,profile_module]}}
with patch.object(socket.socket,'connect',side_effect=RuntimeError('Offline only')):
 profile=declared_profile_for_table('cfr_sections');result['cfr_profile']=dataclasses.asdict(profile)
 # Real eCFR corpus URL, deliberately passed to FR-only locator API: must refuse.
 try:body_source_locators({'document_number':'390.5','publication_date':'2026-08-19','body_html_url':'https://www.ecfr.gov/api/versioner/v1/full/2026-08-19/title-49.xml'})
 except Exception as e:result['ecfr_on_fr_api']={'type':type(e).__name__,'message':str(e)}
 # Constructed FR metadata control tests URL derivation only, not availability.
 result['constructed_fr_locator']=dataclasses.asdict(body_source_locators({'document_number':'2026-12345','publication_date':'2026-08-19','body_html_url':'https://www.federalregister.gov/documents/full_text/html/2026/08/19/2026-12345.html'}))
with (ROOT/'spicydocs-results.json').open('x') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps(result,ensure_ascii=False,indent=2))
