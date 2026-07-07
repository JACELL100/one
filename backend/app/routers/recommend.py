"""Recommendation endpoint: hybrid ranker over fit + performance profile."""

from fastapi import APIRouter

from ..schemas import RecommendRequest, RecommendResponse
from ..services import recommender

router = APIRouter(prefix="/recommend", tags=["recommend"])


@router.post("", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    gait = req.gait.model_dump() if req.gait else None
    result = recommender.recommend(
        length_mm=req.length_mm,
        goals=req.goals.model_dump(),
        gait=gait,
        limit=req.limit,
        # llm_rewrite hook wired in production when LLM creds are present.
        llm_rewrite=None,
    )
    return RecommendResponse(**result)
