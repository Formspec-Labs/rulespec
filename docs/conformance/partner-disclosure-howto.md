# Partner disclosure howto

A partner publishes what it claims by filing a conformance disclosure under
`conformance/partners/<name>.yaml`. Disclosure is **self-certified** — no
central authority pre-1.0; the falsifiability gate is the audit or reporter
run named in the file. Levels and their gates live in
[`spec/rkaf-conformance.md`](../spec/rkaf-conformance.md); the document shape
is [`conformance/self-certification.template.yaml`](../conformance/self-certification.template.yaml).

Two paths exist, and they never mix in one file.

## Path A — L0, vocabulary mapping of a non-JSON-LD carrier

Use this when the carrier is tabular (Parquet, SQL) or otherwise not JSON-LD
and you are mapping its columns to Rulespec terms.

1. **Author the mapping** in the carrier's own repository as one or more
   fenced `yaml rkaf-l0-mapping` blocks. Each block pins the contract digest
   and declares per-column `subject_type`, `term`, `direction`,
   `value_kind`, an identifier `transform` and executable `samples`.
   The worked example is the spicy-regs `rule_targets` mapping in its
   `docs/ontology.md`.
2. **Pin the contract digest** the mapping was written against:
   ```sh
   python3 tools/l0_mapping_audit.py --print-contract-version
   ```
   Copy that `sha256:…` into every block's `rulespec_version`.
3. **Audit the mapping**: `python3 tools/l0_mapping_audit.py <mapping.md>`.
   Fix every issue it names — a wrong term domain, an unregistered scheme,
   or a sample whose output does not match its transform all fail the gate.
4. **File the declaration** as `conformance/partners/<name>.yaml`:
   `declared_levels: [L0]`, the same `rulespec_version` digest, an immutable
   `test_corpus_version`, `carrier_mapping` pointing at the published mapping
   file (resolved relative to this repository root or the YAML's directory),
   `terms_used` equal to the unique set of mapped term IRIs, and
   `results: {L0: pass}`. **Omit `adoption_depth`** — Appendix D defines no
   vocabulary-only depth. Optionally record machine-legible scope carve-outs
   as `excluded_terms` / `excluded_tables`; a carve-out in `notes` prose is
   invisible to the audit and reads the same whether the scope grew or
   shrank.
5. **Re-run the audit with no arguments** — it discovers every partner YAML
   and fails the run on any issue, so a declaration cannot rot silently.

## Path B — L1–L4, JSON-LD implementation

Use this for an implementation that parses and validates Rulespec JSON-LD.

1. **Run the reporter against the fixture corpus**:
   ```sh
   python3 tools/conformance_report.py --level L1 --level L2 --level L3
   ```
   L4 additionally runs the behavior fixtures through the runtime CLI
   (`rkaf-runtime-cli`); see `spec/rkaf-conformance.md` §4 and
   `spec/rkaf-behavior.md`.
2. **Emit the document**:
   ```sh
   python3 tools/conformance_report.py --self-certify \
     --source-revision <40-character-tested-commit> \
     > conformance/partners/<name>.yaml
   ```
   Fill any `not-claimed` result honestly; `pass` means every positive
   fixture passed and every negative failed as expected at that level.
3. **Record the tested identity**: `source_revision` must name the exact
   commit or tag the fixtures were tested against; a local uncommitted
   candidate may use `null` but cannot support a published claim.
4. **Keep `notes` explicit** about intentional gaps and documented
   divergences. A divergence documented in `notes` is a decision; an
   undocumented one is a defect nobody can tell from a release blocker.

## Both paths

- Levels are cumulative for L1–L4 (declaring L3 implies L2 + L1); L0 is
  declared alone.
- A disclosure that names a level it does not actually gate on is worse than
  `not-claimed`: the audits exist so that a claim costs a failing run, not a
  promise.
