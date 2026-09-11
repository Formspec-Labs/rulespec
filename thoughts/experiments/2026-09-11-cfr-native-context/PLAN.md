# Omitted CFR titles: source context versus citation context

Decision: determine which source-supported title strategy is safe enough to
connect to the existing reference/discovery commands under R9. Reuse RefSpec's
coordinate, range, list and qualification readers; do not insert an invented
title into the input or change model output.

Hypotheses:

1. Missing native TITLE context explains the omitted-reference failures. If it
   is sufficient, supplying that title will recover section citations without
   attributing citations to another authority to the current document's title.
2. Native context is necessary but sometimes insufficient: a citation's own
   wording can select another authority. Explicit local scope (`of this title`,
   `of this chapter`, `of this subchapter`, `of this part`) should distinguish
   some safe readings, but restricting all reads to those phrases may omit
   useful unqualified references. Count those omissions, not just precision.

Arms: A is the installed/current explicit-only RefSpec reader. B additionally
uses the existing item/list/qualifier code with the native title on marked
decimal section citations. C uses B but accepts only a complete citation group
with explicit local scope. C is a diagnostic alternative, not a redefinition
of the broad R9 acceptance gate. No parser or application adoption is implied
by a narrow gain.

Cases: actual paragraphs from pinned eCFR titles 17, 40, 41 and 49, including
the saved refrigerant and driver-definition failure families; cross-authority
citations found during raw source inspection; and declared constructed controls
for missing/conflicting/unverified context, explicit other titles, repeated
occurrences, list scope, note/open-ended/range qualifications, and misleading
numbers. Retain complete selected paragraph XML, ancestor attributes/headings,
full source digests and source XPath. Paragraph selection is a diagnostic sample,
not an unbiased benchmark. Human labels are revisable and uncertainty is explicit.

Held constant: original paragraph characters, existing explicit parser,
coordinate/list/range/qualifier implementation, source reader and code versions.
One deterministic execution per arm; no model calls. Bound: at most 12 real
paragraphs and 24 constructed controls, followed by one raw output review.

Decision rule: recommend adoption only if all declared target citations are
recovered with exact evidence, no foreign or ambiguous title becomes an accepted
local target, absent/conflicting/unverified context stays unresolved, and explicit
readings/qualified refusals remain unchanged. Otherwise retain the failed gate,
identify the missing distinction, and specify a next implementation or comparison.
All syntax/refusal losses and false positives count, including intermediate
failures. A failed broad gate cannot become a passed gate by dropping cases.

Scope: this tests recognition and context attribution, not legal applicability,
paragraph existence, edition matching, model comprehension, or general extraction
accuracy. Source lookup remains a separate consumer. Production stays unchanged
until this comparison supports a coherent implementation.

Input-selection correction before running any arms: the first capture retained
nine paragraphs and its two unmatched selectors. The Treasury reference lives
in an appendix, not a SECTION, so the capture now retains either native container.
The actual `§§ 82.155` practices paragraph is in another section; the original
82.156-only selector was incorrect. The completed selection is saved separately
from the first attempt. Neither correction removes a negative case or changes
the acceptance rule.
