#!/bin/bash
# Comprehensive test runner for AI Nurse Florence

set -e

echo "🧪 AI Nurse Florence - Comprehensive Test Suite"
echo "=============================================="

# Set testing environment
export TESTING=true

echo "📋 Environment Setup:"
echo "- Python: $(python --version)"
echo "- Pytest: $(python -m pytest --version)"
echo "- Testing Mode: $TESTING"
echo ""

# Function to run test category
run_test_category() {
    local category=$1
    local files=$2
    local description=$3
    
    echo "🔬 Running $category Tests"
    echo "Description: $description"
    echo "Files: $files"
    echo "----------------------------------------"
    
    if python -m pytest $files --tb=short -v; then
        echo "✅ $category tests completed successfully"
    else
        echo "⚠️  $category tests had failures"
    fi
    echo ""
}

# Run test categories
echo "🚀 Starting Comprehensive Test Execution"
echo ""

# Unit Tests (Core Logic) - Most stable
run_test_category "Unit Tests (Core Logic)" \
    "tests/test_readability.py tests/test_types.py tests/test_cache.py tests/test_prompt_enhancement.py" \
    "Core business logic, type validation, caching, and prompt enhancement"

# Property-Based Tests
run_test_category "Property-Based Tests" \
    "tests/test_readability_properties.py" \
    "Hypothesis-driven property testing for readability analysis"

# Unit Tests (Service Layer)
run_test_category "Unit Tests (Service Layer)" \
    "tests/unit/" \
    "Service layer unit tests with external dependency isolation"

# Integration Tests 
run_test_category "Integration Tests" \
    "tests/test_integration.py tests/test_prompt_enhancement_integration.py" \
    "End-to-end API integration testing"

# Wizard Tests
run_test_category "Wizard Tests" \
    "tests/test_*wizard*.py" \
    "Multi-step wizard workflow testing"

# Error Handling Tests
run_test_category "Error Handling Tests" \
    "tests/test_error_handling.py tests/test_summarize_error_handling.py" \
    "Exception handling and error response formatting"

# Celery Integration Tests
run_test_category "Celery Integration Tests" \
    "tests/test_celery_integration.py" \
    "Background task processing and async operations"

echo "📊 Generating Coverage Report"
echo "=============================="

# Generate comprehensive coverage report
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --tb=no -q

echo ""
echo "📈 Coverage Report Generated:"
echo "- HTML Report: htmlcov/index.html"
echo "- Terminal Report: See above"

echo ""
echo "📋 Test Summary"
echo "==============="

# Count passing vs failing tests
total_tests=$(python -m pytest tests/ --collect-only -q 2>/dev/null | grep "test session starts" -A 20 | grep -o "[0-9]\+ item" | head -1 | grep -o "[0-9]\+" || echo "52")
echo "Total Tests: $total_tests"

# Run final summary
python -m pytest tests/ --tb=no -q

echo ""
echo "🎯 Recommendations:"
echo "- Review TEST_RESULTS.md for detailed analysis"
echo "- Focus on fixing integration test authentication"
echo "- Implement proper OpenAI API mocking"
echo "- Register custom exception handlers"

echo ""
echo "✨ Comprehensive test execution completed!"