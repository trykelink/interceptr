#!/bin/sh
# install.sh — One-command installer for Interceptr
# Usage: curl -sSL https://raw.githubusercontent.com/trykelink/interceptr/main/install.sh | sh

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

info()    { printf "${GREEN}%s${RESET}\n" "$1"; }
warn()    { printf "${YELLOW}WARNING: %s${RESET}\n" "$1"; }
error()   { printf "${RED}ERROR: %s${RESET}\n" "$1" >&2; exit 1; }

printf "\n"
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"
printf "${GREEN}  Installing Interceptr — AI Agent Security Middleware${RESET}\n"
printf "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}\n"
printf "\n"

# 1. Detect OS
OS="$(uname -s)"
case "$OS" in
  Darwin) info "Detected macOS" ;;
  Linux)  info "Detected Linux" ;;
  *)      error "Unsupported OS: $OS. Interceptr supports macOS and Linux only." ;;
esac

# 2. Check Python >= 3.10
if ! command -v python3 >/dev/null 2>&1; then
  error "Python 3 is not installed.\nInstall it from https://www.python.org/downloads/ (>= 3.10 required)."
fi

PY_VERSION="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
PY_MAJOR="$(echo "$PY_VERSION" | cut -d. -f1)"
PY_MINOR="$(echo "$PY_VERSION" | cut -d. -f2)"

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  error "Python >= 3.10 is required (found $PY_VERSION).\nPlease upgrade: https://www.python.org/downloads/"
fi

info "Python $PY_VERSION detected"

# 3. Check Docker (optional, non-blocking)
if ! command -v docker >/dev/null 2>&1; then
  printf "${YELLOW}⚠  Docker not found.${RESET}\n"
  printf "   Interceptr requires Docker to run the server.\n"
  printf "   Install Docker: https://docs.docker.com/get-docker/\n"
  printf "   Then run: interceptr start\n\n"
else
  info "Docker detected"
fi

# 4. Check / install pipx
if ! command -v pipx >/dev/null 2>&1; then
  info "pipx not found — installing..."
  python3 -m pip install --user pipx
  python3 -m pipx ensurepath
  export PATH="$PATH:$HOME/.local/bin"
else
  info "pipx detected"
fi

# 5. Install interceptr via pipx
info "Installing Interceptr..."
pipx install git+https://github.com/trykelink/interceptr.git

# 6. Verify installation
if ! command -v interceptr >/dev/null 2>&1; then
  warn "interceptr command not found in PATH."
  warn "You may need to restart your shell or run: source ~/.zshrc"
else
  interceptr --version 2>/dev/null || true
fi

# 7. Success message
printf "\n"
printf "${GREEN}✅ Interceptr installed successfully!${RESET}\n"
printf "\n"
printf "Get started:\n"
printf "  ${GREEN}interceptr start${RESET}   — downloads, starts server, opens dashboard\n"
printf "  ${GREEN}interceptr stop${RESET}    — stops the server\n"
printf "  ${GREEN}interceptr help${RESET}    — show all commands\n"
printf "\n"
printf "Docker is required to run Interceptr: https://docs.docker.com/get-docker/\n"
printf "Built by Kelink: https://kelink.dev\n"
printf "\n"
