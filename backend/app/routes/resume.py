import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.parser.pipeline import ResumePipeline
from app.models.schemas import ResumeParseResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resume", tags=["Resume"])

pipeline = ResumePipeline()


@router.post("/parse", response_model=ResumeParseResponse)
async def parse_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    try:
        pdf_bytes = await file.read()
        result    = pipeline.process(pdf_bytes)

        if result.extraction_method == "failed":
            raise HTTPException(status_code=422, detail="Could not extract text from PDF")

        return ResumeParseResponse(
            candidate_id      = str(uuid.uuid4()),
            name              = result.name,
            email             = result.email,
            phone             = result.phone,
            skills            = result.skills,
            skills_by_category= result.skills_by_category,
            sections          = result.sections,
            skills_source     = result.skills_source,
            extraction_method = result.extraction_method,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Resume parsing failed: %s", e)
        raise HTTPException(status_code=500, detail="Resume parsing failed")


@router.post("/parse-multiple", response_model=list[ResumeParseResponse])
async def parse_multiple_resumes(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    results = []
    for file in files:
        if not file.filename.endswith(".pdf"):
            logger.warning("Skipping non-PDF file: %s", file.filename)
            continue

        try:
            pdf_bytes = await file.read()
            result    = pipeline.process(pdf_bytes)

            results.append(ResumeParseResponse(
                candidate_id      = str(uuid.uuid4()),
                name              = result.name,
                email             = result.email,
                phone             = result.phone,
                skills            = result.skills,
                skills_by_category= result.skills_by_category,
                sections          = result.sections,
                skills_source     = result.skills_source,
                extraction_method = result.extraction_method,
            ))

        except Exception as e:
            logger.error("Failed to parse %s: %s", file.filename, e)
            continue

    if not results:
        raise HTTPException(status_code=422, detail="No resumes could be parsed")

    return results