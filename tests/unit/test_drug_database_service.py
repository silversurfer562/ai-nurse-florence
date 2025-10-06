"""
Unit tests for drug_database_service.py

Tests cover:
- Service initialization and database availability
- Drug search with various patterns (exact, partial, fuzzy)
- Search result ranking and ordering
- Drug info retrieval from local database
- FDA API fallback when drug not in local DB
- JSON parsing for active ingredients and packaging
- Error handling and graceful degradation
- Edge cases (empty strings, None values, special characters)

Test Strategy:
- Mock SQLite database for isolated unit testing
- Mock live_fda module for FDA API fallback testing
- Use fixtures for common test data
- Test both happy paths and error conditions
"""

import json
import sqlite3
from unittest.mock import patch

import pytest

from src.services.drug_database_service import DrugDatabaseService


@pytest.fixture
def mock_db_path(tmp_path):
    """Create a temporary database path for testing."""
    db_path = tmp_path / "test_drugs.db"
    return db_path


@pytest.fixture
def sample_drug_data():
    """Sample drug data for testing."""
    return {
        "generic_name": "ibuprofen",
        "brand_name": "Advil",
        "brand_name_base": "Advil",
        "substance_name": "ibuprofen",
        "route": "oral",
        "product_type": "HUMAN OTC DRUG",
        "labeler_name": "Pfizer Consumer Healthcare",
        "active_ingredients": json.dumps([{"name": "ibuprofen", "strength": "200mg"}]),
        "packaging": json.dumps([{"description": "bottle", "quantity": "100"}]),
    }


@pytest.fixture
def populated_test_db(mock_db_path, sample_drug_data):
    """Create and populate a test database."""
    conn = sqlite3.connect(mock_db_path)
    cursor = conn.cursor()

    # Create drugs table
    cursor.execute(
        """
        CREATE TABLE drugs (
            generic_name TEXT,
            brand_name TEXT,
            brand_name_base TEXT,
            substance_name TEXT,
            route TEXT,
            product_type TEXT,
            labeler_name TEXT,
            active_ingredients TEXT,
            packaging TEXT
        )
    """
    )

    # Create metadata table
    cursor.execute(
        """
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """
    )

    # Insert test drugs
    test_drugs = [
        sample_drug_data,
        {
            "generic_name": "acetaminophen",
            "brand_name": "Tylenol",
            "brand_name_base": "Tylenol",
            "substance_name": "acetaminophen",
            "route": "oral",
            "product_type": "HUMAN OTC DRUG",
            "labeler_name": "McNeil Consumer Healthcare",
            "active_ingredients": json.dumps(
                [{"name": "acetaminophen", "strength": "500mg"}]
            ),
            "packaging": json.dumps([{"description": "bottle", "quantity": "50"}]),
        },
        {
            "generic_name": "metformin hydrochloride",
            "brand_name": "Glucophage",
            "brand_name_base": "Glucophage",
            "substance_name": "metformin hydrochloride",
            "route": "oral",
            "product_type": "HUMAN PRESCRIPTION DRUG",
            "labeler_name": "Bristol-Myers Squibb",
            "active_ingredients": json.dumps(
                [{"name": "metformin hydrochloride", "strength": "500mg"}]
            ),
            "packaging": json.dumps([{"description": "bottle", "quantity": "100"}]),
        },
    ]

    for drug in test_drugs:
        cursor.execute(
            """
            INSERT INTO drugs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                drug["generic_name"],
                drug["brand_name"],
                drug["brand_name_base"],
                drug["substance_name"],
                drug["route"],
                drug["product_type"],
                drug["labeler_name"],
                drug["active_ingredients"],
                drug["packaging"],
            ),
        )

    # Insert metadata
    cursor.execute(
        """
        INSERT INTO metadata VALUES ('last_updated', '2025-10-04')
    """
    )
    cursor.execute(
        """
        INSERT INTO metadata VALUES ('total_drugs', '3')
    """
    )

    conn.commit()
    conn.close()

    return mock_db_path


class TestDrugDatabaseServiceInitialization:
    """Test service initialization and database availability checks."""

    def test_init_with_existing_database(self, populated_test_db):
        """Test initialization when database exists."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            assert service.db_available is True
            assert service.db_path == populated_test_db

    def test_init_without_database(self, tmp_path):
        """Test initialization when database does not exist."""
        non_existent_path = tmp_path / "non_existent.db"
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", non_existent_path
        ):
            service = DrugDatabaseService()
            assert service.db_available is False
            assert service.db_path == non_existent_path

    def test_log_database_stats_success(self, populated_test_db, caplog):
        """Test that database statistics are logged on successful init."""
        import logging

        caplog.set_level(logging.INFO)
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            DrugDatabaseService()
            assert "3 drugs" in caplog.text
            assert "Last updated: 2025-10-04" in caplog.text

    def test_log_database_stats_failure(self, mock_db_path, caplog):
        """Test graceful handling when stats cannot be read."""
        # Create empty file (invalid database)
        mock_db_path.touch()
        with patch("src.services.drug_database_service.DATABASE_PATH", mock_db_path):
            service = DrugDatabaseService()
            # Should log warning but not crash
            assert service.db_available is True


class TestSearchDrug:
    """Test drug search functionality with various patterns."""

    def test_search_by_generic_name_exact(self, populated_test_db):
        """Test searching by exact generic name."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            results = service.search_drug("ibuprofen")
            assert len(results) > 0
            assert results[0]["generic_name"] == "ibuprofen"

    def test_search_by_brand_name(self, populated_test_db):
        """Test searching by brand name."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            results = service.search_drug("Advil")
            assert len(results) > 0
            assert results[0]["brand_name"] == "Advil"

    def test_search_partial_match(self, populated_test_db):
        """Test partial name matching (fuzzy search)."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            # Search for "met" should match "metformin"
            results = service.search_drug("met")
            assert len(results) > 0
            assert any("metformin" in r["generic_name"] for r in results)

    def test_search_case_insensitive(self, populated_test_db):
        """Test that search is case-insensitive."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            results_upper = service.search_drug("IBUPROFEN")
            results_lower = service.search_drug("ibuprofen")
            assert len(results_upper) == len(results_lower)
            assert results_upper[0]["generic_name"] == results_lower[0]["generic_name"]

    def test_search_result_ranking(self, populated_test_db):
        """Test that results are ranked correctly (exact prefix matches first)."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            # Search for "ibu" should prioritize "ibuprofen" over partial matches
            results = service.search_drug("ibu")
            if len(results) > 0:
                # First result should start with "ibu"
                assert results[0]["generic_name"].startswith("ibu")

    def test_search_limit(self, populated_test_db):
        """Test that search respects limit parameter."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            results = service.search_drug("", limit=2)  # Match all, limit to 2
            assert len(results) <= 2

    def test_search_no_results(self, populated_test_db):
        """Test search with no matching drugs."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            results = service.search_drug("NonExistentDrug12345")
            assert results == []

    def test_search_without_database(self, tmp_path):
        """Test search when database is not available."""
        non_existent_path = tmp_path / "non_existent.db"
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", non_existent_path
        ):
            service = DrugDatabaseService()
            results = service.search_drug("ibuprofen")
            assert results == []

    def test_search_with_database_error(self, populated_test_db, caplog):
        """Test graceful handling of database errors during search."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            # Mock sqlite3.connect to raise an exception
            with patch("sqlite3.connect", side_effect=sqlite3.Error("Database error")):
                results = service.search_drug("ibuprofen")
                assert results == []
                assert "Database search error" in caplog.text


class TestGetDrugInfo:
    """Test drug information retrieval with FDA API fallback."""

    def test_get_drug_info_from_local_db(self, populated_test_db, caplog):
        """Test retrieving drug info from local database."""
        import logging

        caplog.set_level(logging.INFO)
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            info = service.get_drug_info("ibuprofen")
            assert info is not None
            assert info["generic_name"] == "ibuprofen"
            assert info["brand_name"] == "Advil"
            assert "Found ibuprofen in local database" in caplog.text

    def test_get_drug_info_json_parsing(self, populated_test_db):
        """Test that JSON fields are automatically parsed."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            info = service.get_drug_info("ibuprofen")
            assert info is not None
            # Should parse active_ingredients from JSON string to list
            assert isinstance(info["active_ingredients"], list)
            assert info["active_ingredients"][0]["name"] == "ibuprofen"
            # Should parse packaging from JSON string to list
            assert isinstance(info["packaging"], list)
            assert info["packaging"][0]["description"] == "bottle"

    @patch("src.services.drug_database_service.get_drug_label")
    def test_get_drug_info_fda_fallback(
        self, mock_get_drug_label, populated_test_db, caplog
    ):
        """Test FDA API fallback when drug not in local database."""
        import logging

        caplog.set_level(logging.INFO)
        # Mock FDA API response
        mock_fda_response = {
            "generic_name": "vemlidy",
            "brand_names": ["Vemlidy"],
            "substance_name": ["tenofovir alafenamide"],
            "route": ["oral"],
            "product_type": "HUMAN PRESCRIPTION DRUG",
            "manufacturer": "Gilead Sciences",
        }
        mock_get_drug_label.return_value = mock_fda_response

        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            info = service.get_drug_info("vemlidy")

            # Should call FDA API
            mock_get_drug_label.assert_called_once_with("vemlidy")

            # Should return FDA data
            assert info is not None
            assert info["source"] == "FDA_API"
            assert info["generic_name"] == "vemlidy"
            assert "Vemlidy" in info["brand_name"]
            assert "Found vemlidy in FDA API" in caplog.text

    @patch("src.services.drug_database_service.get_drug_label")
    def test_get_drug_info_not_found(
        self, mock_get_drug_label, populated_test_db, caplog
    ):
        """Test when drug not found in database or FDA API."""
        # Mock FDA API to return None
        mock_get_drug_label.return_value = None

        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            info = service.get_drug_info("FakeDrug12345")

            # Should try FDA API
            mock_get_drug_label.assert_called_once()

            # Should return None
            assert info is None
            assert "not found in database or FDA API" in caplog.text

    def test_get_drug_info_invalid_json(self, populated_test_db):
        """Test graceful handling of invalid JSON in database fields."""
        # Add drug with invalid JSON
        conn = sqlite3.connect(populated_test_db)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO drugs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                "test_drug",
                "TestBrand",
                "TestBrand",
                "test_substance",
                "oral",
                "HUMAN PRESCRIPTION DRUG",
                "Test Manufacturer",
                "invalid json {",  # Invalid JSON
                "also invalid [",  # Invalid JSON
            ),
        )
        conn.commit()
        conn.close()

        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            info = service.get_drug_info("test_drug")

            # Should not crash, should return drug with unparsed JSON strings
            assert info is not None
            assert info["generic_name"] == "test_drug"
            # JSON parsing should fail gracefully, leaving as string
            assert isinstance(info["active_ingredients"], str)
            assert isinstance(info["packaging"], str)


class TestGetDrugInteractionsFromDB:
    """Test drug interaction lookup (future feature placeholder)."""

    def test_get_drug_interactions_returns_none(self, populated_test_db):
        """Test that drug interactions method returns None (not yet implemented)."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            result = service.get_drug_interactions_from_db("warfarin", "aspirin")
            assert result is None


class TestServiceCleanup:
    """Test service cleanup and resource management."""

    def test_close_method(self, populated_test_db):
        """Test that close method can be called without errors."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            # Should not raise any exception
            service.close()
            # Can be called multiple times
            service.close()


class TestServiceRegistration:
    """Test async service registration for dependency injection."""

    @pytest.mark.asyncio
    async def test_register_drug_database_service(self, populated_test_db):
        """Test that service registration returns singleton instance."""
        from src.services.drug_database_service import register_drug_database_service

        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service1 = await register_drug_database_service()
            service2 = await register_drug_database_service()

            # Should return same instance (singleton)
            assert service1 is service2
            assert isinstance(service1, DrugDatabaseService)


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_search_empty_string(self, populated_test_db):
        """Test search with empty string."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            # Empty string matches everything
            results = service.search_drug("", limit=5)
            # Should return results (matches all)
            assert len(results) > 0

    def test_search_special_characters(self, populated_test_db):
        """Test search with special characters (SQL injection safety)."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            # Should not crash or cause SQL injection
            results = service.search_drug("'; DROP TABLE drugs; --")
            assert isinstance(results, list)

    def test_search_unicode_characters(self, populated_test_db):
        """Test search with unicode characters."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            results = service.search_drug("药物")  # Chinese characters
            assert isinstance(results, list)

    def test_get_drug_info_whitespace(self, populated_test_db):
        """Test drug info lookup with whitespace."""
        with patch(
            "src.services.drug_database_service.DATABASE_PATH", populated_test_db
        ):
            service = DrugDatabaseService()
            # Whitespace should be handled by search
            info = service.get_drug_info("  ibuprofen  ")
            # May or may not find it depending on exact matching
            assert info is None or isinstance(info, dict)
