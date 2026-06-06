#!/usr/bin/env bash
# Reproducibly build the friendlyJump-patched Fairy-Stockfish for Shogi4.
#
# Clones upstream Fairy-Stockfish at the PINNED commit, applies
# engine/shogi4-friendlyjump.patch (the 36-line friendly-jump feature), and builds.
# Result: <dest>/src/stockfish, which plays Shogi4 via engine/shogi4.ini.
#
#   ./build-shogi4-engine.sh [dest_dir] [ARCH]
#
# dest_dir defaults to ./Fairy-Stockfish (errors if it already exists, so it won't
# clobber a live checkout). ARCH is auto-detected (apple-silicon / x86-64-modern);
# override as the 2nd arg or see `make help` in src/.
set -euo pipefail

UPSTREAM="https://github.com/fairy-stockfish/Fairy-Stockfish.git"
PIN="1b5bdd40499bd5c7417bdc532d52fef8847bdf3f"   # upstream master @ 2026-06-05

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${1:-$HERE/Fairy-Stockfish}"
PATCH="$HERE/shogi4-friendlyjump.patch"

ARCH="${2:-}"
if [ -z "$ARCH" ]; then
  case "$(uname -m)" in
    arm64|aarch64) ARCH="apple-silicon" ;;
    x86_64)        ARCH="x86-64-modern" ;;
    *)             ARCH="" ;;            # fall back to the Makefile's own detection
  esac
fi

[ -f "$PATCH" ] || { echo "error: patch not found: $PATCH" >&2; exit 1; }
if [ -e "$DEST" ]; then
  echo "error: $DEST already exists (this is your live checkout)." >&2
  echo "       remove it or pass a fresh target dir, e.g. ./build-shogi4-engine.sh /tmp/fsf" >&2
  exit 1
fi

echo ">> cloning $UPSTREAM @ ${PIN:0:10}"
git clone --quiet "$UPSTREAM" "$DEST"
git -C "$DEST" checkout --quiet "$PIN"

echo ">> applying shogi4-friendlyjump.patch"
git -C "$DEST" apply "$PATCH"

echo ">> building (ARCH=${ARCH:-auto-detect})"
if [ -n "$ARCH" ]; then make -C "$DEST/src" -j build ARCH="$ARCH"
else                    make -C "$DEST/src" -j build; fi

echo ">> done -> $DEST/src/stockfish"
echo "   load with: setoption name VariantPath value $HERE/shogi4.ini"
echo "              setoption name UCI_Variant value shogi4"
