"""
Pydantic v2 Schemas for all IMI API endpoints.
Covers: Forward Predict, Inverse Design, Conditional Search, Digital Twin.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


# ─────────────────────────────────────────────────────────────────────────────
#  Shared
# ─────────────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    ensemble_loaded: bool
    dataset_rows: int


# ─────────────────────────────────────────────────────────────────────────────
#  Forward Prediction  —  POST /api/predict
# ─────────────────────────────────────────────────────────────────────────────

class PredictRequest(BaseModel):
    smiles: str = Field(
        ...,
        description="SMILES string of the polymer (lightweight RDKit features only)",
        example="CC(F)(C(F)(F)F)CC(F)(I)"
    )
    processing_temp_c: float = Field(
        ..., ge=100.0, le=300.0,
        description="Processing temperature in °C (bounds: 100–300)",
        example=200.0
    )
    crystallinity: float = Field(
        ..., ge=0.10, le=0.90,
        description="Crystallinity fraction (bounds: 0.10–0.90)",
        example=0.45
    )

class PredictResponse(BaseModel):
    predicted_eb: float = Field(..., description="Predicted dielectric breakdown strength (MV/m)")
    model_used: str     = Field(..., description="'ensemble' or 'mlp'")
    smiles: str
    processing_temp_c: float
    crystallinity: float


# ─────────────────────────────────────────────────────────────────────────────
#  Inverse Design  —  POST /api/inverse-design
# ─────────────────────────────────────────────────────────────────────────────

class InverseDesignRequest(BaseModel):
    smiles: str = Field(
        ...,
        description="Polymer SMILES to optimize processing conditions for",
        example="CC(F)(C(F)(F)F)CC(F)(I)"
    )
    target_eb: float = Field(
        ..., gt=0.0,
        description="Target dielectric breakdown strength in MV/m",
        example=700.0
    )
    max_iter: int = Field(
        500, ge=50, le=5000,
        description="Maximum L-BFGS-B optimizer iterations"
    )

class InverseDesignResponse(BaseModel):
    success: bool
    smiles: str
    target_eb: float
    optimal_temp_c: Optional[float]
    optimal_crystallinity: Optional[float]
    predicted_eb: Optional[float]
    absolute_error: Optional[float]
    optimizer_message: str
    model_used: str


# ─────────────────────────────────────────────────────────────────────────────
#  Conditional Search  —  POST /api/conditional-search
# ─────────────────────────────────────────────────────────────────────────────

class ConditionalSearchRequest(BaseModel):
    target_eb: float = Field(
        ..., gt=0.0,
        description="Target Eb in MV/m",
        example=600.0
    )
    polymer_class: str = Field(
        ...,
        description="Polymer family: 'PP', 'PET', or 'PVDF'",
        example="PVDF"
    )
    top_k: int = Field(
        5, ge=1, le=20,
        description="Number of candidate polymers to return"
    )

class CandidatePolymer(BaseModel):
    rank: int
    smiles: str
    polymer_class: str
    target_eb_dataset: float
    eb_delta: float
    processing_temp_c: float
    crystallinity: float

class ConditionalSearchResponse(BaseModel):
    query_target_eb: float
    query_polymer_class: str
    candidates: List[CandidatePolymer]
    total_found: int


# ─────────────────────────────────────────────────────────────────────────────
#  Digital Twin  —  POST /api/twin/predict  |  POST /api/twin/correct
# ─────────────────────────────────────────────────────────────────────────────

class TelemetryInput(BaseModel):
    smiles: str = Field(
        ...,
        description="SMILES of the polymer currently being processed",
        example="CC(F)(C(F)(F)F)CC(F)(I)"
    )
    temperature: float = Field(
        ..., ge=50.0, le=400.0,
        description="Real-time reactor temperature in °C",
        example=235.0
    )
    pressure_bar: float = Field(
        ..., ge=0.5, le=20.0,
        description="Reactor pressure in bar (mapped to crystallinity via empirical curve)",
        example=4.5
    )

class TwinPredictionResponse(BaseModel):
    smiles: str
    temperature: float
    pressure_bar: float
    estimated_crystallinity: float
    predicted_eb: float
    good_fit: bool
    model_used: str

class CorrectionRequest(BaseModel):
    smiles: str
    current_eb: float   = Field(..., description="Currently predicted/measured Eb (MV/m)")
    desired_eb: float   = Field(..., description="Target Eb to correct towards (MV/m)")
    current_temp: float = Field(..., description="Current reactor temperature (°C)")
    current_cryst: float = Field(..., description="Current crystallinity fraction")

class CorrectionResponse(BaseModel):
    delta_temp_c: float          = Field(..., description="Recommended temperature adjustment (°C)")
    delta_crystallinity: float   = Field(..., description="Recommended crystallinity adjustment")
    recommended_temp_c: float
    recommended_crystallinity: float
    projected_eb: float
    projected_error: float

# ─────────────────────────────────────────────────────────────────────────────
#  Generative Design (De Novo GA)  —  POST /api/generative-design
# ─────────────────────────────────────────────────────────────────────────────

class GenerativeDesignRequest(BaseModel):
    target_eb: float = Field(
        ..., gt=0.0,
        description="Target dielectric breakdown strength in MV/m",
        example=650.0
    )
    generations: int = Field(
        10, ge=1, le=50,
        description="Number of genetic algorithm generations"
    )
    pop_size: int = Field(
        30, ge=10, le=200,
        description="Population size per generation"
    )

class GenerativeDesignResponse(BaseModel):
    target_eb: float
    best_smiles: str
    predicted_eb: float
    absolute_error: float
    generations_run: int
