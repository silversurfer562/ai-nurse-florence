#!/bin/bash
# Git Repository Cleanup Script
# Removes problematic files and provides proper git workflow

set -euo pipefail

echo "🧹 Git Repository Cleanup Tool"
echo "==============================="

# Navigate to repo root
cd "$(dirname "$0")"

echo "📍 Current directory: $(pwd)"
echo ""

# Check current git status
echo "📊 Current git status:"
git status --porcelain
echo ""

# List problematic files that are tracked
echo "🚨 Problematic files currently tracked in git:"
PROBLEMATIC_FILES=(
    "# Add this to app.py for debugging"
    "=2.2,"
    "=2.7," 
    "nul"
    "src\\app_enhanced.py"
    "src\\static\\css\\clinical-swagger.css"
    "src\\static\\js\\clinical-components.js"
    ".rebuild-1759171525"
)

for file in "${PROBLEMATIC_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "  ❌ $file"
    fi
done
echo ""

# Function to safely remove problematic files
cleanup_files() {
    echo "🗑️  Removing problematic files from git tracking..."
    
    for file in "${PROBLEMATIC_FILES[@]}"; do
        if [[ -f "$file" ]]; then
            echo "  Removing: $file"
            git rm --cached "$file" 2>/dev/null || true
            rm -f "$file" 2>/dev/null || true
        fi
    done
    
    echo "✅ Cleanup complete!"
}

# Function to update .gitignore
update_gitignore() {
    echo "📝 Updating .gitignore to prevent future issues..."
    
    # Add rules to prevent problematic files
    cat >> .gitignore << 'EOF'

# ================================
# CLEANUP: Prevent problematic files
# ================================
# Files with special characters that cause issues
*=*,*
nul
*.tmp.*
*#*debugging*
*\\*
.rebuild-*

# Command artifacts and temporary files
*.save
temp_*
*_temp*
*_backup*

EOF
    
    echo "✅ .gitignore updated!"
}

# Function to show proper git workflow
show_workflow() {
    echo ""
    echo "📚 PROPER GIT WORKFLOW:"
    echo "======================="
    echo ""
    echo "🔍 1. Check what files are modified or new:"
    echo "   git status"
    echo ""
    echo "📂 2. Add specific files (recommended):"
    echo "   git add path/to/specific/file.py"
    echo "   git add utils/config.py"
    echo ""
    echo "📂 3. Or add all files in a directory:"
    echo "   git add src/"
    echo "   git add utils/"
    echo ""
    echo "📂 4. Or add all modified files (be careful!):"
    echo "   git add ."
    echo ""
    echo "💾 5. Commit your changes:"
    echo "   git commit -m \"feat: descriptive commit message\""
    echo ""
    echo "🚀 6. Push to remote:"
    echo "   git push origin branch-name"
    echo ""
    echo "⚠️  ALWAYS review files before adding with 'git status' and 'git diff'"
}

# Main execution
echo "Select an action:"
echo "1) Clean up problematic files"
echo "2) Update .gitignore rules"
echo "3) Show proper git workflow"
echo "4) Do all of the above"
echo "5) Just show current status"
echo ""

if [[ "${1:-}" == "--auto" ]]; then
    echo "🤖 Auto mode: Performing cleanup and updates..."
    cleanup_files
    update_gitignore
    show_workflow
else
    read -p "Enter choice (1-5): " choice
    
    case $choice in
        1)
            cleanup_files
            ;;
        2)
            update_gitignore
            ;;
        3)
            show_workflow
            ;;
        4)
            cleanup_files
            update_gitignore
            show_workflow
            ;;
        5)
            echo "📊 Current status:"
            git status
            ;;
        *)
            echo "❌ Invalid choice"
            exit 1
            ;;
    esac
fi

echo ""
echo "🎉 Git cleanup script completed!"
echo "💡 Run 'git status' to see current state"