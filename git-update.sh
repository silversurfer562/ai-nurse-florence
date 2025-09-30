#!/bin/bash

# AI Nurse Florence - Enhanced Git Update Script
# Safely updates the repository with proper error handling and safety checks

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_BRANCH="main"
COMMIT_MESSAGE_PREFIX="update"
BACKUP_BRANCH_PREFIX="backup"

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_error "Not in a git repository!"
        exit 1
    fi
}

# Get current branch name
get_current_branch() {
    git branch --show-current 2>/dev/null || git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "HEAD"
}

# Check if there are uncommitted changes
has_uncommitted_changes() {
    ! git diff-index --quiet HEAD --
}

# Check if there are untracked files
has_untracked_files() {
    [ -n "$(git ls-files --others --exclude-standard)" ]
}

# Create backup branch
create_backup() {
    local current_branch=$(get_current_branch)
    local backup_branch="${BACKUP_BRANCH_PREFIX}-$(date +%Y%m%d-%H%M%S)-${current_branch}"
    
    log_info "Creating backup branch: $backup_branch"
    if git branch "$backup_branch"; then
        log_success "Backup branch created successfully"
        echo "$backup_branch"
    else
        log_error "Failed to create backup branch"
        return 1
    fi
}

# Generate meaningful commit message
generate_commit_message() {
    local files_changed=$(git diff --cached --name-only | wc -l)
    local files_added=$(git diff --cached --name-status | grep -c "^A" || echo 0)
    local files_modified=$(git diff --cached --name-status | grep -c "^M" || echo 0)
    local files_deleted=$(git diff --cached --name-status | grep -c "^D" || echo 0)
    
    local message="${COMMIT_MESSAGE_PREFIX}: "
    
    if [ "$files_changed" -eq 1 ]; then
        # Single file change - use filename
        local filename=$(git diff --cached --name-only)
        message="${message}update $(basename "$filename")"
    else
        # Multiple files - use summary
        local parts=()
        [ "$files_added" -gt 0 ] && parts+=("${files_added} added")
        [ "$files_modified" -gt 0 ] && parts+=("${files_modified} modified")  
        [ "$files_deleted" -gt 0 ] && parts+=("${files_deleted} deleted")
        
        if [ ${#parts[@]} -gt 0 ]; then
            message="${message}$(IFS=', '; echo "${parts[*]}")"
        else
            message="${message}latest changes"
        fi
    fi
    
    echo "$message"
}

# Main update function
perform_git_update() {
    local target_branch="${1:-$DEFAULT_BRANCH}"
    local current_branch=$(get_current_branch)
    
    log_info "Starting git update process..."
    log_info "Current branch: $current_branch"
    log_info "Target branch: $target_branch"
    
    # Check if there are any changes to commit
    if ! has_uncommitted_changes && ! has_untracked_files; then
        log_warning "No changes to commit. Checking for remote updates..."
        
        # Fetch to check for remote changes
        log_info "Fetching remote changes..."
        if ! git fetch origin "$target_branch"; then
            log_error "Failed to fetch from remote"
            return 1
        fi
        
        # Check if we're behind remote
        local behind_count=$(git rev-list --count HEAD..origin/"$target_branch" 2>/dev/null || echo 0)
        if [ "$behind_count" -gt 0 ]; then
            log_info "Remote has $behind_count new commits. Pulling changes..."
            if git pull --rebase origin "$target_branch"; then
                log_success "Successfully pulled $behind_count commits from remote"
            else
                log_error "Failed to pull from remote"
                return 1
            fi
        else
            log_success "Repository is up to date"
        fi
        return 0
    fi
    
    # Create backup before making changes
    local backup_branch
    if ! backup_branch=$(create_backup); then
        return 1
    fi
    
    # Add changes to staging
    log_info "Adding changes to staging area..."
    if ! git add .; then
        log_error "Failed to add changes to staging"
        return 1
    fi
    
    # Generate and show commit message
    local commit_message=$(generate_commit_message)
    log_info "Commit message: $commit_message"
    
    # Commit changes
    log_info "Committing changes..."
    if ! git commit -m "$commit_message"; then
        log_error "Failed to commit changes"
        return 1
    fi
    
    log_success "Changes committed successfully"
    
    # Fetch latest from remote
    log_info "Fetching latest changes from remote..."
    if ! git fetch origin "$target_branch"; then
        log_error "Failed to fetch from remote"
        log_warning "You can restore from backup branch: $backup_branch"
        return 1
    fi
    
    # Rebase with remote
    log_info "Rebasing with remote changes..."
    if ! git pull --rebase origin "$target_branch"; then
        log_error "Rebase failed - you may need to resolve conflicts manually"
        log_warning "You can restore from backup branch: $backup_branch"
        log_info "To resolve conflicts:"
        log_info "  1. Fix conflicts in the files"
        log_info "  2. Run: git add <conflicted-files>"
        log_info "  3. Run: git rebase --continue"
        log_info "  4. Run: git push origin $target_branch"
        return 1
    fi
    
    log_success "Rebase completed successfully"
    
    # Push to remote
    log_info "Pushing changes to remote..."
    if ! git push origin "$target_branch"; then
        log_error "Failed to push to remote"
        log_warning "You can restore from backup branch: $backup_branch"
        return 1
    fi
    
    log_success "Successfully pushed changes to remote"
    log_success "Git update completed successfully!"
    log_info "Backup branch available: $backup_branch"
    
    return 0
}

# Parse command line arguments
show_help() {
    echo "Usage: $0 [OPTIONS] [BRANCH]"
    echo ""
    echo "Enhanced git update script with safety checks and error handling"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help     Show this help message"
    echo "  -v, --verbose  Enable verbose output"
    echo ""
    echo "ARGUMENTS:"
    echo "  BRANCH         Target branch (default: main)"
    echo ""
    echo "EXAMPLES:"
    echo "  $0                    # Update main branch"
    echo "  $0 develop            # Update develop branch" 
    echo "  $0 -v main            # Update main branch with verbose output"
}

# Main execution
main() {
    local target_branch="$DEFAULT_BRANCH"
    local verbose=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
            *)
                target_branch="$1"
                shift
                ;;
        esac
    done
    
    # Enable verbose output if requested
    if [ "$verbose" = true ]; then
        set -x
    fi
    
    # Run pre-checks
    check_git_repo
    
    # Perform the update
    if perform_git_update "$target_branch"; then
        exit 0
    else
        exit 1
    fi
}

# Run main function with all arguments
main "$@"
