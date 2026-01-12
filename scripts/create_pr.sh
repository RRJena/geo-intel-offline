#!/bin/bash
#
# Script to create a Pull Request
# Usage: bash scripts/create_pr.sh [branch-name] [repo-url]
#

set -e

BRANCH_NAME=${1:-"feature/initial-release"}
REPO_URL=${2:-""}

echo "=" 
echo "GITHUB PULL REQUEST CREATION"
echo "="
echo ""

# Check if remote exists
if ! git remote get-url origin >/dev/null 2>&1; then
    if [ -z "$REPO_URL" ]; then
        echo "⚠ No remote 'origin' configured."
        echo ""
        echo "Please provide your GitHub repository URL:"
        read -p "Repository URL (e.g., https://github.com/username/geo-intel-offline.git): " REPO_URL
    fi
    
    if [ -z "$REPO_URL" ]; then
        echo "✗ Repository URL required. Exiting."
        exit 1
    fi
    
    echo "Adding remote origin..."
    git remote add origin "$REPO_URL"
    echo "✓ Remote added"
    echo ""
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "master")

# Check if we have commits
if ! git rev-parse HEAD >/dev/null 2>&1; then
    echo "No commits found. Creating initial commit..."
    
    # Stage all files
    git add .
    
    # Create initial commit
    git commit -m "Initial commit: Production-ready offline geo-intelligence library

- 99.92% accuracy across 258 countries
- < 1ms lookup time, < 15MB memory
- Automatic data compression (66% size reduction)
- Comprehensive documentation and examples
- Full test coverage (258 countries, 2513 test points)
- Complete GitHub setup (CI/CD, PR templates, issue templates)"
    
    echo "✓ Initial commit created"
    echo ""
    
    # Push to main/master first
    echo "Pushing initial commit to $CURRENT_BRANCH..."
    git push -u origin "$CURRENT_BRANCH" || {
        echo "⚠ Push failed. You may need to:"
        echo "  1. Create repository on GitHub first: https://github.com/new"
        echo "  2. Or check your git credentials"
        exit 1
    }
    echo "✓ Pushed to $CURRENT_BRANCH"
    echo ""
fi

# Create feature branch if not already on it
if [ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]; then
    echo "Creating feature branch: $BRANCH_NAME"
    git checkout -b "$BRANCH_NAME"
    echo "✓ Switched to $BRANCH_NAME"
    echo ""
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "Staging and committing changes..."
    git add .
    
    git commit -m "feat: Production-ready geo-intelligence library

Features:
- Offline country resolution (lat/lon → country, ISO, continent, timezone)
- 99.92% accuracy across 258 countries
- < 1ms lookup time, < 15MB memory footprint
- Automatic data compression (66% reduction)
- Comprehensive documentation with examples
- Full test coverage

Documentation:
- Complete README with storytelling and use cases
- Architecture documentation
- Test results report
- Contributing guidelines

Infrastructure:
- GitHub Actions CI/CD
- PR and issue templates
- Package ready for PyPI/uv distribution"
    
    echo "✓ Changes committed"
    echo ""
fi

# Push branch
echo "Pushing branch $BRANCH_NAME to remote..."
git push -u origin "$BRANCH_NAME" || {
    echo "✗ Push failed. Check your credentials and repository URL."
    exit 1
}
echo "✓ Pushed to remote"
echo ""

# Get repository URL
REMOTE_URL=$(git remote get-url origin)
if [[ $REMOTE_URL == git@* ]]; then
    # SSH format: git@github.com:user/repo.git
    REPO_PATH=$(echo "$REMOTE_URL" | sed 's/.*github\.com[:/]\(.*\)\.git/\1/')
    GITHUB_URL="https://github.com/$REPO_PATH"
elif [[ $REMOTE_URL == https://* ]]; then
    # HTTPS format: https://github.com/user/repo.git
    GITHUB_URL=$(echo "$REMOTE_URL" | sed 's/\.git$//')
else
    GITHUB_URL="$REMOTE_URL"
fi

echo "=" 
echo "PULL REQUEST READY"
echo "="
echo ""
echo "Branch '$BRANCH_NAME' has been pushed to GitHub."
echo ""
echo "Next steps:"
echo ""
echo "1. Go to: $GITHUB_URL/compare/$BRANCH_NAME"
echo ""
echo "2. Or manually:"
echo "   - Visit: $GITHUB_URL"
echo "   - Click 'Compare & pull request'"
echo "   - Fill in PR description (template will auto-populate)"
echo "   - Submit PR"
echo ""
echo "PR Template will include:"
echo "  - Description of changes"
echo "  - Type of change checklist"
echo "  - Testing checklist"
echo ""
echo "=" 
echo ""
