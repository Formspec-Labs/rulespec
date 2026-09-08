@experiment(explicitopen)
package composed

import (
    profile "rulespec.invalid/profile:documentunderstanding"
    attached "rulespec.invalid/attached:trial"
)

// Complete meanings first. Conditions and exceptions remain in the statement
// and scope even though this pass does not create their relationship records.
#FirstMeaning: {
    kind!: profile.#Kind
    // Select every source passage establishing inherited cases and timing.
    scope_quotes!: [...attached.#SourceRef]
    scope_text!: profile.#ScopeText
    // Explanations aid interpretation without becoming applicability conditions.
    context_quotes!: [...attached.#SourceRef]
    modality_quote!: profile.#ModalityQuote
    modality!: profile.#Modality
    // Every leaf option with its complete qualifying wording; preserve all groups.
    alternative_quotes!: [...attached.#SourceRef]
    // A contiguous passage/range supporting the complete choice, or empty.
    choice_quote!: attached.#SourceRef
    choice_text!: profile.#ChoiceText
    logic_text!: profile.#LogicText
    references!: profile.#References
    statement!: profile.#Summary @title("Source-faithful statement")
}

// Capture independently referenceable complete meanings, including substantive
// explanations. Must, should, may and might retain their distinct source force.
#MeaningResponse: {
    extractions!: [...{
        unit!: attached.#SourceRef
        unit_attributes!: #FirstMeaning
    }]
}

// Add qualifications to existing statements without rewriting those statements.
// A supplied statement identifier locates the target; source passages establish
// whether the relationship is supported. Empty qualifications are appropriate.
#RelationshipResponse: {
    extractions!: [...{
        // Copy the supplied B000-style identifier exactly; never invent a target.
        unit!: string @title("Existing statement identifier")
        unit_attributes!: {
            qualifications!: [...attached.#Qualification]
        }
    }]
}
