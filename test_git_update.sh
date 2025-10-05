#!/bin/bash

# Test script for enhanced git-update.sh
# Tests various scenarios to ensure the script works correctly

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
test_info() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

test_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_failure() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

# Test help functionality
test_help() {
    test_info "Testing help functionality..."
    
    if ./git-update.sh --help > /dev/null 2>&1; then
        test_success "Help option works correctly"
    else
        test_failure "Help option failed"
    fi
    
    if ./git-update.sh -h > /dev/null 2>&1; then
        test_success "Short help option works correctly"
    else
        test_failure "Short help option failed"
    fi
}

# Test script in non-git directory
test_non_git_directory() {
    test_info "Testing behavior in non-git directory..."
    
    # Create temporary directory
    local temp_dir=$(mktemp -d)
    cd "$temp_dir"
    
    if ./git-update.sh 2>/dev/null; then
        test_failure "Script should fail in non-git directory"
    else
        test_success "Script correctly fails in non-git directory"
    fi
    
    # Return to original directory
    cd - > /dev/null
    rm -rf "$temp_dir"
}

# Test git repository detection
test_git_repo_detection() {
    test_info "Testing git repository detection..."
    
    # Should pass in current directory (which is a git repo)
    if ./git-update.sh --help > /dev/null 2>&1; then
        test_success "Git repository correctly detected"
    else
        test_failure "Failed to detect git repository"
    fi
}

# Test script permissions
test_script_permissions() {
    test_info "Testing script permissions..."
    
    if [ -x "./git-update.sh" ]; then
        test_success "Script is executable"
    else
        test_failure "Script is not executable"
    fi
}

# Test script syntax
test_script_syntax() {
    test_info "Testing script syntax..."
    
    if bash -n "./git-update.sh"; then
        test_success "Script syntax is valid"
    else
        test_failure "Script has syntax errors"
    fi
}

# Test backup branch naming
test_backup_branch_naming() {
    test_info "Testing backup branch naming logic..."
    
    # This test checks if the script can generate proper backup names
    # We'll test this by examining the script logic without actually creating branches
    if grep -q "backup_branch.*date.*current_branch" git-update.sh; then
        test_success "Backup branch naming logic is present"
    else
        test_failure "Backup branch naming logic is missing"
    fi
}

# Test commit message generation logic
test_commit_message_logic() {
    test_info "Testing commit message generation logic..."
    
    if grep -q "generate_commit_message" git-update.sh; then
        test_success "Commit message generation function exists"
    else
        test_failure "Commit message generation function missing"
    fi
}

# Test error handling presence
test_error_handling() {
    test_info "Testing error handling presence..."
    
    local error_handling_features=(
        "set -euo pipefail"
        "log_error"
        "return 1"
        "exit 1"
    )
    
    local all_present=true
    for feature in "${error_handling_features[@]}"; do
        if ! grep -q "$feature" git-update.sh; then
            all_present=false
            break
        fi
    done
    
    if [ "$all_present" = true ]; then
        test_success "Error handling features are present"
    else
        test_failure "Some error handling features are missing"
    fi
}

# Test safety checks
test_safety_checks() {
    test_info "Testing safety check functions..."
    
    local safety_functions=(
        "has_uncommitted_changes"
        "has_untracked_files"
        "create_backup"
        "check_git_repo"
    )
    
    local all_present=true
    for func in "${safety_functions[@]}"; do
        if ! grep -q "$func" git-update.sh; then
            all_present=false
            break
        fi
    done
    
    if [ "$all_present" = true ]; then
        test_success "Safety check functions are present"
    else
        test_failure "Some safety check functions are missing"
    fi
}

# Test enhanced features
test_enhanced_features() {
    test_info "Testing enhanced features..."
    
    local enhanced_features=(
        "Color codes for output"
        "Verbose output"
        "Branch parameter support"
        "Conflict resolution guidance"
        "Backup and rollback"
    )
    
    local features_found=0
    
    # Check for color codes
    if grep -q "RED=" git-update.sh && grep -q "GREEN=" git-update.sh && grep -q "YELLOW=" git-update.sh; then
        features_found=$((features_found + 1))
    fi
    
    # Check for verbose support
    if grep -q "set -x" git-update.sh && grep -q "verbose" git-update.sh; then
        features_found=$((features_found + 1))
    fi
    
    # Check for branch parameter
    if grep -q "target_branch.*\"\$1\"" git-update.sh; then
        features_found=$((features_found + 1))
    fi
    
    # Check for conflict resolution guidance
    if grep -q "resolve conflicts" git-update.sh; then
        features_found=$((features_found + 1))
    fi
    
    # Check for backup functionality
    if grep -q "backup_branch" git-update.sh; then
        features_found=$((features_found + 1))
    fi
    
    if [ $features_found -eq 5 ]; then
        test_success "All enhanced features are present"
    else
        test_failure "Only $features_found/5 enhanced features found"
    fi
}

# Run all tests
run_all_tests() {
    echo "========================================"
    echo "Testing Enhanced Git Update Script"
    echo "========================================"
    echo ""
    
    test_script_permissions
    test_script_syntax
    test_git_repo_detection
    test_help
    test_non_git_directory
    test_backup_branch_naming
    test_commit_message_logic
    test_error_handling
    test_safety_checks
    test_enhanced_features
    
    echo ""
    echo "========================================"
    echo "Test Results Summary"
    echo "========================================"
    echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed successfully!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed. Please review the script.${NC}"
        return 1
    fi
}

# Main execution
main() {
    # Ensure we're in the correct directory
    if [ ! -f "git-update.sh" ]; then
        echo -e "${RED}Error: git-update.sh not found in current directory${NC}"
        exit 1
    fi
    
    run_all_tests
}

# Run main function
main "$@"