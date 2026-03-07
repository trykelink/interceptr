#!/bin/sh
# uninstall.sh — Uninstaller for Interceptr
# Usage: curl -sSL https://raw.githubusercontent.com/trykelink/interceptr/main/uninstall.sh | sh
# Or: interceptr uninstall

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m'

info()  { printf "${GREEN}%s${RESET}\n" "$1"; }
warn()  { printf "${YELLOW}%s${RESET}\n" "$1"; }

printf "\n"
info "Uninstalling Interceptr..."

# Remove interceptr via pipx
if command -v pipx >/dev/null 2>&1; then
  pipx uninstall interceptr || warn "interceptr was not installed via pipx (or already removed)."
else
  warn "pipx not found — nothing to uninstall."
fi

# Ask if user wants to remove pipx too
printf "\n"
printf "Do you also want to remove pipx? [y/N] "
read -r REMOVE_PIPX
case "$REMOVE_PIPX" in
  [Yy]*)
    info "Removing pipx..."
    python3 -m pip uninstall -y pipx 2>/dev/null || warn "pipx could not be removed via pip."
    ;;
  *)
    info "Keeping pipx."
    ;;
esac

printf "\n"
info "Interceptr has been removed from your system."
printf "\n"
