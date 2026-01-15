#!/bin/bash
#
# Upload package to PyPI
# Usage: bash scripts/upload_to_pypi.sh [test]
#

set -e

echo "=" 
echo "PyPI UPLOAD SCRIPT"
echo "="
echo ""

if [ "$1" = "test" ]; then
    echo "📦 Uploading to PyPI Test Repository..."
    echo ""
    echo "You'll be prompted for:"
    echo "  • Username: __token__ (if using API token)"
    echo "  • Password: Your PyPI API token"
    echo ""
    echo "Or:"
    echo "  • Username: Your PyPI username"
    echo "  • Password: Your PyPI password"
    echo ""
    python3 -m twine upload --repository testpypi build/*.whl build/*.tar.gz
    echo ""
    echo "✅ Uploaded to PyPI Test!"
    echo "Test install: pip install -i https://test.pypi.org/simple/ geo-intel-offline"
else
    echo "📦 Uploading to PyPI Production..."
    echo ""
    echo "You'll be prompted for:"
    echo "  • Username: __token__ (if using API token)"
    echo "  • Password: Your PyPI API token"
    echo ""
    echo "Or:"
    echo "  • Username: Your PyPI username"
    echo "  • Password: Your PyPI password"
    echo ""
    echo "⚠️  WARNING: This will publish to PyPI production!"
    
    # Skip confirmation if TWINE_SKIP_CONFIRM is set
    if [ -z "$TWINE_SKIP_CONFIRM" ]; then
        echo "Press Ctrl+C to cancel, or Enter to continue..."
        read
    fi
    
    # Use python3 -m twine to ensure we use the installed version
    python3 -m twine upload build/*.whl build/*.tar.gz
    echo ""
    echo "✅ Uploaded to PyPI!"
    echo "Install: pip install geo-intel-offline"
fi

echo ""
echo "=" 
echo ""
