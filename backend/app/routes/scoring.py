import logging
from fastapi import APIRouter, HTTPException

from app.services.embedding_service import EmbeddingService
from app.services.scorer import ResumeScorer
from app.models.schemas import (
    ScoreRequest, ScoreResponse,
    RankRequest, RankResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scoring", tags=["Scoring"])

embedding_service = EmbeddingService()
scorer            = ResumeScorer(embedding_service)


@router.post("/score", response_model=ScoreResponse)
async def score_one(request: ScoreRequest):
    try:
        result = scorer.score(
            jd_text       = request.jd_text,
            resume_text   = request.resume_text,
            jd_skills     = request.jd_skills,
            resume_skills = request.resume_skills,
        )

        return ScoreResponse(
            candidate_id   = request.candidate_id,
            final_score    = result["final_score"],
            semantic_score = result["semantic_score"],
            skill_score    = result["skill_score"],
            llm_score      = result["llm_score"],
            matched_skills = result["matched_skills"],
            missing_skills = result["missing_skills"],
            llm_reasoning  = result["llm_reasoning"],
        )

    except Exception as e:
        logger.error("Scoring failed: %s", e)
        raise HTTPException(status_code=500, detail="Scoring failed")


@router.post("/rank", response_model=RankResponse)
async def rank_resumes(request: RankRequest):
    if not request.resumes:
        raise HTTPException(status_code=400, detail="No resumes provided")

    try:
        ranked = scorer.rank_resumes(
            jd_text   = request.jd_text,
            jd_skills = request.jd_skills,
            resumes   = request.resumes,
        )

        rankings = [
            ScoreResponse(
                candidate_id   = r["id"],
                final_score    = r["final_score"],
                semantic_score = r["semantic_score"],
                skill_score    = r["skill_score"],
                llm_score      = r["llm_score"],
                matched_skills = r["matched_skills"],
                missing_skills = r["missing_skills"],
                llm_reasoning  = r["llm_reasoning"],
            )
            for r in ranked
        ]

        return RankResponse(rankings=rankings)

    except Exception as e:
        logger.error("Ranking failed: %s", e)
        raise HTTPException(status_code=500, detail="Ranking failed")