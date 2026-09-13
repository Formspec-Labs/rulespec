# Temporary preview setup repair

After three initial extractions and the first recovery response, processing
stopped in `ReviewStore` with `ReviewIntegrityError`: the extraction manifest was
missing from the temporary preview directory. The reused earlier research helper
copied only document.json, run.json and rulebook.json. These fresh production
captures correctly require their full original manifest and frozen artifacts.

The first request and response were saved normally before this local failure.
No proposal was filtered or chosen based on its outcome. Preserve the original
run.py and its pre-extraction hash. `resume.py` changes only temporary preview
setup: copy the complete original extraction directory, retain its manifest
verification and open `ReviewStore` in that temporary copy. The historical IEP
book continues through its original helper. No manifest guard is bypassed.

Preflight all four stores, decode the already saved response, and continue the
remaining frozen requests without retrying the provider call. The original
nineteen-call/time/token bounds and labels remain unchanged. Save expected request
objects and verify them against the actual provider requests. The first expected
request receipt is retrospective; its prompt and schema were already frozen
before that original request. No production code, prompt, model configuration,
source, book or original extraction history changes.

Use `resume.py verify` for the final replay, since the original run.py retains
the incomplete temporary-copy helper. This is a local experiment harness failure,
not a model, extraction-schema or semantic failure.
