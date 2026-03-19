import logging
from fastapi import APIRouter, HTTPException

from app.services.parser.skill_extractor import SkillExtractor
from app.models.schemas import JDRequest, JDParseResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jd", tags=["Job Description"])

skill_extractor = SkillExtractor()


@router.post("/parse", response_model=JDParseResponse)
async def parse_jd(request: JDRequest):
    if not request.jd_text.strip():
        raise HTTPException(status_code=400, detail="JD text cannot be empty")

    try:
        result = skill_extractor.extract(cleaned_text=request.jd_text)

        return JDParseResponse(
            jd_text = request.jd_text,
            skills  = result["found"],
        )

    except Exception as e:
        logger.error("JD parsing failed: %s", e)
        raise HTTPException(status_code=500, detail="JD parsing failed")