#!/bin/bash

echo "🚀 AI Nurse Florence - Git Upload Fix"
echo "===================================="
echo
echo "If you have files in VS Code that aren't uploading to Git, this script will help!"
echo

# Make sure we're in the right directory
if [ ! -f "app.py" ] || [ ! -f "git-update.sh" ]; then
    echo "❌ Please run this script from the ai-nurse-florence project root directory"
    exit 1
fi

echo "📋 Checking your current situation..."
echo

# Run diagnostic
./git-diagnostic.sh

echo
echo "🔧 Solutions Available:"
echo

echo "1. 📊 QUICK DIAGNOSIS:"
echo "   ./git-diagnostic.sh"
echo

echo "2. 🚀 QUICK FIX (add, commit, and push all changes):"
echo "   ./git-update.sh \"describe your changes\""
echo

echo "3. 📖 DETAILED TROUBLESHOOTING GUIDE:"
echo "   See: docs/git-troubleshooting.md"
echo "   Or run: cat docs/git-troubleshooting.md"
echo

echo "4. 🔍 MANUAL COMMANDS:"
echo "   git status                    # See what's happening"
echo "   git add .                     # Add all files"
echo "   git commit -m \"message\"       # Commit changes"
echo "   git push origin \$(git rev-parse --abbrev-ref HEAD)  # Push to current branch"
echo

echo "💡 Most Common Issues Solved:"
echo "   ✅ Fixed git-update.sh to work with any branch (not just main)"
echo "   ✅ Added proper error handling and status checks"
echo "   ✅ Created diagnostic tools to identify issues"
echo "   ✅ Improved .gitignore to prevent accidental exclusions"
echo "   ✅ Added comprehensive troubleshooting documentation"
echo

echo "🎯 For VS Code users specifically:"
echo "   • Make sure Git is enabled in VS Code (File → Preferences → Settings → search 'git.enabled')"
echo "   • Check the Source Control panel (Ctrl+Shift+G)"
echo "   • Ensure you're in the correct folder/workspace"
echo "   • Try refreshing the Git status in VS Code"
echo

echo "❓ Still having issues?"
echo "   1. Run './git-diagnostic.sh' and check the output"
echo "   2. Read 'docs/git-troubleshooting.md' for detailed solutions"
echo "   3. Check VS Code's Git output panel for error messages"
echo

echo "🎉 The git-update.sh script has been improved and should now work perfectly!"
echo "    Just run: ./git-update.sh \"your commit message\""