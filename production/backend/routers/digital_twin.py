"""
Router: Phase E — Digital Twin
  POST /api/twin/predict  — maps real-time telemetry to Eb prediction
  POST /api/twin/correct  — given current vs desired Eb, returns ΔTemp + ΔCryst
  GET  /api/twin/simulate — returns a synthetic telemetry snapshot for demo

Pressure → Crystallinity empirical mapping:
  crystallinity = clip(0.05 * pressure_bar + 0.10, 0.10, 0.90)
  (a simple linear proxy: higher pressure drives higher crystallinity)
"""
import os
import sys
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from scipy.optimize import minimize

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..')
)
sys.path.insert(0, _PROJECT_ROOT)

import config
from production.backend.core.model_loader import get_best_model, get_dataset
from production.backend.models.schemas    import (
    TelemetryInput,
    TwinPredictionResponse,
    CorrectionRequest,
    CorrectionResponse,
)
from code_10_conditional_search import get_candidate_features

router = APIRouter(prefix="/api/twin", tags=["Digital Twin"])


def _pressure_to_crystallinity(pressure_bar: float) -> float:
    """
    Empirical pressure → crystallinity proxy.
    At 0.5 bar → ~0.125 cryst | At 20 bar → ~1.10 (clipped to 0.90)
    """
    cryst = 0.05 * pressure_bar + 0.10
    return float(np.clip(cryst, config.CRYST_BOUNDS[0], config.CRYST_BOUNDS[1]))


def _build_feature_row(smiles: str, temp: float, cryst: float, feature_order: list) -> pd.DataFrame:
    """Builds a model-ready feature DataFrame from SMILES + process conditions."""
    features = get_candidate_features(smiles)
    features['ProcessingTemp_C'] = temp
    features['Crystallinity']    = cryst
    return pd.DataFrame([features])[feature_order]


@router.post("/predict", response_model=TwinPredictionResponse)
def twin_predict(body: TelemetryInput):
    """
    Digital Twin forward pass.

    Accepts real-time sensor telemetry (temperature + pressure), maps pressure
    to crystallinity via empirical curve, and predicts Eb using the production model.
    """
    model = get_best_model()
    if model is None:
        raise HTTPException(status_code=503, detail="No model loaded.")

    # Map pressure → crystallinity
    estimated_cryst = _pressure_to_crystallinity(body.pressure_bar)

    # Clamp temperature to training bounds
    clamped_temp = float(np.clip(body.temperature, config.TEMP_BOUNDS[0], config.TEMP_BOUNDS[1]))

    try:
        df_ref        = get_dataset()
        feature_order = [c for c in df_ref.columns if c not in ('SMILES', 'Target_Eb')]
        df_input      = _build_feature_row(body.smiles, clamped_temp, estimated_cryst, feature_order)
        predicted_eb  = float(model.predict(df_input)[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Twin prediction failed: {e}")

    model_name = "ensemble" if hasattr(model, 'estimators_') else "mlp"

    return TwinPredictionResponse(
        smiles                  = body.smiles,
        temperature             = clamped_temp,
        pressure_bar            = body.pressure_bar,
        estimated_crystallinity = round(estimated_cryst, 4),
        predicted_eb            = round(predicted_eb, 2),
        good_fit                = predicted_eb >= config.GOOD_FIT_THRESHOLD,
        model_used              = model_name,
    )


@router.post("/correct", response_model=CorrectionResponse)
def twin_correct(body: CorrectionRequest):
    """
    Digital Twin correction loop.

    Given current process state and a desired Eb, runs L-BFGS-B to find
    the nearest (Temp, Cryst) that achieves the desired Eb, then computes
    the delta from the current state as the corrective setpoint recommendation.
    """
    model = get_best_model()
    if model is None:
        raise HTTPException(status_code=503, detail="No model loaded.")

    try:
        df_ref        = get_dataset()
        feature_order = [c for c in df_ref.columns if c not in ('SMILES', 'Target_Eb')]
        base_features = get_candidate_features(body.smiles)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature extraction failed: {e}")

    def objective(x):
        feat = base_features.copy()
        feat['ProcessingTemp_C'] = x[0]
        feat['Crystallinity']    = x[1]
        df_c = pd.DataFrame([feat])[feature_order]
        return abs(float(model.predict(df_c)[0]) - body.desired_eb)

    # Start optimizer from current state
    x0 = [
        np.clip(body.current_temp,  *config.TEMP_BOUNDS),
        np.clip(body.current_cryst, *config.CRYST_BOUNDS),
    ]
    res = minimize(
        objective,
        x0      = x0,
        method  = 'L-BFGS-B',
        bounds  = [config.TEMP_BOUNDS, config.CRYST_BOUNDS],
        options = {'maxiter': 300, 'disp': False},
    )

    rec_temp  = round(float(res.x[0]), 2)
    rec_cryst = round(float(res.x[1]), 4)

    # Compute projected Eb at recommended setpoint
    base_features['ProcessingTemp_C'] = rec_temp
    base_features['Crystallinity']    = rec_cryst
    df_proj       = pd.DataFrame([base_features])[feature_order]
    projected_eb  = float(model.predict(df_proj)[0])

    return CorrectionResponse(
        delta_temp_c           = round(rec_temp  - body.current_temp,  2),
        delta_crystallinity    = round(rec_cryst - body.current_cryst, 4),
        recommended_temp_c     = rec_temp,
        recommended_crystallinity = rec_cryst,
        projected_eb           = round(projected_eb, 2),
        projected_error        = round(abs(projected_eb - body.desired_eb), 2),
    )


@router.get("/simulate")
def twin_simulate():
    """
    Returns a synthetic telemetry snapshot for frontend demo / IoT bridge testing.
    Generates a random valid (temp, pressure) pair and runs a twin prediction.
    """
    import random
    # Pick a random polymer from the dataset for demo
    df    = get_dataset()
    idx   = random.randint(0, len(df) - 1)
    smiles = df.iloc[idx]['SMILES']

    fake_temp     = round(random.uniform(*config.TEMP_BOUNDS), 1)
    fake_pressure = round(random.uniform(0.5, 20.0), 2)

    # Inline prediction (avoids HTTP round-trip)
    model = get_best_model()
    cryst = _pressure_to_crystallinity(fake_pressure)

    feature_order = [c for c in df.columns if c not in ('SMILES', 'Target_Eb')]
    features      = get_candidate_features(smiles)
    features['ProcessingTemp_C'] = fake_temp
    features['Crystallinity']    = cryst
    df_input     = pd.DataFrame([features])[feature_order]
    predicted_eb = float(model.predict(df_input)[0])

    return {
        "simulated":             True,
        "smiles":                smiles,
        "temperature":           fake_temp,
        "pressure_bar":          fake_pressure,
        "estimated_crystallinity": round(cryst, 4),
        "predicted_eb":          round(predicted_eb, 2),
        "good_fit":              predicted_eb >= config.GOOD_FIT_THRESHOLD,
    }
