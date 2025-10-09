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
Patient Service - Complete example from Tutorial 4

This is the complete, working code from Tutorial 4: Adding a New Service Method.
Use this as a reference when implementing your own service methods.

Clinical Context:
- Calculate age for medication dosing
- Determine age-appropriate care protocols
- Support clinical decision-making

Pattern: Service Layer Pattern
See: docs/PATTERNS.md#service-layer-pattern
"""

import logging
from datetime import date, datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class PatientService:
    """
    Business logic for patient operations.

    Clinical Context:
    - Calculate age for medication dosing
    - Determine age-appropriate care protocols
    - Support clinical decision-making

    Pattern: Service Layer Pattern
    See: docs/PATTERNS.md#service-layer-pattern
    """

    def __init__(self):
        """Initialize patient service."""
        logger.info("PatientService initialized")

    def calculate_age(
        self, date_of_birth: str, reference_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate patient age from date of birth.

        Clinical Use Cases:
        - Pediatric dosing calculations (age in months matters)
        - Geriatric risk assessments (age in years)
        - Age-appropriate care protocols

        Args:
            date_of_birth: Patient's birth date in YYYY-MM-DD format
            reference_date: Calculate age as of this date (default: today)

        Returns:
            Dict containing:
                - years: Age in years (int)
                - months: Additional months (int)
                - days: Additional days (int)
                - total_days: Total age in days (int)
                - age_category: Pediatric/Adult/Geriatric (str)
                - date_of_birth: Input DOB (str)
                - reference_date: Reference date used (str)

        Raises:
            ValueError: If date format is invalid or date is in future

        Example:
            >>> service = PatientService()
            >>> service.calculate_age("2000-01-15")
            {
                "years": 25,
                "months": 8,
                "days": 22,
                "total_days": 9396,
                "age_category": "adult",
                "date_of_birth": "2000-01-15",
                "reference_date": "2025-10-07"
            }
        """
        # Step 1: Validate and parse date of birth
        try:
            dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(
                f"Invalid date format: {date_of_birth}. Use YYYY-MM-DD format."
            ) from e

        # Step 2: Determine reference date
        if reference_date:
            try:
                ref_date = datetime.strptime(reference_date, "%Y-%m-%d").date()
            except ValueError as e:
                raise ValueError(
                    f"Invalid reference date: {reference_date}. Use YYYY-MM-DD format."
                ) from e
        else:
            ref_date = date.today()

        # Step 3: Validate date is not in future
        if dob > ref_date:
            raise ValueError(
                f"Date of birth {date_of_birth} is in the future. Cannot calculate age."
            )

        # Step 4: Calculate age components
        years = ref_date.year - dob.year
        months = ref_date.month - dob.month
        days = ref_date.day - dob.day

        # Adjust for negative days
        if days < 0:
            months -= 1
            # Get days in previous month
            prev_month = ref_date.month - 1 if ref_date.month > 1 else 12
            prev_month_year = ref_date.year if ref_date.month > 1 else ref_date.year - 1
            days_in_prev_month = (
                date(prev_month_year, prev_month + 1, 1)
                - date(prev_month_year, prev_month, 1)
            ).days
            days += days_in_prev_month

        # Adjust for negative months
        if months < 0:
            years -= 1
            months += 12

        # Calculate total days
        total_days = (ref_date - dob).days

        # Determine age category (clinical classification)
        age_category = self._determine_age_category(years)

        # Step 5: Return structured result
        result = {
            "years": years,
            "months": months,
            "days": days,
            "total_days": total_days,
            "age_category": age_category,
            "date_of_birth": date_of_birth,
            "reference_date": ref_date.isoformat(),
        }

        logger.info(
            f"Age calculated: {years}y {months}m {days}d (category: {age_category})"
        )

        return result

    def _determine_age_category(self, years: int) -> str:
        """
        Determine clinical age category.

        Categories based on clinical practice:
        - Neonate: 0-1 month (handled in months)
        - Infant: 1-12 months (handled in months)
        - Pediatric: 1-12 years
        - Adolescent: 13-17 years
        - Adult: 18-64 years
        - Geriatric: 65+ years

        Args:
            years: Age in years

        Returns:
            Age category as string (infant/pediatric/adolescent/adult/geriatric)
        """
        if years < 1:
            return "infant"
        elif years < 13:
            return "pediatric"
        elif years < 18:
            return "adolescent"
        elif years < 65:
            return "adult"
        else:
            return "geriatric"


# Example usage (for testing this file directly)
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Create service instance
    service = PatientService()

    # Example 1: Adult patient
    print("\n=== Example 1: Adult Patient ===")
    result = service.calculate_age("2000-01-15")
    print(f"Age: {result['years']}y {result['months']}m {result['days']}d")
    print(f"Category: {result['age_category']}")
    print(f"Total days: {result['total_days']}")

    # Example 2: Pediatric patient
    print("\n=== Example 2: Pediatric Patient ===")
    result = service.calculate_age("2018-03-20")
    print(f"Age: {result['years']}y {result['months']}m {result['days']}d")
    print(f"Category: {result['age_category']}")

    # Example 3: Geriatric patient
    print("\n=== Example 3: Geriatric Patient ===")
    result = service.calculate_age("1950-06-10")
    print(f"Age: {result['years']}y {result['months']}m {result['days']}d")
    print(f"Category: {result['age_category']}")

    # Example 4: With specific reference date
    print("\n=== Example 4: Age as of Specific Date ===")
    result = service.calculate_age("2000-01-15", "2025-01-15")
    print(
        f"Age on 2025-01-15: {result['years']}y {result['months']}m {result['days']}d"
    )

    # Example 5: Error handling - future date
    print("\n=== Example 5: Error Handling ===")
    try:
        service.calculate_age("2030-01-01")
    except ValueError as e:
        print(f"Error (expected): {e}")

    # Example 6: Error handling - invalid format
    try:
        service.calculate_age("01/15/2000")
    except ValueError as e:
        print(f"Error (expected): {e}")
