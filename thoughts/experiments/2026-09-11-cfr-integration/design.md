# Connect the existing CFR occurrence reader

Decision: Import RefSpec's useful CFR occurrence capability into the application
reference scan while retaining the already connected SpicySearch families.

Hypothesis: The existing occurrence API supplies complete explicit CFR members,
attached labels and title-bearing context that the five-family adapter omits.
The thin adapter can preserve those facts using existing Rulespec evidence IDs.
Counterhypothesis: list-context offsets or native refusal flags are lost during
integration, causing an apparently grounded but incomplete reading.

Arms: current installed five-family application; source application with RefSpec
`find_cfr_citations`, then its installed wheel. Same pinned source text, existing
five-family labels, dependency builds and evidence rules. No model calls.

Cases: Frozen upstream CFR occurrence tests and the previous integration's real
source cases. New adapter assertions cover two-member lists with different labels,
spaced labels, repeated references after Unicode, impossible titles, implausible
parts, absent document context, and a list title located in inserted text. The
source of the inherited title must be separately grounded. Freeze expected fields
and quotes before implementation; preserve the original five-family labels as a
separate expectation, not a completeness claim for CFR.

Decision rule: All established five-family readings remain identical. Every new
CFR occurrence retains native title/part/section, flags, pinpoint labels and exact
source context. Invalid/ungrounded readings remain inspectable without a resolved
target. Both CLI paths and installed-wheel checks must pass. No new Core grammar,
model response fields, or mandatory Core dependency. This test justifies the
bounded CFR integration, not closure of the overall import goal or proof of
semantic completeness. The user has authorized implementation of useful features.

Stop this individual comparison after integration checks; use failures to choose
the next upstream change rather than hiding them or shrinking the supported forms.
