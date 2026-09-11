# Local commit checkpoint

The verified reader, schema and extraction changes are now committed locally.
The commit containing this note separately preserves the research, including raw
captures, failed attempts, counterexamples and the remaining task list.

| Repository | Commit | Change |
| --- | --- | --- |
| SpicySearch | `10824d44ab31260e081b66b8da54678132b9ffe0` | Opt-in strict citation readers and parenthetical public-law recognition |
| RefSpec | `31ca84c22f6dcab518bb05bc5653cd350538bc8d` | Citation occurrences, qualifiers, source-credit evidence and ambiguous act identities |
| RefSpec | `48617754c1f08dbfcd21463aa9d957719127883b` | Shared publisher XML text and reference reader |
| Rulespec | `b358244d43f7d24fc8751423c40c0e006ddfc5b7` | XPath selector shape, generated files and plain-string validation |
| Rulespec | `dfd900597530e9b030f96ae732f99b5025182cd8` | Extraction retention, reader integration, review boundaries and runtime capture |

Before committing, source files in all three Python packages matched their
previously verified wheels. The extractor's two bundled license files were checked
against the build's declared repository-root inputs; the first comparison had
incorrectly looked for them under the package source directory. No production
code changed to resolve that comparison error. The retention and reader-capture
manifests still match their original evidence. Staging used exact inspected paths,
with checks for intervening branch, index or file changes.
The existing ignore rules keep local review databases, environments and wheels
outside Git. They remain on disk; JSON review exports and wheel identities are
committed. Those retained database files are needed to reproduce every file in
the original local delivery manifests.

No new model calls or test suites were run for this commit-only step. The latest
application test evidence remains the [559-test source and installed checkpoint](../experiments/2026-09-11-reader-runtime-capture/README.md).
The commits preserve those tested source bytes. Installed wheels, published
packages and deployed systems remain distinct: no push, publication or deployment
occurred here.

Qualified USC integration remains open. Its [29 prepared cases](../experiments/2026-09-11-qualified-usc-comparison/README.md)
have no parser results from the first attempt, which stopped at the host-load
gate. The broader reuse goal remains active; committing the delivered work does
not complete the remaining [R1–R26 backlog](../plans/2026-09-10-reference-integration-task-list.md).
