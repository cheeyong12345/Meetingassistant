#!/bin/bash

# GitHub Upload Script for Meeting Assistant
# This script helps you upload your project to GitHub

echo "🚀 Meeting Assistant - GitHub Upload Helper"
echo "=========================================="
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository"
    echo "Run: git init"
    exit 1
fi

# Check if there are commits
if ! git log -1 > /dev/null 2>&1; then
    echo "❌ Error: No commits found"
    echo "Run: git commit -m 'Initial commit'"
    exit 1
fi

echo "📊 Repository Status:"
echo "-------------------"
git log -1 --oneline
echo ""
git status --short | head -10
echo ""

# Check if remote exists
if git remote get-url origin > /dev/null 2>&1; then
    REMOTE_URL=$(git remote get-url origin)
    echo "✅ Remote 'origin' already configured:"
    echo "   $REMOTE_URL"
    echo ""
    read -p "Push to this remote? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to GitHub..."
        git push -u origin main
        echo ""
        echo "✅ Upload complete!"
        echo "🌐 Check your repository at: $REMOTE_URL"
    fi
else
    echo "❌ No remote repository configured"
    echo ""
    echo "Please follow these steps:"
    echo ""
    echo "1. Create a new repository on GitHub:"
    echo "   https://github.com/new"
    echo ""
    echo "2. Then run:"
    echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo "   git push -u origin main"
    echo ""
    echo "Or use this command (replace YOUR_USERNAME and YOUR_REPO):"
    echo ""
    echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git && git push -u origin main"
fi

echo ""
echo "📚 For detailed instructions, see: GITHUB_SETUP.md"
