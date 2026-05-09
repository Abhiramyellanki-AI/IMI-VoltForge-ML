"""
Router: POST /api/generative-design
Triggers the Genetic Algorithm to synthesize a De Novo polymer for a target Eb.
"""
import os
import sys
from fastapi import APIRouter, HTTPException

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..')
)
sys.path.insert(0, _PROJECT_ROOT)

from production.backend.models.schemas import GenerativeDesignRequest, GenerativeDesignResponse
from code_11_generative_design import run_genetic_algorithm

router = APIRouter(prefix="/api", tags=["Generative Design"])

@router.post("/generative-design", response_model=GenerativeDesignResponse)
def generative_design(body: GenerativeDesignRequest):
    """
    De Novo Generative Design endpoint.
    Runs the Genetic Algorithm for the given target_eb, generating novel
    valid SMILES strings using mutation and crossover operations.
    """
    try:
        result = run_genetic_algorithm(
            target_eb=body.target_eb,
            generations=body.generations,
            pop_size=body.pop_size
        )
        
        if result['best_smiles'] is None:
            raise HTTPException(status_code=500, detail="Genetic Algorithm failed to generate any valid molecules.")
            
        return GenerativeDesignResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
