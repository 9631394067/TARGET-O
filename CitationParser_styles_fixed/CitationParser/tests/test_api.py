# ============================================
# tests/test_api.py - API Integration Tests
# ============================================
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from main import app
from app.models.citation import CitationMetadata, CitationType

client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "openai_enabled" in data
        assert "crossref_enabled" in data


class TestDOIEndpoint:

    def test_invalid_doi_format(self):
        response = client.post("/api/v1/parse/doi", json={"doi": "not-a-doi"})
        assert response.status_code == 400

    def test_invalid_doi_missing_slash(self):
        response = client.post("/api/v1/parse/doi", json={"doi": "10.1234"})
        assert response.status_code == 400

    @patch("app.api.routes.CrossRefService.lookup_doi", new_callable=AsyncMock)
    def test_doi_found(self, mock_lookup):
        mock_lookup.return_value = CitationMetadata(
            title="Test Indian Journal Paper",
            authors=["R. Sharma", "P. Gupta"],
            year="2023",
            doi="10.1234/test.2023",
            journal="Indian Journal of Computer Science",
            volume="10",
            issue="2",
            pages="45-60",
            citation_type=CitationType.ARTICLE,
            confidence_score=0.95,
            source="crossref_api"
        )
        response = client.post("/api/v1/parse/doi", json={"doi": "10.1234/test.2023"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["bibtex"] is not None
        assert "@article" in data["bibtex"].lower()
        assert "Sharma" in data["bibtex"]

    @patch("app.api.routes.CrossRefService.lookup_doi", new_callable=AsyncMock)
    def test_doi_not_found(self, mock_lookup):
        mock_lookup.return_value = None
        response = client.post("/api/v1/parse/doi", json={"doi": "10.9999/nonexistent.2023"})
        assert response.status_code == 404


class TestTextParseEndpoint:

    def test_parse_apa_citation(self):
        """Test parsing APA style citation (regex fallback, no AI)"""
        with patch("app.services.openai_service.openai_service.is_available", False):
            response = client.post("/api/v1/parse/text", json={
                "text": "Sharma, R. (2023). Deep Learning in Agriculture. Indian Journal of CS, 14(2), 45-67.",
                "citation_style": "APA"
            })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["metadata"]["year"] == "2023"

    def test_parse_text_with_doi(self):
        """Text containing DOI should trigger CrossRef lookup"""
        with patch("app.api.routes.CrossRefService.lookup_doi", new_callable=AsyncMock) as mock:
            mock.return_value = None  # DOI not in CrossRef
            with patch("app.services.openai_service.openai_service.is_available", False):
                response = client.post("/api/v1/parse/text", json={
                    "text": "Sharma R. (2023). ML Paper. IJCA, 10(1), 12-20. doi: 10.5120/test2023",
                    "citation_style": "APA"
                })
        assert response.status_code == 200

    def test_empty_text(self):
        response = client.post("/api/v1/parse/text", json={"text": ""})
        # Should return 422 (validation error) for empty text
        assert response.status_code == 422


class TestBibtexEndpoint:

    @patch("app.api.routes.CrossRefService.lookup_doi", new_callable=AsyncMock)
    def test_bibtex_plain_text_response(self, mock_lookup):
        mock_lookup.return_value = CitationMetadata(
            title="Smart Irrigation System",
            authors=["A. Patel"],
            year="2022",
            doi="10.1234/sis.2022",
            citation_type=CitationType.ARTICLE,
            confidence_score=0.9,
            source="crossref_api"
        )
        response = client.post("/api/v1/bibtex/from-doi", json={"doi": "10.1234/sis.2022"})
        assert response.status_code == 200
        # Should return plain text, not JSON
        assert "@article" in response.text.lower() or "@" in response.text


class TestPDFEndpoint:

    def test_non_pdf_rejected(self):
        from io import BytesIO
        fake_txt = BytesIO(b"This is a text file, not PDF")
        response = client.post(
            "/api/v1/parse/pdf",
            files={"file": ("test.txt", fake_txt, "text/plain")}
        )
        assert response.status_code == 400

    def test_valid_pdf_structure(self):
        """Test with minimal valid PDF bytes"""
        # Minimal PDF header
        minimal_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"
        from io import BytesIO
        response = client.post(
            "/api/v1/parse/pdf",
            files={"file": ("test.pdf", BytesIO(minimal_pdf), "application/pdf")}
        )
        # Should not crash - either returns result or "could not extract text"
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
