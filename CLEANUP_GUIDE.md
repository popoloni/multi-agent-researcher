# Cleanup Script Guide

## 🧹 Overview

The `cleanup.sh` script removes temporary files, build artifacts, screenshots, logs, and other runtime-generated files that should not be committed to GitHub.

## 🚀 Usage

### Basic Usage
```bash
# Make the script executable (first time only)
chmod +x cleanup.sh

# Run the cleanup
./cleanup.sh
```

### When to Use
- **Before committing**: Ensure no temporary files are accidentally committed
- **After development sessions**: Clean up generated files and logs
- **Before creating releases**: Ensure a clean repository state
- **When repository size grows**: Remove unnecessary build artifacts

## 🗂️ What Gets Cleaned

### Build Artifacts
- `frontend/node_modules/` - Node.js dependencies
- `frontend/build/` - React build output
- `frontend/dist/` - Frontend distribution files
- `__pycache__/` - Python cache directories
- `*.egg-info/` - Python package info
- `.pytest_cache/` - Pytest cache

### Log Files
- `*.log` - All log files
- `server.log` - Backend server logs
- `frontend.log` - Frontend logs
- `ollama.log` - Ollama service logs

### Temporary Files
- `tmp/`, `temp/` - Temporary directories
- `*.tmp`, `*.temp` - Temporary files
- `*~` - Backup files
- `.DS_Store` - macOS system files
- `Thumbs.db` - Windows thumbnail cache

### Screenshots and Media
- `screenshot*.png` - Screenshot files
- `screen_*.png` - Screen capture files
- `capture_*.png` - Capture files
- `screenshots/` - Screenshots directory

### Development Files
- `.coverage` - Coverage data
- `htmlcov/` - Coverage HTML reports
- `.eslintcache` - ESLint cache
- `.vscode/settings.json` - VS Code local settings
- `*.swp`, `*.swo` - Vim swap files

### Database Files
- `*.db`, `*.sqlite`, `*.sqlite3` - SQLite databases

### Environment Files
- `.env.local` - Local environment files
- `.env.development.local` - Local development config
- `config.local.json` - Local configuration

## 🛡️ Safety Features

### Safe Removal
- Checks if files/directories exist before attempting removal
- Uses `rm -rf` safely with existence checks
- Provides colored output for clear feedback
- Shows what was found and what was removed

### Large File Detection
- Scans for files larger than 10MB
- Warns about large files that might need attention
- Suggests adding them to `.gitignore` if appropriate

## 📊 Output Explanation

### Color Coding
- 🟡 **Yellow**: Action being taken (removing files)
- 🟢 **Green**: Successful completion
- 🔵 **Blue**: Information (file not found, section headers)
- 🔴 **Red**: Errors (if any)

### Example Output
```
🧹 Starting cleanup of temporary and build files...
📁 Cleaning up build artifacts and dependencies...
Removing Node.js dependencies: frontend/node_modules
✓ Removed Node.js dependencies
ℹ Frontend distribution files not found: frontend/dist
```

## 🔧 Customization

### Adding Custom Patterns
Edit the script to add your own cleanup patterns:

```bash
# Add custom file patterns
remove_pattern "*.custom" "custom files"

# Add custom directories
safe_remove "custom_dir" "custom directory"
```

### Excluding Certain Files
Comment out or modify sections you don't want to clean:

```bash
# Comment out to keep log files
# remove_pattern "*.log" "log files"
```

## 📋 Integration with Git

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
./cleanup.sh
```

### Git Alias
Add to your git config:
```bash
git config alias.cleanup '!./cleanup.sh'
# Then use: git cleanup
```

## 🚨 Important Notes

### What's NOT Removed
- Source code files
- Configuration files (except local overrides)
- Documentation files
- Git history and configuration
- Package.json and requirements.txt
- .gitignore and other important dot files

### Backup Recommendation
The script is designed to be safe, but if you're unsure:
```bash
# Create a backup before running
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz .
./cleanup.sh
```

### Repository Size
The script shows repository size after cleanup to help track improvements.

## 🔄 Automation

### Regular Cleanup
Add to your development workflow:
```bash
# In your package.json scripts
"scripts": {
  "clean": "./cleanup.sh",
  "precommit": "./cleanup.sh && git add ."
}
```

### CI/CD Integration
Use in GitHub Actions or other CI systems:
```yaml
- name: Clean repository
  run: ./cleanup.sh
```

## 🆘 Troubleshooting

### Permission Denied
```bash
chmod +x cleanup.sh
```

### Script Not Found
Ensure you're in the repository root directory:
```bash
cd /path/to/multi-agent-researcher
./cleanup.sh
```

### Files Keep Coming Back
Add patterns to `.gitignore` to prevent regeneration:
```bash
# Add to .gitignore
*.log
node_modules/
__pycache__/
```

## 📈 Benefits

- **Smaller Repository**: Reduces repository size significantly
- **Faster Operations**: Git operations are faster with fewer files
- **Clean Commits**: Prevents accidental commits of temporary files
- **Better Collaboration**: Team members don't see irrelevant files
- **Security**: Removes potential sensitive data in logs/temp files

---

*Run `./cleanup.sh` regularly to maintain a clean and efficient repository!*