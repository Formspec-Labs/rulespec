#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
caller="$PWD"
out="${1:-$repo/dist/case-evaluator}"
case "$out" in /*) ;; *) out="$caller/$out" ;; esac
cd "$repo"

version="$(cat VERSION)"
host="$(rustc -vV | sed -n 's/^host: //p')"
bundle="rulespec-case-evaluator-$version-$host"
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$repo/crates/target}"
cargo build --locked --release --target "$host" --manifest-path crates/Cargo.toml -p rkaf-runtime-cli

checksum() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$@"
  else
    shasum -a 256 "$@"
  fi
}

stage="$(mktemp -d)"
trap 'rm -rf -- "$stage"' EXIT
install="$stage/$bundle"
mkdir -p "$install/bin" "$install/examples/case-date/sources" "$install/fixtures/behavior" "$install/context"
cp "$CARGO_TARGET_DIR/$host/release/rulespec-case-review" "$CARGO_TARGET_DIR/$host/release/rkaf-behavior-validate" "$install/bin/"
cp fixtures/behavior/point-in-time-filing-date.jsonld "$install/fixtures/behavior/"
cp context/rkaf-context.jsonld "$install/context/"
cp examples/case-date/{cases.csv,filing-evidence.csv} "$install/examples/case-date/"
cp examples/case-date/sources/{404-1527.xml,404-1520c.xml,SHA256SUMS} "$install/examples/case-date/sources/"
cp examples/case-date/QUICKSTART.md "$install/README.md"
cp LICENSE-CODE LICENSE-SPEC VERSION "$install/"
(
  cd "$install/examples/case-date/sources"
  checksum -c SHA256SUMS >&2
)
"$install/bin/rkaf-behavior-validate" "$install/fixtures/behavior/point-in-time-filing-date.jsonld" >&2

mkdir -p "$out"
tar -C "$stage" -czf "$stage/$bundle.tar.gz" "$bundle"
(
  cd "$stage"
  checksum "$bundle.tar.gz" > "$bundle.tar.gz.sha256"
)
mv "$stage/$bundle.tar.gz" "$stage/$bundle.tar.gz.sha256" "$out/"
printf '%s\n' "$out/$bundle.tar.gz"
