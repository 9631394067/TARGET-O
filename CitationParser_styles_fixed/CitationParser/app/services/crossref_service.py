# ============================================
# app/services/crossref_service.py - CrossRef API
# ============================================
import httpx
import logging
from typing import Optional, Dict, Any, List
from app.core.config import settings
from app.models.citation import CitationMetadata, CitationType

logger = logging.getLogger(__name__)


class CrossRefService:
    """
    CrossRef API integration for DOI-based metadata lookup.
    Free API, no key required. Email improves rate limits.

    Docs: https://api.crossref.org/swagger-ui/index.html
    """

    BASE_URL = "https://api.crossref.org/works"
    HEADERS = {
        "User-Agent": f"CitationParser/1.0 (mailto:{settings.CROSSREF_EMAIL})"
    }
    TIMEOUT = 15.0

    @classmethod
    async def lookup_doi(cls, doi: str) -> Optional[CitationMetadata]:
        """
        Look up metadata for a DOI from CrossRef API.
        Returns CitationMetadata or None if not found.
        """
        clean_doi = doi.strip().lstrip('https://doi.org/').lstrip('http://dx.doi.org/')

        url = f"{cls.BASE_URL}/{clean_doi}"
        logger.info(f"CrossRef lookup: {url}")

        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                response = await client.get(url, headers=cls.HEADERS)

                if response.status_code == 200:
                    data = response.json()
                    return cls._parse_crossref_response(data.get('message', {}))
                elif response.status_code == 404:
                    logger.warning(f"DOI not found in CrossRef: {doi}")
                    return None
                else:
                    logger.warning(f"CrossRef returned {response.status_code} for {doi}")
                    return None

        except httpx.TimeoutException:
            logger.error(f"CrossRef timeout for DOI: {doi}")
            return None
        except Exception as e:
            logger.error(f"CrossRef API error: {e}")
            return None

    @classmethod
    async def search_by_title(cls, title: str, limit: int = 3) -> List[Dict]:
        """Search CrossRef by paper title."""
        try:
            async with httpx.AsyncClient(timeout=cls.TIMEOUT) as client:
                params = {
                    "query.title": title,
                    "rows": limit,
                    "select": "DOI,title,author,published-print,container-title,volume,issue,page,ISSN"
                }
                response = await client.get(
                    cls.BASE_URL,
                    params=params,
                    headers=cls.HEADERS
                )
                if response.status_code == 200:
                    items = response.json().get('message', {}).get('items', [])
                    return items
        except Exception as e:
            logger.error(f"CrossRef title search error: {e}")
        return []

    @classmethod
    def _parse_crossref_response(cls, msg: Dict) -> CitationMetadata:
        """Parse CrossRef API response into CitationMetadata."""

        # Authors
        authors = []
        for author in msg.get('author', []):
            given = author.get('given', '')
            family = author.get('family', '')
            if family:
                full = f"{given} {family}".strip()
                authors.append(full)

        # Year
        year = None
        date_parts = (
            msg.get('published-print', {}).get('date-parts', [[None]]) or
            msg.get('published-online', {}).get('date-parts', [[None]]) or
            [[None]]
        )
        if date_parts and date_parts[0] and date_parts[0][0]:
            year = str(date_parts[0][0])

        # Title
        titles = msg.get('title', [])
        title = titles[0] if titles else None

        # Journal / Conference
        containers = msg.get('container-title', [])
        journal = containers[0] if containers else None

        # Type
        crossref_type = msg.get('type', 'journal-article')
        if crossref_type in ['proceedings-article', 'paper-conference']:
            citation_type = CitationType.INPROCEEDINGS
        elif crossref_type == 'journal-article':
            citation_type = CitationType.ARTICLE
        else:
            citation_type = CitationType.MISC

        # ISSN
        issns = msg.get('ISSN', [])
        issn = issns[0] if issns else None

        # Pages
        page = msg.get('page')

        return CitationMetadata(
            title=title,
            authors=authors if authors else None,
            year=year,
            doi=msg.get('DOI'),
            journal=journal if citation_type == CitationType.ARTICLE else None,
            conference=journal if citation_type == CitationType.INPROCEEDINGS else None,
            volume=str(msg.get('volume', '')) or None,
            issue=str(msg.get('issue', '')) or None,
            pages=page,
            publisher=msg.get('publisher'),
            issn=issn,
            citation_type=citation_type,
            confidence_score=0.95,  # CrossRef data is highly reliable
            source="crossref_api"
        )
