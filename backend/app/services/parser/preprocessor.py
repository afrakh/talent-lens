import re


class TextPreprocessor:
    def clean_for_sections(self, text: str) -> str:
        text = re.sub(r'[ \t]+', ' ', text)       
        text = re.sub(r'\n{3,}', '\n\n', text)    
        return text.strip()

    def clean_for_skills(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^a-z0-9 +.#]', ' ', text)
        return text.strip()