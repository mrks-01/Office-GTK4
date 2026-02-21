#!/usr/bin/env bash
# ============================================================
#  Office-GTK4 — Installer
#  Installs to ~/.local/share/Office-GTK4
# ============================================================

set -euo pipefail

APP_NAME="Office-GTK4"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
DESKTOP_FILE="$DESKTOP_DIR/Office-GTK4.desktop"
LAUNCHER="$BIN_DIR/Office-GTK4"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colours ─────────────────────────────────────────────────
GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"
info()    { echo -e "${GREEN}[✓]${NC} $*"; }
warning() { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[✗]${NC} $*" >&2; exit 1; }

echo ""
echo "  Installing $APP_NAME …"
echo "  Target : $INSTALL_DIR"
echo ""

# ── 1. Check source file exists ─────────────────────────────
[[ -f "$SCRIPT_DIR/Office-GTK4.py" ]] \
    || error "Office-GTK4.py not found next to install.sh (expected in $SCRIPT_DIR)"

# ── 2. Dependency check ─────────────────────────────────────
check_python_deps() {
    python3 - <<'EOF' 2>/dev/null
import gi
gi.require_version("Gtk",    "4.0")
gi.require_version("Adw",    "1")
gi.require_version("WebKit", "6.0")
from gi.repository import Gtk, Adw, WebKit
EOF
}

if ! command -v python3 &>/dev/null; then
    error "python3 is not installed. Please install it and re-run."
fi

if ! check_python_deps; then
    warning "Required GObject/WebKit bindings not found. Attempting to install…"
    if command -v apt-get &>/dev/null; then
        sudo apt-get install -y \
            python3-gi python3-gi-cairo \
            gir1.2-gtk-4.0 gir1.2-adw-1 \
            gir1.2-webkit-6.0 libwebkitgtk-6.0-4
    elif command -v dnf &>/dev/null; then
        sudo dnf install -y \
            python3-gobject gtk4 libadwaita webkitgtk6.0
    elif command -v pacman &>/dev/null; then
        sudo pacman -S --noconfirm \
            python-gobject gtk4 libadwaita webkitgtk-6.0
    else
        error "Cannot auto-install dependencies.\nPlease manually install: GTK4, libadwaita, WebKitGTK 6.0, python3-gi"
    fi

    check_python_deps \
        || error "Dependency installation failed. Please install them manually and re-run."
fi
info "Python dependencies OK"

# ── 3. Create install directory ─────────────────────────────
mkdir -p "$INSTALL_DIR"
info "Created $INSTALL_DIR"

# ── 4. Copy application file ────────────────────────────────
cp "$SCRIPT_DIR/Office-GTK4.py" "$INSTALL_DIR/Office-GTK4.py"
chmod 644 "$INSTALL_DIR/Office-GTK4.py"
info "Copied Office-GTK4.py → $INSTALL_DIR/"

# ── 5. Create launcher in ~/.local/bin ──────────────────────
mkdir -p "$BIN_DIR"
cat > "$LAUNCHER" <<LAUNCHER_EOF
#!/usr/bin/env bash
exec python3 "$INSTALL_DIR/Office-GTK4.py" "\$@"
LAUNCHER_EOF
chmod +x "$LAUNCHER"
info "Created launcher → $LAUNCHER"

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    warning "$BIN_DIR is not in your PATH."
    warning "Add the following to your ~/.bashrc or ~/.zshrc:"
    echo ""
    echo '    export PATH="$HOME/.local/bin:$PATH"'
    echo ""
fi

# ── 6. Install icon ─────────────────────────────────────────
mkdir -p "$ICON_DIR"
cat > "$ICON_DIR/Office-GTK4.svg" <<'SVG_EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
  <rect x="2"  y="2"  width="28" height="28" rx="4" fill="#D83B01"/>
  <rect x="34" y="2"  width="28" height="28" rx="4" fill="#217346"/>
  <rect x="2"  y="34" width="28" height="28" rx="4" fill="#0078D4"/>
  <rect x="34" y="34" width="28" height="28" rx="4" fill="#743DA3"/>
</svg>
SVG_EOF
info "Installed icon → $ICON_DIR/Office-GTK4.svg"

# ── 7. Install .desktop entry ───────────────────────────────
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_FILE" <<DESKTOP_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Office-GTK4
GenericName=Office-GTK4
Comment=Microsoft 365 app in GTK4
Exec=$LAUNCHER
Icon=Office-GTK4
Terminal=false
Categories=Office;Network;
Keywords=word;excel;powerpoint;onenote;outlook;office;microsoft;
StartupWMClass=com.mrks.office-gtk4
DESKTOP_EOF
chmod 644 "$DESKTOP_FILE"
info "Installed .desktop → $DESKTOP_FILE"

# ── 8. Refresh icon cache & desktop database ─────────────────
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    info "Icon cache updated"
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
    info "Desktop database updated"
fi

# ── Done ─────────────────────────────────────────────────────
echo ""
echo -e "  ${GREEN}Installation complete!${NC}"
echo ""
echo "  Run from terminal : Office-GTK4"
echo "  Or launch from    : your app menu (Office-GTK4)"
echo ""
