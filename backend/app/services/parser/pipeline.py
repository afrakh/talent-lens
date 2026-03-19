import logging
from typing import Union
from pathlib import Path
from dataclasses import dataclass, field

from app.services.parser.pdf_reader import PDFReader
from app.services.parser.ocr_reader import OCRReader
from app.services.parser.preprocessor import TextPreprocessor
from app.services.parser.entity_extractor import EntityExtractor
from app.services.parser.section_extractor import SectionExtractor
from app.services.parser.skill_extractor import SkillExtractor

logger = logging.getLogger(__name__)

_TAXONOMY_PATH = Path(__file__).parent / "data" / "common_skills.json"
@dataclass
class ResumeResult:
    name:               str | None
    email:              str | None
    phone:              str | None
    skills:             list[str]       = field(default_factory=list)
    skills_by_category: dict            = field(default_factory=dict)
    sections:           dict[str, str]  = field(default_factory=dict)
    skills_source:      str             = "unknown"
    extraction_method:  str             = "unknown"


class ResumePipeline:

    def __init__(self, taxonomy_path: str = _TAXONOMY_PATH):
        self.pdf_reader        = PDFReader()
        self.ocr_reader        = OCRReader()
        self.preprocessor      = TextPreprocessor()
        self.entity_extractor  = EntityExtractor()
        self.section_extractor = SectionExtractor()
        self.skill_extractor   = SkillExtractor(taxonomy_path=taxonomy_path)

    def process(self, file: Union[str, bytes]) -> ResumeResult:
        # Step 1: Extract raw text
        raw_text, extraction_method = self._extract_text(file)

        if not raw_text.strip():
            logger.error("Could not extract any text from resume")
            return ResumeResult(
                name=None, email=None, phone=None,
                extraction_method="failed"
            )

        soft_cleaned = self.preprocessor.clean_for_sections(raw_text)

        sections = self.section_extractor.extract_all(soft_cleaned)

        name  = self.entity_extractor.extract_name(raw_text)
        email = self.entity_extractor.extract_email(raw_text)
        phone = self.entity_extractor.extract_phone(raw_text)

        skill_text     = self.preprocessor.clean_for_skills(raw_text)
        skill_sections = {
            k: self.preprocessor.clean_for_skills(v)
            for k, v in sections.items()
        }

        skill_result = self.skill_extractor.extract(
            cleaned_text=skill_text,
            sections=skill_sections
        )

        return ResumeResult(
            name              = name,
            email             = email,
            phone             = phone,
            skills            = skill_result["found"],
            skills_by_category= skill_result["by_category"],
            sections          = sections,
            skills_source     = skill_result["source"],
            extraction_method = extraction_method,
        )

    def _extract_text(self, file: Union[str, bytes]) -> tuple[str, str]:
        text = self.pdf_reader.extract_text(file)
        if text.strip():
            return text, "pdf_reader"

        logger.warning("PDFReader returned empty — trying OCR fallback")
        text = self.ocr_reader.extract_text_from_pdf(file)
        if text.strip():
            return text, "ocr_reader"

        return "", "failed"