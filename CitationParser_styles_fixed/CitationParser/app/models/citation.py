# ============================================
# app/models/citation.py - Data Models
# ============================================
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class CitationType(str, Enum):
    ARTICLE = "article"
    INPROCEEDINGS = "inproceedings"
    CONFERENCE = "conference"
    TECHREPORT = "techreport"
    MISC = "misc"


class CitationMetadata(BaseModel):
    """Complete citation metadata model"""

    # Core Fields
    title: Optional[str] = Field(None, description="Paper title")
    authors: Optional[List[str]] = Field(None, description="List of authors")
    year: Optional[str] = Field(None, description="Publication year")
    doi: Optional[str] = Field(None, description="DOI identifier")

    # Journal/Conference Fields
    journal: Optional[str] = Field(None, description="Journal name")
    conference: Optional[str] = Field(None, description="Conference name")
    volume: Optional[str] = Field(None, description="Volume number")
    issue: Optional[str] = Field(None, description="Issue number")
    pages: Optional[str] = Field(None, description="Page range e.g. 12-25")
    publisher: Optional[str] = Field(None, description="Publisher name")

    # Indian Journal Specific
    issn: Optional[str] = Field(None, description="ISSN number")
    isbn: Optional[str] = Field(None, description="ISBN number")
    abstract: Optional[str] = Field(None, description="Paper abstract")
    keywords: Optional[List[str]] = Field(None, description="Keywords")
    institution: Optional[str] = Field(None, description="Author institution")
    url: Optional[str] = Field(None, description="Paper URL")

    # Internal
    citation_type: CitationType = Field(CitationType.ARTICLE, description="BibTeX entry type")
    confidence_score: float = Field(0.0, description="Parsing confidence 0-1")
    source: str = Field("pdf_extraction", description="How metadata was obtained")

    model_config = {"use_enum_values": True}


class ParseResponse(BaseModel):
    """API Response model"""
    success: bool
    message: str
    metadata: Optional[CitationMetadata] = None
    bibtex: Optional[str] = None
    formatted_citation: Optional[str] = None
    citation_style: Optional[str] = None
    raw_text_preview: Optional[str] = None
    errors: Optional[List[str]] = None


class DOILookupRequest(BaseModel):
    """DOI direct lookup request"""
    doi: str = Field(..., description="DOI string e.g. 10.1234/example")


class TextParseRequest(BaseModel):
    """Parse citation from raw text"""
    text: str = Field(..., description="Raw citation text to parse")
    citation_style: Optional[str] = Field("APA", description="APA, MLA, or IEEE")
