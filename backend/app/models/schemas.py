from pydantic import BaseModel
from typing import Optional

class ResumeParseResponse(BaseModel):
    candidate_id:   str
    name:           Optional[str]
    email:          Optional[str]
    phone:          Optional[str]
    skills:         list[str]
    skills_by_category: dict[str, list[str]]
    sections:       dict[str, str]
    skills_source:  str
    extraction_method: str


class JDRequest(BaseModel):
    jd_text: str


class JDParseResponse(BaseModel):
    jd_text:  str
    skills:   list[str]


class ScoreRequest(BaseModel):
    jd_text:        str
    jd_skills:      list[str]
    candidate_id:   str
    resume_text:    str
    resume_skills:  list[str]


class ScoreResponse(BaseModel):
    candidate_id:   str
    final_score:    float
    semantic_score: float
    skill_score:    float
    llm_score:      float
    matched_skills: list[str]
    missing_skills: list[str]
    llm_reasoning:  str


class RankRequest(BaseModel):
    jd_text:   str
    jd_skills: list[str]
    resumes:   dict[str, dict]  # {candidate_id: {"text": str, "skills": list[str]}}


class RankResponse(BaseModel):
    rankings: list[ScoreResponse]