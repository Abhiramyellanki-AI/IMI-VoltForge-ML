#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# IMI — Start FastAPI Backend
# Must be run from any directory; resolves project root automatically.
# Usage: bash production/start_backend.sh
# ═══════════════════════════════════════════════════════════════════════════════
set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
info() { echo -e "${CYAN}[IMI-Backend]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"

# ─── Activate venv ────────────────────────────────────────────────────────────
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
    info "Virtual environment activated: $VENV_DIR"
else
    info "No venv found — using system Python. Run setup.sh first for an isolated environment."
fi

# ─── Verify model exists ──────────────────────────────────────────────────────
if [ ! -f "$PROJECT_ROOT/mlp_pipeline.pkl" ] && [ ! -f "$PROJECT_ROOT/ensemble_pipeline.pkl" ]; then
    echo -e "\033[0;31m[ERROR]\033[0m No model file found in $PROJECT_ROOT"
    echo "        Run: python3 code_7_train_model.py  (from $PROJECT_ROOT)"
    exit 1
fi

info "Starting FastAPI backend on http://0.0.0.0:8000 ..."
info "API docs: http://localhost:8000/docs"
echo ""

# ─── Launch uvicorn from project root so production.* imports resolve ─────────
cd "$PROJECT_ROOT"
uvicorn production.backend.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
