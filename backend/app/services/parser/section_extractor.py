import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)
SECTION_HEADERS: dict[str, list[str]] = {
    "contact": [
        "contact", "contact information", "personal information",
        "personal details", "contact details"
    ],
    "summary": [
        "summary", "professional summary", "objective",
        "career objective", "profile", "about me", "overview"
    ],
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "work history", "career history",
        "internship", "internships"
    ],
    "education": [
        "education", "academic background", "educational background",
        "qualifications", "academic qualifications", "degrees"
    ],
    "skills": [
        "skills", "technical skills", "core skills", "key skills",
        "soft skills", "competencies", "proficiencies",
        "expertise", "abilities", "capabilities", "tech stack",
        "tools and technologies", "technologies"
    ],
    "projects": [
        "projects", "personal projects", "academic projects",
        "key projects", "notable projects"
    ],
    "certifications": [
        "certifications", "certificates", "licences", "licenses",
        "professional certifications", "accreditations"
    ],
    "languages": [
        "languages", "language skills", "spoken languages"
    ],
    "awards": [
        "awards", "honors", "achievements", "accomplishments",
        "recognition"
    ],
    "publications": [
        "publications", "research", "papers", "articles"
    ],
    "references": [
        "references", "referees"
    ],
}

_HEADER_LOOKUP: dict[str, str] = {
    alias: section
    for section, aliases in SECTION_HEADERS.items()
    for alias in aliases
}


class SectionExtractor:
    _MAX_HEADING_WORDS = 4

    def _identify_section(self, line: str) -> Optional[str]:
        stripped = line.strip().lower()
        stripped = re.sub(r'[:\-]+$', '', stripped).strip()  # remove trailing : or -

        if not stripped:
            return None

        if stripped in _HEADER_LOOKUP:
            return _HEADER_LOOKUP[stripped]

        if len(stripped.split()) <= self._MAX_HEADING_WORDS:
            for alias, section in _HEADER_LOOKUP.items():
                if alias in stripped:
                    return section

        return None

    def extract_all(self, text: str) -> dict[str, str]:
        lines = text.splitlines()
        sections: dict[str, str] = {}

        current_section: Optional[str] = None
        current_lines: list[str] = []

        for line in lines:
            section = self._identify_section(line)

            if section:
                if current_section and current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()

                current_section = section
                current_lines = []
            else:
                if current_section:
                    current_lines.append(line)

        if current_section and current_lines:
            sections[current_section] = "\n".join(current_lines).strip()

        if not sections:
            logger.warning("No sections detected — headings may be unrecognised")
        else:
            logger.debug("Detected sections: %s", list(sections.keys()))

        return sections

    def extract_section(self, text: str, section: str) -> Optional[str]:
        sections = self.extract_all(text)
        result = sections.get(section)

        if result is None:
            logger.debug("Section '%s' not found in resume", section)

        return result