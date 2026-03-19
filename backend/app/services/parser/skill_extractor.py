import re
import json
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
_DEFAULT_TAXONOMY = Path(__file__).parent / "data" / "common_skills.json"
 
SYNONYMS = {
    # Programming
    "py":        "python",
    "js":        "javascript",
    "ts":        "typescript",
    "node":      "node.js",
    "reactjs":   "react",
    "react.js":  "react",
    "nextjs":    "next.js",
    "k8s":       "kubernetes",
    "tf":        "tensorflow",
    "sklearn":   "scikit-learn",
    # ML / AI
    "ml":        "machine learning",
    "ai":        "artificial intelligence",
    "dl":        "deep learning",
    "nlp":       "natural language processing",
    "cv":        "computer vision",
    # Business / Tools
    "pm":        "project management",
    "ba":        "business analysis",
    "bi":        "business intelligence",
    "hr":        "human resources",
    "crm":       "customer relationship management",
    "powerbi":   "power bi",
    "aws":       "amazon web services",
    "gcp":       "google cloud platform",
    "ga":        "google analytics",
    "sf":        "salesforce",
}


class SkillExtractor:
    def __init__(self, taxonomy_path: str = str(_DEFAULT_TAXONOMY)):
        self.taxonomy_path = Path(taxonomy_path)
        self.category_map: dict[str, list[str]] = self._load_taxonomy()

        self.skills_list: list[str] = sorted(
            {skill for skills in self.category_map.values() for skill in skills},
            key=len,
            reverse=True
        )

        self._patterns: dict[str, re.Pattern] = self._build_patterns()

        logger.info(
            "SkillExtractor ready — %d skills across %d categories",
            len(self.skills_list), len(self.category_map)
        )

    
    def _load_taxonomy(self) -> dict[str, list[str]]:
        if not self.taxonomy_path.is_file():
            raise FileNotFoundError(f"Skills file missing: {self.taxonomy_path}")

        with self.taxonomy_path.open(encoding="utf-8") as f:
            data = json.load(f)

        skills_dict = data.get("skills", {})
        if not isinstance(skills_dict, dict):
            raise ValueError("'skills' in JSON must be a dict of {category: [skill, ...]}")

        return {
            category: [s.strip() for s in skill_list if s.strip()]
            for category, skill_list in skills_dict.items()
            if isinstance(skill_list, list)
        }

    def _build_patterns(self) -> dict[str, re.Pattern]:
        return {
            skill: re.compile(rf"\b{re.escape(skill.lower())}\b", re.IGNORECASE)
            for skill in self.skills_list
        }

    
    def _replace_synonyms(self, text: str) -> str:
        for abbr, full in SYNONYMS.items():
            text = re.sub(rf"\b{re.escape(abbr)}\b", full, text, flags=re.IGNORECASE)
        return text

    def _get_priority_text(
        self,
        cleaned_text: str,
        sections: Optional[dict[str, str]]
    ) -> tuple[str, str]:
        
        if sections and "skills" in sections:
            return sections["skills"], "skills_section"

        return cleaned_text, "full_text"

    def _match_skills(self, text: str) -> set[str]:
        return {
            skill for skill, pattern in self._patterns.items()
            if pattern.search(text)
        }

    def _group_by_category(self, found: set[str]) -> dict[str, list[str]]:
        return {
            category: sorted(set(skills) & found)
            for category, skills in self.category_map.items()
            if set(skills) & found
        }

    def extract(
        self,
        cleaned_text: str,
        sections: Optional[dict[str, str]] = None
    ) -> dict:
       
        search_text, source = self._get_priority_text(cleaned_text, sections)

        search_text = self._replace_synonyms(search_text)

        found = self._match_skills(search_text)

        if not found:
            logger.warning("No skills detected — source: %s", source)
        else:
            logger.debug("Matched %d skills — source: %s", len(found), source)

        return {
            "found":       sorted(found),
            "by_category": self._group_by_category(found),
            "count":       len(found),
            "source":      source,
        }