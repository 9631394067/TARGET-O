# ============================================
# app/parsers/doi_parser.py - DOI Extraction
# ============================================
import re
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)


class DOIParser:
    """
    Extracts DOI from PDF text using multiple regex patterns.
    Handles various Indian journal DOI formats.
    """

    # Common DOI patterns
    DOI_PATTERNS = [
        # Standard: 10.XXXX/something
        r'\b(10\.\d{4,9}/[^\s,;"\'\)\]>]+)',

        # With "DOI:" prefix
        r'(?:DOI|doi|Doi)\s*[:\s]\s*(10\.\d{4,9}/[^\s,;"\'\)\]>]+)',

        # With "https://doi.org/" prefix
        r'https?://(?:dx\.)?doi\.org/(10\.\d{4,9}/[^\s,;"\'\)\]>]+)',

        # In brackets [DOI: ...]
        r'\[(?:DOI|doi)\s*:\s*(10\.\d{4,9}/[^\s,;"\'\)\]>]+)\]',

        # Indian journal format: doi:10.XXXX
        r'doi\s*:\s*(10\.[0-9]{4}/[^\s]+)',
    ]

    # Chars to strip from end of DOI (common OCR artifacts)
    TRAILING_JUNK = r'[.,;:)\]}"\']+$'

    @classmethod
    def extract_doi(cls, text: str) -> Optional[str]:
        """
        Extract the first valid DOI from text.
        Returns cleaned DOI string or None.
        """
        for pattern in cls.DOI_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                doi = matches[0]
                doi = re.sub(cls.TRAILING_JUNK, '', doi).strip()
                if cls.is_valid_doi(doi):
                    logger.info(f"DOI found: {doi}")
                    return doi

        return None

    @classmethod
    def extract_all_dois(cls, text: str) -> List[str]:
        """Extract all DOIs from text (for multi-reference documents)."""
        found = set()
        for pattern in cls.DOI_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for doi in matches:
                doi = re.sub(cls.TRAILING_JUNK, '', doi).strip()
                if cls.is_valid_doi(doi):
                    found.add(doi)
        return list(found)

    @staticmethod
    def is_valid_doi(doi: str) -> bool:
        """Validate DOI format: must start with 10. followed by registrant code."""
        if not doi:
            return False
        # DOI must start with 10. and have a slash
        pattern = r'^10\.\d{4,9}/.+'
        return bool(re.match(pattern, doi))

    @staticmethod
    def clean_doi(doi: str) -> str:
        """
        Clean a DOI string:
        - Remove URL prefix if present
        - Remove trailing junk
        - Lowercase
        """
        # Remove URL prefix
        doi = re.sub(r'https?://(?:dx\.)?doi\.org/', '', doi, flags=re.IGNORECASE)
        # Remove trailing junk
        doi = re.sub(r'[.,;:)\]}"\']+$', '', doi).strip()
        return doi.lower()

    @staticmethod
    def to_url(doi: str) -> str:
        """Convert DOI to full URL."""
        clean = doi.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
        return f"https://doi.org/{clean}"
