#!/usr/bin/env bash
set -euo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
caller="$PWD"
out="${1:-$repo/dist/case-evaluator}"
case "$out" in /*) ;; *) out="$caller/$out" ;; esac
cd "$repo"

version="$(cat VERSION)"
host="$(rustc -vV | sed -n 's/^host: //p')"
revision="$(git rev-parse --short=12 HEAD)"
bundle="rulespec-case-evaluator-$version-$host-g$revision"
archive="$bundle.tar.gz"

if ! git diff --quiet HEAD --; then
  printf '%s\n' 'Commit the release inputs before packaging the evaluator.' >&2
  exit 1
fi

checksum() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$@"
  else
    shasum -a 256 "$@"
  fi
}

mkdir -p "$out"
if [[ -e "$out/$archive" || -e "$out/$archive.sha256" ]]; then
  (cd "$out" && checksum -c "$archive.sha256") >&2
  printf '%s\n' "$out/$archive"
  exit 0
fi

export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$repo/crates/target}"
PYTHON="${PYTHON:-python3}" bash tools/compile_all.sh --runtime-schemas
cargo build --locked --release --target "$host" --manifest-path crates/Cargo.toml -p rkaf-runtime-cli -p rkaf-validate-cli

stage="$(mktemp -d "$out/.case-evaluator.XXXXXX")"
trap 'rm -rf -- "$stage"' EXIT
install="$stage/$bundle"
mkdir -p "$install/bin" "$install/examples/case-date/sources" "$install/fixtures/behavior" "$install/context"
cp "$CARGO_TARGET_DIR/$host/release/"{rulespec-case-review,rkaf-behavior-validate,rkaf-validate} "$install/bin/"
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

# macOS tar otherwise adds AppleDouble files containing the build host's extended attributes.
COPYFILE_DISABLE=1 tar -C "$stage" -czf "$stage/$archive" "$bundle"
(
  cd "$stage"
  checksum "$archive" > "$archive.sha256"
)
# Hard links refuse to replace an existing archive, including concurrent builds.
ln "$stage/$archive" "$out/$archive"
ln "$stage/$archive.sha256" "$out/$archive.sha256"
printf '%s\n' "$out/$archive"
