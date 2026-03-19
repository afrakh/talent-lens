import re
import spacy
from typing import Optional

nlp = spacy.load("en_core_web_sm")

class EntityExtractor:
    EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    PHONE_RE = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")

    def extract_email(self, text: str) -> Optional[str]:
        match = self.EMAIL_RE.search(text)
        return match.group(0) if match else None

    def extract_phone(self, text: str) -> Optional[str]:
        match = self.PHONE_RE.search(text)
        return match.group(0) if match else None

    def extract_name(self, text: str) -> Optional[str]:
        doc = nlp(text[:1000])  
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None