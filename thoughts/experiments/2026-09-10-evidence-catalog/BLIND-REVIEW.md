# Manual review before revealing treatment labels

Reviewed all six shuffled raw proposal payloads, all challenge verdicts and their
exact quotations, decoder issues and final changed records. Reading copies list
unchanged fields instead of repeating them; complete captures remain preserved.
Labels were hidden, but quoting style and error behavior may make treatment partly
inferable. Same agent authored the expectations and reviewed the data; no gold labels.

**Alcohol outputs 1 and 2:** both add the two correct possession exceptions and
target only C0002. Neither excuses use of alcohol by the driver or changes employer
notice. Both retain the review-dependent State-report deadline as grouped meaning.
Both challenges support both proposals, and all four changes apply. Output 1
adds concept labels and more source context; output 2 adds actor fields that remain
ambiguous in evidence resolution. The meaning and target choices are equivalent;
structured component grounding differs. Neither contains a catalog key in place
of quotation text.

**Railroad output 3:** all five existing exemptions retain their entire fields and
quotes except relation/targets; all five target C0000 and apply. Correctly preserves
the narrow no-stop effect and does not target gear-changing or sign-consent rules.

**Railroad output 6:** proposes the same five correct links with unchanged exemption
meanings. The challenge supports all five semantically, but its P0000 quotation
renders `§ 390.5` with an ordinary space where the source has U+2009 thin space.
That quote fails exact grounding, so P0000 has no valid challenge judgment and its
edit is not applied. The other four apply. This is a loss of one usable edge, not
wrong target selection or loss of the retained standalone exemption's meaning.
The counterexample matters even if the model's interpretation was substantively
correct. Do not silently normalize the capture or score it as applied.

**Refrigerant outputs 4 and 5:** both preserve both complete exemption records and
link each to C0000 venting prohibition. All specified end uses, the propane effective
date, good-faith condition, first-route conjunction and alternative subpart-B route
remain unchanged. Neither improperly exempts the knowing post-recovery release
statement C0003 or the service-prerequisite duty C0004 through the de minimis rule.
Both challenges support the two edits and they apply.

Both refrigerant outputs omit the preregistered C0001 → C0004 link. Output 4 claims
the other subpart duties are unavailable remotely, although C0004 is a local
appliance-service rule. Output 5 supplies no omission explanation. This is the
same missing expected relationship in both, not successful complete target recovery.
C0004 already says non-exempt substitute, so omission does not create a newly
overbroad default statement. The broader explicit applicability model is incomplete.

No incorrect target or destructive meaning edit observed. Full semantic and target
parity fails for the railroad final graph if output 6 is the intervention; it
improves if output 3 is the intervention. Do not decide that until revealing labels.
Source text reconstruction and model copying reliability are separate dimensions.
