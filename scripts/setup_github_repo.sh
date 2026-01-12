#!/bin/bash
#
# Setup script for creating GitHub repository and initial push
# Usage: bash scripts/setup_github_repo.sh
#

set -e

echo "="
echo "GitHub Repository Setup"
echo "="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "Initializing git repository..."
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already initialized"
fi

echo ""

# Check current git status
echo "Current git status:"
git status --short | head -10 || echo "  (no changes to show)"
echo ""

# Check if remote exists
if git remote get-url origin 2>/dev/null; then
    echo "⚠ Remote 'origin' already exists:"
    git remote get-url origin
    echo ""
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter GitHub repository URL (e.g., https://github.com/username/geo-intel-offline.git): " REPO_URL
        git remote set-url origin "$REPO_URL"
        echo "✓ Remote updated"
    fi
else
    echo "No remote 'origin' found."
    read -p "Enter GitHub repository URL (e.g., https://github.com/username/geo-intel-offline.git): " REPO_URL
    git remote add origin "$REPO_URL"
    echo "✓ Remote added"
fi

echo ""
echo "="
echo "Setup Complete"
echo "="
echo ""
echo "Next steps:"
echo ""
echo "1. Stage all files:"
echo "   git add ."
echo ""
echo "2. Make initial commit:"
echo "   git commit -m 'Initial commit: Production-ready offline geo-intelligence library'"
echo ""
echo "3. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "4. Create a Pull Request on GitHub (if working from a branch)"
echo ""
echo "Note: Make sure your GitHub repository is created first at:"
echo "  https://github.com/new"
echo ""
