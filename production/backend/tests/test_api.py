import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import sys

# Ensure the root project directory is in the Python path so config imports work
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, _PROJECT_ROOT)

# -------------------------------------------------------------------------
# MOCKING: Prevent loading massive .pkl models and 10MB CSV datasets
# -------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def mock_ml_infrastructure():
    # Mock the joblib.load function to return a dummy model
    with patch('joblib.load') as mock_load:
        dummy_model = MagicMock()
        # Mock predict to return a consistent Eb prediction of 450.0 MV/m
        dummy_model.predict.return_value = [450.0]
        # Set estimators_ to mock it as an ensemble VotingRegressor
        dummy_model.estimators_ = True 
        mock_load.return_value = dummy_model

        # Mock the dataset loader to return a tiny dummy DataFrame instead of hitting disk
        with patch('production.backend.core.model_loader._load_dataset') as mock_ds:
            import pandas as pd
            # Create a mock dataframe that has the target columns
            mock_df = pd.DataFrame({'Target_Eb': [100.0], 'SMILES': ['CC']})
            # Populate dummy features to satisfy the feature extraction length
            for i in range(1700):
                mock_df[f'feature_{i}'] = [0.0]
            mock_ds.return_value = mock_df
            
            yield mock_load

# -------------------------------------------------------------------------
# IMPORT APP AND INITIALIZE TEST CLIENT
# -------------------------------------------------------------------------
from production.backend.main import app
client = TestClient(app)

def test_inverse_design_valid():
    """
    Test posting valid data to the L-BFGS-B optimization endpoint.
    Asserts a 200 OK and validates the core response fields.
    """
    response = client.post(
        "/api/inverse-design",
        json={
            "target_eb": 500.0,
            "smiles": "CC",
            "max_iter": 10
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["target_eb"] == 500.0
    assert "optimal_temp_c" in data
    assert "optimal_crystallinity" in data
    assert data["model_used"] == "ensemble"

def test_inverse_design_invalid_target_eb():
    """
    Test posting physically impossible data to the endpoint.
    Asserts a 422 Unprocessable Entity (Pydantic validation catch).
    """
    response = client.post(
        "/api/inverse-design",
        json={
            "target_eb": -500.0,  # Invalid: schema enforces gt=0.0
            "smiles": "CC",
            "max_iter": 10
        }
    )
    
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Ensure the error is specifically about target_eb validation
    assert data["detail"][0]["loc"] == ["body", "target_eb"]
