# ============================================
# app/services/openai_service.py - OpenAI API for Smart Extraction
# ============================================
import json
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

# Support both openai v1.x and v3.x
try:
    from openai import AsyncOpenAI
    _OPENAI_NEW = True
except ImportError:
    AsyncOpenAI = None
    _OPENAI_NEW = False
from app.models.citation import CitationMetadata, CitationType

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Uses OpenAI GPT to extract citation metadata from non-standard
    Indian journal PDFs where regex fails.

    This is the fallback / enhancement layer on top of regex parsing.
    """

    # System prompt for citation extraction
    SYSTEM_PROMPT = """You are an expert academic citation parser specializing in Indian regional journals and conference proceedings.

Your task is to extract citation metadata from PDF text and return it as structured JSON.

Rules:
1. Extract ONLY information present in the text - do NOT hallucinate
2. For Indian journals, watch for: authors listed below title, ISSN in header/footer
3. Return null for fields you cannot find
4. Authors should be in format: ["First Last", "First Last"]
5. Year should be 4-digit string
6. DOI if present should start with "10."
7. Determine if it's a journal article or conference paper

Return ONLY valid JSON, no markdown, no explanation."""

    EXTRACTION_PROMPT = """Extract citation metadata from this PDF text and return as JSON with these fields:
{
  "title": "paper title or null",
  "authors": ["Author 1", "Author 2"] or null,
  "year": "YYYY" or null,
  "doi": "10.XXXX/..." or null,
  "journal": "journal name if journal article, else null",
  "conference": "conference name if conference paper, else null",
  "volume": "volume number or null",
  "issue": "issue number or null",
  "pages": "start-end or null",
  "publisher": "publisher name or null",
  "issn": "XXXX-XXXX or null",
  "abstract": "first 300 chars of abstract or null",
  "keywords": ["kw1", "kw2"] or null,
  "institution": "author institution or null",
  "citation_type": "article" or "inproceedings" or "misc"
}

PDF Text (first 3000 characters):
"""

    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_api_key_here":
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")
        else:
            logger.warning("OpenAI API key not set - AI extraction disabled")

    @property
    def is_available(self) -> bool:
        return self.client is not None

    async def extract_metadata(self, text: str) -> Optional[CitationMetadata]:
        """
        Use GPT to extract metadata from PDF text.
        Returns CitationMetadata or None if extraction fails.
        """
        if not self.is_available:
            logger.info("OpenAI not available, skipping AI extraction")
            return None

        # Use first 3000 chars (metadata is usually in first page)
        text_sample = text[:3000]

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap, good for structured extraction
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": self.EXTRACTION_PROMPT + text_sample}
                ],
                temperature=0.1,   # Low temperature for consistent extraction
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            raw_json = response.choices[0].message.content
            logger.info(f"OpenAI response: {raw_json[:200]}...")

            return self._parse_ai_response(raw_json)

        except Exception as e:
            logger.error(f"OpenAI extraction error: {e}")
            return None

    @staticmethod
    def _parse_ai_response(raw_json: str) -> Optional[CitationMetadata]:
        """Parse OpenAI JSON response into CitationMetadata."""
        try:
            data: Dict[str, Any] = json.loads(raw_json)

            # Map citation_type string to enum
            ct_str = data.get('citation_type', 'article').lower()
            if ct_str == 'inproceedings':
                ct = CitationType.INPROCEEDINGS
            elif ct_str == 'article':
                ct = CitationType.ARTICLE
            else:
                ct = CitationType.MISC

            return CitationMetadata(
                title=data.get('title'),
                authors=data.get('authors'),
                year=data.get('year'),
                doi=data.get('doi'),
                journal=data.get('journal'),
                conference=data.get('conference'),
                volume=str(data.get('volume', '')) or None,
                issue=str(data.get('issue', '')) or None,
                pages=data.get('pages'),
                publisher=data.get('publisher'),
                issn=data.get('issn'),
                abstract=data.get('abstract'),
                keywords=data.get('keywords'),
                institution=data.get('institution'),
                citation_type=ct,
                confidence_score=0.85,
                source="openai_gpt4o_mini"
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return None

    async def parse_citation_text(self, citation_text: str, style: str = "APA") -> Optional[CitationMetadata]:
        """
        Parse a raw citation string (APA/MLA/IEEE format) into structured metadata.
        """
        if not self.is_available:
            return None

        prompt = f"""Parse this {style} formatted citation into structured JSON:

Citation: {citation_text}

Return JSON with fields: title, authors (list), year, doi, journal, conference, volume, issue, pages, publisher, citation_type"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a citation parser. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            return self._parse_ai_response(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Citation text parse error: {e}")
            return None


# Singleton instance
openai_service = OpenAIService()
