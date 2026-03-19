import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.resume  import router as resume_router
from app.routes.jd      import router as jd_router
from app.routes.scoring import router as scoring_router

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Screening API",
    description="Parse resumes, extract skills, score and rank candidates against a JD.",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(resume_router)
app.include_router(jd_router)
app.include_router(scoring_router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "Resume Screening API is running"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}