# Cost accounting before choosing an optimization

Read the 16 original captures from `2026-09-10-exemption-end-to-end`; excluded
copied workspaces, base runs, frozen snapshots and replay outputs. No provider calls.
The hypothesis/decision note was saved before this accounting in
[the refinement efficiency plan](../../plans/2026-09-10-refinement-efficiency-hypotheses.md).

| Stage group | Reported total tokens | Share of full workflow |
| --- | ---: | ---: |
| Extraction | 12,140 | 4.9% |
| Initial and final audits | 86,114 | 35.1% |
| Recovery (both responses empty) | 41,635 | 16.9% |
| Relationship proposals and challenges | 105,794 | 43.1% |
| Total | 245,683 | 100% |

Prior audit judgments occupy 32.9% of the serialized model-facing relationship
packets, compared with 3.8% for the focus source itself. Claim objects contain
48.2%, including the statements and evidence. This makes repeated evidence and
audit commentary distinct hypotheses. It does not show which can be removed
without harming the model's decisions.

Shrinking complete link-edit responses alone has a limited direct saving: the
relationship proposal answers total 4,695 tokens, less than 2% of the complete
workflow. Effects on model reasoning, refusal rate or later prompts are unmeasured.

All stage totals match the saved full-run usage. Packet rendering matches the
actual captured prompts. Missing thinking usage remains null in per-call records;
aggregate fields include a missing count. Serialized characters are not token
estimates. Costs of downstream stages would change if earlier stages were removed,
so this table must not be presented as a tested cheaper execution path.

Run with:

```sh
PYTHONPATH=packages/rulespec-extrapolator/src .tools/document-poc-venv/bin/python thoughts/experiments/2026-09-10-refinement-cost-accounting/account.py
```

See [results.json](results.json) for request/response hashes, per-stage usage and
packet fields. No production changes, commits or live optimization tests.
