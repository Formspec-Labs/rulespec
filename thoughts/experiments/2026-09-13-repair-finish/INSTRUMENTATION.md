# Ledger pin correction

After the first generation call completed, the next launch stopped locally: the
generation pin set mistakenly included `calls.json`, which must change after every
call. It also included the extraction-stage `usage.json`, another mutable receipt.
No second provider request was sent and no response was retried.

Retain the original `generation-pins.json` and its exact runner bytes in
`run-before-ledger-fix.py`. `execution-pins.json` excludes only those two mutable
receipts and updates the runner hash for the one-line pin-file selection change.
Every source, actual request, schema, label, selected target and model setting is
unchanged. Resume at cell 02, keeping cell 01 and its tokens/time in the results.
This is an instrumentation correction, not a changed treatment or outcome rule.
