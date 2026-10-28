# ============================================
# tests/test_doi_parser.py - DOI Parser Tests
# ============================================
import pytest
from app.parsers.doi_parser import DOIParser


class TestDOIParser:

    def test_standard_doi(self):
        text = "Published with DOI: 10.1016/j.ins.2023.119450"
        assert DOIParser.extract_doi(text) == "10.1016/j.ins.2023.119450"

    def test_doi_with_url_prefix(self):
        text = "Available at https://doi.org/10.1145/3474123.3474456"
        doi = DOIParser.extract_doi(text)
        assert doi == "10.1145/3474123.3474456"

    def test_doi_with_dx_prefix(self):
        text = "See http://dx.doi.org/10.1109/ACCESS.2023.3298765"
        doi = DOIParser.extract_doi(text)
        assert doi == "10.1109/ACCESS.2023.3298765"

    def test_doi_in_brackets(self):
        text = "[DOI: 10.4018/IJOCI.2023010105]"
        doi = DOIParser.extract_doi(text)
        assert doi == "10.4018/IJOCI.2023010105"

    def test_doi_case_insensitive(self):
        text = "doi:10.1234/test.paper.2023"
        doi = DOIParser.extract_doi(text)
        assert doi == "10.1234/test.paper.2023"

    def test_no_doi(self):
        text = "This paper has no DOI reference in the text."
        assert DOIParser.extract_doi(text) is None

    def test_invalid_doi(self):
        assert DOIParser.is_valid_doi("not-a-doi") is False
        assert DOIParser.is_valid_doi("10.1234") is False  # missing suffix
        assert DOIParser.is_valid_doi("10.1234/valid") is True

    def test_extract_all_dois(self):
        text = """
        First paper: 10.1016/j.ins.2023.001
        Second paper: 10.1145/3474123.3474456
        Third: https://doi.org/10.1109/ACCESS.2023.001
        """
        dois = DOIParser.extract_all_dois(text)
        assert len(dois) == 3

    def test_clean_doi_removes_url(self):
        doi = DOIParser.clean_doi("https://doi.org/10.1234/test")
        assert doi == "10.1234/test"

    def test_to_url(self):
        url = DOIParser.to_url("10.1234/test")
        assert url == "https://doi.org/10.1234/test"

    def test_trailing_punctuation_removed(self):
        text = "DOI: 10.1234/test.paper.2023."
        doi = DOIParser.extract_doi(text)
        assert doi is not None
        assert not doi.endswith('.')

    def test_indian_journal_doi(self):
        """Indian journals often use IJCA, IJSR, etc. style DOIs"""
        text = "doi: 10.5120/ijca2023922876"
        doi = DOIParser.extract_doi(text)
        assert doi == "10.5120/ijca2023922876"
