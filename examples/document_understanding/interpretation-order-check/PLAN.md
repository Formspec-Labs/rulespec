# Does explicit interpretation help, and does its position matter?

Decision: choose whether existing interpretation fields merit a further adoption
proposal, and whether placing them before the statement deserves preference.
This experiment does not authorize or change production behavior.

Observation: the latest sparse extraction omitted scope/choice/logic enrichment
on all 29 passport/waste records. Several reviewed statements retained complex
meaning anyway. The saved notice example has a known standalone qualification
omission; an audit rationalization did not fix it.

Competing hypotheses:

1. Explicitly requesting useful scope/choice interpretation improves retention
   of governing conditions and nested alternatives. Both treatment orders should
   improve over baseline if the extra interpretation instruction is sufficient.
2. Producing interpretation before the statement helps retention beyond that
   instruction. Early should outperform late, provided actual output follows the
   requested order. We measure output behavior, not hidden reasoning.
3. Interpretation adds repetition or introduces a mistaken condition. Extra
   tokens without improved standalone statements, or false conditions on controls,
   weaken the proposal. Correct interpretation plus an incomplete statement is
   not a successful repair.

Arms: B uses the current CUE-generated provider schema and extraction prompt.
L uses the same schema/order plus a focused instruction to populate existing
scope_text/choice_text when inherited scope or nontrivial choices need explanation.
E uses exactly L's prompt/schema content, moving scope_text/scope_quotes and
choice_text/choice_quote before statement. No new interpretation field is added.
E versus L tests only property serialization order; B versus L tests the added
instruction. Optional fields remain optional/null. Evidence references remain
separate from generated interpretation.

Cases, frozen before calls:

- Full saved 29 CFR 825.303 notice source: known designated-number example must
  retain the unforeseeable-leave setting and unusual-circumstances qualification
  in its own statement. Check stabilization/access-to-phone exception, first-time
  versus repeat leave reasons, and recommendation versus obligation distinctions.
- Full saved Ohio satellite-waste source: preserve nested venting exceptions,
  AND label components, excess-accumulation trigger, three-day deadline and every
  compliance/removal destination. Preserve cross-reference exceptions without
  guessing their contents. These are mostly-correct controls from recent runs.
- Constructed branch-control text: infant badge exception does not qualify map
  permission; a lost-card parent condition governs both replacement and urgent
  temporary-pass rules but not the found-card branch. A category's grammatical
  'and' must not require belonging to both categories. Simple descriptive material
  should not acquire obligations or unnecessary interpretation.

Held constant: model gemini-3.8-flash, temperature 0, low thinking, maximum output
16384 tokens, one full document window per case, current parser/Core processing,
and no repairs/audit/refinement calls. Nine calls total: one per arm per case,
fixed randomized dispatch order. No retries or follow-on calls. This first screen
does not measure within-case variability; temperature zero does not imply stability.

Assess mechanical validity, actual emitted key order, interpretation population,
source-grounded interpretations, statement completeness, false-condition controls,
and actual input/output/thinking tokens separately. Read canonicalized outputs in
randomized opaque order without arm names or usage before unblinding. Review is
by Codex, with revisable development judgments rather than human-approved gold.

Decision rule: a treatment is worth further adoption consideration if it repairs
at least one actual baseline semantic miss in the statement, preserves the named
correct controls, adds no unsupported interpretation, and follows its intended
behavior. Extra interpretation alone is not improvement. Prefer E over L only
with a statement-level gain and observed order adherence; a tie establishes no
ordering advantage. Any failures remain counted. One call per cell supports only
a bounded observation and cannot establish a stable ordering effect. If baseline
already passes, report that the historical miss did not reproduce in this run.

Save exact schemas, requests, responses, settings, runtime hashes/snapshot,
refusals, raw/Core results, blind review and decision. Replay without provider
access. Production and earlier captures remain unchanged.
