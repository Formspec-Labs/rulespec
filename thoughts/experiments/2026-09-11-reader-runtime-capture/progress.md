# Reader capture delivery complete

Source changes are limited to `extraction.py`'s existing source/version capture:
two application adapters, nine installed reader/helper modules, and optional
RefSpec/SpicySearch versions. The package README selects the new capture wheel.
`test_runtime_readers.py` adds five controls. No model/schema change or provider call.

Completed:

- The installed retention baseline fails the missing-reader control as expected.
- Five focused source controls pass, including mutated/restored reader code,
  absent optional packages and a broken transitive dependency.
- Full source and isolated installed suites each pass 559 tests, with no skips.
- Normal reprocess/replay/reference/discovery/review commands pass in isolation.
- Candidates, refusals, reference scans and discovery output match the previous
  delivered retention result exactly. All review content matches except its run
  record and the graph's derived lineage ID. The verifier checks that ID against
  each run and permits only that exact substitution; changed model information
  or source evidence still fails. The first overly strict byte-comparison failure
  and verifier are preserved. The original design is retained with its pinned hash.
- The new wheel is installed in the working environment. The isolated verifier
  passes against all seven wheel filesets and the source. The previous retention
  experiment's sealed files still match its manifest.

The working commands and `verify_delivery.py working` completed successfully.
Session 6307 is terminal, as are 22310, 19877, 94260, 19366, 4893, 23500 and 20142.
Both installations and the source match the pinned wheels; working exports match
the isolated outputs. The README, canonical R1 status and final manifest close
this slice. Preserve the completed retention manifest. Raw graphs differ in the
run-derived lineage ID only; every other graph field remains checked.

Next: continue R5/R6 qualified USC work. Current RefSpec `AuthorityCitation` retains
note/appendix/chapter/range distinctions; its `parse_authority_citation` has no
occurrence API. The nested `_read` already centralizes regex matches and status
construction, so inspect it before adding another scanner. General local paragraph
resolution, external bodies, vocabulary/metadata consumers and fresh product-value
checks remain open. No commit, push, publication or deployment occurred this turn.
