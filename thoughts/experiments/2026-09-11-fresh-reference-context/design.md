# Fresh extraction with existing publisher context

Prepared 2026-09-11 before selecting comparison outputs or making provider calls.
This experiment addresses R15/R16, with source selection under R20/R24. It does
not replace the broader end-to-end quality evaluation with a three-case score.

**Decision:** whether the existing USLM source/target reader supplies useful
context to the current extraction pass, without another model stage or schema.

**Hypotheses:**

- H1: some missing conditions or defined-term limits come from unsupplied source.
  Adding located target text and complete short enclosing sections should improve
  the complete focus statements on fresh sources.
- H2: target availability is insufficient; the model still omits the qualification
  or cannot determine its relationship. Score available source separately from
  its correct use in extracted meaning.
- H3: added context causes false inheritance or independent context-only rules.
  Negative source cases must retain their actor, modality and limited scope.

**Arms:** A, unchanged production windows/context/prompt/schema. B, the same
focus window and production request with additional source context selected from
the existing publisher-reference/target tables and source section coordinates.
No changed instructions, model fields, model settings, manual answer insertion,
new reference grammar or network target fetching. B is a context-selection bundle;
it cannot isolate target text from enclosing-section text.

**Fresh source selection:** use the verified local USLM release 119-102 archive,
considering titles 29, 38 and 20 in that order. Inspect bounded whole chapters
(roughly 30,000–150,000 prepared characters) with an operative, uniquely located
reference to text outside a production focus window. Prefer a referenced
definition or qualification whose source can be read completely. Retain exact
chapter bytes in the original root wrapper, archive/member/fragment hashes and
source positions. Exclude the saved passport, seatbelt, refrigerant and prior
title 5/42 cases. Check prior experiment case/plan records before labeling an
input previously untuned. Selection deliberately seeks context opportunities;
it is not random sampling or a general accuracy population.

Use at most one natural focus window per title, three cases total. Inspect and
freeze the actual window, relevant complete meanings, unrelated-duty and
uncertainty controls before creating the live request sequence. The selected
case file is the remaining prerequisite for the live comparison.

**B's bounded selection:** preserve A's supplied source. First consider uniquely
located targets referenced by operative publisher occurrences inside the focus.
Use the complete short target section when it is at most 6,000 characters;
otherwise use the exact supplied target node. Then consider complete enclosing
focus sections at most 12,000 characters. Add at most 12,000 distinct characters
beyond A, in source-reference order. Deduplicate source positions, exclude focus
text already supplied, and decline a whole addition that exceeds the budget
rather than truncate its conditions. One hop only. Preserve absent, ambiguous,
empty and omitted targets as diagnostics. Editorial/source-credit references do
not trigger context expansion. Existing source/evidence helpers check the result.

**Held constant:** current generated provider schema, examples and prompt;
`gemini-3.8-flash`, low thinking, temperature 0, 16,384 output-token limit;
the production 24,000-character window plan; identical focus per pair. Two
observations per arm/case, balanced AB/BA order, at most twelve calls and 45 minutes
from the first request. No automatic retries or tuning. Retain failed/refused
attempts and actual request bodies. Credentials use the existing redacted capture
helper and never enter experiment files.

**Decision rule:** an ordinary-extraction change requires a complete missing
meaning to be recovered on at least two natural cases in both observations, no
new critical unsupported scope/actor/modality/exception decision on the frozen
negative controls or manual raw review, and preserved exact evidence. Mean total
reported tokens for B must be at most 1.5 times A for this adoption decision.
Report disagreements, variability and limitations rather than treating an agent
assessment as gold. A source-availability gain without meaning gain does not pass.
A quality/cost tradeoff remains a tradeoff, not a silently relaxed passing gate.
New omissions outside the frozen focus criteria are reported separately.

**Validation and delivery:** inspect original source, prepared passages, actual
requests, raw responses, parsed/refused rows, Core records and discovery evidence.
Reuse `_record_window`, `parse_raw_response`, the generated schemas and current
compilation/capture functions. Compare fixed saved outputs for deterministic
processing checks; only provider calls test model behavior. If the gate passes,
integrate the smallest optional application connection, test direct imports,
rebuild the affected wheel and check installed commands. Keep validation local
and replayable; a resolved source link does not establish legal applicability.
