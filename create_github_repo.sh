#!/bin/bash

# Script to create GitHub repository and push code
# Run this after manually creating the repository on GitHub

echo "🚀 Setting up GitHub repository for Multi-Agent Research System"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run this from the project root."
    exit 1
fi

# Get the repository URL from user
echo "📝 Please create a new repository on GitHub named 'multi-agent-researcher'"
echo "🌐 Go to: https://github.com/new"
echo ""
echo "Repository settings:"
echo "  - Name: multi-agent-researcher"
echo "  - Description: A comprehensive implementation of Anthropic's Multi-Agent Research System that outperforms single-agent workflows by 90%"
echo "  - Public repository"
echo "  - Do NOT initialize with README, .gitignore, or license (we already have these)"
echo ""

read -p "Enter your GitHub username: " username
repo_url="https://github.com/${username}/multi-agent-researcher.git"

echo "📡 Setting up remote origin..."
git remote add origin $repo_url

echo "🔄 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🌐 Repository URL: https://github.com/${username}/multi-agent-researcher"
    echo "📚 Documentation: https://github.com/${username}/multi-agent-researcher#readme"
    echo ""
    echo "Next steps:"
    echo "1. Visit your repository on GitHub"
    echo "2. Add topics/tags for discoverability"
    echo "3. Enable GitHub Pages for documentation (optional)"
    echo "4. Set up GitHub Actions for CI/CD (optional)"
else
    echo "❌ Failed to push to GitHub. Please check:"
    echo "1. Repository exists and is accessible"
    echo "2. You have push permissions"
    echo "3. GitHub token/credentials are set up correctly"
    echo ""
    echo "Manual push command:"
    echo "git remote add origin $repo_url"
    echo "git push -u origin main"
fi