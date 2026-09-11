# Complete CFR readings and their consumers

Decision: adopt complete compound/range reading only with consumers that retain
both endpoints or explicitly decline unsupported scope.

Hypothesis: the observed loss has two causes: partial lexical capture and
single-target data handling. Reading whole items and preserving endpoint pairs
together should fix the saved compounds and explicit ranges. Whole tokens alone
already failed this decision in `../2026-09-11-cfr-whole-tokens`.

Arms: the copied RefSpec `566df1d4` grammar and current consumer behavior versus
one shared item reader, a range containing two existing `CfrCitation` endpoints,
and coordinated authority/typed-row/explanation/application handling. This is a
deliberate bundle; no result will be attributed to one component alone.

Cases: all eight frozen publisher XML contexts and formatting variants from the
whole-token experiment; its twelve constructed controls; the 8,424 structured
OFR index keys; mixed lists, cross-part sections, endpoint pinpoints, incomplete
ends, malformed hyphen chains, prose numbers and paragraph boundaries. Index
keys check identities, not prose interpretation or existence. Existing tests
cover compilation, subpart and qualified citation behavior. These are development
and regression cases, not an independent accuracy benchmark.

Held constant: pinned source XML/manifest, source text and offsets, existing
list-expansion policies and non-CFR readers. Direct imports first. No model
calls, range enumeration, per-match catalog lookup or new dependency. Stop after
one coordinated implementation and focused regression comparison; preserve
failed runs and report a larger redesign rather than accumulating special cases.

Decision rule: both written endpoints and their pinpoints survive; compound
parts preserve their complete supported identity; uncertain/incomplete tails
cannot become accepted first-endpoint targets. Following list members survive.
All typed schemas, identities, joins, part-note comparisons, term explanations
and the Rulespec adapter preserve or refuse range scope. Existing single-reading
controls agree except frozen, justified divergences. Adoption requires relevant
source and installed-wheel checks. A narrower lexical gain is not a passed gate.

Design judgment: a two-endpoint range type makes an unconverted single-citation
consumer fail visibly. Flat optional fields were considered; they require less
type branching but allow old consumers to ignore the end silently. Existing
tabular authority records will use explicit endpoint columns. No new Core
identifier scheme is needed. The root owns application integration and delivery;
two agents own grammar and RefSpec consumers in separate files.

## Follow-up boundaries recorded during implementation

- Flat Authority/Arrow rows cannot represent endpoint pinpoints. They preserve
  coordinates and raw input but explicitly refuse that finer scope as
  `range_pinpoints_not_represented`. Native occurrences and the Rulespec adapter
  preserve both endpoint labels. No new Core fields were introduced for this.
- The full authority-note comparison identified existing hyphenated-section
  forms such as `48 CFR 1.301-1.304`. Those stay complete observed tokens with
  explicit refusal; this iteration does not add another interpretation grammar.
- Root boundary probes caught a new overlap defect: refusing a range end that
  starts another explicit CFR citation consumed that citation's title. Fixing
  this is necessary to preserve the original other-citation stop rule. The
  before results are retained in `boundary-probes-before.json`.
- User requested an overall status/value assessment. After this bounded fix,
  prioritize useful reference text/context and an end-to-end consumer over
  accumulating more parser families. This is a prioritization judgment, not a
  measured ranking of every backlog item.
