#!/usr/bin/env bash
# Build PSELinearA-Setup-<version>.exe (run in Git Bash on Windows).
#
# Contents: PyInstaller bundle of the app + PySide6 + numpy, icon, LICENSE,
# NOTICE; packed by Inno Setup into a per-user installer (no admin). The
# release build runs on GitHub's Windows runner (see build-exe.yml).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
PY="${PYTHON:-$ROOT/.venv/Scripts/python.exe}"
VERSION="${1:-0.1.0}"
PKG="pse-linear-a"
STAGE="$HERE/stage-win"
OUT="$ROOT/dist"
ISCC="${ISCC:-/c/Program Files (x86)/Inno Setup 6/ISCC.exe}"

echo "== PyInstaller bundle"
rm -rf "$ROOT/build/pyi" "$STAGE"
"$PY" -m PyInstaller --noconfirm --clean --onedir --windowed --name "$PKG" \
  --icon "$HERE/$PKG.ico" \
  --distpath "$ROOT/build/pyi/dist" --workpath "$ROOT/build/pyi/work" --specpath "$ROOT/build/pyi" \
  --collect-submodules pse_linear_a --collect-data pse_linear_a \
  "$HERE/entry.py"

APP="$STAGE/$PKG"
mkdir -p "$APP"
cp -a "$ROOT/build/pyi/dist/$PKG/." "$APP/"
cp -r "$ROOT/data" "$APP/data" 2>/dev/null || true
cp "$HERE/$PKG.ico" "$APP/"
cp "$ROOT/LICENSE" "$APP/LICENSE.txt"
cp "$ROOT/NOTICE" "$APP/NOTICE.txt"

echo "== Inno Setup"
mkdir -p "$OUT"
MSYS2_ARG_CONV_EXCL="*" "$ISCC" "/DAppVersion=$VERSION" "/DSourceDir=$(cygpath -w "$APP")" "/DOutDir=$(cygpath -w "$OUT")" \
  "$(cygpath -w "$HERE/$PKG.iss")"
echo "built $OUT/PSELinearA-Setup-$VERSION.exe"
