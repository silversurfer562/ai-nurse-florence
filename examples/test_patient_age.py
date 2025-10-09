# Copyright 2025 Deep Study AI, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Unit Tests for PatientService - Complete example from Tutorial 5

This is the complete, working test file from Tutorial 5: Writing Tests for Healthcare Code.
Use this as a reference when writing tests for your own service methods.

Test Coverage:
- Basic functionality tests
- Edge cases (leap years, boundary dates)
- All clinical age categories
- Error handling (invalid inputs, future dates)
- Fixtures for reusable test data

Testing Pattern: Arrange-Act-Assert
See: docs/PATTERNS.md#testing-patterns
"""

from datetime import date

import pytest

from examples.patient_age_service import PatientService

# ============================================================================
# Fixtures - Reusable test data
# ============================================================================


@pytest.fixture
def patient_service():
    """
    Fixture providing a PatientService instance.

    Returns:
        PatientService: Fresh service instance for each test
    """
    return PatientService()


@pytest.fixture
def sample_adult_birthdate():
    """Fixture providing a birthdate for an adult patient."""
    return "2000-01-15"


@pytest.fixture
def sample_pediatric_birthdate():
    """Fixture providing a birthdate for a pediatric patient."""
    return "2018-03-20"


@pytest.fixture
def sample_geriatric_birthdate():
    """Fixture providing a birthdate for a geriatric patient."""
    return "1950-03-20"


@pytest.fixture
def sample_reference_date():
    """Fixture providing a standard test reference date."""
    return "2025-10-07"


# ============================================================================
# Test Suite
# ============================================================================


class TestPatientService:
    """Test suite for PatientService."""

    # ------------------------------------------------------------------------
    # Basic Functionality Tests
    # ------------------------------------------------------------------------

    def test_calculate_age_basic(self, patient_service):
        """Test basic age calculation for an adult patient."""
        # Arrange: Set up test data
        date_of_birth = "2000-01-15"
        reference_date = "2025-01-15"  # Exactly 25 years later

        # Act: Call the method
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert: Verify results
        assert result["years"] == 25
        assert result["months"] == 0
        assert result["days"] == 0
        assert result["age_category"] == "adult"
        assert result["total_days"] == 9131  # 25 years including leap years

    def test_calculate_age_partial_year(self, patient_service, sample_reference_date):
        """Test age calculation with partial year (months and days)."""
        # Arrange
        date_of_birth = "2000-01-15"

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=sample_reference_date
        )

        # Assert
        assert result["years"] == 25
        assert result["months"] == 8
        assert result["days"] == 22  # From Jan 15 to Oct 7
        assert result["age_category"] == "adult"
        # total_days should be positive and reasonable
        assert result["total_days"] > 9000

    def test_calculate_age_today_default(self, patient_service):
        """Test age calculation defaults to today when no reference date provided."""
        # Arrange
        date_of_birth = "2000-01-15"

        # Act
        result = patient_service.calculate_age(date_of_birth=date_of_birth)

        # Assert
        # Should use today's date
        assert result["reference_date"] == date.today().isoformat()
        # Age should be approximately 25 (depends on when test runs)
        assert result["years"] >= 25

    # ------------------------------------------------------------------------
    # Clinical Age Category Tests
    # ------------------------------------------------------------------------

    def test_calculate_age_infant(self, patient_service):
        """Test age calculation for infant (under 1 year)."""
        # Arrange
        date_of_birth = "2024-06-15"
        reference_date = "2025-10-07"  # About 16 months old

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert
        assert result["years"] == 1
        assert result["months"] == 3
        assert result["age_category"] == "infant"  # Under 1 year

    def test_calculate_age_pediatric(
        self, patient_service, sample_pediatric_birthdate, sample_reference_date
    ):
        """Test age calculation for pediatric patient (1-12 years)."""
        # Arrange (using fixtures)

        # Act
        result = patient_service.calculate_age(
            date_of_birth=sample_pediatric_birthdate,
            reference_date=sample_reference_date,
        )

        # Assert
        assert result["years"] == 7
        assert result["age_category"] == "pediatric"

    def test_calculate_age_adolescent(self, patient_service):
        """Test age calculation for adolescent (13-17 years)."""
        # Arrange
        date_of_birth = "2010-05-10"
        reference_date = "2025-10-07"

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert
        assert result["years"] == 15
        assert result["age_category"] == "adolescent"

    def test_calculate_age_adult(
        self, patient_service, sample_adult_birthdate, sample_reference_date
    ):
        """Test age calculation for adult (18-64 years)."""
        # Arrange (using fixtures)

        # Act
        result = patient_service.calculate_age(
            date_of_birth=sample_adult_birthdate, reference_date=sample_reference_date
        )

        # Assert
        assert result["years"] == 25
        assert result["age_category"] == "adult"

    def test_calculate_age_geriatric(
        self, patient_service, sample_geriatric_birthdate, sample_reference_date
    ):
        """Test age calculation for geriatric patient (65+ years)."""
        # Arrange (using fixtures)

        # Act
        result = patient_service.calculate_age(
            date_of_birth=sample_geriatric_birthdate,
            reference_date=sample_reference_date,
        )

        # Assert
        assert result["years"] == 75
        assert result["age_category"] == "geriatric"

    # ------------------------------------------------------------------------
    # Edge Case Tests
    # ------------------------------------------------------------------------

    def test_calculate_age_leap_year_birthday(self, patient_service):
        """Test age calculation for someone born on leap day."""
        # Arrange
        date_of_birth = "2000-02-29"  # Leap year
        reference_date = "2025-03-01"

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert
        assert result["years"] == 25
        # Should handle leap year correctly
        assert result["months"] == 0
        assert result["days"] == 1  # March 1 is 1 day after Feb 29

    def test_calculate_age_same_day(self, patient_service):
        """Test age calculation on exact birthday."""
        # Arrange
        date_of_birth = "2000-10-07"
        reference_date = "2025-10-07"  # Same month/day, 25 years later

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert
        assert result["years"] == 25
        assert result["months"] == 0
        assert result["days"] == 0

    def test_calculate_age_one_day_before_birthday(self, patient_service):
        """Test age calculation one day before birthday."""
        # Arrange
        date_of_birth = "2000-10-08"
        reference_date = "2025-10-07"  # One day before birthday

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert
        assert result["years"] == 24  # Still 24, not 25 yet
        assert result["months"] == 11
        assert result["days"] >= 28  # About a month minus 1 day

    # ------------------------------------------------------------------------
    # Error Handling Tests
    # ------------------------------------------------------------------------

    def test_calculate_age_future_date_raises_error(self, patient_service):
        """Test that future date of birth raises ValueError."""
        # Arrange
        date_of_birth = "2030-01-01"  # Future date
        reference_date = "2025-10-07"

        # Act & Assert: Verify exception is raised
        with pytest.raises(ValueError, match="is in the future"):
            patient_service.calculate_age(
                date_of_birth=date_of_birth, reference_date=reference_date
            )

    def test_calculate_age_invalid_format_raises_error(self, patient_service):
        """Test that invalid date format raises ValueError."""
        # Arrange
        date_of_birth = "01/15/2000"  # Wrong format (MM/DD/YYYY)

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid date format"):
            patient_service.calculate_age(date_of_birth=date_of_birth)

    def test_calculate_age_invalid_date_raises_error(self, patient_service):
        """Test that invalid date (e.g., Feb 30) raises ValueError."""
        # Arrange
        date_of_birth = "2000-02-30"  # February doesn't have 30 days

        # Act & Assert
        with pytest.raises(ValueError):
            patient_service.calculate_age(date_of_birth=date_of_birth)

    def test_calculate_age_empty_string_raises_error(self, patient_service):
        """Test that empty string raises ValueError."""
        # Arrange
        date_of_birth = ""

        # Act & Assert
        with pytest.raises(ValueError):
            patient_service.calculate_age(date_of_birth=date_of_birth)

    def test_calculate_age_invalid_reference_date_raises_error(self, patient_service):
        """Test that invalid reference date raises ValueError."""
        # Arrange
        date_of_birth = "2000-01-15"
        reference_date = "invalid-date"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid reference date"):
            patient_service.calculate_age(
                date_of_birth=date_of_birth, reference_date=reference_date
            )

    # ------------------------------------------------------------------------
    # Boundary Tests
    # ------------------------------------------------------------------------

    def test_calculate_age_boundary_infant_to_pediatric(self, patient_service):
        """Test age category boundary between infant and pediatric (1 year)."""
        # Arrange
        date_of_birth = "2024-10-07"
        reference_date = "2025-10-07"  # Exactly 1 year

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert
        assert result["years"] == 1
        assert result["months"] == 0
        # At exactly 1 year, should be infant (under 1 year in months)
        # But our logic uses years, so it's infant
        assert result["age_category"] == "infant"

    def test_calculate_age_boundary_pediatric_to_adolescent(self, patient_service):
        """Test age category boundary between pediatric and adolescent (13 years)."""
        # Arrange
        date_of_birth = "2012-10-07"
        reference_date = "2025-10-07"  # Exactly 13 years

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert
        assert result["years"] == 13
        assert result["age_category"] == "adolescent"

    def test_calculate_age_boundary_adolescent_to_adult(self, patient_service):
        """Test age category boundary between adolescent and adult (18 years)."""
        # Arrange
        date_of_birth = "2007-10-07"
        reference_date = "2025-10-07"  # Exactly 18 years

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert
        assert result["years"] == 18
        assert result["age_category"] == "adult"

    def test_calculate_age_boundary_adult_to_geriatric(self, patient_service):
        """Test age category boundary between adult and geriatric (65 years)."""
        # Arrange
        date_of_birth = "1960-10-07"
        reference_date = "2025-10-07"  # Exactly 65 years

        # Act
        result = patient_service.calculate_age(
            date_of_birth=date_of_birth, reference_date=reference_date
        )

        # Assert
        assert result["years"] == 65
        assert result["age_category"] == "geriatric"


# ============================================================================
# Run tests with coverage
# ============================================================================

if __name__ == "__main__":
    """
    Run tests directly from this file.

    Usage:
        python examples/test_patient_age.py

    Or better, use pytest:
        pytest examples/test_patient_age.py -v
        pytest examples/test_patient_age.py --cov=examples.patient_age_service --cov-report=term-missing
    """
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=examples.patient_age_service",
            "--cov-report=term-missing",
        ]
    )
