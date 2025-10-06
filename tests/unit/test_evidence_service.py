"""
Unit tests for evidence_service.py

Tests cover:
- Service initialization and mock database loading
- Literature search with evidence level classification
- Keyword matching in title, abstract, and keywords
- Year-based filtering
- Evidence level distribution analysis
- Evidence summary generation
- Clinical practice guidelines retrieval
- Fallback chain (PubMed → Mock database)
- Singleton pattern
- Caching behavior

Test Strategy:
- Test mock database search (primary functionality)
- Verify evidence level classification (Johns Hopkins model)
- Test keyword extraction and theme identification
- Verify year filtering
- Test guideline retrieval for known/unknown conditions
"""

import pytest

from src.models.schemas import EvidenceLevel, LiteratureSearchRequest
from src.services.evidence_service import EvidenceService, get_evidence_service


class TestEvidenceServiceInitialization:
    """Test service initialization and setup."""

    def test_init_loads_mock_database(self):
        """Test that initialization loads mock literature database."""
        service = EvidenceService()
        assert service.mock_database is not None
        assert len(service.mock_database) == 6  # 6 mock articles
        assert all("title" in article for article in service.mock_database)
        assert all("evidence_level" in article for article in service.mock_database)

    def test_mock_database_structure(self):
        """Test that mock articles have correct structure."""
        service = EvidenceService()
        for article in service.mock_database:
            assert "title" in article
            assert "authors" in article
            assert "journal" in article
            assert "year" in article
            assert "abstract" in article
            assert "evidence_level" in article
            assert isinstance(article["authors"], list)
            assert isinstance(article["year"], int)

    def test_mock_database_evidence_levels(self):
        """Test that mock articles have valid evidence levels."""
        service = EvidenceService()
        for article in service.mock_database:
            assert isinstance(article["evidence_level"], EvidenceLevel)
            assert article["evidence_level"] in [
                EvidenceLevel.LEVEL_I,
                EvidenceLevel.LEVEL_II,
                EvidenceLevel.LEVEL_III,
                EvidenceLevel.LEVEL_IV,
                EvidenceLevel.LEVEL_V,
                EvidenceLevel.LEVEL_VI,
                EvidenceLevel.LEVEL_VII,
            ]


class TestLiteratureSearch:
    """Test literature search functionality."""

    @pytest.mark.asyncio
    async def test_search_literature_basic(self):
        """Test basic literature search with keyword matching."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="diabetes", max_results=10)

        response = await service.search_literature(request)

        assert response is not None
        assert response.total_found >= 1
        assert len(response.articles) >= 1
        # Should find diabetes article
        assert any("diabetes" in article.title.lower() for article in response.articles)

    @pytest.mark.asyncio
    async def test_search_literature_case_insensitive(self):
        """Test that search is case-insensitive."""
        service = EvidenceService()
        request_lower = LiteratureSearchRequest(query="diabetes", max_results=10)
        request_upper = LiteratureSearchRequest(query="DIABETES", max_results=10)

        response_lower = await service.search_literature(request_lower)
        response_upper = await service.search_literature(request_upper)

        assert response_lower.total_found == response_upper.total_found

    @pytest.mark.asyncio
    async def test_search_literature_matches_title(self):
        """Test keyword matching in article titles."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="heart failure", max_results=10)

        response = await service.search_literature(request)

        assert response.total_found >= 1
        # Should find heart failure article
        assert any(
            "heart failure" in article.title.lower() for article in response.articles
        )

    @pytest.mark.asyncio
    async def test_search_literature_matches_abstract(self):
        """Test keyword matching in article abstracts."""
        service = EvidenceService()
        # "glycemic" appears in diabetes article abstract
        request = LiteratureSearchRequest(query="glycemic", max_results=10)

        response = await service.search_literature(request)

        assert response.total_found >= 1
        assert any(
            "glycemic" in article.abstract.lower() for article in response.articles
        )

    @pytest.mark.asyncio
    async def test_search_literature_matches_keywords(self):
        """Test keyword matching in article keyword lists."""
        service = EvidenceService()
        # "RCT" is in keywords of diabetes article
        request = LiteratureSearchRequest(query="RCT", max_results=10)

        response = await service.search_literature(request)

        assert response.total_found >= 1

    @pytest.mark.asyncio
    async def test_search_literature_no_results(self):
        """Test search with no matching results."""
        service = EvidenceService()
        request = LiteratureSearchRequest(
            query="nonexistentmedicalterm12345", max_results=10
        )

        response = await service.search_literature(request)

        assert response.total_found == 0
        assert len(response.articles) == 0
        assert "No evidence found" in response.evidence_summary

    @pytest.mark.asyncio
    async def test_search_literature_max_results_limit(self):
        """Test that max_results parameter limits returned articles."""
        service = EvidenceService()
        # Search for common term that matches multiple articles
        request = LiteratureSearchRequest(query="nursing", max_results=2)

        response = await service.search_literature(request)

        # Should limit to 2 even if more match
        assert len(response.articles) <= 2

    @pytest.mark.asyncio
    async def test_search_literature_year_filter(self):
        """Test filtering by publication year."""
        service = EvidenceService()
        # Filter for articles from 2023 or later
        request = LiteratureSearchRequest(
            query="nursing", max_results=10, filter_years=2023
        )

        response = await service.search_literature(request)

        # All returned articles should be from 2023 or later
        for article in response.articles:
            assert article.year >= 2023

    @pytest.mark.asyncio
    async def test_search_literature_year_filter_excludes_old(self):
        """Test that year filter excludes older articles."""
        service = EvidenceService()
        # COPD article is from 2022, should be excluded with 2023 filter
        request = LiteratureSearchRequest(
            query="COPD", max_results=10, filter_years=2023
        )

        response = await service.search_literature(request)

        # Should not find COPD article (2022) with 2023 filter
        assert response.total_found == 0

    @pytest.mark.asyncio
    async def test_search_literature_returns_correct_fields(self):
        """Test that returned articles have all required fields."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="diabetes", max_results=10)

        response = await service.search_literature(request)

        for article in response.articles:
            assert article.title is not None
            assert article.authors is not None
            assert article.journal is not None
            assert article.year is not None
            assert article.abstract is not None
            assert article.evidence_level is not None
            assert isinstance(article.authors, list)

    @pytest.mark.asyncio
    async def test_search_literature_evidence_levels(self):
        """Test that articles have valid evidence levels."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="nursing", max_results=10)

        response = await service.search_literature(request)

        for article in response.articles:
            assert isinstance(article.evidence_level, EvidenceLevel)


class TestEvidenceSummary:
    """Test evidence summary generation."""

    @pytest.mark.asyncio
    async def test_evidence_summary_generated(self):
        """Test that evidence summary is generated."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="diabetes", max_results=10)

        response = await service.search_literature(request)

        assert response.evidence_summary is not None
        assert len(response.evidence_summary) > 0
        assert "diabetes" in response.evidence_summary.lower()

    @pytest.mark.asyncio
    async def test_evidence_summary_includes_count(self):
        """Test that summary includes article count."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="nursing", max_results=10)

        response = await service.search_literature(request)

        assert "Found" in response.evidence_summary
        assert "studies" in response.evidence_summary

    @pytest.mark.asyncio
    async def test_evidence_summary_distribution(self):
        """Test that summary includes evidence level distribution."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="nursing", max_results=10)

        response = await service.search_literature(request)

        # Should mention evidence levels
        assert "Evidence Strength Distribution" in response.evidence_summary
        # Should include at least one level (Level I, II, etc.)
        assert any(
            level in response.evidence_summary
            for level in ["Level I", "Level II", "Level III"]
        )

    @pytest.mark.asyncio
    async def test_evidence_summary_themes(self):
        """Test that summary includes key themes."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="diabetes", max_results=10)

        response = await service.search_literature(request)

        assert "Key themes identified:" in response.evidence_summary

    @pytest.mark.asyncio
    async def test_evidence_summary_no_results(self):
        """Test summary when no results found."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="nonexistentterm123", max_results=10)

        response = await service.search_literature(request)

        assert "No evidence found" in response.evidence_summary
        assert "nonexistentterm123" in response.evidence_summary


class TestClinicalGuidelines:
    """Test clinical practice guideline retrieval."""

    @pytest.mark.asyncio
    async def test_get_clinical_guidelines_diabetes(self):
        """Test retrieving diabetes clinical guidelines."""
        service = EvidenceService()

        guidelines = await service.get_clinical_guidelines("diabetes")

        assert guidelines is not None
        assert "organization" in guidelines
        assert "year" in guidelines
        assert "key_recommendations" in guidelines
        assert "evidence_level" in guidelines
        assert "American Diabetes Association" in guidelines["organization"]
        assert len(guidelines["key_recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_get_clinical_guidelines_heart_failure(self):
        """Test retrieving heart failure clinical guidelines."""
        service = EvidenceService()

        guidelines = await service.get_clinical_guidelines("heart failure")

        assert guidelines is not None
        assert "American Heart Association" in guidelines["organization"]
        assert len(guidelines["key_recommendations"]) > 0
        # Check for specific recommendation
        assert any("ACE inhibitors" in rec for rec in guidelines["key_recommendations"])

    @pytest.mark.asyncio
    async def test_get_clinical_guidelines_case_insensitive(self):
        """Test that guideline lookup is case-insensitive."""
        service = EvidenceService()

        guidelines_lower = await service.get_clinical_guidelines("diabetes")
        guidelines_upper = await service.get_clinical_guidelines("DIABETES")

        assert guidelines_lower["organization"] == guidelines_upper["organization"]

    @pytest.mark.asyncio
    async def test_get_clinical_guidelines_space_handling(self):
        """Test that guideline lookup handles spaces correctly."""
        service = EvidenceService()

        guidelines = await service.get_clinical_guidelines("heart failure")

        assert guidelines is not None
        assert "American Heart Association" in guidelines["organization"]

    @pytest.mark.asyncio
    async def test_get_clinical_guidelines_unknown_condition(self):
        """Test fallback for unknown condition."""
        service = EvidenceService()

        guidelines = await service.get_clinical_guidelines("unknown_condition_xyz")

        assert guidelines is not None
        assert "General Clinical Practice" in guidelines["organization"]
        assert len(guidelines["key_recommendations"]) > 0
        assert guidelines["evidence_level"] == EvidenceLevel.LEVEL_VII

    @pytest.mark.asyncio
    async def test_get_clinical_guidelines_evidence_level(self):
        """Test that guidelines have valid evidence levels."""
        service = EvidenceService()

        guidelines = await service.get_clinical_guidelines("diabetes")

        assert isinstance(guidelines["evidence_level"], EvidenceLevel)
        # Major organization guidelines should be Level I
        assert guidelines["evidence_level"] == EvidenceLevel.LEVEL_I


class TestSearchStrategy:
    """Test search strategy reporting."""

    @pytest.mark.asyncio
    async def test_search_strategy_reported(self):
        """Test that search strategy is reported in response."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="diabetes", max_results=10)

        response = await service.search_literature(request)

        assert response.search_strategy is not None
        assert "Keyword search" in response.search_strategy
        assert "diabetes" in response.search_strategy


class TestSingletonPattern:
    """Test singleton service accessor."""

    def test_get_evidence_service_returns_instance(self):
        """Test that get_evidence_service returns a service instance."""
        service = get_evidence_service()
        assert service is not None
        assert isinstance(service, EvidenceService)

    def test_get_evidence_service_returns_same_instance(self):
        """Test that get_evidence_service returns singleton."""
        service1 = get_evidence_service()
        service2 = get_evidence_service()
        assert service1 is service2


class TestPubMedFallback:
    """Test PubMed search fallback behavior."""

    @pytest.mark.asyncio
    async def test_search_pubmed_returns_none(self):
        """Test that _search_pubmed currently returns None (not implemented)."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="diabetes", max_results=10)

        result = await service._search_pubmed(request)

        # Currently not implemented, should return None to trigger fallback
        assert result is None

    @pytest.mark.asyncio
    async def test_search_falls_back_to_mock(self):
        """Test that search falls back to mock data when PubMed unavailable."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="diabetes", max_results=10)

        # Should fall back to mock and still return results
        response = await service.search_literature(request)

        assert response is not None
        assert response.total_found >= 1


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_search_empty_query_validation(self):
        """Test that empty query is rejected by Pydantic validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            LiteratureSearchRequest(query="", max_results=10)

        assert "String should have at least 3 characters" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_special_characters(self):
        """Test search with special characters."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="@#$%", max_results=10)

        response = await service.search_literature(request)

        # Special chars won't match
        assert response.total_found == 0

    def test_search_max_results_zero_validation(self):
        """Test that max_results=0 is rejected by Pydantic validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            LiteratureSearchRequest(query="diabetes", max_results=0)

        assert "greater than or equal to 1" in str(exc_info.value)

    def test_search_very_large_max_results_validation(self):
        """Test that very large max_results is capped by Pydantic validation."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            LiteratureSearchRequest(query="nursing", max_results=1000)

        assert "less than or equal to 50" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_search_max_results_at_limit(self):
        """Test search with max_results at validation limit (50)."""
        service = EvidenceService()
        request = LiteratureSearchRequest(query="nursing", max_results=50)

        response = await service.search_literature(request)

        # Should not crash, returns all available matches (max 6 from mock)
        assert len(response.articles) <= 6


class TestMockDatabaseContent:
    """Test specific mock database content."""

    def test_mock_database_has_systematic_reviews(self):
        """Test that mock database includes Level I evidence (systematic reviews)."""
        service = EvidenceService()

        level_i_articles = [
            article
            for article in service.mock_database
            if article["evidence_level"] == EvidenceLevel.LEVEL_I
        ]

        assert len(level_i_articles) > 0

    def test_mock_database_has_rcts(self):
        """Test that mock database includes Level II evidence (RCTs)."""
        service = EvidenceService()

        level_ii_articles = [
            article
            for article in service.mock_database
            if article["evidence_level"] == EvidenceLevel.LEVEL_II
        ]

        assert len(level_ii_articles) > 0

    def test_mock_database_covers_multiple_topics(self):
        """Test that mock database covers diverse nursing topics."""
        service = EvidenceService()

        topics = set()
        for article in service.mock_database:
            # Extract topic from title (first few words)
            topic_words = article["title"].split()[:3]
            topics.add(" ".join(topic_words))

        # Should have at least 4 different topics
        assert len(topics) >= 4

    def test_mock_database_recent_years(self):
        """Test that mock database includes recent publications."""
        service = EvidenceService()

        recent_articles = [
            article for article in service.mock_database if article["year"] >= 2022
        ]

        # All mock articles should be recent (2022+)
        assert len(recent_articles) == len(service.mock_database)
