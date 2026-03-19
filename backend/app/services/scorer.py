import re
import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

WEIGHTS = {
    "semantic": 0.40,
    "skill":    0.40,
    "llm":      0.20,
}

LLM_MODEL = "llama-3.3-70b-versatile"

class ResumeScorer:
    def __init__(
        self,
        embedding_service,
        use_llm: bool = True,
    ):
        self.embedding_service = embedding_service
        self.use_llm = use_llm

        if use_llm:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError(
                    "GROQ_API_KEY not found — add it to your .env file"
                )
            self.client = Groq(api_key=api_key)

        logger.info("ResumeScorer ready — LLM: %s", "enabled" if use_llm else "disabled")

    def score(
        self,
        jd_text: str,
        resume_text: str,
        jd_skills: list[str],
        resume_skills: list[str],
    ) -> dict:
        
        semantic_score = self.embedding_service.score(jd_text, resume_text)

        skill_score, matched, missing = self._compute_skill_score(
            jd_skills, resume_skills
        )

        if self.use_llm:
            llm_score, llm_reasoning = self._compute_llm_score(
                jd_text, resume_text, matched, missing
            )
        else:
            llm_score, llm_reasoning = 0.0, "LLM scoring disabled"

        final_score = self._weighted_score(semantic_score, skill_score, llm_score)

        logger.debug(
            "Scores — final: %.1f | semantic: %.1f | skill: %.1f | llm: %.1f",
            final_score, semantic_score, skill_score, llm_score
        )

        return {
            "final_score":    final_score,
            "semantic_score": semantic_score,
            "skill_score":    skill_score,
            "llm_score":      llm_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "llm_reasoning":  llm_reasoning,
        }

    def rank_resumes(
        self,
        jd_text: str,
        jd_skills: list[str],
        resumes: dict[str, dict],
    ) -> list[dict]:

        if not resumes:
            logger.warning("rank_resumes called with empty resumes")
            return []

        results = []
        for candidate_id, data in resumes.items():
            result = self.score(
                jd_text=jd_text,
                resume_text=data["text"],
                jd_skills=jd_skills,
                resume_skills=data["skills"],
            )
            results.append({"id": candidate_id, **result})

        results.sort(key=lambda x: x["final_score"], reverse=True)

        logger.debug(
            "Ranked %d resumes — top: %s (%.1f)",
            len(results), results[0]["id"], results[0]["final_score"]
        )

        return results

    def _compute_skill_score(
        self,
        jd_skills: list[str],
        resume_skills: list[str],
    ) -> tuple[float, list[str], list[str]]:
        
        if not jd_skills:
            return 0.0, [], []

        jd_set     = {s.lower() for s in jd_skills}
        resume_set = {s.lower() for s in resume_skills}

        matched = sorted(jd_set & resume_set)
        missing = sorted(jd_set - resume_set)
        score   = round(len(matched) / len(jd_set) * 100, 2)

        return score, matched, missing

    def _compute_llm_score(
        self,
        jd_text: str,
        resume_text: str,
        matched_skills: list[str],
        missing_skills: list[str],
    ) -> tuple[float, str]:
        
        prompt = f"""You are an HR assistant. Score this candidate and write one short sentence (max 20 words) about fit.
 
Job: {jd_text[:500]}
Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}
 
Respond in exactly this format:
SCORE: <0-100>
REASONING: <four to five sentences max, plain English, no jargon>"""

        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.choices[0].message.content.strip()
            return self._parse_llm_response(response_text)

        except Exception as e:
            logger.error("LLM scoring failed: %s", e)
            return 0.0, "LLM scoring failed"

    def _parse_llm_response(self, text: str) -> tuple[float, str]:
        score     = 0.0
        reasoning = "Could not parse LLM response"

        score_match = re.search(r"SCORE:\s*(\d+(?:\.\d+)?)", text)
        if score_match:
            score = min(float(score_match.group(1)), 100.0)

        reasoning_match = re.search(r"REASONING:\s*(.+)", text, re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip()

        return round(score, 2), reasoning

    def _weighted_score(
        self,
        semantic_score: float,
        skill_score: float,
        llm_score: float,
    ) -> float:

        if not self.use_llm:
            half = WEIGHTS["llm"] / 2
            weights = {
                "semantic": WEIGHTS["semantic"] + half,
                "skill":    WEIGHTS["skill"] + half,
                "llm":      0.0,
            }
        else:
            weights = WEIGHTS

        final = (
            semantic_score * weights["semantic"] +
            skill_score    * weights["skill"]    +
            llm_score      * weights["llm"]
        )
        return round(final, 2)