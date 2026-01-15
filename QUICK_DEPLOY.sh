#!/bin/bash
# Quick deployment script for JavaScript library

set -e

echo "=========================================="
echo "JavaScript Library Deployment"
echo "=========================================="
echo ""

JS_DIR="geo_intel_offline_java_script"
REPO_NAME="geo-intel-offline-javascript"
GITHUB_USER="RRJena"

cd "$JS_DIR"

echo "Step 1: Building package..."
npm run build

echo ""
echo "Step 2: Checking git status..."
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

if ! git remote get-url origin >/dev/null 2>&1; then
    echo "Adding GitHub remote..."
    git remote add origin "https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
fi

echo ""
echo "Step 3: Staging files..."
git add .

if ! git diff --staged --quiet; then
    echo "Committing changes..."
    git commit -m "Initial commit: JavaScript/TypeScript version v1.0.3

- 100% accuracy across 258 countries
- Full TypeScript support
- Works in Node.js and browsers
- Comprehensive test coverage"
fi

echo ""
echo "=========================================="
echo "Ready to deploy!"
echo "=========================================="
echo ""
echo "1. Push to GitHub:"
echo "   git push -u origin main"
echo ""
echo "2. Create release on GitHub:"
echo "   https://github.com/${GITHUB_USER}/${REPO_NAME}/releases/new"
echo ""
echo "3. Publish to npm:"
echo "   npm login"
echo "   npm publish"
echo ""

read -p "Push to GitHub now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push -u origin main
    echo "✅ Pushed to GitHub!"
fi

