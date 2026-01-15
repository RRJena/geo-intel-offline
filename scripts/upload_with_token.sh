#!/bin/bash
#
# Upload to PyPI using API Token
# Usage: bash scripts/upload_with_token.sh [TOKEN]
#

set -e

echo "=" 
echo "PyPI UPLOAD WITH API TOKEN"
echo "="
echo ""

if [ -z "$1" ]; then
    echo "Usage: bash scripts/upload_with_token.sh YOUR_API_TOKEN"
    echo ""
    echo "Get your API token from: https://pypi.org/manage/account/token/"
    echo ""
    echo "The token should start with 'pypi-'"
    exit 1
fi

TOKEN="$1"

if [[ ! "$TOKEN" =~ ^pypi- ]]; then
    echo "⚠️  Warning: Token should start with 'pypi-'"
    echo "Continuing anyway..."
    echo ""
fi

echo "📦 Uploading to PyPI Production..."
echo ""
echo "Using API token authentication"
echo ""

python3 -m twine upload \
    --username __token__ \
    --password "$TOKEN" \
    build/*.whl build/*.tar.gz

echo ""
echo "✅ Upload complete!"
echo ""
echo "Your package is now available at:"
echo "  https://pypi.org/project/geo-intel-offline/"
echo ""
echo "Install with:"
echo "  pip install geo-intel-offline"
echo ""
