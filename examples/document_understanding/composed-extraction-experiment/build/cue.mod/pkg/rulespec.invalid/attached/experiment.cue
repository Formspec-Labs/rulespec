@experiment(explicitopen)
package trial

import profile "rulespec.invalid/profile:documentunderstanding"

// A supplied passage ID, such as P003, or a contiguous inclusive range P003:P009.
// Select actual source evidence; never invent IDs or copy/rewrite its text here.
// Ranges may span an introductory rule and its complete list of alternatives.
// IDs identify text locations, not meanings. A broad passage does not prove
// every claim about it. Keep the statement specific even when evidence is broad.
#SourceRef: string @title("Source passage reference")

// One locally supported qualification OF THE CONTAINING STATEMENT. The nesting
// identifies its target; do not repeat the baseline or its quote to create a link.
// A conditional permission does not cancel another duty merely by being nearby.
#Qualification: {
    // scope, prerequisite, trigger or exception. An unless/except clause may be
    // an exception; assess the meaning and limits rather than the keyword alone.
    relation!: profile.#Relation
    // State the complete qualification, preserving the parent's case and limits.
    // An exception to should does not erase a legal duty. Never strengthen force.
    statement!: profile.#Summary
    // Source passages establishing this qualification, including inherited cases.
    evidence!: [...#SourceRef]
    references!: profile.#References
}

#Meaning: {
    concepts!: [...profile.#ConceptTag]
    claimants!: [...profile.#Claimant]
    typed_values!: [...profile.#TypedValue]
    effective_periods!: [...profile.#Period]
    // Baseline kind only; put condition/exception records in qualifications.
    kind!: profile.#Kind
    // Select all governing source passages; do not infer scope from list nesting.
    scope_quotes!: [...#SourceRef]
    scope_text!: profile.#ScopeText
    context_quotes!: [...#SourceRef]
    modality_quote!: profile.#ModalityQuote
    modality!: profile.#Modality
    // Every leaf option's passage ID, retaining its source qualifiers. A range
    // may include a parent category and both children. Do not rewrite list text.
    alternative_quotes!: [...#SourceRef]
    // Source passage/range for complete grouping, or empty if no choice applies.
    choice_quote!: #SourceRef
    choice_text!: profile.#ChoiceText
    logic_text!: profile.#LogicText
    actor_quote!: profile.#ActorQuote
    actor!: profile.#Actor
    action_quote!: profile.#ActionQuote
    action!: profile.#Action
    object_quote!: profile.#ObjectQuote
    object!: profile.#Object
    jurisdiction_quote!: profile.#JurisdictionQuote
    jurisdiction!: profile.#Jurisdiction
    references!: profile.#References
    // Locally explicit conditions and exceptions belong here. Code constructs
    // their Core records and links to this statement. No extra target IDs needed.
    // Remote-only exceptions stay as references and in the complete statement;
    // do not invent unavailable exception content as a local qualification.
    qualifications!: [...#Qualification]
    // Write a direct natural statement, preserving all governing scope, timing,
    // qualifications and force. Include exceptions here AS WELL AS in their
    // qualification entries, so a reader of this statement gets the whole rule.
    // Useful explanatory statements also deserve units. Say X means Y, not
    // Defines X as Y. Keep you unless its professional role is actually named.
    statement!: string @title("Source-faithful statement")
}

// Extract source-supported statements with attached qualifications. Inspect
// unless/except/other than, if/when/provided that/only if, must/shall/should/may/
// not required, either/one or more/all of, within/before/after/at least, and
// means/refers to/defined as. These are cues, not automatic legal operators.
// Preserve descriptive might and generally. Do not promote should to must.
// The supplied paragraph structure locates evidence; it does not establish scope.
#Response: {
    extractions!: [...{
        unit!: #SourceRef
        unit_attributes!: #Meaning
    }]
}
