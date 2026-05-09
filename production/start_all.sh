#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# IMI — Start Everything (Backend + Frontend) in one terminal using tmux.
# If tmux is not installed, falls back to running backend in background.
# Usage: bash production/start_all.sh
# ═══════════════════════════════════════════════════════════════════════════════
set -e

GREEN='\033[0;32m'; CYAN='\033[0;36m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${CYAN}[IMI]${NC}     $1"; }
success() { echo -e "${GREEN}[IMI]${NC}     $1"; }
warn()    { echo -e "${YELLOW}[IMI]${NC}     $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_SCRIPT="$SCRIPT_DIR/start_backend.sh"
FRONTEND_SCRIPT="$SCRIPT_DIR/start_frontend.sh"

echo ""
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  IMI Polymer Informatics v2.0 — Full Stack Launcher${NC}"
echo -e "${GREEN}══════════════════════════════════════════════════════════${NC}"
echo ""

# ─── Option A: tmux (best experience) ─────────────────────────────────────────
if command -v tmux &>/dev/null; then
    SESSION="imi"
    info "tmux detected — launching in split panes (session: $SESSION)"
    echo ""

    # Kill existing session if any
    tmux kill-session -t "$SESSION" 2>/dev/null || true

    # Create new session with backend in pane 0
    tmux new-session -d -s "$SESSION" -x 220 -y 50
    tmux rename-window -t "$SESSION:0" "IMI Full Stack"
    tmux send-keys -t "$SESSION:0" "bash '$BACKEND_SCRIPT'" Enter

    # Split horizontally and start frontend in pane 1
    tmux split-window -h -t "$SESSION:0"
    tmux send-keys -t "$SESSION:0.1" "sleep 3 && bash '$FRONTEND_SCRIPT'" Enter

    # Attach to the session
    echo "  Backend  → http://localhost:8000"
    echo "  API Docs → http://localhost:8000/docs"
    echo "  Frontend → http://localhost:5173"
    echo ""
    info "Attaching to tmux session '$SESSION' ... (Ctrl+B then D to detach)"
    echo ""
    tmux attach-session -t "$SESSION"

# ─── Option B: background process (fallback) ──────────────────────────────────
else
    warn "tmux not found — starting backend in background, frontend in foreground."
    warn "Install tmux for a better experience: sudo apt-get install tmux"
    echo ""

    VENV_DIR="$PROJECT_ROOT/venv"
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    fi

    # Start backend in background, log to file
    LOG_FILE="$PROJECT_ROOT/backend.log"
    info "Starting backend (logs → $LOG_FILE) ..."
    cd "$PROJECT_ROOT"
    uvicorn production.backend.main:app \
        --reload --host 0.0.0.0 --port 8000 \
        --log-level info >"$LOG_FILE" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PROJECT_ROOT/backend.pid"
    info "Backend PID: $BACKEND_PID"

    # Wait for backend to be ready
    info "Waiting for backend to start..."
    for i in {1..15}; do
        if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
            success "Backend is ready!"
            break
        fi
        sleep 1
    done

    echo ""
    echo "  Backend  → http://localhost:8000"
    echo "  API Docs → http://localhost:8000/docs"
    echo "  Frontend → http://localhost:5173  (starting now...)"
    echo ""
    info "Starting frontend (Ctrl+C to stop both) ..."
    echo ""

    # Trap Ctrl+C to also kill the backend
    cleanup() {
        echo ""
        info "Shutting down..."
        kill "$BACKEND_PID" 2>/dev/null || true
        rm -f "$PROJECT_ROOT/backend.pid"
        info "All services stopped."
        exit 0
    }
    trap cleanup INT TERM

    # Start frontend in foreground
    cd "$SCRIPT_DIR/frontend"
    npm run dev
fi
