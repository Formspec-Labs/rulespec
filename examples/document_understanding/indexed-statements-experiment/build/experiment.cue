@experiment(explicitopen)

package trial

import profile "rulespec.invalid/profile:documentunderstanding"

// A person or role actually named or addressed in the supplied text. Reuse its
// ID consistently. A topic, institution citation or document is not an actor.
// Preserve you when its professional title is not established in supplied text.
#Role: {
    id!: string
    label!: string
    // Exact professional title if established; empty when unstated. Never infer
    // processor/adjudicator from the document topic or from outside knowledge.
    title!: string
    // Exact alternative names or pronouns that this source establishes for this
    // same role. Empty if unresolved; two uses of you need not share a role.
    aliases!: [...string]
    // Exact naming passage. Include the antecedent when resolving a pronoun.
    quote!: string
    // Exact evidence establishing where this role/title applies; empty if absent.
    scope_quote!: string
}

// One cited reference in supplied text. Index all distinct citation labels,
// including remote ones. Repeated occurrences can share an ID. This records a
// mention, not the referenced content, an issuer, or an assertion of authority.
#Citation: {
    id!: string
    label!: string
    quote!: string
}

// Shared topic identity, distinct from actor identity and citation identity.
// Reuse a concept for the same sense, without turning every rule into a topic.
#Concept: {
    id!: string
    topic!: profile.#ConceptTag
}

#Meaning: {
    // Index role ID, or empty if no responsible actor is established. actor and
    // actor_quote must agree with that role. Use no unsupported job titles in
    // statement, even if the structured actor remains the source pronoun.
    role_ref!: string
    concept_refs!: [...string]
    citation_refs!: [...string]
    // Existing CUE definitions supply all meaning, evidence and Core components.
    claimants!: [...profile.#Claimant]
    typed_values!: [...profile.#TypedValue]
    effective_periods!: [...profile.#Period]
    kind!: profile.#Kind
    scope_quotes!: profile.#ScopeQuotes
    scope_text!: profile.#ScopeText
    context_quotes!: profile.#ContextQuotes
    modality_quote!: profile.#ModalityQuote
    modality!: profile.#Modality
    alternative_quotes!: profile.#AlternativeQuotes
    choice_quote!: profile.#ChoiceQuote
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
    relation!: profile.#Relation
    applies_to!: profile.#AppliesTo
    // A direct, natural statement of what the source says, not commentary about
    // a document. Preserve source terms and may/must/should/generally/negation.
    // Include every governing condition and exception, including inherited ones.
    // Say X means Y rather than Defines X as Y; avoid This rule states and
    // Requirement for. Do not add a professional title or imply extra duties.
    // A topic label is not a substitute for the statement. Retain useful
    // explanations as statements when independently meaningful.
    statement!: string @title("Source-faithful statement")
}

// Examine lexical signals as prompts to inspect meaning, not automatic legal
// operators: unless/except/other than (possible exception); if/when/provided
// that/only if (condition); must/shall/should/may/not required (force);
// either/one or more/all of (grouping); within/before/after/at least (limits);
// means/refers to/defined as (definition). May can express possibility, not
// permission. Not required is not prohibited. Preserve generally and might.
// Account for these signals in each statement's actual meaning, not only its
// evidence quotes. For an explicit local exception, retain the qualified
// baseline and emit a separate exception linked to its exact main quotation.
// Determine its target from meaning, not proximity. Do not invent remote rules.
// Shared indexes come first so later statements use consistent names and refs.
#Response: {
    roles!: [...#Role]
    citations!: [...#Citation]
    concepts!: [...#Concept]
    extractions!: [...{
        unit!: string @title("Exact main quotation")
        unit_attributes!: #Meaning
    }]
}
