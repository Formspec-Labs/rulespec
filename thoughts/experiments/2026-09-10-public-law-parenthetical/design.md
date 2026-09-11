# Parenthetical public-law parser fix

Decision: Fix the real-source omission upstream in SpicySearch and verify the rebuilt wheel before using it in Rulespec's reference experiments.

Hypothesis: Allowing the explicit parenthetical abbreviation `(Pub. L.)` between the law label and its number recovers the frozen real-source occurrence with an exact span, without reading arbitrary parentheticals or malformed numbers as citations. Ordinary whitespace handling already works and remains unchanged.

Arms: Prior installed strict-mode wheel and direct import of the edited SpicySearch source, followed by the rebuilt wheel. Preserve prior experimental captures. No Rulespec grammar or production extraction changes.

Cases: The frozen real-source, additive-family, and broader-parser cases; owner-repository regression tests containing the full failed source passage plus alternate whitespace, optional No., Unicode-prefix span checks, unrelated parentheticals, incomplete numbers and fused suffixes. Label new controls before editing the parser. Run those tests red first. The frozen failed source is development data now, not a fresh benchmark.

Held constant: Baseline scan, five-family filter, source labels, normalization and output schema. One before/after comparison plus source-to-wheel equivalence; no model calls or timing claims. Stop after the targeted syntax fix, counterexample checks, package rebuild and frozen replay. Preserve failures and review any differences rather than relabeling cases.

Decision rule: The actual source omission must be reproduced before the fix and recovered after it with the full original source span; counterexamples and prior matches must retain expected behavior. The real-source gate must pass on its original labels, and broader/addivitve outputs must show no unrelated change. Review the changed query detector upstream, including why parenthetical recognition does not imply existence or applicability. A source-to-wheel mismatch blocks the local dependency update. No release, deployment or broad extraction rollout follows.
