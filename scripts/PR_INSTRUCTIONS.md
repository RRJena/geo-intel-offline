# Creating a Pull Request - Step by Step Guide

## Option 1: Using the Automated Script (Recommended)

### Step 1: Create GitHub Repository

If you haven't created the repository yet:

1. Go to https://github.com/new
2. Repository name: `geo-intel-offline`
3. Description: `Production-ready, offline geo-intelligence library for resolving lat/lon to country, ISO codes, continent, and timezone`
4. Visibility: Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Run the PR Script

```bash
# Run the script (it will prompt for repo URL if needed)
bash scripts/create_pr.sh

# Or provide repository URL directly:
bash scripts/create_pr.sh feature/initial-release https://github.com/YOUR_USERNAME/geo-intel-offline.git
```

The script will:
- Add remote repository (if needed)
- Create initial commit (if needed)
- Create feature branch
- Stage and commit all changes
- Push to GitHub
- Provide PR link

### Step 3: Create PR on GitHub

The script will provide a direct link to create the PR. Or manually:
1. Visit your repository on GitHub
2. Click "Compare & pull request" (usually appears after push)
3. PR template will auto-populate
4. Review and submit

---

## Option 2: Manual Steps

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create repository (don't initialize with files)

### Step 2: Add Remote

```bash
git remote add origin https://github.com/YOUR_USERNAME/geo-intel-offline.git
```

### Step 3: Create Feature Branch

```bash
git checkout -b feature/initial-release
```

### Step 4: Stage and Commit

```bash
# Stage all files
git add .

# Create commit
git commit -m "Initial commit: Production-ready offline geo-intelligence library

- 99.92% accuracy across 258 countries
- < 1ms lookup time, < 15MB memory
- Automatic data compression
- Comprehensive documentation
- Full test coverage"
```

### Step 5: Push to GitHub

```bash
# Push initial commit to main/master
git push -u origin master  # or 'main' if that's your default branch

# Push feature branch
git push -u origin feature/initial-release
```

### Step 6: Create PR on GitHub

1. Go to your repository: https://github.com/YOUR_USERNAME/geo-intel-offline
2. Click "Compare & pull request" (or go to Pull Requests → New)
3. Base: `master` (or `main`)
4. Compare: `feature/initial-release`
5. PR template will auto-populate
6. Fill in details and submit

---

## PR Description Template

The PR template (`.github/pull_request_template.md`) will auto-populate. Here's what to include:

```markdown
## Description

Initial release of geo-intel-offline - a production-ready, offline geo-intelligence library.

## Type of Change

- [x] New feature (non-breaking change which adds functionality)

## Testing

- [x] I have tested my changes locally
- [x] I have added tests for my changes
- [x] All existing tests pass (258 countries, 2513 test points, 99.92% accuracy)

## Key Features

- ✅ Offline country resolution (no API calls)
- ✅ 99.92% accuracy across 258 countries
- ✅ < 1ms lookup time
- ✅ < 15MB memory footprint
- ✅ Automatic data compression (66% reduction)
- ✅ Comprehensive documentation
- ✅ Full test coverage
- ✅ GitHub Actions CI/CD setup
- ✅ Ready for PyPI/uv distribution

## Files Changed

- Core library modules
- Complete documentation (README, ARCHITECTURE, TEST_RESULTS)
- GitHub templates (PR, issues)
- CI/CD workflows
- Package configuration (setup.py, pyproject.toml)
```

---

## After Creating PR

1. ✅ Review the PR diff on GitHub
2. ✅ Ensure CI/CD passes (if enabled)
3. ✅ Address any review comments
4. ✅ Merge when ready

---

## Troubleshooting

### Issue: "remote origin already exists"

If you need to update the remote URL:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/geo-intel-offline.git
```

### Issue: "Push failed - authentication required"

Set up authentication:
```bash
# Option 1: Use GitHub CLI
gh auth login

# Option 2: Use personal access token
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/geo-intel-offline.git
```

### Issue: "Repository not found"

- Ensure repository exists on GitHub
- Check repository URL is correct
- Verify you have push access
