#!/bin/bash

# Multi-Agent Researcher - Cleanup Script
# Removes temporary files, build artifacts, screenshots, logs, and other runtime files
# that should not be committed to GitHub

set -e  # Exit on any error

echo "🧹 Starting cleanup of temporary and build files..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to safely remove files/directories
safe_remove() {
    local path="$1"
    local description="$2"
    
    if [ -e "$path" ]; then
        echo -e "${YELLOW}Removing $description: $path${NC}"
        rm -rf "$path"
        echo -e "${GREEN}✓ Removed $description${NC}"
    else
        echo -e "${BLUE}ℹ $description not found: $path${NC}"
    fi
}

# Function to remove files by pattern
remove_pattern() {
    local pattern="$1"
    local description="$2"
    
    echo -e "${YELLOW}Searching for $description...${NC}"
    found_files=$(find . -name "$pattern" -type f 2>/dev/null || true)
    
    if [ -n "$found_files" ]; then
        echo "$found_files" | while read -r file; do
            if [ -f "$file" ]; then
                echo -e "${YELLOW}Removing: $file${NC}"
                rm -f "$file"
            fi
        done
        echo -e "${GREEN}✓ Removed $description${NC}"
    else
        echo -e "${BLUE}ℹ No $description found${NC}"
    fi
}

# Function to remove directories by pattern
remove_dir_pattern() {
    local pattern="$1"
    local description="$2"
    
    echo -e "${YELLOW}Searching for $description directories...${NC}"
    found_dirs=$(find . -name "$pattern" -type d 2>/dev/null || true)
    
    if [ -n "$found_dirs" ]; then
        echo "$found_dirs" | while read -r dir; do
            if [ -d "$dir" ]; then
                echo -e "${YELLOW}Removing directory: $dir${NC}"
                rm -rf "$dir"
            fi
        done
        echo -e "${GREEN}✓ Removed $description directories${NC}"
    else
        echo -e "${BLUE}ℹ No $description directories found${NC}"
    fi
}

echo -e "${BLUE}📁 Cleaning up build artifacts and dependencies...${NC}"

# Node.js build artifacts and dependencies
safe_remove "frontend/node_modules" "Node.js dependencies"
safe_remove "frontend/build" "React build output"
safe_remove "frontend/dist" "Frontend distribution files"
safe_remove "frontend/.next" "Next.js build cache"
safe_remove "frontend/out" "Next.js static export"

# Python build artifacts and caches
echo -e "${BLUE}🐍 Cleaning up Python artifacts...${NC}"
safe_remove "__pycache__" "Python cache directory"
remove_dir_pattern "__pycache__" "Python cache"
remove_dir_pattern "*.egg-info" "Python egg info"
safe_remove ".pytest_cache" "Pytest cache"
safe_remove ".coverage" "Coverage data"
safe_remove "htmlcov" "Coverage HTML reports"
safe_remove "dist" "Python distribution files"
safe_remove "build" "Python build directory"

# Log files
echo -e "${BLUE}📝 Cleaning up log files...${NC}"
remove_pattern "*.log" "log files"
safe_remove "server.log" "server log file"
safe_remove "frontend.log" "frontend log file"
safe_remove "server_ui.log" "server UI log file"
safe_remove "ollama.log" "Ollama log file"
safe_remove "logs" "logs directory"

# Temporary files and directories
echo -e "${BLUE}🗂️ Cleaning up temporary files...${NC}"
safe_remove "tmp" "temporary directory"
safe_remove "temp" "temp directory"
safe_remove "/tmp/kenobi_repos" "Kenobi temporary repositories"
remove_pattern "*.tmp" "temporary files"
remove_pattern "*.temp" "temp files"
remove_pattern "*~" "backup files"
remove_pattern ".DS_Store" "macOS system files"
remove_pattern "Thumbs.db" "Windows thumbnail cache"

# Screenshots and media files
echo -e "${BLUE}📸 Cleaning up screenshots and media...${NC}"
remove_pattern "screenshot*.png" "screenshot files"
remove_pattern "screen_*.png" "screen capture files"
remove_pattern "capture_*.png" "capture files"
remove_pattern "demo_*.png" "demo screenshot files"
remove_pattern "test_*.png" "test screenshot files"
safe_remove "screenshots" "screenshots directory"
safe_remove "captures" "captures directory"

# Database files (if using SQLite for development)
echo -e "${BLUE}🗄️ Cleaning up database files...${NC}"
remove_pattern "*.db" "SQLite database files"
remove_pattern "*.sqlite" "SQLite files"
remove_pattern "*.sqlite3" "SQLite3 files"

# IDE and editor files
echo -e "${BLUE}💻 Cleaning up IDE and editor files...${NC}"
safe_remove ".vscode/settings.json" "VS Code local settings"
safe_remove ".idea" "IntelliJ IDEA files"
remove_pattern "*.swp" "Vim swap files"
remove_pattern "*.swo" "Vim swap files"
remove_pattern ".*.swp" "hidden Vim swap files"

# Environment and configuration files that might contain secrets
echo -e "${BLUE}🔐 Cleaning up environment files...${NC}"
safe_remove ".env.local" "local environment file"
safe_remove ".env.development.local" "local development environment"
safe_remove ".env.production.local" "local production environment"
safe_remove "config.local.json" "local configuration"

# Package manager files
echo -e "${BLUE}📦 Cleaning up package manager artifacts...${NC}"
safe_remove "package-lock.json.bak" "npm lock backup"
safe_remove "yarn-error.log" "Yarn error log"
safe_remove ".yarn" "Yarn cache"
safe_remove "node_modules.tar.gz" "compressed node modules"

# Test artifacts
echo -e "${BLUE}🧪 Cleaning up test artifacts...${NC}"
safe_remove "test-results" "test results directory"
safe_remove "coverage" "coverage directory"
safe_remove ".nyc_output" "NYC coverage output"
safe_remove "junit.xml" "JUnit test results"

# Docker artifacts (if any)
echo -e "${BLUE}🐳 Cleaning up Docker artifacts...${NC}"
remove_pattern "docker-compose.override.yml" "Docker compose override"
safe_remove ".dockerignore.bak" "Docker ignore backup"

# Git artifacts that shouldn't be committed
echo -e "${BLUE}📋 Cleaning up Git artifacts...${NC}"
safe_remove ".git/gc.log" "Git garbage collection log"
safe_remove ".git/hooks/pre-commit.sample" "Git hook samples"

# Cache directories
echo -e "${BLUE}💾 Cleaning up cache directories...${NC}"
safe_remove ".cache" "general cache directory"
safe_remove ".parcel-cache" "Parcel cache"
safe_remove ".eslintcache" "ESLint cache"

# OS-specific files
echo -e "${BLUE}🖥️ Cleaning up OS-specific files...${NC}"
remove_pattern ".DS_Store" "macOS Finder files"
remove_pattern "desktop.ini" "Windows desktop files"
remove_pattern "*.lnk" "Windows shortcut files"

# Backup files
echo -e "${BLUE}💾 Cleaning up backup files...${NC}"
remove_pattern "*.bak" "backup files"
remove_pattern "*.backup" "backup files"
remove_pattern "*.orig" "original files"

# Compressed files that might be temporary
echo -e "${BLUE}🗜️ Cleaning up temporary archives...${NC}"
remove_pattern "temp_*.zip" "temporary zip files"
remove_pattern "temp_*.tar.gz" "temporary tar files"
remove_pattern "backup_*.zip" "backup zip files"

# Development server files
echo -e "${BLUE}🌐 Cleaning up development server files...${NC}"
safe_remove ".next" "Next.js cache"
safe_remove ".nuxt" "Nuxt.js cache"
safe_remove ".vuepress" "VuePress cache"

# Monitoring and profiling files
echo -e "${BLUE}📊 Cleaning up monitoring files...${NC}"
remove_pattern "*.prof" "profiling files"
remove_pattern "*.trace" "trace files"
remove_pattern "*.heap" "heap dump files"

# Custom application temporary files
echo -e "${BLUE}🔧 Cleaning up application-specific files...${NC}"
safe_remove "static/uploads" "uploaded files directory"
safe_remove "media/temp" "temporary media files"
safe_remove "downloads" "downloads directory"

# Check for large files that might be accidentally included
echo -e "${BLUE}📏 Checking for large files...${NC}"
large_files=$(find . -type f -size +10M 2>/dev/null | grep -v ".git" | grep -v "node_modules" || true)
if [ -n "$large_files" ]; then
    echo -e "${YELLOW}⚠️ Found large files (>10MB):${NC}"
    echo "$large_files"
    echo -e "${YELLOW}Consider adding these to .gitignore if they shouldn't be committed${NC}"
else
    echo -e "${GREEN}✓ No large files found${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}🎉 Cleanup completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Summary of cleanup actions:${NC}"
echo "• Removed Node.js dependencies and build artifacts"
echo "• Cleaned Python cache and build files"
echo "• Removed log files and temporary directories"
echo "• Deleted screenshots and media files"
echo "• Cleaned IDE and editor temporary files"
echo "• Removed test artifacts and coverage reports"
echo "• Cleaned OS-specific and backup files"
echo ""
echo -e "${YELLOW}💡 Tip: Run this script before committing to ensure a clean repository${NC}"
echo -e "${YELLOW}💡 Consider adding frequently generated files to .gitignore${NC}"

# Optional: Show current repository size
if command -v du >/dev/null 2>&1; then
    echo ""
    echo -e "${BLUE}📊 Current repository size:${NC}"
    du -sh . 2>/dev/null || echo "Could not calculate size"
fi

echo ""
echo -e "${GREEN}✨ Repository is now clean and ready for commit!${NC}"