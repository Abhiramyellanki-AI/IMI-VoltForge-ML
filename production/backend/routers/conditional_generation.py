"""
Router: POST /api/conditional-search
Conditional polymer generation — given (target_eb, polymer_class), returns top-K
structurally diverse polymer candidates from the dataset.
Directly wraps code_10_conditional_search.search_by_eb_and_class().
"""
import os
import sys
from fastapi import APIRouter, HTTPException

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
)
sys.path.insert(0, _PROJECT_ROOT)

from production.backend.models.schemas import (
    ConditionalSearchRequest,
    ConditionalSearchResponse,
    CandidatePolymer,
)
from code_10_conditional_search import search_by_eb_and_class

router = APIRouter(prefix="/api", tags=["Conditional Generation"])


@router.post("/conditional-search", response_model=ConditionalSearchResponse)
def conditional_search(body: ConditionalSearchRequest):
    """
    Conditional polymer search endpoint.

    Filters the dataset by polymer class, ranks candidates by proximity
    to the target Eb, then applies a greedy max-min Morgan diversity
    re-ranking to return structurally varied top-K candidates.
    """
    try:
        raw_results = search_by_eb_and_class(
            target_eb     = body.target_eb,
            polymer_class = body.polymer_class,
            top_k         = body.top_k,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")

    candidates = [CandidatePolymer(**r) for r in raw_results]

    return ConditionalSearchResponse(
        query_target_eb    = body.target_eb,
        query_polymer_class = body.polymer_class.upper(),
        candidates         = candidates,
        total_found        = len(candidates),
    )
