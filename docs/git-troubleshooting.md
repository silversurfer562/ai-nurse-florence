# Git Troubleshooting Guide

## Common Issues with VS Code Git Integration

### Issue: Files Not Uploading to Git

If you have files in VS Code that aren't uploading to Git, here are the most common causes and solutions:

#### 1. Check Git Status
First, check what Git sees:
```bash
git status
```

This will show:
- Untracked files (new files not added to Git)
- Modified files (changes to existing files)
- Staged files (ready to commit)

#### 2. Check .gitignore
Some files might be intentionally ignored:
```bash
git ls-files --others --ignored --exclude-standard
```

Common patterns in `.gitignore` that might affect your files:
- `*.log` - Log files
- `__pycache__/` - Python cache directories
- `.venv/` - Virtual environments
- `node_modules/` - Node.js dependencies
- `.DS_Store` - macOS system files

#### 3. Add Files to Git
If files are untracked, add them:
```bash
# Add specific files
git add filename.py

# Add all files in current directory
git add .

# Add all Python files
git add *.py
```

#### 4. Commit Changes
After adding files, commit them:
```bash
git commit -m "Add new features"
```

#### 5. Push to Remote
Push your changes to GitHub:
```bash
# Push to current branch
git push origin $(git rev-parse --abbrev-ref HEAD)

# Or use our helper script
./git-update.sh "Your commit message"
```

### Using the Updated git-update.sh Script

The `git-update.sh` script has been improved to:
- ✅ Work with any branch (not just main)
- ✅ Check for changes before committing
- ✅ Handle new branches gracefully
- ✅ Provide clear error messages
- ✅ Allow custom commit messages

Usage:
```bash
# With default commit message
./git-update.sh

# With custom commit message
./git-update.sh "Fix user authentication bug"
```

### VS Code Git Integration Tips

#### Enable Git in VS Code
1. Open VS Code
2. Go to File → Preferences → Settings
3. Search for "git.enabled"
4. Ensure it's checked ✅

#### Check Git Path
If VS Code can't find Git:
1. Open Terminal in VS Code (Ctrl+`)
2. Type `git --version`
3. If not found, install Git or check PATH

#### Common VS Code Git Issues

**Files showing as modified but no changes visible:**
- Check for line ending differences (CRLF vs LF)
- Run: `git config core.autocrlf true` (Windows) or `false` (Mac/Linux)

**Can't see Git options in VS Code:**
- Ensure you're in a Git repository
- Check that `.git` folder exists in your project root

**Permission denied when pushing:**
- Check your GitHub authentication
- Use VS Code's built-in GitHub authentication
- Or setup SSH keys

### Branch Management

#### Check Current Branch
```bash
git branch
```

#### Switch Branches
```bash
# Switch to existing branch
git checkout branch-name

# Create and switch to new branch
git checkout -b new-branch-name
```

#### List All Branches
```bash
# Local branches
git branch

# All branches (local and remote)
git branch -a
```

### Emergency Recovery

#### Undo Last Commit (but keep changes)
```bash
git reset --soft HEAD~1
```

#### Discard All Local Changes
```bash
git reset --hard HEAD
```

#### Restore Specific File
```bash
git checkout -- filename.py
```

### Getting Help

If you're still having issues:

1. **Check Git logs:**
   ```bash
   git log --oneline -5
   ```

2. **Check remote configuration:**
   ```bash
   git remote -v
   ```

3. **Test connectivity:**
   ```bash
   git ls-remote origin
   ```

4. **Enable verbose output:**
   ```bash
   git push -v origin branch-name
   ```

### Best Practices

1. **Commit often** - Small, frequent commits are better than large ones
2. **Use descriptive commit messages** - Help future you understand what changed
3. **Pull before pushing** - Avoid conflicts by staying up to date
4. **Check status before committing** - Know what you're committing
5. **Use .gitignore effectively** - Don't commit build artifacts or secrets

### Environment Files Security

⚠️ **Important:** Never commit sensitive files like:
- `.env` files with API keys
- `OPENAI_API_KEY.env`
- Database passwords
- Private keys

These are already in `.gitignore`, but double-check before committing!