#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# IMI Polymer Informatics v2.0 — One-time Ubuntu Setup Script
# Run this ONCE before starting the project for the first time.
# Usage: bash setup.sh
# ═══════════════════════════════════════════════════════════════════════════════
set -e   # exit on any error

# ─── Colours ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC}  $1"; }
success() { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $1"; }

# Resolve the IMI project root (directory this script lives in)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"    # production/ → IMI/
info "Project root: $PROJECT_ROOT"

# ─── 1. System dependencies ───────────────────────────────────────────────────
info "Checking system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    nodejs npm \
    build-essential curl git 2>/dev/null
success "System packages installed"

# ─── 2. Python virtual environment ───────────────────────────────────────────
VENV_DIR="$PROJECT_ROOT/venv"
if [ ! -d "$VENV_DIR" ]; then
    info "Creating Python virtual environment at $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    success "Virtual environment created"
else
    warn "Virtual environment already exists — skipping creation"
fi

# Activate venv
source "$VENV_DIR/bin/activate"
pip install --upgrade pip -q

# ─── 3. Python backend dependencies ──────────────────────────────────────────
info "Installing Python backend dependencies..."
pip install -r "$PROJECT_ROOT/production/backend/requirements.txt"
success "Backend Python packages installed"

# ─── 4. Hardware bridge dependencies (optional) ──────────────────────────────
info "Installing hardware bridge dependencies..."
pip install -r "$PROJECT_ROOT/production/hardware/requirements_hw.txt"
success "Hardware packages installed"

# ─── 5. Node.js frontend dependencies ────────────────────────────────────────
FRONTEND_DIR="$PROJECT_ROOT/production/frontend"
info "Installing frontend Node.js packages..."
cd "$FRONTEND_DIR"
npm install --silent
success "Frontend Node.js packages installed"
cd "$PROJECT_ROOT"

# ─── 6. Train the model (if needed) ──────────────────────────────────────────
source "$VENV_DIR/bin/activate"
if [ ! -f "$PROJECT_ROOT/mlp_pipeline.pkl" ]; then
    info "No model found — running Phase A training (this may take a few minutes)..."
    cd "$PROJECT_ROOT"
    python3 code_7_train_model.py
    success "Model trained and saved: mlp_pipeline.pkl + ensemble_pipeline.pkl"
else
    success "Model already exists — skipping training (delete mlp_pipeline.pkl to retrain)"
fi

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  IMI Setup Complete!${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo ""
echo "  Next steps:"
echo "    bash production/start_backend.sh     # Terminal 1"
echo "    bash production/start_frontend.sh    # Terminal 2"
echo "  OR:"
echo "    bash production/start_all.sh         # Both at once (requires tmux)"
echo ""
