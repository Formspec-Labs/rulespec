#!/usr/bin/env bash
# Install the CUE version .tool-versions pins into DEST (default: this repository's .tools/), after
# checking the release archive's sha256 against tools/cue-checksums.txt. Re-runnable.
# Usage: tools/install-cue.sh [DEST]
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${1:-$ROOT/.tools}"
VERSION="$(awk '$1 == "cue" { print $2 }' "$ROOT/.tool-versions")"
[ -n "$VERSION" ] || { echo "No cue entry in $ROOT/.tool-versions" >&2; exit 1; }
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
case "$OS" in
  darwin|linux) PLAT="$OS" ;;
  *) echo "Unsupported OS: $OS" >&2; exit 1 ;;
esac
case "$(uname -m)" in
  arm64|aarch64) ARCH_TAG="arm64" ;;
  x86_64|amd64)  ARCH_TAG="amd64" ;;
  *) echo "Unsupported arch: $(uname -m)" >&2; exit 1 ;;
esac
ARCHIVE="cue_v${VERSION}_${PLAT}_${ARCH_TAG}.tar.gz"
EXPECTED="$(awk -v archive="$ARCHIVE" '$2 == archive { print $1 }' "$ROOT/tools/cue-checksums.txt")"
[ -n "$EXPECTED" ] || { echo "No sha256 for $ARCHIVE in tools/cue-checksums.txt; add it from the release's checksums.txt" >&2; exit 1; }
WORK="$(mktemp -d)"
trap 'rm -rf "${WORK:?}"' EXIT
curl -sSfL "https://github.com/cue-lang/cue/releases/download/v${VERSION}/${ARCHIVE}" -o "$WORK/$ARCHIVE"
if command -v sha256sum >/dev/null; then ACTUAL="$(sha256sum "$WORK/$ARCHIVE")"; else ACTUAL="$(shasum -a 256 "$WORK/$ARCHIVE")"; fi
ACTUAL="${ACTUAL%% *}"
[ "$ACTUAL" = "$EXPECTED" ] || { echo "$ARCHIVE has sha256 $ACTUAL, not $EXPECTED (tools/cue-checksums.txt)" >&2; exit 1; }
tar -C "$WORK" -xzf "$WORK/$ARCHIVE" cue
mkdir -p "$DEST"
mv "$WORK/cue" "$DEST/cue"
chmod 0755 "$DEST/cue"
"$DEST/cue" version
