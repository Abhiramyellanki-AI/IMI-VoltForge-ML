"""
Router: POST /api/predict
Forward prediction — given SMILES + processing conditions, returns predicted Eb.
Uses lightweight RDKit features only (no PolyBERT transformer dependency).
"""
import os
import sys
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..')
)
sys.path.insert(0, _PROJECT_ROOT)

import config
from production.backend.core.model_loader import get_best_model, get_dataset
from production.backend.models.schemas    import PredictRequest, PredictResponse
from code_10_conditional_search           import get_candidate_features, infer_polymer_class

router = APIRouter(prefix="/api", tags=["Prediction"])


@router.post("/predict", response_model=PredictResponse)
def predict_eb(body: PredictRequest):
    """
    Forward prediction endpoint.

    Computes structural, physical, and Morgan features from the provided SMILES
    (lightweight mode — no PolyBERT), then predicts Eb using the best available model.
    """
    model = get_best_model()
    if model is None:
        raise HTTPException(status_code=503, detail="No model loaded. Run code_7_train_model.py first.")

    # ── Build feature row ──────────────────────────────────────────────────
    try:
        features = get_candidate_features(body.smiles)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Feature extraction failed: {e}")

    features['ProcessingTemp_C'] = body.processing_temp_c
    features['Crystallinity']    = body.crystallinity

    # ── Align columns to training schema ──────────────────────────────────
    try:
        df_ref    = get_dataset()
        train_cols = [c for c in df_ref.columns if c not in ('SMILES', 'Target_Eb')]
        df_input   = pd.DataFrame([features])[train_cols]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Column alignment failed: {e}")

    # ── Inference ──────────────────────────────────────────────────────────
    try:
        predicted_eb = float(model.predict(df_input)[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {e}")

    # Determine which model was used
    model_name = "ensemble" if hasattr(model, 'estimators_') else "mlp"

    return PredictResponse(
        predicted_eb      = round(predicted_eb, 2),
        model_used        = model_name,
        smiles            = body.smiles,
        processing_temp_c = body.processing_temp_c,
        crystallinity     = body.crystallinity,
    )
