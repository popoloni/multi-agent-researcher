#!/bin/bash

# Multi-Agent Researcher - Development Environment Cleanup Script
# Removes virtual environments, IDE configurations, and other developer-specific files
# This is more aggressive than the regular cleanup.sh and should be used carefully

set -e  # Exit on any error

echo "🔧 Starting development environment cleanup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to safely remove files/directories with confirmation
safe_remove_with_confirm() {
    local path="$1"
    local description="$2"
    local force="$3"
    
    if [ -e "$path" ]; then
        if [ "$force" != "force" ]; then
            echo -e "${YELLOW}Found $description: $path${NC}"
            read -p "Remove $description? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${BLUE}ℹ Skipped $description${NC}"
                return
            fi
        fi
        
        echo -e "${YELLOW}Removing $description: $path${NC}"
        rm -rf "$path"
        echo -e "${GREEN}✓ Removed $description${NC}"
    else
        echo -e "${BLUE}ℹ $description not found: $path${NC}"
    fi
}

# Function to remove files by pattern with confirmation
remove_pattern_with_confirm() {
    local pattern="$1"
    local description="$2"
    local force="$3"
    
    echo -e "${YELLOW}Searching for $description...${NC}"
    found_files=$(find . -name "$pattern" -type f 2>/dev/null || true)
    
    if [ -n "$found_files" ]; then
        echo -e "${YELLOW}Found $description:${NC}"
        echo "$found_files"
        
        if [ "$force" != "force" ]; then
            read -p "Remove all $description? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo -e "${BLUE}ℹ Skipped $description${NC}"
                return
            fi
        fi
        
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

# Check for force flag
FORCE_MODE=""
if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
    FORCE_MODE="force"
    echo -e "${RED}⚠️ Running in FORCE mode - no confirmations will be asked${NC}"
    echo -e "${RED}⚠️ This will remove ALL development environment files${NC}"
    if [ "$FORCE_MODE" != "force" ]; then
        read -p "Are you sure you want to continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${BLUE}ℹ Cleanup cancelled${NC}"
            exit 0
        fi
    fi
fi

echo -e "${BLUE}🐍 Cleaning up Python virtual environments...${NC}"

# Python virtual environments
safe_remove_with_confirm "venv" "Python virtual environment (venv)" "$FORCE_MODE"
safe_remove_with_confirm "env" "Python virtual environment (env)" "$FORCE_MODE"
safe_remove_with_confirm ".venv" "Python virtual environment (.venv)" "$FORCE_MODE"
safe_remove_with_confirm ".env" "Python virtual environment (.env)" "$FORCE_MODE"
safe_remove_with_confirm "researcher-env" "Project virtual environment" "$FORCE_MODE"
safe_remove_with_confirm "virtualenv" "Python virtual environment (virtualenv)" "$FORCE_MODE"
safe_remove_with_confirm "pyenv" "Python environment (pyenv)" "$FORCE_MODE"

# Conda environments (local)
safe_remove_with_confirm "conda-env" "Conda environment" "$FORCE_MODE"
safe_remove_with_confirm ".conda" "Local Conda directory" "$FORCE_MODE"

echo -e "${BLUE}💻 Cleaning up IDE and editor configurations...${NC}"

# VS Code
safe_remove_with_confirm ".vscode" "VS Code workspace settings" "$FORCE_MODE"

# IntelliJ IDEA / PyCharm
safe_remove_with_confirm ".idea" "IntelliJ IDEA/PyCharm settings" "$FORCE_MODE"

# Sublime Text
safe_remove_with_confirm "*.sublime-workspace" "Sublime Text workspace" "$FORCE_MODE"
safe_remove_with_confirm "*.sublime-project" "Sublime Text project" "$FORCE_MODE"

# Atom
safe_remove_with_confirm ".atom" "Atom editor settings" "$FORCE_MODE"

# Vim/Neovim
remove_pattern_with_confirm "*.swp" "Vim swap files" "$FORCE_MODE"
remove_pattern_with_confirm "*.swo" "Vim swap files" "$FORCE_MODE"
remove_pattern_with_confirm ".*.swp" "Hidden Vim swap files" "$FORCE_MODE"
safe_remove_with_confirm ".vim" "Vim configuration" "$FORCE_MODE"
safe_remove_with_confirm ".nvim" "Neovim configuration" "$FORCE_MODE"

# Emacs
remove_pattern_with_confirm "*~" "Emacs backup files" "$FORCE_MODE"
remove_pattern_with_confirm "#*#" "Emacs auto-save files" "$FORCE_MODE"

echo -e "${BLUE}🔧 Cleaning up development tools...${NC}"

# Git hooks (local)
safe_remove_with_confirm ".git/hooks/pre-commit" "Local pre-commit hook" "$FORCE_MODE"
safe_remove_with_confirm ".git/hooks/post-commit" "Local post-commit hook" "$FORCE_MODE"
safe_remove_with_confirm ".git/hooks/pre-push" "Local pre-push hook" "$FORCE_MODE"

# Development databases
safe_remove_with_confirm "dev.db" "Development database" "$FORCE_MODE"
safe_remove_with_confirm "test.db" "Test database" "$FORCE_MODE"
safe_remove_with_confirm "local.db" "Local database" "$FORCE_MODE"

# Local configuration files
safe_remove_with_confirm "config.local.py" "Local Python config" "$FORCE_MODE"
safe_remove_with_confirm "settings.local.py" "Local Python settings" "$FORCE_MODE"
safe_remove_with_confirm "local_settings.py" "Local settings file" "$FORCE_MODE"

echo -e "${BLUE}📦 Cleaning up package manager artifacts...${NC}"

# Node.js
safe_remove_with_confirm "node_modules" "Node.js dependencies" "$FORCE_MODE"
safe_remove_with_confirm ".npm" "NPM cache" "$FORCE_MODE"
safe_remove_with_confirm ".yarn" "Yarn cache" "$FORCE_MODE"

# Python
safe_remove_with_confirm ".pip" "Pip cache" "$FORCE_MODE"
safe_remove_with_confirm ".cache/pip" "Pip cache directory" "$FORCE_MODE"

echo -e "${BLUE}🗄️ Cleaning up local data and caches...${NC}"

# Application data
safe_remove_with_confirm "data" "Local data directory" "$FORCE_MODE"
safe_remove_with_confirm "uploads" "Uploads directory" "$FORCE_MODE"
safe_remove_with_confirm "downloads" "Downloads directory" "$FORCE_MODE"
safe_remove_with_confirm "cache" "Cache directory" "$FORCE_MODE"

# Browser testing artifacts
safe_remove_with_confirm ".browser_screenshots" "Browser screenshots" "$FORCE_MODE"
safe_remove_with_confirm "selenium-screenshots" "Selenium screenshots" "$FORCE_MODE"

echo -e "${BLUE}🔐 Cleaning up security and credential files...${NC}"

# SSH keys (be very careful with these)
if [ "$FORCE_MODE" != "force" ]; then
    echo -e "${RED}⚠️ Found potential SSH key files - please review manually:${NC}"
    find . -name "id_rsa*" -o -name "id_ed25519*" -o -name "*.pem" -o -name "*.key" 2>/dev/null || true
fi

# API keys and secrets (local)
remove_pattern_with_confirm "*.secret" "Secret files" "$FORCE_MODE"
remove_pattern_with_confirm "*.credentials" "Credential files" "$FORCE_MODE"

echo -e "${BLUE}🧪 Cleaning up test and development artifacts...${NC}"

# Test artifacts
safe_remove_with_confirm "test_output" "Test output directory" "$FORCE_MODE"
safe_remove_with_confirm "test_reports" "Test reports directory" "$FORCE_MODE"
safe_remove_with_confirm ".pytest_cache" "Pytest cache" "$FORCE_MODE"
safe_remove_with_confirm ".coverage" "Coverage data" "$FORCE_MODE"
safe_remove_with_confirm "htmlcov" "HTML coverage reports" "$FORCE_MODE"

# Development logs
remove_pattern_with_confirm "dev_*.log" "Development log files" "$FORCE_MODE"
remove_pattern_with_confirm "debug_*.log" "Debug log files" "$FORCE_MODE"

echo -e "${BLUE}📊 Checking for remaining large files...${NC}"
large_files=$(find . -type f -size +50M 2>/dev/null | grep -v ".git" || true)
if [ -n "$large_files" ]; then
    echo -e "${YELLOW}⚠️ Found large files (>50MB):${NC}"
    echo "$large_files"
    echo -e "${YELLOW}Consider reviewing these files manually${NC}"
else
    echo -e "${GREEN}✓ No large files found${NC}"
fi

# Summary
echo ""
echo -e "${GREEN}🎉 Development environment cleanup completed!${NC}"
echo ""
echo -e "${BLUE}📋 Summary of cleanup actions:${NC}"
echo "• Removed Python virtual environments"
echo "• Cleaned IDE and editor configurations"
echo "• Removed development tool artifacts"
echo "• Cleaned package manager caches"
echo "• Removed local data and cache directories"
echo "• Cleaned test and development artifacts"
echo ""
echo -e "${YELLOW}💡 Tip: You may need to recreate your virtual environment${NC}"
echo -e "${YELLOW}💡 Tip: Reconfigure your IDE settings as needed${NC}"
echo -e "${RED}⚠️ Warning: This cleanup removes development-specific configurations${NC}"

# Show how to recreate virtual environment
echo ""
echo -e "${BLUE}🔄 To recreate your Python virtual environment:${NC}"
echo "python -m venv researcher-env"
echo "source researcher-env/bin/activate  # On Windows: researcher-env\\Scripts\\activate"
echo "pip install -r requirements.txt"

echo ""
echo -e "${GREEN}✨ Development environment is now clean!${NC}"