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
- `frontend/.next/`, `.next/`, `frontend/out/` - Next.js build and static export
- `dist/`, `build/` - Python and general build directories
- `*.egg-info/` - Python package info
- `__pycache__/` - Python cache directories
- `.pytest_cache/` - Pytest cache
- `.coverage`, `htmlcov/` - Coverage data and reports

### Log Files
- `*.log` - All log files
- `server.log`, `frontend.log`, `server_ui.log`, `ollama.log` - Service logs
- `logs/` - Logs directory
- `yarn-error.log` - Yarn error log

### Temporary Files
- `tmp/`, `temp/`, `/tmp/kenobi_repos` - Temporary directories
- `*.tmp`, `*.temp` - Temporary files
- `*~` - Backup files
- `.DS_Store` - macOS system files
- `Thumbs.db` - Windows thumbnail cache
- `.cache/`, `.parcel-cache/` - General and Parcel cache
- `.eslintcache` - ESLint cache

### Screenshots and Media
- `screenshot*.png`, `screen_*.png`, `capture_*.png`, `demo_*.png`, `test_*.png` - Screenshot and capture files
- `screenshots/`, `captures/` - Screenshot and capture directories
- `static/uploads/`, `media/temp/`, `downloads/` - Uploaded, temp, and download directories

### Development Files
- `.vscode/settings.json` - VS Code local settings
- `.idea/` - IntelliJ IDEA files
- `*.swp`, `*.swo`, `.*.swp` - Vim swap files
- `.nyc_output/` - NYC coverage output
- `junit.xml` - JUnit test results
- `test-results/`, `coverage/` - Test results and coverage directories

### Database Files
- `*.db`, `*.sqlite`, `*.sqlite3` - SQLite databases

### Environment Files
- `.env.local`, `.env.development.local`, `.env.production.local` - Local environment files
- `config.local.json` - Local configuration

### Package Manager Files
- `package-lock.json.bak` - npm lock backup
- `.yarn/` - Yarn cache
- `node_modules.tar.gz` - Compressed node modules

### Docker and Git Artifacts
- `docker-compose.override.yml` - Docker compose override
- `.dockerignore.bak` - Docker ignore backup
- `.git/gc.log` - Git garbage collection log
- `.git/hooks/pre-commit.sample` - Git hook samples

### OS-Specific and Backup Files
- `.DS_Store`, `desktop.ini`, `*.lnk` - OS-specific files
- `*.bak`, `*.backup`, `*.orig` - Backup files

### Compressed and Archive Files
- `temp_*.zip`, `temp_*.tar.gz`, `backup_*.zip` - Temporary and backup archives

### Dev Server and Monitoring Files
- `.nuxt/`, `.vuepress/` - Nuxt.js and VuePress caches
- `*.prof`, `*.trace`, `*.heap` - Profiling, trace, and heap dump files

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
- **Cleaner Commits**: Prevents accidental commits of temp files
- **Faster CI/CD**: Less clutter for automated pipelines
- **Easier Collaboration**: Consistent clean state for all contributors

---

*Run `./cleanup.sh` regularly to maintain a clean and efficient repository!*