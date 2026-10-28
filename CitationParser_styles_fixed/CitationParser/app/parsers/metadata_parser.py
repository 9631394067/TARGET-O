# ============================================
# app/parsers/metadata_parser.py - Regex-based Metadata Extraction
# ============================================
import re
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class MetadataParser:
    """
    Rule-based parser for extracting metadata from Indian journal PDFs.
    Works even without OpenAI API key.
    """

    # Explicit key/value metadata labels (most reliable for pasted structured text)
    LABELS = {
        'title': r'title', 'authors': r'authors?', 'year': r'year|publication year|published',
        'doi': r'doi', 'journal': r'journal|journal name|publication',
        'conference': r'conference|conference name|booktitle',
        'volume': r'volume|vol', 'issue': r'issue|number|no',
        'pages': r'pages?|page range', 'publisher': r'publisher|publishing house',
        'issn': r'issn', 'isbn': r'isbn', 'keywords': r'keywords?|key words|index terms',
        'abstract': r'abstract', 'institution': r'institution|affiliation|university',
    }

    @classmethod
    def extract_labeled_fields(cls, text: str) -> Dict[str, Any]:
        """Extract explicit `Label: value` lines without swallowing adjacent fields."""
        result: Dict[str, Any] = {}
        # Match each line independently; tolerate uppercase labels and whitespace.
        for line in text.splitlines():
            line = line.strip().strip('•-* ')
            m = re.match(r'^([A-Za-z][A-Za-z ]{1,24})\s*[:=]\s*(.*?)\s*$', line)
            if not m:
                continue
            label = re.sub(r'\s+', ' ', m.group(1)).strip().lower()
            value = m.group(2).strip()
            field = None
            for key, aliases in cls.LABELS.items():
                if re.fullmatch(aliases, label, re.IGNORECASE):
                    field = key
                    break
            if not field or not value:
                continue
            if field in {'authors', 'keywords'}:
                vals = [x.strip() for x in re.split(r';|\s+and\s+|,(?!\s*[A-Z]\.)', value) if x.strip()]
                result[field] = vals
            elif field == 'pages':
                pm = re.search(r'(\d{1,5})\s*[-–—]\s*(\d{1,5})', value)
                result[field] = f'{pm.group(1)}-{pm.group(2)}' if pm else value
            elif field == 'year':
                ym = re.search(r'\b(19\d{2}|20\d{2})\b', value)
                result[field] = ym.group(1) if ym else value
            else:
                result[field] = value
        return result

    # ── YEAR ──────────────────────────────────────────────────────────────────
    YEAR_PATTERNS = [
        r'(?:Published|Received|Accepted|©|Copyright)\s*[:\-]?\s*(19[89]\d|20[012]\d)',
        r'\b(20[012]\d|19[89]\d)\b',  # any 4-digit year
    ]

    # ── VOLUME / ISSUE ────────────────────────────────────────────────────────
    VOLUME_PATTERNS = [
        r'[Vv]ol(?:ume)?\.?\s*(\d+)',
        r'[Vv]\.?\s*(\d+)(?:\s*[,\(])',
    ]
    ISSUE_PATTERNS = [
        r'[Nn]o\.?\s*(\d+)',
        r'[Ii]ssue\.?\s*(\d+)',
        r'[Nn]umber\.?\s*(\d+)',
        r'(?:Vol\.?\s*\d+\s*)\((\d+)\)',  # Vol.5(2)
    ]

    # ── PAGES (strict — must be pp. or Pages: prefix, NOT bare ISSN-like) ────
    PAGE_PATTERNS = [
        r'[Pp]p?\.?\s*(\d{1,4})\s*[-–—]\s*(\d{1,4})',   # pp. 12-19
        r'[Pp]ages?\s*(\d{1,4})\s*[-–—]\s*(\d{1,4})',    # Pages 12-19
        r'Pages?:\s*(\d{1,4})\s*[-–—]\s*(\d{1,4})',      # Pages: 14-22
    ]

    # ── ISSN (exact XXXX-XXXX format, must have ISSN keyword) ────────────────
    ISSN_PATTERN = r'ISSN\s*[:\-]?\s*(\d{4}-\d{3}[\dXx])'

    # ── ISBN ──────────────────────────────────────────────────────────────────
    ISBN_PATTERN = r'ISBN\s*[:\-]?\s*([\d\-Xx]{10,17})'

    # ── JOURNAL NAME ──────────────────────────────────────────────────────────
    JOURNAL_PATTERNS = [
        r'(?:Published in|Journal of|International Journal of|Indian Journal of)\s+([A-Z][^\n,\.]{5,80})',
        r'([A-Z][a-zA-Z\s]+Journal[^\n,\.]{0,60})',
        r'([A-Z][a-zA-Z\s]+Proceedings[^\n,\.]{0,60})',
    ]

    # ── TITLE (first meaningful line on page 1) ───────────────────────────────
    TITLE_PATTERNS = [
        # Title before "Abstract" on page 1
        r'^(.{20,250})\n(?:[A-Z][a-z]+\s+[A-Z]|Abstract|ABSTRACT)',
        # Fallback: first long line
        r'^(.{30,200})$',
    ]

    # ── KEYWORDS ──────────────────────────────────────────────────────────────
    KEYWORD_PATTERNS = [
        r'[Kk]ey\s*[Ww]ords?\s*[:\-—]\s*(.+?)(?:\n\n|\n[A-Z1I]|\.\s*\n)',
        r'[Ii]ndex\s*[Tt]erms?\s*[:\-—]\s*(.+?)(?:\n\n|\n[A-Z1I])',
    ]

    # ── ABSTRACT ─────────────────────────────────────────────────────────────
    ABSTRACT_PATTERNS = [
        r'[Aa]bstract\s*[:\-]?\s*([\s\S]{100,1500}?)(?:[Kk]ey\s*[Ww]ords?|[Ii]ntroduction|1\.\s)',
    ]

    @classmethod
    def extract_year(cls, text: str) -> Optional[str]:
        # First try context-aware patterns
        for pattern in cls.YEAR_PATTERNS[:1]:
            m = re.search(pattern, text)
            if m:
                return m.group(1)
        # Fallback: most recent year in text
        matches = re.findall(cls.YEAR_PATTERNS[1], text)
        if matches:
            years = [int(y) for y in matches if 1970 <= int(y) <= 2030]
            if years:
                return str(max(years))
        return None

    @classmethod
    def extract_volume(cls, text: str) -> Optional[str]:
        for pattern in cls.VOLUME_PATTERNS:
            m = re.search(pattern, text)
            if m:
                return m.group(1)
        return None

    @classmethod
    def extract_issue(cls, text: str) -> Optional[str]:
        for pattern in cls.ISSUE_PATTERNS:
            m = re.search(pattern, text)
            if m:
                return m.group(1)
        return None

    @classmethod
    def extract_pages(cls, text: str) -> Optional[str]:
        """Extract page range — strict patterns only to avoid ISSN false positives."""
        for pattern in cls.PAGE_PATTERNS:
            m = re.search(pattern, text)
            if m:
                start = m.group(1)
                end = m.group(2)
                # Sanity check: page numbers shouldn't be > 9999
                if int(start) < 9999 and int(end) < 9999 and int(end) > int(start):
                    return f"{start}-{end}"
        return None

    @classmethod
    def extract_issn(cls, text: str) -> Optional[str]:
        m = re.search(cls.ISSN_PATTERN, text)
        return m.group(1) if m else None

    @classmethod
    def extract_isbn(cls, text: str) -> Optional[str]:
        m = re.search(cls.ISBN_PATTERN, text)
        return m.group(1) if m else None

    @classmethod
    def extract_journal(cls, text: str) -> Optional[str]:
        for pattern in cls.JOURNAL_PATTERNS:
            m = re.search(pattern, text)
            if m:
                name = m.group(1).strip()
                if len(name) > 5:
                    return name
        return None

    @classmethod
    def extract_title(cls, text: str) -> Optional[str]:
        """Extract title from first page — usually first large text block."""
        first_500 = text[:500].strip()
        for pattern in cls.TITLE_PATTERNS:
            m = re.search(pattern, first_500, re.MULTILINE)
            if m:
                title = m.group(1).strip()
                # Clean up
                title = re.sub(r'\s+', ' ', title)
                if len(title) > 15 and not title.startswith('---'):
                    return title
        # Ultimate fallback: first non-empty line longer than 20 chars
        for line in text.split('\n'):
            line = line.strip()
            if len(line) > 20 and not line.startswith('---'):
                return line[:300]
        return None

    @classmethod
    def extract_keywords(cls, text: str) -> Optional[List[str]]:
        for pattern in cls.KEYWORD_PATTERNS:
            m = re.search(pattern, text, re.DOTALL)
            if m:
                raw = m.group(1).strip()
                keywords = re.split(r'[,;•\n]+', raw)
                cleaned = [k.strip() for k in keywords if k.strip() and len(k.strip()) > 2]
                if cleaned:
                    return cleaned[:10]  # max 10 keywords
        return None

    @classmethod
    def extract_abstract(cls, text: str) -> Optional[str]:
        for pattern in cls.ABSTRACT_PATTERNS:
            m = re.search(pattern, text, re.DOTALL)
            if m:
                abstract = m.group(1).strip()
                abstract = re.sub(r'\s+', ' ', abstract)
                if len(abstract) > 50:
                    return abstract[:1500]
        return None

    @classmethod
    def extract_authors_regex(cls, text: str) -> Optional[List[str]]:
        """Extract author names from first page of Indian journal papers."""
        patterns = [
            r'(?:Authors?|BY|by)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]*\.?)+(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]*\.?)+)*)',
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+\s+[A-Z][a-z]+)*)[\s\n]',
        ]
        for pattern in patterns:
            m = re.search(pattern, text[:2000], re.MULTILINE)
            if m:
                raw = m.group(1)
                authors = [a.strip() for a in re.split(r',\s*|\s+and\s+', raw) if a.strip()]
                if 1 <= len(authors) <= 10:
                    return authors
        return None

    @classmethod
    def parse_all(cls, text: str) -> Dict[str, Any]:
        """Run labeled and heuristic parsers; explicit labels take precedence."""
        labeled = cls.extract_labeled_fields(text)
        parsed = {
            "title":         cls.extract_title(text),
            "year":          cls.extract_year(text),
            "volume":        cls.extract_volume(text),
            "issue":         cls.extract_issue(text),
            "pages":         cls.extract_pages(text),
            "issn":          cls.extract_issn(text),
            "isbn":          cls.extract_isbn(text),
            "journal":       cls.extract_journal(text),
            "keywords":      cls.extract_keywords(text),
            "abstract":      cls.extract_abstract(text),
            "authors_regex": cls.extract_authors_regex(text),
        }
        # Explicit labels should override heuristic guesses (e.g. TITLE line).
        for field in ('title', 'year', 'volume', 'issue', 'pages', 'issn', 'isbn',
                      'journal', 'keywords', 'abstract', 'publisher', 'institution', 'conference'):
            if labeled.get(field):
                parsed[field] = labeled[field]
        if labeled.get('authors'):
            parsed['authors_regex'] = labeled['authors']
        return parsed
