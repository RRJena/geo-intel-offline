#!/bin/bash
# Helper script to create GitHub repo and push JS library

set -e

REPO_NAME="geo-intel-offline-javascript"
GITHUB_USER="RRJena"
JS_DIR="$(cd "$(dirname "$0")/../geo_intel_offline_java_script" && pwd)"

echo "=========================================="
echo "Setting up GitHub repository for JS library"
echo "=========================================="
echo ""

cd "$JS_DIR"

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "GitHub CLI found. Creating repository..."
    gh repo create "$REPO_NAME" --public --description "Production-ready, offline geo-intelligence library for JavaScript/TypeScript - 100% accuracy across 258 countries" --source=. --remote=origin --push
    echo ""
    echo "✅ Repository created and code pushed!"
else
    echo "GitHub CLI not found. Please create the repository manually:"
    echo ""
    echo "1. Go to: https://github.com/new"
    echo "2. Repository name: $REPO_NAME"
    echo "3. Description: Production-ready, offline geo-intelligence library for JavaScript/TypeScript"
    echo "4. Make it public"
    echo "5. Don't initialize with README (we already have one)"
    echo ""
    echo "Then run the setup script in the JS directory:"
    echo "  cd $JS_DIR"
    echo "  bash setup_github_repo.sh"
fi
