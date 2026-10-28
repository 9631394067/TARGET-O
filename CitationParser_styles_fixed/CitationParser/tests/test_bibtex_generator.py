# ============================================
# tests/test_bibtex_generator.py - BibTeX Tests
# ============================================
import pytest
from app.parsers.bibtex_generator import BibTeXGenerator
from app.models.citation import CitationMetadata, CitationType


def make_full_metadata():
    return CitationMetadata(
        title="Deep Learning Based Plant Disease Detection Using CNN",
        authors=["Ramesh Sharma", "Priya Gupta", "Anil Kumar Singh"],
        year="2021",
        doi="10.5120/ijca2021921534",
        journal="International Journal of Computer Applications",
        volume="183",
        issue="22",
        pages="12-19",
        issn="0975-8887",
        keywords=["Deep Learning", "CNN", "Plant Disease"],
        citation_type=CitationType.ARTICLE,
        confidence_score=0.95,
        source="crossref_api"
    )


class TestBibTeXGenerator:

    def test_basic_generation(self):
        meta = make_full_metadata()
        bibtex = BibTeXGenerator.generate(meta)
        assert bibtex is not None
        assert "@article{" in bibtex.lower() or "@article{" in bibtex

    def test_contains_title(self):
        meta = make_full_metadata()
        bibtex = BibTeXGenerator.generate(meta)
        assert "Plant Disease Detection" in bibtex

    def test_contains_authors(self):
        meta = make_full_metadata()
        bibtex = BibTeXGenerator.generate(meta)
        assert "Sharma" in bibtex
        assert "and" in bibtex  # Multiple authors joined with 'and'

    def test_contains_year(self):
        meta = make_full_metadata()
        bibtex = BibTeXGenerator.generate(meta)
        assert "2021" in bibtex

    def test_contains_doi(self):
        meta = make_full_metadata()
        bibtex = BibTeXGenerator.generate(meta)
        assert "10.5120/ijca2021921534" in bibtex

    def test_pages_double_dash(self):
        """BibTeX requires -- for page ranges"""
        meta = make_full_metadata()
        bibtex = BibTeXGenerator.generate(meta)
        assert "12--19" in bibtex

    def test_cite_key_format(self):
        meta = make_full_metadata()
        key = BibTeXGenerator.generate_cite_key(meta)
        assert "sharma" in key.lower()
        assert "2021" in key

    def test_inproceedings_type(self):
        meta = CitationMetadata(
            title="ML for Smart Cities",
            authors=["Amit Verma"],
            year="2022",
            conference="National Conference on AI",
            citation_type=CitationType.INPROCEEDINGS
        )
        bibtex = BibTeXGenerator.generate(meta)
        assert "@inproceedings{" in bibtex.lower()
        assert "booktitle" in bibtex

    def test_minimal_metadata(self):
        """Should work even with minimal info"""
        meta = CitationMetadata(title="Some Paper", year="2023")
        bibtex = BibTeXGenerator.generate(meta)
        assert "@article{" in bibtex.lower() or bibtex.startswith("@")
        assert "Some Paper" in bibtex

    def test_doi_generates_url(self):
        meta = make_full_metadata()
        bibtex = BibTeXGenerator.generate(meta)
        assert "https://doi.org/" in bibtex

    def test_multiple_entries(self):
        m1 = make_full_metadata()
        m2 = CitationMetadata(title="Paper Two", authors=["B. Kumar"], year="2022")
        result = BibTeXGenerator.generate_multiple([m1, m2])
        assert result.count("@article") == 2

    def test_special_chars_escaped(self):
        meta = CitationMetadata(
            title="Study of CO2 & NOx Emissions: A Review",
            authors=["R. Sharma"],
            year="2023"
        )
        bibtex = BibTeXGenerator.generate(meta)
        # & should be escaped as \&
        assert "\\&" in bibtex or "&" not in bibtex.split("title")[1][:50]

    def test_author_format_last_first(self):
        """Authors should be formatted as 'Last, First'"""
        meta = CitationMetadata(
            authors=["Priya Gupta", "Anil Singh"],
            title="Test", year="2023"
        )
        bibtex = BibTeXGenerator.generate(meta)
        assert "Gupta, Priya" in bibtex
        assert "Singh, Anil" in bibtex
