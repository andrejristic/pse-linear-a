#!/usr/bin/env bash
# Build pse-linear-a_<version>_amd64.deb (self-contained PyInstaller bundle).
#
# Contents: /opt/pse-linear-a (PyInstaller bundle of the app + PySide6 + numpy),
# /usr/bin/pse-linear-a, desktop entry, icon, LICENSE and NOTICE. No system
# Python or PySide6 needed at run time. The release build runs on Ubuntu 22.04
# so the binary runs on Ubuntu 22.04+ and Debian 12+ (see build-deb.yml).
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(dirname "$HERE")"
PY="${PYTHON:-$ROOT/.venv/bin/python}"
VERSION="${1:-0.1.0}"
ARCH="${ARCH:-amd64}"
PKG="pse-linear-a"
STAGE="$HERE/stage"
OUT="$ROOT/dist"

echo "== PyInstaller bundle"
rm -rf "$ROOT/build/pyi" "$STAGE"
"$PY" -m PyInstaller --noconfirm --clean --onedir --name "$PKG" \
  --distpath "$ROOT/build/pyi/dist" --workpath "$ROOT/build/pyi/work" --specpath "$ROOT/build/pyi" \
  --collect-submodules pse_linear_a --collect-data pse_linear_a \
  "$HERE/entry.py"

APP="$STAGE/opt/$PKG"
mkdir -p "$APP"
cp -a "$ROOT/build/pyi/dist/$PKG/." "$APP/"
cp -r "$ROOT/data" "$APP/data" 2>/dev/null || true
cp "$ROOT/LICENSE" "$APP/LICENSE"
cp "$ROOT/NOTICE" "$APP/NOTICE"

mkdir -p "$STAGE/usr/bin" "$STAGE/usr/share/applications" \
         "$STAGE/usr/share/icons/hicolor/scalable/apps" \
         "$STAGE/usr/share/doc/$PKG" "$STAGE/DEBIAN"
ln -s "/opt/$PKG/$PKG" "$STAGE/usr/bin/$PKG"
cp "$HERE/$PKG.desktop" "$STAGE/usr/share/applications/"
cp "$HERE/$PKG.svg" "$STAGE/usr/share/icons/hicolor/scalable/apps/"
cp "$ROOT/LICENSE" "$STAGE/usr/share/doc/$PKG/LICENSE"
cp "$ROOT/NOTICE" "$STAGE/usr/share/doc/$PKG/NOTICE"

SIZE="$(du -sk "$STAGE/opt" "$STAGE/usr" | awk '{s+=$1} END{print s}')"
cat > "$STAGE/DEBIAN/control" <<EOF
Package: $PKG
Version: $VERSION
Section: science
Priority: optional
Architecture: $ARCH
Installed-Size: $SIZE
Maintainer: Andrej Ristic <andrej.s.ristic@gmail.com>
Depends: libc6 (>= 2.34), libgl1, libegl1, libfontconfig1, libxkbcommon0, libdbus-1-3
Homepage: https://github.com/andrejristic/pse-linear-a
Description: PSE Linear A - decipherment swarm
 A Partial Self-Extension swarm that gathers evidence about the undeciphered
 Minoan script Linear A, with Linear B as the deciphered anchor, and works to
 get closer to reading it. Reading engines, a calibration gate, two Guardians,
 and a read-only State of Knowledge.
EOF

echo "== dpkg-deb"
mkdir -p "$OUT"
DEB="$OUT/${PKG}_${VERSION}_${ARCH}.deb"
dpkg-deb --root-owner-group -Zxz --build "$STAGE" "$DEB"
echo "built $DEB"
