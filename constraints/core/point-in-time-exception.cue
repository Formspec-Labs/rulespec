package rkaf

import "time"

// PointInTimeException (v0.1 §4.6).
//
// A lifecycle packet MAY include `pointInTimeExceptions[]`, each declaring an
// `evaluationAnchor` (from the EvaluationAnchor vocabulary), a scope
// description, and `retainsAssertion` / `retainsWorkProduct`. Consumers
// evaluate a dated assertion exception against a verified case date;
// they MUST refuse an unsupported anchor (behavior §4).
#PointInTimeException: {
	"@type":                  "rkaf:PointInTimeException"
	"rkaf:evaluationAnchor":  #EvaluationAnchor
	// A PIT exception MUST retain at least one of: an Assertion or a
	// WorkProduct. The disjunction lives in the hand-authored Pattern-C
	// shape `shapes/rkaf-shapes-pattern-c.ttl::PointInTimeExceptionRetainsShape`.
	// The CUE source uses optional fields because CUE cannot express an
	// "exactly-one-of-these-two" cardinality constraint that compiles
	// straight to a per-property JSON Schema; the invariant is L3 SHACL.
	"rkaf:retainsAssertion"?:   string // IRI of the retained Assertion
	"rkaf:retainsWorkProduct"?: string // IRI of the retained GeneratedWorkProduct
	"rkaf:exceptionScope"?:     string // additional conditions requiring human review
	"rkaf:anchorDateBefore"?:   time.Format("2006-01-02") // exclusive cutoff for the retained assertion
	"rkaf:successorAssertion"?: string // optional assertion selected on or after the cutoff
}
