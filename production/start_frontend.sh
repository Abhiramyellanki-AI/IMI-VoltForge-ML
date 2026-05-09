#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# IMI — Start React Frontend (Vite dev server)
# Usage: bash production/start_frontend.sh
# ═══════════════════════════════════════════════════════════════════════════════
set -e

CYAN='\033[0;36m'; NC='\033[0m'
info() { echo -e "${CYAN}[IMI-Frontend]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo -e "\033[0;31m[ERROR]\033[0m node_modules not found. Run setup.sh first."
    exit 1
fi

info "Starting Vite dev server on http://localhost:5173 ..."
info "Connecting to API at http://localhost:8000"
echo ""

cd "$FRONTEND_DIR"
npm run dev
