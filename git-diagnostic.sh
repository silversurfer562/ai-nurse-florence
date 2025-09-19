#!/bin/bash

echo "🔍 Git Diagnostic Tool for AI Nurse Florence"
echo "==========================================="
echo

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a Git repository!"
    echo "   Run 'git init' to initialize a repository."
    exit 1
fi

echo "✅ In a Git repository"
echo

# Show current status
echo "📍 Current Status:"
echo "   Branch: $(git rev-parse --abbrev-ref HEAD)"
echo "   Commit: $(git rev-parse --short HEAD)"
echo

# Check for uncommitted changes
echo "📝 Working Directory Status:"
if git diff-index --quiet HEAD --; then
    echo "   ✅ No uncommitted changes"
else
    echo "   ⚠️  You have uncommitted changes:"
    git status --porcelain | head -10
    if [ $(git status --porcelain | wc -l) -gt 10 ]; then
        echo "   ... and $(( $(git status --porcelain | wc -l) - 10 )) more files"
    fi
fi
echo

# Check staged files
STAGED=$(git diff --cached --name-only | wc -l)
if [ $STAGED -gt 0 ]; then
    echo "   📦 $STAGED files staged for commit:"
    git diff --cached --name-only | head -5
    if [ $STAGED -gt 5 ]; then
        echo "   ... and $(( $STAGED - 5 )) more files"
    fi
else
    echo "   📦 No files staged for commit"
fi
echo

# Check untracked files
UNTRACKED=$(git ls-files --others --exclude-standard | wc -l)
if [ $UNTRACKED -gt 0 ]; then
    echo "   🆕 $UNTRACKED untracked files:"
    git ls-files --others --exclude-standard | head -5
    if [ $UNTRACKED -gt 5 ]; then
        echo "   ... and $(( $UNTRACKED - 5 )) more files"
    fi
    echo "   💡 Use 'git add <file>' to track them"
else
    echo "   🆕 No untracked files"
fi
echo

# Check remote configuration
echo "🌐 Remote Configuration:"
if git remote | grep -q origin; then
    echo "   ✅ Origin remote configured:"
    echo "      $(git remote get-url origin)"
    
    # Test connectivity
    echo "   🔗 Testing connection..."
    if git ls-remote origin > /dev/null 2>&1; then
        echo "   ✅ Can connect to remote"
    else
        echo "   ❌ Cannot connect to remote"
        echo "      This might be an authentication issue"
    fi
else
    echo "   ❌ No origin remote configured"
    echo "      Add with: git remote add origin <repository-url>"
fi
echo

# Check .gitignore patterns affecting untracked files
if [ $UNTRACKED -gt 0 ] && [ -f .gitignore ]; then
    echo "🚫 Files ignored by .gitignore:"
    IGNORED=$(git ls-files --others --ignored --exclude-standard | wc -l)
    if [ $IGNORED -gt 0 ]; then
        echo "   $IGNORED files are being ignored:"
        git ls-files --others --ignored --exclude-standard | head -3
        if [ $IGNORED -gt 3 ]; then
            echo "   ... and $(( $IGNORED - 3 )) more files"
        fi
    else
        echo "   No additional files are being ignored"
    fi
    echo
fi

# VS Code specific checks
if [ -d .vscode ]; then
    echo "💻 VS Code Configuration:"
    if [ -f .vscode/settings.json ]; then
        echo "   ✅ VS Code settings found"
        if grep -q "git" .vscode/settings.json 2>/dev/null; then
            echo "   🔧 Git-related settings detected"
        fi
    fi
    echo
fi

# Recommendations
echo "💡 Recommendations:"

if [ $UNTRACKED -gt 0 ]; then
    echo "   • You have $UNTRACKED untracked files. Add them with:"
    echo "     git add <filename>  # for specific files"
    echo "     git add .           # for all files"
fi

if ! git diff-index --quiet HEAD --; then
    echo "   • You have uncommitted changes. Commit them with:"
    echo "     git commit -m \"Your commit message\""
fi

if [ $STAGED -gt 0 ]; then
    echo "   • You have staged files ready to commit:"
    echo "     git commit -m \"Your commit message\""
fi

# Check if our git-update.sh would work
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "   • You're on branch '$CURRENT_BRANCH', not 'main'"
    echo "     The updated git-update.sh script handles this automatically"
fi

echo
echo "🚀 Quick Actions:"
echo "   • Run './git-update.sh' to commit and push all changes"
echo "   • Run 'git status' for detailed status"
echo "   • See 'docs/git-troubleshooting.md' for more help"