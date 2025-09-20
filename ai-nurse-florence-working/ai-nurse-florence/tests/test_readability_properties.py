"""
Property-based tests for readability service.

These tests verify that the readability service behaves correctly with a variety of inputs.
"""
import pytest
from hypothesis import given, strategies as st
from services.readability_service import analyze_readability


@given(st.text())
def test_analyze_readability_handles_any_text(text):
    """Test that analyze_readability handles any text input without errors."""
    result = analyze_readability(text)
    assert isinstance(result, dict)


@given(st.text(min_size=1, max_size=10000))
def test_analyze_readability_output_structure(text):
    """Test that analyze_readability returns a consistent structure for non-empty text."""
    result = analyze_readability(text)
    assert isinstance(result, dict)
    # Check expected keys based on implementation
    expected_keys = {"flesch_reading_ease", "flesch_kincaid_grade", "sentences", "words", "syllables", "suggestions"}
    for key in expected_keys:
        assert key in result, f"Expected key '{key}' missing from result"


@given(st.text(min_size=100, max_size=1000))
def test_analyze_readability_consistent_scores(text):
    """Test that analyze_readability returns consistent scores for the same input."""
    result1 = analyze_readability(text)
    result2 = analyze_readability(text)
    assert result1 == result2, "Readability analysis should be deterministic"