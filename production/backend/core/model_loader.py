"""
Singleton model loader for the IMI FastAPI backend.

Uses functools.lru_cache to ensure models and dataset are loaded
exactly once at startup — not re-loaded on every request.

Provides FastAPI Depends()-compatible getter functions.
"""
import os
import sys
import joblib
import pandas as pd
from functools import lru_cache
from typing import Tuple, Any

# model_loader.py lives at IMI/production/backend/core/  → 3 levels up = IMI/
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..')
)
sys.path.insert(0, _PROJECT_ROOT)

import config


def _resolve(filename: str) -> str:
    """Resolves a filename to an absolute path under the project root."""
    return os.path.join(_PROJECT_ROOT, filename)


@lru_cache(maxsize=1)
def _load_models() -> Tuple[Any, Any]:
    """
    Loads and caches both models.
    Returns (ensemble_model, mlp_model).
    ensemble_model may be None if ensemble_pipeline.pkl doesn't exist yet
    (i.e., code_7 hasn't been run with Phase A yet).
    """
    # Try ensemble first (Phase A output)
    ensemble_path = _resolve(config.ENSEMBLE_PATH)
    mlp_path      = _resolve(config.MODEL_PATH)

    ensemble_model = None
    mlp_model      = None

    if os.path.exists(ensemble_path):
        try:
            ensemble_model = joblib.load(ensemble_path)
            print(f"[ModelLoader] Ensemble model loaded from {ensemble_path}")
        except Exception as e:
            print(f"[ModelLoader] WARNING: Could not load ensemble: {e}")

    if os.path.exists(mlp_path):
        try:
            mlp_model = joblib.load(mlp_path)
            print(f"[ModelLoader] MLP model loaded from {mlp_path}")
        except Exception as e:
            print(f"[ModelLoader] WARNING: Could not load MLP: {e}")

    if mlp_model is None and ensemble_model is None:
        raise RuntimeError(
            "No model files found. "
            f"Run code_7_train_model.py to generate {config.MODEL_PATH} first."
        )

    return ensemble_model, mlp_model


@lru_cache(maxsize=1)
def _load_dataset() -> pd.DataFrame:
    """Loads and caches the ready_polymer_dataset.csv."""
    path = _resolve(config.DATASET_PATH)
    if not os.path.exists(path):
        raise RuntimeError(
            f"Dataset not found at {path}. Run code_6_main.py first."
        )
    df = pd.read_csv(path)
    print(f"[ModelLoader] Dataset loaded: {df.shape[0]} rows × {df.shape[1]} cols")
    return df


# ─── FastAPI Dependency Injectors ────────────────────────────────────────────

def get_best_model() -> Any:
    """Returns ensemble if available, falls back to MLP."""
    ensemble, mlp = _load_models()
    return ensemble if ensemble is not None else mlp


def get_ensemble_model() -> Any:
    ensemble, _ = _load_models()
    return ensemble


def get_mlp_model() -> Any:
    _, mlp = _load_models()
    return mlp


def get_dataset() -> pd.DataFrame:
    return _load_dataset()


@lru_cache(maxsize=1)
def get_feature_order() -> list:
    df = _load_dataset()
    return [c for c in df.columns if c not in ('SMILES', 'Target_Eb')]


def model_status() -> dict:
    """Returns a status dict for the /health endpoint."""
    try:
        ensemble, mlp = _load_models()
        df            = _load_dataset()
        return {
            "model_loaded":    mlp      is not None,
            "ensemble_loaded": ensemble is not None,
            "dataset_rows":    len(df),
        }
    except Exception:
        return {
            "model_loaded":    False,
            "ensemble_loaded": False,
            "dataset_rows":    0,
        }


def warmup():
    """Pre-warms caches at startup."""
    try:
        _load_models()
        _load_dataset()
        print("[ModelLoader] Warmup complete.")
    except Exception as e:
        print(f"[ModelLoader] Warmup warning: {e}")
