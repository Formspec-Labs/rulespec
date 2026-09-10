# Raw output review before revealing the arm mapping

Reviewed all six shuffled payloads against the supplied source text and frozen
expected targets. Empty fields were hidden in the reading copy; original complete
provider captures remain unchanged. The arm mapping was hidden during this review,
but the instructed exemption behavior makes arms partly inferable. These are
revisable engineering judgments by the same agent that authored the fixtures.

- **Output 1, extinguishers:** correct proposed outside-building exemption target
  C0003 → C0000, but rewrites/reclassifies the exemption and changes its quote.
  Omits the designated-user exemption edge C0002 → C0000, explicitly calling the
  standalone representation sufficient. The added during-use exception correctly
  identifies the location duty, not an excuse from maintenance. No wrong target
  observed. The limitation to location is stated in its summary.
- **Output 2, recordkeeping:** identifies the correct industry-exemption target
  C0003 → C0000 but reclassifies and rewrites it. Correctly leaves incident reporting
  independent and does not target the >10 duty with the small-company exemption.
  The written-notice override is acknowledged in prose but no explicit edge is added.
- **Output 3, extinguishers:** links both existing exemptions to C0000, preserving
  their statements, force and main quotes. Neither exemption targets C0001. Adds
  the separate during-use location exception. Flags the unrepresented section-wide
  evacuation exemption instead of creating or linking it. Correct on the scored
  existing exemptions; broader completeness remains unestablished.
- **Output 4, process safety:** links the grouped section exclusion C0004 to all
  three employee-participation duties and leaves the hot-work definition alone.
  Preserves the OR between excluded facility/operation categories. Reports missing
  positive application conditions rather than constructing them. Correct on all
  scored targets; this does not complete the section's applicability model.
- **Output 5, process safety:** adds a generally relevant positive applicability
  condition to all three duties but leaves the existing section exclusion unlinked,
  explicitly stating that no link is needed. Its `logic_text` is visibly synthesized
  and contains literal ellipses, contradicting the verbatim-field instruction.
  Its summary also risks reading the flammable-branch exceptions across the first
  alternative; do not count this addition as a fully faithful positive result.
  These concerns are separate from the frozen exemption-link score.
- **Output 6, recordkeeping:** links C0003 → C0000 with the original statement and
  main quote, preserving exemption/not_required. Does not link the small-company
  exemption to a disjoint >10 duty or to incident reporting. Reports its unavailable
  general baseline as unresolved. Correct on both the positive and negative cases.

No new proposal duplicates an existing exemption into a companion statement.
Outputs 1 and 2 attempt replacement/reclassification, a different problem from
duplicate additions. Outputs 3, 4 and 6 visibly satisfy the link-only intent;
exact preservation and decoder acceptance still require mechanical confirmation.

Raw target recovery: outputs 1/3 recover 1/2 and 2/2 extinguisher edges;
outputs 2/6 both recover the one industry edge; outputs 5/4 recover 0/3 and 3/3
process-safety exclusion edges. No incorrect exemption targets observed in any
output. This assesses proposed target selection, not acceptance or actual editing.
