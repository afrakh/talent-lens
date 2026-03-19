import pdfplumber
import fitz
import logging

logger = logging.getLogger(__name__)


class PDFReader:
    def extract_text(self, file) -> str:
        text = ""

        try:
            if isinstance(file, str):
                with pdfplumber.open(file) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)

            elif isinstance(file, bytes):
                doc = fitz.open(stream=file, filetype="pdf")
                text = "\n".join(page.get_text() for page in doc)
                doc.close()

            if text.strip():
                return text

        except Exception as e:
            logger.warning(f"Primary PDF extraction failed: {e}")

        try:
            if isinstance(file, str):
                doc = fitz.open(file)
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
                return text
        except Exception as e:
            logger.error(f"Fallback extraction failed: {e}")

        return ""