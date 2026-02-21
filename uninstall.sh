#!/usr/bin/env bash
# ============================================================
#  Office-GTK4 — Uninstaller
# ============================================================

set -euo pipefail

APP_NAME="Office-GTK4"
INSTALL_DIR="$HOME/.local/share/$APP_NAME"
LAUNCHER="$HOME/.local/bin/Office-GTK4"
DESKTOP_FILE="$HOME/.local/share/applications/Office-GTK4.desktop"
ICON_FILE="$HOME/.local/share/icons/hicolor/scalable/apps/Office-GTK4.svg"

# ── Colours ─────────────────────────────────────────────────
GREEN="\033[0;32m"; YELLOW="\033[1;33m"; RED="\033[0;31m"; NC="\033[0m"
info()    { echo -e "${GREEN}[✓]${NC} $*"; }
warning() { echo -e "${YELLOW}[!]${NC} $*"; }

echo ""
echo "  Uninstalling $APP_NAME …"
echo ""

# ── Confirm ──────────────────────────────────────────────────
read -rp "  Are you sure you want to uninstall $APP_NAME? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { echo "  Aborted."; echo ""; exit 0; }
echo ""

# ── Remove app directory ─────────────────────────────────────
if [[ -d "$INSTALL_DIR" ]]; then
    rm -rf "$INSTALL_DIR"
    info "Removed $INSTALL_DIR"
else
    warning "Install directory not found, skipping: $INSTALL_DIR"
fi

# ── Remove launcher ──────────────────────────────────────────
if [[ -f "$LAUNCHER" ]]; then
    rm -f "$LAUNCHER"
    info "Removed launcher $LAUNCHER"
else
    warning "Launcher not found, skipping: $LAUNCHER"
fi

# ── Remove .desktop entry ────────────────────────────────────
if [[ -f "$DESKTOP_FILE" ]]; then
    rm -f "$DESKTOP_FILE"
    info "Removed $DESKTOP_FILE"
else
    warning ".desktop file not found, skipping: $DESKTOP_FILE"
fi

# ── Remove icon ──────────────────────────────────────────────
if [[ -f "$ICON_FILE" ]]; then
    rm -f "$ICON_FILE"
    info "Removed icon $ICON_FILE"
else
    warning "Icon not found, skipping: $ICON_FILE"
fi

# ── Optionally remove user data & cache ─────────────────────
DATA_DIR="$HOME/.local/share/Office-GTK4"
CACHE_DIR="$HOME/.cache/Office-GTK4"

if [[ -d "$DATA_DIR" || -d "$CACHE_DIR" ]]; then
    echo ""
    read -rp "  Remove saved cookies and cache too? [y/N] " purge
    if [[ "$purge" =~ ^[Yy]$ ]]; then
        [[ -d "$DATA_DIR" ]]  && { rm -rf "$DATA_DIR";  info "Removed user data $DATA_DIR"; }
        [[ -d "$CACHE_DIR" ]] && { rm -rf "$CACHE_DIR"; info "Removed cache $CACHE_DIR"; }
    else
        warning "Keeping user data and cache (cookies, session)."
    fi
fi

# ── Refresh icon cache & desktop database ───────────────────
if command -v gtk-update-icon-cache &>/dev/null; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    info "Icon cache updated"
fi
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
    info "Desktop database updated"
fi

# ── Done ────────────────────────────────────────────────────
echo ""
echo -e "  ${GREEN}$APP_NAME has been uninstalled.${NC}"
echo ""
