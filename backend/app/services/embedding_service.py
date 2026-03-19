from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self._cache: dict[str, np.ndarray] = {}
        logger.info("EmbeddingService ready, model: %s", model_name)

    def _encode(self, text: str) -> np.ndarray:
        if text not in self._cache:
            self._cache[text] = self.model.encode(text, convert_to_numpy=True)
        return self._cache[text]

    def _similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        score = cosine_similarity([vec_a], [vec_b])[0][0]
        return round(float(score) * 100, 2)

    def score(self, jd_text: str, resume_text: str) -> float:
        jd_vec     = self._encode(jd_text)
        resume_vec = self._encode(resume_text)
        return self._similarity(jd_vec, resume_vec)

    def rank_resumes(
        self,
        jd_text: str,
        resumes: dict[str, str],
    ) -> list[dict]:
        if not resumes:
            logger.warning("rank_resumes called with empty resumes dict")
            return []

        jd_vec = self._encode(jd_text)

        results = []
        for candidate_id, resume_text in resumes.items():
            resume_vec = self._encode(resume_text)
            results.append({
                "id":    candidate_id,
                "score": self._similarity(jd_vec, resume_vec),
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        logger.debug(
            "Ranked %d resumes — top score: %s (id: %s)",
            len(results), results[0]["score"], results[0]["id"]
        )

        return results

    def clear_cache(self) -> None:
        self._cache.clear()
        logger.debug("Embedding cache cleared")