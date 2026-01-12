#!/bin/bash
# Download Natural Earth data for comprehensive testing

set -e

DATA_DIR="data_sources"
mkdir -p "$DATA_DIR"

echo "Downloading Natural Earth Admin 0 Countries..."

# Natural Earth 10m Cultural Vectors - Admin 0 Countries
URL="https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip"

if command -v wget &> /dev/null; then
    wget -O "$DATA_DIR/ne_10m_admin_0_countries.zip" "$URL"
elif command -v curl &> /dev/null; then
    curl -L -o "$DATA_DIR/ne_10m_admin_0_countries.zip" "$URL"
else
    echo "Error: wget or curl required to download data"
    exit 1
fi

echo "Extracting..."
cd "$DATA_DIR"
unzip -o ne_10m_admin_0_countries.zip

echo "✓ Natural Earth data downloaded to $DATA_DIR/"
echo ""
echo "To generate data files, run:"
echo "  python3 -m geo_intel_offline.data_builder $DATA_DIR/ne_10m_admin_0_countries.geojson geo_intel_offline/data"
