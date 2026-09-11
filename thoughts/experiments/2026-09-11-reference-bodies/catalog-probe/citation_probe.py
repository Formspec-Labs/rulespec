"""Exercise SpicySearch's existing citation surface, offline; not a resolver."""
import dataclasses,hashlib,json,socket
from pathlib import Path
from unittest.mock import patch
from spicysearch.cfr_citations import extract_citations
import spicysearch.cfr_citations as module
root=Path(__file__).resolve().parent
queries=['49 CFR 390.5','49 CFR 382.107','40 CFR 82.158','§ 390.5','99 CFR 999999.999999','49 CFR 390.5T']
with patch.object(socket.socket,'connect',side_effect=RuntimeError('Offline only')):
 out={'network_calls':0,'module':module.__file__,'module_sha256':hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),'cases':[{'input':q,'output':[{**dataclasses.asdict(c),'part_level_key':c.key} for c in extract_citations(q,strict=True,keep_rejected=True)]} for q in queries]}
with (root/'citation-results.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2)
print(json.dumps(out,ensure_ascii=False,indent=2))
