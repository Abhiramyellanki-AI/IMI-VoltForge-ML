"""
Router: POST /api/inverse-design
Inverse design — given a target Eb and SMILES, finds optimal ProcessingTemp + Crystallinity
using the exact L-BFGS-B approach from code_8_inverse_design.py, adapted for the API.
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
from production.backend.core.model_loader import get_best_model, get_dataset, get_feature_order
from production.backend.models.schemas    import InverseDesignRequest, InverseDesignResponse
from code_10_conditional_search           import get_candidate_features

router = APIRouter(prefix="/api", tags=["Inverse Design"])


def _objective(x, model, base_features: dict, feature_order: list, target_eb: float) -> float:
    """
    L-BFGS-B objective function.
    x[0] = ProcessingTemp_C,  x[1] = Crystallinity
    Returns absolute distance from target_eb.
    """
    candidate = base_features.copy()
    candidate['ProcessingTemp_C'] = x[0]
    candidate['Crystallinity']    = x[1]

    df_candidate = pd.DataFrame([candidate])[feature_order]
    prediction   = model.predict(df_candidate)[0]
    return (float(prediction) - target_eb) ** 2


@router.post("/inverse-design", response_model=InverseDesignResponse)
def inverse_design(body: InverseDesignRequest):
    """
    Inverse design endpoint.

    Freezes all molecular features of the provided SMILES, then uses
    SciPy L-BFGS-B to find the (Temperature, Crystallinity) pair that
    minimizes |predicted_Eb - target_Eb|.
    """
    model = get_best_model()
    if model is None:
        raise HTTPException(status_code=503, detail="No model loaded.")

    # ── Extract base features for the SMILES ──────────────────────────────
    try:
        base_features = get_candidate_features(body.smiles)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Feature extraction failed: {e}")

    # ── Align to training column order ────────────────────────────────────
    try:
        feature_order = get_feature_order()
        # Initialize processing cols at midpoint (required for column alignment)
        base_features['ProcessingTemp_C'] = (config.TEMP_BOUNDS[0] + config.TEMP_BOUNDS[1]) / 2
        base_features['Crystallinity']    = (config.CRYST_BOUNDS[0] + config.CRYST_BOUNDS[1]) / 2
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Column alignment failed: {e}")

    # ── L-BFGS-B Optimization ──────────────────────────────────────────────
    initial_guesses = [
        [config.TEMP_BOUNDS[0] + 10, config.CRYST_BOUNDS[0] + 0.1],
        [(config.TEMP_BOUNDS[0] + config.TEMP_BOUNDS[1]) / 2, (config.CRYST_BOUNDS[0] + config.CRYST_BOUNDS[1]) / 2],
        [config.TEMP_BOUNDS[1] - 10, config.CRYST_BOUNDS[1] - 0.1]
    ]

    best_res = None
    bounds = [config.TEMP_BOUNDS, config.CRYST_BOUNDS]
    for guess in initial_guesses:
        try:
            res = minimize(
                _objective,
                x0      = guess,
                args    = (model, base_features, feature_order, body.target_eb),
                method  = 'L-BFGS-B',
                bounds  = bounds,
                options = {'disp': False, 'maxiter': body.max_iter},
            )
            if best_res is None or res.fun < best_res.fun:
                best_res = res
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            raise RuntimeError(f"Optimizer objective evaluation failed. Internal Error: {e}\n{err}") from e
            
    if best_res is None:
        raise HTTPException(status_code=500, detail="Optimizer failed on all starts.")
    res = best_res

    model_name = "ensemble" if hasattr(model, 'estimators_') else "mlp"

    if res.success or res.fun < 50.0:  # Accept near-convergence too
        # Compute final prediction at optimal point
        base_features['ProcessingTemp_C'] = res.x[0]
        base_features['Crystallinity']    = res.x[1]
        df_final     = pd.DataFrame([base_features])[feature_order]
        predicted_eb = float(model.predict(df_final)[0])

        return InverseDesignResponse(
            success               = True,
            smiles                = body.smiles,
            target_eb             = body.target_eb,
            optimal_temp_c        = round(float(res.x[0]), 2),
            optimal_crystallinity = round(float(res.x[1]), 4),
            predicted_eb          = round(predicted_eb, 2),
            absolute_error        = round(abs(predicted_eb - body.target_eb), 2),
            optimizer_message     = str(res.message),
            model_used            = model_name,
        )
    else:
        return InverseDesignResponse(
            success               = False,
            smiles                = body.smiles,
            target_eb             = body.target_eb,
            optimal_temp_c        = None,
            optimal_crystallinity = None,
            predicted_eb          = None,
            absolute_error        = None,
            optimizer_message     = str(res.message),
            model_used            = model_name,
        )
