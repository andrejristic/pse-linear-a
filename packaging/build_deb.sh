#!/usr/bin/env bash
# Build a .deb for PSE Linear A. Run on a Debian/Ubuntu system with dpkg-deb.
# Route: system PySide6 dependency (no bundling). For a self-contained build,
# swap the depends line for a PyInstaller onefile and drop it in /opt.
set -euo pipefail

VERSION="${1:-0.1.0}"
ARCH="all"
PKG="pse-linear-a"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="$(mktemp -d)/${PKG}_${VERSION}"
echo "Staging in $STAGE"

mkdir -p "$STAGE/DEBIAN" \
         "$STAGE/opt/$PKG" \
         "$STAGE/usr/bin" \
         "$STAGE/usr/share/applications" \
         "$STAGE/usr/share/icons/hicolor/scalable/apps"

# --- app payload ---
cp -r "$ROOT/pse_linear_a" "$STAGE/opt/$PKG/"
cp -r "$ROOT/data"         "$STAGE/opt/$PKG/" 2>/dev/null || true
cp "$ROOT/README.md"       "$STAGE/opt/$PKG/" 2>/dev/null || true

# --- launcher ---
cat > "$STAGE/usr/bin/$PKG" <<'EOF'
#!/usr/bin/env bash
exec python3 -m pse_linear_a --from /opt/pse-linear-a "$@"
EOF
# ensure the package is importable from /opt
cat > "$STAGE/usr/bin/$PKG" <<EOF
#!/usr/bin/env bash
export PYTHONPATH="/opt/$PKG:\${PYTHONPATH:-}"
exec python3 -m pse_linear_a "\$@"
EOF
chmod 755 "$STAGE/usr/bin/$PKG"

# --- desktop + icon ---
cp "$ROOT/packaging/$PKG.desktop" "$STAGE/usr/share/applications/"
cp "$ROOT/packaging/$PKG.svg"     "$STAGE/usr/share/icons/hicolor/scalable/apps/"

# --- control ---
cat > "$STAGE/DEBIAN/control" <<EOF
Package: $PKG
Version: $VERSION
Section: science
Priority: optional
Architecture: $ARCH
Depends: python3 (>= 3.10), python3-numpy, python3-pyside6.qtwidgets | python3-pyside6
Maintainer: Andrej Ristic <andrej.s.ristic@gmail.com>
Description: PSE Linear A — decipherment swarm
 Partial Self-Extension swarm that scrapes evidence about the undeciphered Minoan
 script Linear A (with Linear B as the deciphered anchor) and tries to get closer to
 reading it. Includes reading engines, calibration gate, two Guardians, and a
 read-only State of Knowledge.
EOF

OUT="$ROOT/${PKG}_${VERSION}_${ARCH}.deb"
dpkg-deb --build --root-owner-group "$STAGE" "$OUT"
echo "Built: $OUT"
