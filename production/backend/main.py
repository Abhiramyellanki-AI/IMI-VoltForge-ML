"""
IMI Polymer Informatics — FastAPI Application Entry Point

Mounts all routers:
  /api/predict              → Forward Eb prediction
  /api/inverse-design       → L-BFGS-B optimizer
  /api/conditional-search   → Phase B similarity search
  /api/generative-design    → Phase C De Novo GA
  /api/twin/*               → Phase E Digital Twin

Run with:
  cd ~/IMI
  uvicorn production.backend.main:app --reload --host 0.0.0.0 --port 8000
"""
import sys
import os

# Ensure project root (IMI/) is on sys.path so all code_* imports resolve.
# main.py lives at IMI/production/backend/main.py  → 2 levels up = IMI/
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from production.backend.core.model_loader import warmup, model_status
from production.backend.routers import (
    predict,
    inverse_design,
    conditional_generation,
    digital_twin,
    generative_design,
)


# ─── Lifespan: pre-warm models at startup ────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[Startup] Pre-warming model caches...")
    warmup()
    print("[Startup] IMI API ready.")
    yield
    print("[Shutdown] IMI API shutting down.")


# ─── App Initialization ───────────────────────────────────────────────────────
app = FastAPI(
    title       = "IMI Polymer Informatics API",
    description = (
        "Production REST API for the Materials Informatics pipeline: "
        "forward Eb prediction, L-BFGS-B inverse design, conditional polymer search, "
        "and Digital Twin telemetry processing."
    ),
    version     = "2.0.0",
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ─── CORS (allow React dev server on port 5173) ───────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ─── Include Routers ──────────────────────────────────────────────────────────
app.include_router(predict.router)
app.include_router(inverse_design.router)
app.include_router(conditional_generation.router)
app.include_router(digital_twin.router)
app.include_router(generative_design.router)


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
def health():
    status = model_status()
    return {
        "status":          "ok",
        "model_loaded":    status["model_loaded"],
        "ensemble_loaded": status["ensemble_loaded"],
        "dataset_rows":    status["dataset_rows"],
    }


@app.get("/", tags=["System"])
def root():
    return {
        "message": "IMI Polymer Informatics API v2.0",
        "docs":    "/docs",
        "health":  "/health",
    }
