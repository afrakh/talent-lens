import pytesseract
from PIL import Image
import fitz
import io
import logging

logger = logging.getLogger(__name__)


class OCRReader:
    def extract_text_from_pdf(self, file) -> str:
        text = ""

        try:
            if isinstance(file, str):
                doc = fitz.open(file)
            else:
                doc = fitz.open(stream=file, filetype="pdf")

            for page in doc:
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                text += pytesseract.image_to_string(img)

            doc.close()

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")

        return text