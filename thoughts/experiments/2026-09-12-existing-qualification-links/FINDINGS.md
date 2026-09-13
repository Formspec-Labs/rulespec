# Text and target identities exist; the relative-reference connection is missing

The existing reader can retrieve the two attendance clauses by their native
identifiers. It does not recognize the ordinary-text references “clause (i)” and
“clause (ii)” in the captured writing requirement. Context export already includes
the writing text, but does not connect the three extracted meanings. This is a
concrete reference/association gap, not a need for more source text or confidence
scoring. No production behavior changed and no model calls were made.

## Read-only trace

Ran existing `references.scan_references` and `context.export_context` on the
unchanged saved IEP and LEA books. The actual source is native USLM XML (United
States Legislative Markup), retaining publisher identifiers and source maps.
All originals remained byte-equivalent when serialized. Provider creation was
blocked throughout the trace.

| Layer | IEP result |
|---|---|
| Captured writing requirement | R006 retains the full writing rule and the two clause-reference strings |
| Native source identifiers | `/us/usc/t20/s1414/d/1/C/i` and `/us/usc/t20/s1414/d/1/C/ii` exist |
| Publisher hyperlink at the writing text | None: the two references are plain text inside a paragraph |
| Existing reference scan | Two external publisher references; neither local clause reference is recognized |
| Current claim relationships | All eight claims have empty `target_ids` |
| Context export for R004/R005 | Includes the writing source in the full 6,853-character section, but no related claims or recognized local references |
| Native lookup given manually selected addresses | Exactly R004 and R005 are contained in the respective targets; neither R003 nor R007 matches |

The two external IEP references and eight LEA publisher references remain
`not_in_selected_source`. No external source bodies were supplied, and the trace
does not fabricate them. The LEA purpose text does not create a reference edge.
The two unrecognized IEP references are silently absent from the scan, rather
than explicitly refused local-reference rows.

The source writing paragraph contains ordinary text, not `<ref>` elements:

```xml
<ns0:p style="-uslm-lc:I14" class="indent3">A parent’s agreement under clause (i) and consent under clause (ii) shall be in writing.</ns0:p>
```

This distinguishes missing recognition from broken publisher-link resolution.
The RefSpec native edge reader reports two `refElementsSeen`, corresponding to
the two actual external references elsewhere in the source. Inspection of the
installed and sibling `citation_grammar` APIs found named-act-relative recognition,
but no callable general local-clause occurrence reader. This matches the existing
open R11 task; no new competing parser was introduced.

## What the manual address controls establish

`manual-address-controls.json` supplies the two exact target addresses after
manual source inspection. Existing `SourceIndex.target` resolves them with native
XML evidence and prepared-text coordinates. Containment of current claims' main
source spans produces one candidate per target: R004 and R005. The team definition
R003 and transition invitation R007 do not match.

This is an explicitly constructed lookup control, not automatic discovery or a
test on fresh documents. It establishes that the delivered source identities and
evidence machinery can perform this part of the work. It does not establish the
semantic relationship, completeness, or reader behavior on ambiguous labels.

## Additional connection boundaries

`context.export_context` follows outgoing references from its focus and existing
claim `target_ids`. It does not search for incoming, unrecognized citations in
other claims. Once recognition exists, showing a claim that refers to the focus
is a distinct, bounded integration; it must not silently label every incoming
reference as a qualification.

There is also an application representation constraint: `core.candidate` permits
qualification targets on condition, exception and appropriately linked exemption
candidates. R006 is currently a `requirement/must`, so adding `applies_to` directly
would not be a supported application update. Core's generic relationship records
are broader than this profile guard. Do not reclassify the writing requirement,
weaken the guard, duplicate its meaning, or invent a new schema just to make a
link fit. Navigation associations can remain separate while a source-supported
semantic representation is selected and tested.

## Next bounded work

1. Extend the owning RefSpec occurrence reader for a small declared set of local
   reference forms, starting with these literal clause references. Reuse its
   lexer/occurrence conventions. Do not reconstruct whole-document hierarchy.
2. Resolve recognized occurrences against Rulespec's verified native source
   index. A source identifier must be supported by the current native parent
   context; preserve ambiguity, absent targets and evidence. Include repeated
   Roman labels in other branches, external-target absence, quoted/example text,
   and unrelated neighboring rules as controls before broadening forms.
3. Map source targets to current claim evidence and expose referring claims as
   navigation candidates. Keep overlapping/compound claims and multiple matches
   visible; a citation is not automatically a `scope` or `exception` link.
4. Only then test whether a supported semantic association makes complete rules
   easier to use on fresh sources. Assess source support, standalone completeness
   and component roles separately. If a model is used, distinguish manually
   supplied correct associations from automatically discovered ones.

This closes the declared two-book, zero-call trace. The unmarked-reference reader
and consumer integration remain open; the failed confidence/narrative prompts
remain experimental. `scope_text` purpose cleanup also remains an independent
profile-guidance experiment, not a change justified by these lookup controls.

Receipts: [plan](PLAN.md), [trace script](trace.py), [summary](summary.json),
[manual native lookup controls](manual-address-controls.json), and the source
scans/context exports in `iep-1/` and `lea-1/`. `pretrace-pins.json` and
`runtime.json` record exact input and implementation identities.
