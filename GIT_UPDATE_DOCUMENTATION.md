# Enhanced Git Update Script Documentation

## Overview

The `git-update.sh` script has been significantly enhanced with safety checks, error handling, and improved functionality for the AI Nurse Florence project.

## Features

### Safety & Error Handling
- **Repository validation**: Ensures script is run in a git repository
- **Backup creation**: Automatically creates backup branches before making changes
- **Error recovery**: Provides clear rollback instructions if operations fail
- **Pre-commit checks**: Validates changes before committing
- **Conflict resolution guidance**: Helps users resolve merge conflicts

### Enhanced Functionality
- **Intelligent commit messages**: Generates descriptive commit messages based on changes
- **Branch awareness**: Works with any branch, not just main
- **Colored output**: Uses colors for better visibility of status messages
- **Verbose mode**: Optional detailed output for debugging
- **Help system**: Comprehensive help and usage examples

### Smart Updates
- **Change detection**: Only commits when there are actual changes
- **Remote synchronization**: Checks for and pulls remote updates
- **Safe rebasing**: Handles rebase operations with proper error handling
- **Push validation**: Pushes to the correct branch based on context

## Usage

### Basic Usage
```bash
# Update current branch with remote changes
./git-update.sh

# Update specific branch
./git-update.sh develop

# Run with verbose output
./git-update.sh -v main
```

### Command Line Options
- `-h, --help`: Show help message
- `-v, --verbose`: Enable verbose output with debug information

### Arguments
- `BRANCH`: Target branch name (default: main)

## Examples

### Standard workflow
```bash
# Make some changes to your files
echo "new feature" >> README.md

# Run the enhanced git update
./git-update.sh
```

The script will:
1. Create a backup branch
2. Generate an intelligent commit message
3. Commit your changes
4. Fetch and rebase with remote
5. Push to the appropriate branch

### Working with feature branches
```bash
# When on a feature branch
git checkout feature/new-feature

# The script will commit and push to your current branch
./git-update.sh
```

### Recovery from failures
If the script fails, it provides clear instructions:
```bash
[ERROR] Rebase failed - you may need to resolve conflicts manually
[WARNING] You can restore from backup branch: backup-20240930-123456-feature/branch
[INFO] To resolve conflicts:
  1. Fix conflicts in the files
  2. Run: git add <conflicted-files>
  3. Run: git rebase --continue
  4. Run: git push origin feature/branch
```

## Testing

The script includes a comprehensive test suite (`test_git_update.sh`) that validates:

- Script permissions and syntax
- Git repository detection
- Help functionality
- Error handling in non-git directories
- Safety check functions
- Enhanced features

Run tests with:
```bash
./test_git_update.sh
```

## Improvements Over Original

### Original Script Issues
The original script had several problems:
- No error handling
- No safety checks
- Hard-coded branch names
- Generic commit messages
- No backup mechanism
- Could fail silently

### Enhanced Script Benefits
- ✅ Comprehensive error handling with colored output
- ✅ Automatic backup branch creation
- ✅ Intelligent commit message generation
- ✅ Branch-aware operations
- ✅ Safe rebase with conflict guidance
- ✅ Verbose mode for debugging
- ✅ Complete test coverage
- ✅ Recovery instructions for failures

## Safety Features

### Backup Protection
Every run creates a backup branch with timestamp:
```
backup-20240930-123456-feature/branch-name
```

### Pre-operation Checks
- Validates git repository
- Checks for uncommitted changes
- Verifies remote connectivity
- Ensures clean working directory state

### Error Recovery
- Clear error messages with color coding
- Rollback instructions
- Backup branch references
- Step-by-step conflict resolution

## Integration with AI Nurse Florence

This enhanced script follows the project's coding standards:
- **Error handling patterns**: Consistent with utils/exceptions.py
- **Logging standards**: Structured output with appropriate levels
- **Safety-first approach**: Aligns with medical software safety requirements
- **Documentation**: Comprehensive inline and external documentation

## Best Practices

### When to Use
- After making changes to multiple files
- Before major deployments
- When syncing with remote changes
- As part of daily development workflow

### When NOT to Use
- During active merge conflicts
- In detached HEAD state
- When working with sensitive production branches (use manual commands)

### Recommended Workflow
1. Make your changes
2. Test locally
3. Run `./git-update.sh -v` for first-time usage
4. Use `./git-update.sh` for regular updates
5. Keep backup branches until changes are verified

## Troubleshooting

### Common Issues
1. **Permission denied**: Run `chmod +x git-update.sh`
2. **Not a git repository**: Ensure you're in the project root
3. **Rebase conflicts**: Follow the on-screen instructions
4. **Push failures**: Check remote permissions and branch existence

### Getting Help
```bash
./git-update.sh --help
./test_git_update.sh  # Run tests to verify setup
```

This enhanced script provides a robust, safe, and user-friendly way to manage git updates in the AI Nurse Florence project while maintaining the highest standards for healthcare software development.