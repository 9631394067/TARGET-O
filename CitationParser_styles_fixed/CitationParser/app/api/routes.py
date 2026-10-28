# ============================================
# app/api/routes.py - FastAPI Routes
# ============================================
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.models.citation import (
    ParseResponse, CitationMetadata, DOILookupRequest,
    TextParseRequest, CitationType
)
from app.core.config import settings
from app.core.pdf_extractor import PDFExtractor
from app.parsers.doi_parser import DOIParser
from app.parsers.metadata_parser import MetadataParser
from app.parsers.bibtex_generator import BibTeXGenerator
from app.services.crossref_service import CrossRefService
from app.services.openai_service import openai_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────────────────────
# Helper: Merge metadata from multiple sources
# Priority: CrossRef > OpenAI > Regex
# ─────────────────────────────────────────────────────────────
def merge_metadata(
    regex_data: dict,
    ai_data: Optional[CitationMetadata],
    crossref_data: Optional[CitationMetadata]
) -> CitationMetadata:
    """Merge metadata from all sources, preferring more reliable sources."""

    # Start with AI data if available, else empty
    base = ai_data or CitationMetadata()

    # Apply regex data where AI/base data is missing
    if not base.title and regex_data.get('title'):
        base.title = regex_data['title']
    if not base.year and regex_data.get('year'):
        base.year = regex_data['year']
    if not base.volume and regex_data.get('volume'):
        base.volume = regex_data['volume']
    if not base.issue and regex_data.get('issue'):
        base.issue = regex_data['issue']
    if not base.pages and regex_data.get('pages'):
        base.pages = regex_data['pages']
    if not base.issn and regex_data.get('issn'):
        base.issn = regex_data['issn']
    if not base.isbn and regex_data.get('isbn'):
        base.isbn = regex_data['isbn']
    if not base.journal and regex_data.get('journal'):
        base.journal = regex_data['journal']
    if not base.keywords and regex_data.get('keywords'):
        base.keywords = regex_data['keywords']
    if not base.abstract and regex_data.get('abstract'):
        base.abstract = regex_data['abstract']
    if not base.publisher and regex_data.get('publisher'):
        base.publisher = regex_data['publisher']
    if not base.institution and regex_data.get('institution'):
        base.institution = regex_data['institution']
    if not base.conference and regex_data.get('conference'):
        base.conference = regex_data['conference']
    if not base.authors and regex_data.get('authors_regex'):
        base.authors = regex_data['authors_regex']

    # CrossRef data OVERRIDES everything (most reliable)
    if crossref_data:
        if crossref_data.title:
            base.title = crossref_data.title
        if crossref_data.authors:
            base.authors = crossref_data.authors
        if crossref_data.year:
            base.year = crossref_data.year
        if crossref_data.doi:
            base.doi = crossref_data.doi
        if crossref_data.journal:
            base.journal = crossref_data.journal
        if crossref_data.conference:
            base.conference = crossref_data.conference
        if crossref_data.volume:
            base.volume = crossref_data.volume
        if crossref_data.issue:
            base.issue = crossref_data.issue
        if crossref_data.pages:
            base.pages = crossref_data.pages
        if crossref_data.publisher:
            base.publisher = crossref_data.publisher
        if crossref_data.issn:
            base.issn = crossref_data.issn
        if crossref_data.citation_type:
            base.citation_type = crossref_data.citation_type
        base.confidence_score = crossref_data.confidence_score
        base.source = "crossref_api"
    elif ai_data:
        base.source = "openai_gpt4o_mini"
    else:
        base.source = "regex_only"
        base.confidence_score = 0.5

    return base




def format_citation(metadata: CitationMetadata, style: str) -> str:
    """Format extracted metadata as a readable APA, IEEE, or MLA reference."""
    style = (style or "APA").strip().upper()
    authors = metadata.authors or []
    title = (metadata.title or "Untitled").strip().rstrip(".")
    year = str(metadata.year or "n.d.")
    journal = (metadata.journal or metadata.conference or "").strip()
    volume = str(metadata.volume or "").strip()
    issue = str(metadata.issue or "").strip()
    pages = str(metadata.pages or "").strip().replace("-", "–")
    doi = f"https://doi.org/{metadata.doi}" if metadata.doi else (metadata.url or "")

    def apa_author(a: str) -> str:
        bits = a.strip().split()
        return f"{bits[-1]}, {' '.join(bits[:-1])}" if len(bits) > 1 else a.strip()

    if style == "APA":
        if len(authors) == 1: author_text = apa_author(authors[0])
        elif len(authors) == 2: author_text = f"{apa_author(authors[0])}, & {apa_author(authors[1])}"
        elif authors: author_text = ", ".join(apa_author(a) for a in authors[:-1]) + f", & {apa_author(authors[-1])}"
        else: author_text = "Unknown author"
        result = f"{author_text} ({year}). {title}."
        if journal: result += f" {journal}"
        if volume: result += f", {volume}"
        if issue: result += f"({issue})"
        if pages: result += f", {pages}"
        result += "." if journal or pages else ""
        if doi: result += f" {doi}"
        return result.strip()

    if style == "IEEE":
        author_text = ", ".join(authors) if authors else "Unknown author"
        result = f'[{1}] {author_text}, "{title},"'
        if journal: result += f" {journal},"
        if volume: result += f" vol. {volume},"
        if issue: result += f" no. {issue},"
        if pages: result += f" pp. {pages},"
        result += f" {year}."
        if doi: result += f" doi: {metadata.doi or doi}."
        return result

    # MLA 9-style journal article entry
    if authors:
        first = authors[0].strip().split()
        first_name = f"{first[-1]}, {' '.join(first[:-1])}" if len(first) > 1 else authors[0]
        author_text = first_name
        if len(authors) == 2: author_text += f", and {authors[1]}"
        elif len(authors) > 2: author_text += ", et al."
    else: author_text = "Unknown author"
    result = f'{author_text}. "{title}."'
    if journal: result += f" {journal}"
    if volume: result += f", vol. {volume}"
    if issue: result += f", no. {issue}"
    if year != "n.d.": result += f", {year}"
    if pages: result += f", pp. {pages}"
    result += "."
    if doi: result += f" {doi}"
    return result.strip()


# ─────────────────────────────────────────────────────────────
# Route 1: Parse PDF Upload
# ─────────────────────────────────────────────────────────────
@router.post("/parse/pdf", response_model=ParseResponse, summary="Parse citation from PDF")
async def parse_pdf(
    file: UploadFile = File(..., description="PDF file to parse"),
    use_ai: bool = Query(True, description="Use OpenAI for enhanced extraction"),
    lookup_crossref: bool = Query(True, description="Lookup DOI in CrossRef API")
):
    """
    **Upload a PDF and extract complete citation metadata.**

    Pipeline:
    1. Extract text from PDF (pdfplumber → PyMuPDF fallback)
    2. Find DOI using regex
    3. Lookup DOI in CrossRef API (free, no key needed)
    4. Use OpenAI GPT to parse non-standard metadata
    5. Merge all sources → generate BibTeX

    Works best with Indian regional journals and conference PDFs.
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Check file size
    pdf_bytes = await file.read()
    size_mb = len(pdf_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_mb:.1f}MB (max {settings.MAX_FILE_SIZE_MB}MB)"
        )

    logger.info(f"Processing PDF: {file.filename} ({size_mb:.2f}MB)")
    errors = []

    # ── Step 1: Extract text ─────────────────────────────────
    full_text, extract_method = PDFExtractor.extract(pdf_bytes)
    first_pages_text = PDFExtractor.get_first_pages_text(pdf_bytes, num_pages=2)

    if not full_text.strip():
        return ParseResponse(
            success=False,
            message="Could not extract text from PDF. It may be a scanned image PDF.",
            errors=["PDF text extraction failed - try OCR preprocessing first"]
        )

    logger.info(f"Text extracted using: {extract_method}, chars: {len(full_text)}")

    # ── Step 2: Extract DOI ──────────────────────────────────
    doi = DOIParser.extract_doi(full_text) or DOIParser.extract_doi(first_pages_text)
    logger.info(f"DOI extracted: {doi}")

    # ── Step 3: Regex metadata extraction ───────────────────
    regex_data = MetadataParser.parse_all(first_pages_text or full_text[:3000])

    # ── Step 4: CrossRef API lookup ──────────────────────────
    crossref_data = None
    if doi and lookup_crossref:
        try:
            crossref_data = await CrossRefService.lookup_doi(doi)
            if crossref_data:
                logger.info(f"CrossRef found: {crossref_data.title[:50] if crossref_data.title else 'No title'}")
        except Exception as e:
            errors.append(f"CrossRef lookup failed: {str(e)}")

    # ── Step 5: OpenAI extraction ────────────────────────────
    ai_data = None
    if use_ai and openai_service.is_available:
        try:
            ai_data = await openai_service.extract_metadata(first_pages_text or full_text)
        except Exception as e:
            errors.append(f"AI extraction failed: {str(e)}")

    # ── Step 6: Merge all sources ────────────────────────────
    metadata = merge_metadata(regex_data, ai_data, crossref_data)

    # Set DOI if found but not in metadata
    if doi and not metadata.doi:
        metadata.doi = doi

    # ── Step 7: Generate BibTeX ──────────────────────────────
    bibtex = BibTeXGenerator.generate(metadata)

    return ParseResponse(
        success=True,
        message=f"Parsed successfully via {metadata.source}",
        metadata=metadata,
        bibtex=bibtex,
        raw_text_preview=full_text[:500],
        errors=errors if errors else None
    )


# ─────────────────────────────────────────────────────────────
# Route 2: DOI Direct Lookup
# ─────────────────────────────────────────────────────────────
@router.post("/parse/doi", response_model=ParseResponse, summary="Lookup metadata by DOI")
async def lookup_doi(request: DOILookupRequest):
    """
    **Provide a DOI and get complete citation metadata from CrossRef.**

    Example DOI: `10.1145/3474123.3474456`
    """
    if not DOIParser.is_valid_doi(request.doi):
        raise HTTPException(
            status_code=400,
            detail="Invalid DOI format. DOI must start with '10.' followed by registrant/suffix"
        )

    metadata = await CrossRefService.lookup_doi(request.doi)

    if not metadata:
        raise HTTPException(
            status_code=404,
            detail=f"DOI '{request.doi}' not found in CrossRef database"
        )

    bibtex = BibTeXGenerator.generate(metadata)
    return ParseResponse(
        success=True,
        message="Metadata retrieved from CrossRef API",
        metadata=metadata,
        bibtex=bibtex
    )


# ─────────────────────────────────────────────────────────────
# Route 3: Parse Raw Citation Text
# ─────────────────────────────────────────────────────────────
@router.post("/parse/text", response_model=ParseResponse, summary="Parse citation text string")
async def parse_text(request: TextParseRequest):
    """
    **Paste an APA/MLA/IEEE formatted citation and get structured metadata + BibTeX.**

    Example (APA):
    `Sharma, R., & Gupta, A. (2023). Deep learning for crop disease detection. Journal of Agricultural Informatics, 14(2), 45-67.`
    """
    errors = []

    # Try OpenAI first
    ai_data = None
    if openai_service.is_available:
        ai_data = await openai_service.parse_citation_text(request.text, request.citation_style)

    # Fallback: try regex on the text
    regex_data = MetadataParser.parse_all(request.text)

    # Try CrossRef if DOI found in text
    crossref_data = None
    doi = DOIParser.extract_doi(request.text)
    if doi:
        crossref_data = await CrossRefService.lookup_doi(doi)

    metadata = merge_metadata(regex_data, ai_data, crossref_data)
    if doi and not metadata.doi:
        metadata.doi = doi

    bibtex = BibTeXGenerator.generate(metadata)
    return ParseResponse(
        success=True,
        message="Citation text parsed successfully",
        metadata=metadata,
        bibtex=bibtex,
        formatted_citation=format_citation(metadata, request.citation_style),
        citation_style=(request.citation_style or "APA").upper(),
        errors=errors if errors else None
    )


# ─────────────────────────────────────────────────────────────
# Route 4: Get BibTeX only
# ─────────────────────────────────────────────────────────────
@router.post("/bibtex/from-doi", response_class=PlainTextResponse, summary="Get BibTeX for DOI")
async def get_bibtex_from_doi(request: DOILookupRequest):
    """
    **Returns raw BibTeX text for a DOI** (no JSON wrapper).
    Ready to paste directly into your .bib file!
    """
    metadata = await CrossRefService.lookup_doi(request.doi)
    if not metadata:
        raise HTTPException(status_code=404, detail=f"DOI not found: {request.doi}")
    return BibTeXGenerator.generate(metadata)


# ─────────────────────────────────────────────────────────────
# Route 5: Health check
# ─────────────────────────────────────────────────────────────
@router.get("/health", summary="Health check")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "openai_enabled": openai_service.is_available,
        "crossref_enabled": True,
    }
