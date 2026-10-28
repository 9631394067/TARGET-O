# ============================================
# app/parsers/bibtex_generator.py - BibTeX Output
# ============================================
import re
import logging
from typing import Optional
from app.models.citation import CitationMetadata, CitationType

logger = logging.getLogger(__name__)


class BibTeXGenerator:
    """
    Generates BibTeX formatted strings from CitationMetadata.
    Handles all standard BibTeX entry types.
    """

    @staticmethod
    def generate_cite_key(metadata: CitationMetadata) -> str:
        """
        Generate a BibTeX cite key like: AuthorYear_Title
        e.g., sharma2023_neural
        """
        parts = []

        # First author's last name
        if metadata.authors:
            first_author = metadata.authors[0]
            last_name = first_author.split()[-1] if first_author else "unknown"
            last_name = re.sub(r'[^a-zA-Z]', '', last_name).lower()
            parts.append(last_name[:12])

        # Year
        if metadata.year:
            parts.append(metadata.year)

        # First meaningful word of title
        if metadata.title:
            words = re.findall(r'\b[a-zA-Z]{4,}\b', metadata.title.lower())
            stop_words = {'with', 'using', 'from', 'based', 'into', 'that', 'this', 'for', 'and', 'the'}
            content_words = [w for w in words if w not in stop_words]
            if content_words:
                parts.append(content_words[0][:10])

        return '_'.join(parts) if parts else "citation2024"

    @staticmethod
    def _escape_bibtex(value: str) -> str:
        """Escape special BibTeX characters."""
        if not value:
            return value
        # Escape & % $ # _ { } ~ ^ \
        special = r'&%$#_{}~^\\'
        result = value
        for char in ['\\', '{', '}', '&', '%', '$', '#', '_', '~', '^']:
            if char != '\\':
                result = result.replace(char, f'\\{char}')
        return result

    @classmethod
    def _format_authors(cls, authors: list) -> str:
        """Format authors list as BibTeX: 'Last, First and Last, First'"""
        formatted = []
        for author in authors:
            parts = author.strip().split()
            if len(parts) >= 2:
                # Assume "First Last" format → convert to "Last, First"
                last = parts[-1]
                first = ' '.join(parts[:-1])
                formatted.append(f"{last}, {first}")
            else:
                formatted.append(author.strip())
        return ' and '.join(formatted)

    @classmethod
    def generate(cls, metadata: CitationMetadata) -> str:
        """
        Generate complete BibTeX entry from metadata.
        Returns formatted BibTeX string.
        """
        cite_key = cls.generate_cite_key(metadata)
        # Always get string value regardless of whether it's enum or string
        et = metadata.citation_type or CitationType.ARTICLE
        entry_type = et.value if hasattr(et, 'value') else str(et)

        # Build fields dict (only include non-None values)
        fields = {}

        if metadata.title:
            fields['title'] = f"{{{cls._escape_bibtex(metadata.title)}}}"

        if metadata.authors:
            author_str = cls._format_authors(metadata.authors)
            fields['author'] = f"{{{cls._escape_bibtex(author_str)}}}"

        if metadata.year:
            fields['year'] = f"{{{metadata.year}}}"

        if metadata.journal and entry_type in [CitationType.ARTICLE, "article"]:
            fields['journal'] = f"{{{cls._escape_bibtex(metadata.journal)}}}"

        if metadata.conference and entry_type in [CitationType.INPROCEEDINGS, CitationType.CONFERENCE, "inproceedings", "conference"]:
            fields['booktitle'] = f"{{{cls._escape_bibtex(metadata.conference)}}}"

        if metadata.volume:
            fields['volume'] = f"{{{metadata.volume}}}"

        if metadata.issue:
            fields['number'] = f"{{{metadata.issue}}}"

        if metadata.pages:
            fields['pages'] = f"{{{metadata.pages.replace('-', '--')}}}"

        if metadata.publisher:
            fields['publisher'] = f"{{{cls._escape_bibtex(metadata.publisher)}}}"

        if metadata.doi:
            fields['doi'] = f"{{{metadata.doi}}}"
            fields['url'] = f"{{https://doi.org/{metadata.doi}}}"
        elif metadata.url:
            fields['url'] = f"{{{metadata.url}}}"

        if metadata.issn:
            fields['issn'] = f"{{{metadata.issn}}}"

        if metadata.isbn:
            fields['isbn'] = f"{{{metadata.isbn}}}"

        if metadata.abstract:
            # Truncate abstract for BibTeX
            abstract_short = metadata.abstract[:500] + ('...' if len(metadata.abstract) > 500 else '')
            fields['abstract'] = f"{{{cls._escape_bibtex(abstract_short)}}}"

        if metadata.keywords:
            kw_str = ', '.join(metadata.keywords[:8])
            fields['keywords'] = f"{{{cls._escape_bibtex(kw_str)}}}"

        if metadata.institution:
            fields['institution'] = f"{{{cls._escape_bibtex(metadata.institution)}}}"

        # Format the BibTeX entry
        field_lines = []
        for key, value in fields.items():
            field_lines.append(f"  {key} = {value}")

        bibtex = f"@{entry_type}{{{cite_key},\n"
        bibtex += ',\n'.join(field_lines)
        bibtex += '\n}'

        return bibtex

    @classmethod
    def generate_multiple(cls, metadata_list: list) -> str:
        """Generate multiple BibTeX entries."""
        entries = [cls.generate(m) for m in metadata_list]
        return '\n\n'.join(entries)
