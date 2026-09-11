# Local paragraph addresses: comparison registered before candidate results

Decision: Can the existing Rulespec passage index support exact local paragraph
lookup with a small structural extension, or does it need richer source input?
This addresses R10 and the target-index prerequisite of R11. It does not decide
which paragraph legally governs another or change model defaults on this evidence.

Observed starting point: `source_passages` recognizes limited lowercase list
markers and stores parents, but no written address. The saved seatbelt document
contains uppercase and spaced markers. The refrigerant capture also joins two
levels within a paragraph. The current section-reference resolver matches supplied
section labels only.

## Competing explanations and arms

- A: The current splitter/parent index plus its existing exact spans. Capture its
  output and implementation before editing it. No reference-address field exists.
- B: Reuse that index, extending marker recognition and retaining written label
  components and structural address candidates. Measure boundary and parent changes
  separately. Do not add a second independent passage collection.
- Source check: inspect original publisher markup where available. If it provides
  disambiguating structure that flattened text loses, retain that as a limitation
  rather than silently choose an address. This is source evidence, not another
  model arm.

H1: Missing marker forms explain the unaddressable saved targets. B should recover
their exact locations while preserving existing supported parent relationships.
H2: Flattened text loses distinctions needed for hierarchy. B may recognize labels
but should retain ambiguity when the same label could denote different levels.
H3: Boundary errors, rather than ancestry alone, cause loss. Full marker recognition
should expose these changes; successful lexical matching alone will not pass.

## Cases and bounds

- Original saved seatbelt and refrigerant documents from the design-context cases.
- Existing passport/dotted-list, baggage/combined-marker and `(h)`/`(i)` controls.
- Two newly selected eCFR sections from the pinned RefSpec title 21 and 49 XML:
  first previously unselected section in source order with 8–35 direct `P` elements,
  a leading lowercase marker and at least one uppercase or combined leading marker.
  Select without either candidate's outputs; save whole sections and their source
  identities. If no such section exists, record that and revise selection before
  running the candidate.
- Constructed duplicate-label, missing-parent, Roman/letter ambiguity, section-reset,
  overlapping-section, no-blank-line boundary and source-map controls. Preserve
  literal “of this action” as a future resolver case; do not interpret it here.

Manually record expected source paths and uncertain readings before B runs. Prior
saved sources are development controls. Two fresh sections diagnose transfer; they
cannot establish a general document-accuracy rate.

Held constant: exact input text, section declarations, source maps and digest rules.
No model calls, prompt changes, fetching a different legal edition or source edits.
One deterministic run per arm/input; repeat only after a documented correction.
Bound: these four source documents plus the specified regression/control families.
Stop when the address-index decision is answered; broader range grammar and model
context quality require separate comparisons.

## Decision rule

Adopt the demonstrated structural behavior only if the saved targets and labeled
fresh targets resolve to the correct exact spans, ambiguous controls never choose
a false unique address, and existing supported passage/context checks pass.
Preserve text coverage and source evidence. Passage IDs must remain identical for
unchanged boundaries. Explicitly report changed boundaries, parents and context.
Do not call this a semantic-quality gain. If a hierarchy change affects model
context, keep it experimental until its consumer effect is tested or isolate the
address enrichment from existing context selection.

Reuse current source/evidence types and existing lookup/CLI paths. No new Core
schema, required RefSpec dependency for Core, parallel document index, or generic
parser framework. A failed broader gate remains failed even if a narrower lexical
fix is useful.

## Reuse assessment before implementation

RefSpec supplies the pinned eCFR corpus and a parenthetical pinpoint lexer inside
its citation grammar, but citation labels do not establish source ancestry. Its
USC oracle and USLM edge extractor have different source formats and consumers.
Spicy Regs' CFR reader supplies annual section metadata, not paragraph bodies.
Rulespec already owns exact text passages and source maps; that is the candidate
extension point.

[GPO's format documentation](https://github.com/usgpo/bulk-data/blob/master/ECFR-XML-User-Guide.md#24-paragraphs)
states that numbered eCFR paragraphs are flat elements with embedded labels.
[CFPB regulations-parser](https://github.com/cfpb/regulations-parser) and its
[eRegs successor](https://github.com/eregs/regulations-parser) were inspected; both
are archived. They are reference implementations, not an adopted maintained
dependency. New source evidence may still favor preserving markup over inference.
