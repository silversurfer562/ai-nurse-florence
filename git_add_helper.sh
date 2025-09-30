#!/bin/bash
# Git Helper Script - Safely add files to your git repository
# Usage: ./git_add_helper.sh [options]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Git Add Helper - AI Nurse Florence${NC}"
echo "=================================================="

# Navigate to repository root
REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

# Function to show current status
show_status() {
    echo -e "\n${BLUE}📊 Current Git Status:${NC}"
    echo "======================"
    
    # Show branch info
    echo -e "${GREEN}Current branch:${NC} $(git branch --show-current)"
    
    # Show modified files
    if [[ $(git status --porcelain | wc -l) -eq 0 ]]; then
        echo -e "${GREEN}✅ Working tree is clean${NC}"
    else
        echo -e "\n${YELLOW}📝 Modified files:${NC}"
        git status --short
        
        echo -e "\n${YELLOW}📋 Detailed status:${NC}"
        git status
    fi
}

# Function to add files safely
add_files() {
    local mode="$1"
    
    case "$mode" in
        "interactive")
            echo -e "\n${BLUE}🎯 Interactive file selection:${NC}"
            git add --interactive
            ;;
        "all")
            echo -e "\n${YELLOW}⚠️  Adding ALL modified and new files...${NC}"
            echo "Files to be added:"
            git status --porcelain
            read -p "Are you sure? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                git add .
                echo -e "${GREEN}✅ All files added${NC}"
            else
                echo -e "${RED}❌ Cancelled${NC}"
            fi
            ;;
        "modified")
            echo -e "\n${BLUE}📝 Adding only modified files (not new files):${NC}"
            git add -u
            echo -e "${GREEN}✅ Modified files added${NC}"
            ;;
        "specific")
            echo -e "\n${BLUE}🎯 Add specific files:${NC}"
            echo "Available files to add:"
            git status --porcelain | head -20
            echo ""
            read -p "Enter file path(s) separated by spaces: " files
            if [[ -n "$files" ]]; then
                git add $files
                echo -e "${GREEN}✅ Specified files added${NC}"
            else
                echo -e "${RED}❌ No files specified${NC}"
            fi
            ;;
    esac
}

# Function to commit changes
commit_changes() {
    echo -e "\n${BLUE}💾 Commit Changes:${NC}"
    
    # Check if there are staged changes
    if git diff --staged --quiet; then
        echo -e "${YELLOW}⚠️  No staged changes to commit${NC}"
        return
    fi
    
    echo "Staged changes:"
    git diff --staged --name-only
    
    echo ""
    echo "Commit message examples:"
    echo "  feat: add new medical lookup feature"
    echo "  fix: resolve authentication bug"
    echo "  docs: update API documentation"
    echo "  refactor: improve error handling"
    echo "  test: add unit tests for disease service"
    echo ""
    
    read -p "Enter commit message: " message
    if [[ -n "$message" ]]; then
        git commit -m "$message"
        echo -e "${GREEN}✅ Changes committed${NC}"
        
        # Ask about pushing
        read -p "Push to remote? (y/N): " push_confirm
        if [[ $push_confirm =~ ^[Yy]$ ]]; then
            branch=$(git branch --show-current)
            git push origin "$branch"
            echo -e "${GREEN}✅ Changes pushed to origin/$branch${NC}"
        fi
    else
        echo -e "${RED}❌ No commit message provided${NC}"
    fi
}

# Function to show help
show_help() {
    echo ""
    echo "Git Add Helper Usage:"
    echo "===================="
    echo ""
    echo "Options:"
    echo "  --status     Show current git status"
    echo "  --all        Add all modified and new files"
    echo "  --modified   Add only modified files (not new files)"
    echo "  --specific   Add specific files interactively"
    echo "  --interactive Use git's interactive add mode"
    echo "  --commit     Add files and commit in one step"
    echo "  --help       Show this help message"
    echo ""
    echo "Safety Tips:"
    echo "  - Always review files with --status before adding"
    echo "  - Use --specific for precise control"
    echo "  - Use --modified to avoid adding unwanted new files"
    echo "  - Check .gitignore to ensure proper file exclusions"
    echo ""
}

# Parse command line arguments
case "${1:-}" in
    --status)
        show_status
        ;;
    --all)
        show_status
        add_files "all"
        ;;
    --modified)
        show_status
        add_files "modified"
        ;;
    --specific)
        show_status
        add_files "specific"
        ;;
    --interactive)
        show_status
        add_files "interactive"
        ;;
    --commit)
        show_status
        echo ""
        echo "Choose files to add:"
        echo "1) All files"
        echo "2) Modified files only"
        echo "3) Specific files"
        echo "4) Interactive selection"
        read -p "Enter choice (1-4): " choice
        case $choice in
            1) add_files "all" ;;
            2) add_files "modified" ;;
            3) add_files "specific" ;;
            4) add_files "interactive" ;;
            *) echo -e "${RED}❌ Invalid choice${NC}"; exit 1 ;;
        esac
        commit_changes
        ;;
    --help)
        show_help
        ;;
    "")
        # Interactive mode
        show_status
        echo ""
        echo "What would you like to do?"
        echo "1) Show detailed status"
        echo "2) Add all files"
        echo "3) Add modified files only"
        echo "4) Add specific files"
        echo "5) Use interactive add"
        echo "6) Add and commit"
        echo "7) Show help"
        echo ""
        read -p "Enter choice (1-7): " choice
        
        case $choice in
            1) show_status ;;
            2) add_files "all" ;;
            3) add_files "modified" ;;
            4) add_files "specific" ;;
            5) add_files "interactive" ;;
            6) 
                add_files "all"
                commit_changes
                ;;
            7) show_help ;;
            *) echo -e "${RED}❌ Invalid choice${NC}"; exit 1 ;;
        esac
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        show_help
        exit 1
        ;;
esac

echo -e "\n${GREEN}🎉 Git helper completed!${NC}"