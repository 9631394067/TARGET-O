# ============================================
# tests/test_metadata_parser.py - Metadata Regex Tests
# ============================================
import pytest
from app.parsers.metadata_parser import MetadataParser


SAMPLE_INDIAN_PAPER = """
International Journal of Computer Applications (0975 – 8887)
Volume 183 – No.22, September 2021
ISSN: 0975-8887

Deep Learning Based Plant Disease Detection Using CNN

Dr. Ramesh Sharma1, Priya Gupta2, Anil Kumar Singh3
1Department of Computer Science, IIT Delhi, New Delhi
2Amity University, Noida, UP
3NIT Allahabad, Prayagraj

Abstract: This paper presents a deep learning approach for detecting plant diseases
using convolutional neural networks. The proposed model achieves 97.8% accuracy
on the PlantVillage dataset. Experiments conducted on tomato, potato and corn diseases
showed significant improvement over existing methods. The model can be deployed
on mobile devices for real-time disease detection in field conditions.

Keywords: Deep Learning, CNN, Plant Disease, Image Classification, Agriculture

1. Introduction
Plant diseases cause significant crop losses every year...

Pages: 12-19
doi: 10.5120/ijca2021921534
"""

SAMPLE_CONFERENCE_PAPER = """
Proceedings of the 15th International Conference on Intelligent Systems (ICIS 2023)
Publisher: Springer, New Delhi, India
ISBN: 978-981-19-6234-7

Vol. 45, No. 3, 2023, pp. 234-248

Machine Learning Approaches for Stock Market Prediction: An Indian Market Study
"""


class TestMetadataParser:

    def test_extract_year_basic(self):
        year = MetadataParser.extract_year("Published in year 2023.")
        assert year == "2023"

    def test_extract_year_multiple_prefers_recent(self):
        year = MetadataParser.extract_year("Originally 2018, revised in 2023.")
        assert year == "2023"

    def test_extract_year_from_sample(self):
        year = MetadataParser.extract_year(SAMPLE_INDIAN_PAPER)
        assert year == "2021"

    def test_extract_volume(self):
        vol = MetadataParser.extract_volume("Volume 183 – No.22")
        assert vol == "183"

    def test_extract_volume_abbreviated(self):
        vol = MetadataParser.extract_volume("Vol. 45, No. 3")
        assert vol == "45"

    def test_extract_issue(self):
        issue = MetadataParser.extract_issue("Volume 183 – No.22")
        assert issue == "22"

    def test_extract_issue_from_conference(self):
        issue = MetadataParser.extract_issue(SAMPLE_CONFERENCE_PAPER)
        assert issue == "3"

    def test_extract_pages_with_pp(self):
        pages = MetadataParser.extract_pages("pp. 12-19")
        assert pages == "12-19"

    def test_extract_pages_range(self):
        pages = MetadataParser.extract_pages("Pages: 234-248")
        assert pages is not None
        assert "234" in pages and "248" in pages

    def test_extract_issn(self):
        issn = MetadataParser.extract_issn(SAMPLE_INDIAN_PAPER)
        assert issn == "0975-8887"

    def test_extract_isbn(self):
        isbn = MetadataParser.extract_isbn(SAMPLE_CONFERENCE_PAPER)
        assert isbn is not None
        assert "978" in isbn

    def test_extract_keywords(self):
        keywords = MetadataParser.extract_keywords(SAMPLE_INDIAN_PAPER)
        assert keywords is not None
        assert len(keywords) > 0
        # Should contain at least one of these
        kw_lower = [k.lower() for k in keywords]
        assert any("learning" in k or "cnn" in k or "plant" in k for k in kw_lower)

    def test_extract_abstract(self):
        abstract = MetadataParser.extract_abstract(SAMPLE_INDIAN_PAPER)
        assert abstract is not None
        assert len(abstract) > 50
        assert "deep learning" in abstract.lower() or "convolutional" in abstract.lower()

    def test_parse_all_returns_dict(self):
        result = MetadataParser.parse_all(SAMPLE_INDIAN_PAPER)
        assert isinstance(result, dict)
        expected_keys = ['year', 'volume', 'issue', 'pages', 'issn', 'isbn', 'keywords', 'abstract']
        for key in expected_keys:
            assert key in result

    def test_parse_all_complete(self):
        result = MetadataParser.parse_all(SAMPLE_INDIAN_PAPER)
        assert result['year'] == "2021"
        assert result['volume'] == "183"
        assert result['issn'] == "0975-8887"

    def test_no_data_returns_none(self):
        result = MetadataParser.parse_all("Hello world.")
        assert result['issn'] is None
        assert result['isbn'] is None
