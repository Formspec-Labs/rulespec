@experiment(explicitopen)

package documentunderstanding

import (
	"list"
	"strings"
	core "rulespec.invalid/core:rkaf"
)

// Shared field types and extraction guidance. The records below select their
// required fields and add local evidence constraints without repeating meaning.

#CommonKinds: ["requirement", "permission", "prohibition", "threshold", "definition", "condition", "exception", "recommendation", "exemption", "statement"]

// Semantic kind; must agree with modality and relationship role. Classify the complete meaning, including headings' inherited context. A recommendation remains recommendation; descriptive possibility is statement. Conditions and exceptions are separate qualifications of a baseline; retain the baseline itself. Definitions and useful descriptive explanations also deserve units.
#Kind: or(list.Concat([#CommonKinds, ["authority"]])) @title("Kind") @sortEnum()

// Exact source passages defining the governing conditions, including parent lead-ins outside the main quote. Provide every source passage needed to substantiate scope_text. Parent cases may appear elsewhere in the supplied focus or context. Every item must be contiguous and exact; use separate items for separate passages.
#ScopeQuotes: [...string] @title("Scope quotes")

// ALL source-supported conditions governing this unit, including inherited parent cases and timing; do not transfer neighboring branch scope. Combine all governing conditions for this unit, including inherited lead-ins and antecedents outside its main quotation. Preserve alternative branches and timing boundaries. A split child must still describe the complete case in which it applies; do not import conditions from neighboring independent cases.
#ScopeText: string @title("Scope text")

// Exact explanatory passages that aid interpretation without asserting conditions. Use for explanations and background that help interpret this unit without turning them into prerequisites. Useful descriptive or advisory meaning should also be retained as a unit when independently substantive.
#ContextQuotes: [...string] @title("Context quotes")

// Exact support for modal force; preserve generally, might, should and negation. Include qualifiers that establish the force, such as generally or might. A neighboring must cannot supply the force of a separate recommendation or description. A companion condition can have not_stated while its baseline retains must or should. For factual not_stated meaning, leave this empty rather than quoting a bare copula such as is; quote only wording that establishes modal force.
#ModalityQuote: string @title("Modality quote")

// Normative force: must, should, permission may, prohibition must_not, exemption not_required, descriptive possible, not_stated or uncertain. Use should for recommendations, may for permission, possible for descriptive may/might, and not_required only for an explicit absence of duty. not_stated fits factual definitions and qualifications with no independent normative force. An exception to a recommendation does not itself declare absence of a legal duty. Generally is not universally.
#Modality: "must" | "should" | "may" | "must_not" | "not_required" | "possible" | "not_stated" | "uncertain" @title("Modality")

// Exact source passages supporting EVERY leaf option and its qualifications, not just the list introduction. One passage may support several options; separate strings or substrings for each option are not required. Retain every option, nested grouping and qualification explicitly in the meaning, including choice_text when applicable. Evidence granularity does not determine whether alternatives are complete: a shared passage is sufficient evidence, but evidence alone does not restore an option or qualification omitted from the meaning. A grouped faithful rule can contain all options without creating a separate duty for each option.
#AlternativeQuotes: [...string] @title("Alternative quotes")

// One exact contiguous source passage supporting choice/grouping; never join separate phrases with invented separators. Select a contiguous passage that actually supports the grouping; an entire short list can be appropriate. Do not splice disjoint quotations or invent separators inside the quote.
#ChoiceQuote: string @title("Choice quote")

// Complete source choice/grouping in words, including nested AND/OR and qualifications. Explain the complete choice and its nesting: all required elements, independently sufficient options, one-or-more groups, and alternatives inside an option. Preserve each option's qualifiers. Do not equate a grammatical conjunction in a category description with a requirement that both categories hold.
#ChoiceText: string @title("Choice text")

// Verbatim source wording retaining AND/OR, thresholds, units, dates and negation; no invented executable logic. Retain the source's complete logical wording when relevant. Do not uppercase a conjunction to imply executable Boolean logic. A list of independent categories need not require simultaneous membership in all categories. Preserve exact comparators, units and reference dates.
#LogicText: string @title("Logic text")

// Exact source support for actor, including antecedent if needed. Copy a contiguous passage supporting the actor assignment. An inherited actor may be supported in supplied context. Empty actor has empty support; a matching word alone does not establish its semantic role.
#ActorQuote: string @title("Actor quote")

// Source-supported responsible person or entity; empty if unstated. If the source addresses you without naming a role, retain you rather than inventing a job title. Resolve a pronoun only when the source establishes its antecedent. Do not invent a duty bearer for an impersonal requirement, definition or factual statement. Do not substitute a neighboring actor from a different branch.
#Actor: string @title("Actor")

// Exact source support for action. Copy source wording that supports this action, preserving its direction and negation. Do not rewrite the quoted passage to match a normalized action label.
#ActionQuote: string @title("Action quote")

// Source-supported action; empty when inapplicable or unstated. Represent the action actually attributed to the actor. Distinguish taking an action, being permitted to take it, and an event merely being possible; normative force is recorded in modality.
#Action: string @title("Action")

// Exact source support for object. Copy source wording supporting the chosen object and its option grouping. Do not convert a contextual form, date or actor into the object simply because those words occur nearby.
#ObjectQuote: string @title("Object quote")

// What the action concerns; preserve option grouping; empty if unstated. Identify the semantic object of the action, not merely a nearby quoted noun. A form named in a timing condition is not necessarily what the action changes. Leave uncertain components empty while retaining the complete source meaning.
#Object: string @title("Object")

// Exact source support for jurisdiction; empty when unstated. Quote the supplied source's territorial wording. When there is no explicit territorial scope, leave both jurisdiction fields empty.
#JurisdictionQuote: string @title("Jurisdiction quote")

// Territorial scope only when explicitly supported in supplied text; never infer from URL. Use only territory explicitly provided by source wording. The document title, institution or web address is not evidence for an inferred territorial applicability claim.
#Jurisdiction: string @title("Jurisdiction")

// A condition/exception's relationship to its baseline; none for other kinds. The source decides which baseline a qualification governs. Contextual proximity alone does not. An even-though or despite clause may preserve a duty rather than remove it. The qualification must retain the baseline's scope and the limits of the modification. When a locally stated rule has an explicit exception, retain the complete baseline with its original kind and relation none, and also emit a separate exception unit linked to it. Do not turn the baseline itself into an exception or strip the exception from its meaning. A conditional permission does not by itself cancel a neighboring duty.
#Relation: "none" | "scope" | "prerequisite" | "trigger" | "exception" @title("Relation")

// Exact main-rule quotations targeted by this condition or exception; never summaries or invented remote text. Select the actual baseline whose meaning changes, preserving its complete scope. Never target an unrelated rule just because its quotation is exact. Match the complete main quotation of an emitted baseline unit exactly, including punctuation; a substring may not identify that unit. Leave remote targets unresolved rather than supplying text absent from the request.
#AppliesTo: [...string] @title("Applies to")

// Source section labels for cross-references, including unresolved remote targets. Keep source cross-reference labels even when their content is unavailable. Preserve the topic of each reference in the unit's meaning; a nearby reference is not a license to infer the missing rule.
#References: [...string] @title("References")

// Complete meaning of this unit, preserving governing scope, qualifications and modal force. Make this a self-contained reading of the source. Include every governing parent case, time limit, negation, exception and qualification needed to avoid broadening or narrowing its meaning. A long supporting quote does not compensate for omitted meaning in this field. Keep descriptive and advisory material at its source force.
#Summary: string @title("Summary")

#NonemptyText: string & strings.MinRunes(1)
#EvidenceQuotes: [...#NonemptyText] & list.UniqueItems()

// A source-supported topic, not the identity of an actor or object. Reuse the
// same label and definition for the same sense. Different senses need different
// definitions. Local discovery does not establish RefSpec registration.
#ConceptTag: {
    label!: string
    definition!: string
    // Exact passage supporting this topic's relevance and meaning.
    quote!: string
    // Primary = central topic; substantive = discussed; mention = passing;
    // contextual = background. This is topical association, not entity identity.
    role!: core.#ConceptAssignmentPredicate
}

// Who the SOURCE attributes this statement to, separately from who must act.
// Leave the collection empty when attribution was not established. NotStated
// records an assessed absence, supported by the examined passage; it is not a
// model confidence score. The quotation must establish attribution of THIS
// statement, not merely mention an institution. "Under Agency guidance" or a
// citation identifies a reference, not necessarily the party asserting the claim.
// Do not transfer an agency mentioned in another paragraph to this statement.
// An issuer attribution needs supplied text establishing issuer and coverage.
// Never infer the issuer from a URL or the model. Empty is better than an
// unsupported attribution; it does not make the underlying rule uncertain.
#Claimant: {
    text!: string
    quote!: string
    attribution!: core.#ClaimantAttribution
}

// One source-supported value for later workflow preparation. Preserve the
// exact passage, including comparator, unit and reference event. Give the XSD
// lexical value only when normalization is unambiguous (e.g. one year -> P1Y).
// Do not convert years to days or invent a calendar date for a relative limit.
#TypedValue: {
    name!: string
    quote!: string
    value!: string
    datatype!: core.#ValueDatatype
    // Source wording, e.g. more than, at least, no later than; empty if absent.
    comparator!: string
    // Exact unit wording from quote, including singular/plural; empty if absent.
    unit!: string
    // Exact source phrase in quote naming the reference event; do not paraphrase.
    // This is the event from which a relative limit is measured; empty if absent.
    anchor!: string
}

// An explicit period during which this rule is in force. This is not a filing
// deadline, age threshold or passport validity duration. Only normalize fully
// specified timestamps; preserve date-only effectivity as a typed xsd:date
// value instead of inventing a time or timezone. Empty end means open-ended.
#Period: {
    quote!: string
    start!: core.#EffectivePeriod["rkaf:effectivePeriodStart"]
    end!: core.#EffectivePeriod["rkaf:effectivePeriodStart"]
}

// Interpret this unit using only its source and supplied context. Keep evidence, normative force, conditions, alternatives and meaning mutually consistent. Empty values preserve uncertainty rather than inventing missing details.
#UnitMeaning: {
	@title("Complete unit meaning and component evidence")

	concepts!: [...#ConceptTag]
	claimants!: [...#Claimant]
	typed_values!: [...#TypedValue]
	effective_periods!: [...#Period]
	kind!:               #Kind
	scope_quotes!:       #ScopeQuotes
	scope_text!:         #ScopeText
	context_quotes!:     #ContextQuotes
	modality_quote!:     #ModalityQuote
	modality!:           #Modality
	alternative_quotes!: #AlternativeQuotes
	choice_quote!:       #ChoiceQuote
	choice_text!:        #ChoiceText
	logic_text!:         #LogicText
	actor_quote!:        #ActorQuote
	actor!:              #Actor
	action_quote!:       #ActionQuote
	action!:             #Action
	object_quote!:       #ObjectQuote
	object!:             #Object
	jurisdiction_quote!: #JurisdictionQuote
	jurisdiction!:       #Jurisdiction
	relation!:           #Relation
	applies_to!:         #AppliesTo
	references!:         #References
	summary!:            #Summary
}

// Select a supplied focus (F000) or context (C000) passage, or a contiguous
// inclusive range such as F003:F009. These locate exact source text; they do
// not prove that the text supports the proposed meaning. Never invent IDs.
#SourceRef: string @title("Source passage reference")

#FocusSourceRef: string & =~"^F[0-9]{3,}(:F[0-9]{3,})?$"
#InventoryKind: or(list.Concat([#CommonKinds, ["alternative", "background"]]))

// Source-first meanings to check against a draft. Several meanings may share
// one source passage; selecting a passage does not prove complete enumeration.
#InventoryResponse: {
    units!: [...{
        // Select a focus passage or contiguous focus range supporting this meaning.
        quote_ref!: #FocusSourceRef
        // Select substantive governing lead-ins from focus or context passages,
        // not bare section labels. Use [] when no additional scope is needed.
        scope_refs!: [...#SourceRef]
        kind!: #InventoryKind @sortEnum()
        // Complete source-supported meaning, including inherited conditions,
        // timing, AND/OR, negation and modal distinctions. Evidence alone does
        // not restore an omitted condition, alternative or qualification.
        meaning!: string & strings.MinRunes(1)
    }]
}

// Complete meanings first. Preserve conditions and exceptions in every split
// statement and its scope; this pass does not create relationship records.
#FirstMeaning: {
    kind!: #Kind
    // Select every passage needed for inherited conditions, cases and timing.
    scope_quotes!: [...#SourceRef]
    scope_text!: #ScopeText
    // Select explanatory support without turning it into prerequisites.
    context_quotes!: [...#SourceRef]
    modality_quote!: #ModalityQuote
    modality!: #Modality
    // Select passages supporting EVERY leaf option with its full qualifications
    // and nested groups. One passage ID may support several options; select it
    // once. Preserve each option and qualification explicitly in choice_text
    // and statement; a shared evidence passage does not restore omitted meaning.
    alternative_quotes!: [...#SourceRef]
    // Select the complete choice/grouping passage or range; empty if absent.
    choice_quote!: #SourceRef
    choice_text!: #ChoiceText
    // Select a passage/range retaining complete AND/OR, comparators, units,
    // reference events and negation. Empty if inapplicable. The application
    // copies the original wording; never write or splice logical text here.
    logic_quote!: #SourceRef
    references!: #References
    statement!: #Summary @title("Source-faithful statement")
}

// One independently referenceable source meaning. Separate distinct actions when useful, while preserving their inherited scope and connected qualifications. Overlapping main quotations are allowed. Retain substantive notes and cautions even when they impose no duty, including explanations that one event or document date does not establish the date of its underlying evidence. Keep these as descriptive statements at their source force.
#SemanticUnit: {
	@title("One semantic unit")

	// Select ONE focus passage or contiguous focus range. Never comma-separate
	// disconnected passages. Select the main clause here and its remote lead-in
	// in scope_quotes; preserve the full governing case in statement and scope.
	// Context is support only.
	unit!:            #FocusSourceRef @title("One focus passage or contiguous range")
	unit_attributes!: #FirstMeaning
}

// Retain independently useful rules, definitions, recommendations, permissions, exemptions, qualifications and descriptive statements with exact evidence. Empty collections express absent supported content, never proof of completeness.
#ExtractionResponse: {
	@title("Source-grounded document meanings")
	extractions!: [...#SemanticUnit]
}

// Local candidates require nonempty evidence; unstated components remain optional.
// Shared field types are narrowed here; empty model placeholders may be rejected.
#Candidate: {
	concepts?: [...#ConceptTag]
	claimants?: [...#Claimant]
	typed_values?: [...#TypedValue]
	effective_periods?: [...#Period]
	kind!:               #Kind
	summary!:            #Summary & #NonemptyText
	actor!:              #Actor
	quote!:              #NonemptyText
	action?:             #Action
	object?:             #Object
	actor_quote?:        #ActorQuote
	action_quote?:       #ActionQuote
	object_quote?:       #ObjectQuote
	logic_text?:         #LogicText
	relation?:           #Relation
	section_id?:         string
	window_id?:          string
	modality?:           #Modality
	modality_quote?:     #ModalityQuote
	scope_text?:         #ScopeText
	choice_text?:        #ChoiceText
	choice_quote?:       #ChoiceQuote
	jurisdiction?:       #Jurisdiction
	jurisdiction_quote?: #JurisdictionQuote
	scope_quotes?:       #ScopeQuotes & #EvidenceQuotes
	context_quotes?:     #ContextQuotes & #EvidenceQuotes
	alternative_quotes?: #AlternativeQuotes & #EvidenceQuotes
	start?:              null | (int & >=0)
	end?:                null | (int & >=0)
	applies_to?: #AppliesTo & [...#NonemptyText]
	references?: #References & [...#NonemptyText]
}
