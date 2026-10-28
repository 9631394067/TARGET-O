# ============================================
# app/core/pdf_extractor.py - PDF Text Extraction
# ============================================
import pdfplumber
import io
import logging
from typing import Tuple

# Fix deprecated fitz import
try:
    import pymupdf as fitz
except ImportError:
    import fitz  # fallback to old name

logger = logging.getLogger(__name__)


class PDFExtractor:
    """
    Extracts text from PDF files using two engines:
    1. pdfplumber  - primary (better for text-based PDFs)
    2. PyMuPDF    - fallback (faster, handles more formats)
    """

    @staticmethod
    def extract_text_pdfplumber(pdf_bytes: bytes) -> Tuple[str, bool]:
        try:
            full_text = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        full_text.append(f"--- Page {page_num + 1} ---\n{text}")
            combined = "\n\n".join(full_text)
            if combined.strip():
                logger.debug(f"pdfplumber extracted {len(combined)} characters")
                return combined, True
            return "", False
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}")
            return "", False

    @staticmethod
    def extract_text_pymupdf(pdf_bytes: bytes) -> Tuple[str, bool]:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            full_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    full_text.append(f"--- Page {page_num + 1} ---\n{text}")
            doc.close()
            combined = "\n\n".join(full_text)
            if combined.strip():
                logger.debug(f"PyMuPDF extracted {len(combined)} characters")
                return combined, True
            return "", False
        except Exception as e:
            logger.warning(f"PyMuPDF failed: {e}")
            return "", False

    @classmethod
    def extract(cls, pdf_bytes: bytes) -> Tuple[str, str]:
        """Try both extractors, return best result. Returns: (text, method_used)"""
        text, success = cls.extract_text_pdfplumber(pdf_bytes)
        if success and len(text) > 100:
            return text, "pdfplumber"

        text, success = cls.extract_text_pymupdf(pdf_bytes)
        if success and len(text) > 100:
            return text, "pymupdf"

        text, _ = cls.extract_text_pdfplumber(pdf_bytes)
        return text, "pdfplumber_fallback"

    @staticmethod
    def get_first_pages_text(pdf_bytes: bytes, num_pages: int = 2) -> str:
        """Get text from first N pages only (metadata is usually on page 1-2)."""
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                texts = []
                for i, page in enumerate(pdf.pages[:num_pages]):
                    text = page.extract_text()
                    if text:
                        texts.append(text)
                return "\n\n".join(texts)
        except Exception:
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                texts = []
                for i in range(min(num_pages, len(doc))):
                    texts.append(doc[i].get_text())
                doc.close()
                return "\n\n".join(texts)
            except Exception as e:
                logger.error(f"Both extractors failed for first pages: {e}")
                return ""
