# Preflight implementation checks

The first input-preparation attempt copied only document/run/rulebook JSON into
temporary workspaces. ReviewStore correctly rejected this incomplete copy: native
extractions require their original manifest and captured artifacts. No provider
calls occurred and no requests or labels had been frozen. Rebuild preparation
with the existing full-run copy helper, preserving the native manifest. Only the
incomplete generated preparation files were removed; original experiments remain
unchanged. This is a harness setup correction, not a model retry or changed label.

The second preparation attempt correctly opened the complete native run and
identified a real input difference: ReviewStore computes current link issues,
whereas the earlier raw-book packet used null. Record those differences and
compare every other source/claim field exactly. Keep actual current link status
in the integrated request. This bundle clarification is in PLAN.md before calls.
