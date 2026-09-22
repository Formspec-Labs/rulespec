package rkaf

import "list"

// A minimal, self-contained profile for the projector-parity derive gate.
// Kept small on purpose: the gate pins byte-identical derive output, so every
// field this file states is one the compiler must keep emitting or the gate
// fails. The shapes mirror constraints/core/artifact.cue's conventions.

#ArtifactIdentifierScheme: "rkaf:urn-persistent" | "rkaf:partner-defined"

#ExampleArtifact: artifact={
	"@type":                      "rkaf:Artifact"
	"rkaf:hasArtifactIdentifier": [...string] & list.MinItems(1)
	"rkaf:artifactIdentifierScheme": [...#ArtifactIdentifierScheme] & list.MinItems(1)
	"rkaf:hasContentDigest"?: string & =~"^sha256:[0-9a-f]{64}$"
	"dcterms:format"?: string & =~"^[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+(?:\\s*;.*)?$"
}
