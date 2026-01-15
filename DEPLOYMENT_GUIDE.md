# Deployment Guide

This guide will help you:
1. Set up the JavaScript library in a separate GitHub repository
2. Publish to npm
3. Update the Python library repository (excluding JS folder)
4. Ensure all metadata is correct

## Prerequisites

- GitHub account: RRJena
- npm account: rakesh_ranjan_jena_001
- PyPI token: (provided separately)

## Step 1: Create GitHub Repository for JavaScript Library

### Option A: Using GitHub CLI (if installed)

```bash
cd geo_intel_offline_java_script
bash setup_github_repo.sh
```

### Option B: Manual Setup

1. Go to https://github.com/new
2. Repository name: `geo-intel-offline-javascript`
3. Description: `Production-ready, offline geo-intelligence library for JavaScript/TypeScript - 100% accuracy across 258 countries`
4. Make it **Public**
5. **Don't** initialize with README, .gitignore, or license (we already have them)
6. Click "Create repository"

Then run:

```bash
cd geo_intel_offline_java_script
bash setup_github_repo.sh
```

## Step 2: Push JavaScript Library to GitHub

```bash
cd geo_intel_offline_java_script

# Initialize git if not already done
git init
git branch -M main

# Add remote
git remote add origin https://github.com/RRJena/geo-intel-offline-javascript.git

# Add all files
git add .

# Commit
git commit -m "Initial commit: JavaScript/TypeScript version of geo-intel-offline

- 100% accuracy across 258 countries
- Full TypeScript support
- Works in Node.js and browsers
- Comprehensive test coverage"

# Push
git push -u origin main
```

## Step 3: Create GitHub Release

1. Go to: https://github.com/RRJena/geo-intel-offline-javascript/releases/new
2. **Tag**: `v1.0.3`
3. **Title**: `v1.0.3 - Initial Release`
4. **Description**:
   ```
   Initial release of the JavaScript/TypeScript version of geo-intel-offline.
   
   ## Features
   - 100% accuracy across 258 countries
   - Full TypeScript support with type definitions
   - Works in Node.js, browsers, and modern JavaScript environments
   - Comprehensive test coverage
   - Zero dependencies
   
   ## Installation
   ```bash
   npm install geo-intel-offline
   ```
   
   ## Documentation
   See [README.md](https://github.com/RRJena/geo-intel-offline-javascript#readme) for full documentation.
   ```
5. Click "Publish release"

## Step 4: Publish to npm

```bash
cd geo_intel_offline_java_script

# Login to npm
npm login
# Username: rakesh_ranjan_jena_001
# Password: Prince@6234$

# Build the package
npm run build

# Publish
npm publish
```

## Step 5: Update Python Repository (Exclude JS Folder)

The `.gitignore` has been updated to exclude the JavaScript folder. Now commit and push:

```bash
cd /home/king/myWorkspace/geoIntelLib

# Check status
git status

# Add .gitignore update
git add .gitignore

# Commit
git commit -m "Exclude JavaScript library from Python repository

The JavaScript library is now in a separate repository:
https://github.com/RRJena/geo-intel-offline-javascript"

# Push
git push origin main
```

## Step 6: Verify Package Metadata

### Python Package (PyPI)

Check `setup.py` and `pyproject.toml`:
- ✅ Author: Rakesh Ranjan Jena
- ✅ Email: rakesh@rrjprince.com
- ✅ Repository: https://github.com/RRJena/geo-intel-offline

### JavaScript Package (npm)

Check `package.json`:
- ✅ Author: Rakesh Ranjan Jena
- ✅ Repository: https://github.com/RRJena/geo-intel-offline-javascript
- ✅ Homepage: https://github.com/RRJena/geo-intel-offline-javascript#readme

## Step 7: Update PyPI Package (if needed)

If you need to update the Python package metadata:

```bash
# Update version in setup.py and pyproject.toml if needed
# Then build and upload

python3 -m build
twine upload dist/* --token YOUR_PYPI_TOKEN_HERE
```

## Verification Checklist

- [ ] JavaScript repository created: https://github.com/RRJena/geo-intel-offline-javascript
- [ ] JavaScript code pushed to GitHub
- [ ] GitHub release v1.0.3 created
- [ ] npm package published
- [ ] Python repository updated (JS folder excluded)
- [ ] All README files have correct links
- [ ] Author information correct in all packages
- [ ] Blog/website links correct (rrjprince.com, rakeshranjanjena.com)
- [ ] LinkedIn link correct

## Important URLs

### Python Library
- **GitHub**: https://github.com/RRJena/geo-intel-offline
- **PyPI**: https://pypi.org/project/geo-intel-offline/

### JavaScript Library
- **GitHub**: https://github.com/RRJena/geo-intel-offline-javascript
- **npm**: https://www.npmjs.com/package/geo-intel-offline

### Author Information
- **Blog**: https://www.rrjprince.com/
- **Website**: https://www.rakeshranjanjena.com/
- **LinkedIn**: https://www.linkedin.com/in/rrjprince/
